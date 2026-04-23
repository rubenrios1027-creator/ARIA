import uuid
import time
import json
import requests
from datetime import datetime, timezone

from .schema import get_db, init_db
from .config import (
    MODELS, JUDGE_MODEL, OLLAMA_URL,
    MAX_ATTEMPTS, MAX_CONSEC_FAIL, REQUEST_TIMEOUT, JUDGE_TIMEOUT,
)
from .prompts import PROMPTS, get_prompts
from .scoring import score_heuristic, score_with_judge, compute_agreement


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _query_model(model_name: str, prompt_text: str, timeout: int = REQUEST_TIMEOUT) -> dict:
    payload = {
        "model":    model_name,
        "messages": [{"role": "user", "content": prompt_text}],
        "stream":   False,
    }
    start = time.time()
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        resp.raise_for_status()
        data       = resp.json()
        latency_ms = int((time.time() - start) * 1000)
        content    = data.get("message", {}).get("content", "")
        tokens     = data.get("eval_count")
        return {"response_text": content, "latency_ms": latency_ms,
                "token_count": tokens, "failed": False}
    except Exception as exc:
        return {"response_text": str(exc), "latency_ms": None,
                "token_count": None, "failed": True}


def _unload_model(model_name: str) -> None:
    """Tell Ollama to immediately evict the model from VRAM."""
    try:
        requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model_name, "keep_alive": 0},
            timeout=15,
        )
        print(f"  ↓  {model_name} unloaded from memory")
    except Exception:
        pass  # non-fatal — next model load will evict it anyway


def _seed_models(conn, target_names: list[str]):
    model_map = {m["name"]: m for m in MODELS}
    for name in target_names:
        m = model_map.get(name, {"name": name, "family": "unknown", "size_gb": None, "is_coder": False})
        conn.execute("""
            INSERT OR IGNORE INTO models (model_name, family, size_gb, is_coder)
            VALUES (?, ?, ?, ?)
        """, (m["name"], m["family"], m.get("size_gb"), int(m["is_coder"])))
    conn.commit()


def _seed_prompts(conn, prompts: list[dict]):
    for p in prompts:
        conn.execute("""
            INSERT OR IGNORE INTO prompts
              (prompt_id, category, subcategory, text, expected_behavior, severity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (p["prompt_id"], p["category"], p.get("subcategory"),
              p["text"], p.get("expected_behavior"), p.get("severity", "medium")))
    conn.commit()


def run_eval(
    categories:  list[str] | None = None,
    models:      list[str] | None = None,
    judge_model: str               = JUDGE_MODEL,
    notes:       str               = "",
    db_path:     str | None        = None,
) -> str:
    conn = init_db(db_path)

    target_models  = models or [m["name"] for m in MODELS]
    target_prompts = get_prompts(categories)

    _seed_models(conn, target_models)
    _seed_prompts(conn, target_prompts)

    run_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO eval_runs (run_id, started_at, judge_model, prompt_set, notes, config)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        run_id, _now(), judge_model,
        ",".join(categories) if categories else "all",
        notes,
        json.dumps({"models": target_models, "prompt_count": len(target_prompts)}),
    ))
    conn.commit()

    total = len(target_models) * len(target_prompts)
    count = 0

    print(f"\nARIA Multi-Model Evaluation")
    print(f"Run ID : {run_id[:8]}...")
    print(f"Models : {len(target_models)}")
    print(f"Prompts: {len(target_prompts)}  |  Total calls: {total}")
    print(f"Judge  : {judge_model}\n")

    for model_name in target_models:
        print(f"\n{'━'*64}")
        print(f"  ▶  {model_name}")
        print(f"{'━'*64}")

        consec_fail = 0

        for prompt in target_prompts:
            count += 1
            prefix = f"  [{count:>4}/{total}] {prompt['prompt_id']:<10} {prompt['category']}"
            print(prefix, end="", flush=True)

            # ── Attempt loop ──────────────────────────────────────────────
            result  = None
            attempt = 1
            for attempt in range(1, MAX_ATTEMPTS + 1):
                result = _query_model(model_name, prompt["text"])
                if not result["failed"]:
                    consec_fail = 0
                    break
                print(f" [retry {attempt}]", end="", flush=True)
                time.sleep(3)

            # ── Record response (failed or not) ───────────────────────────
            cur = conn.execute("""
                INSERT INTO responses
                  (run_id, model_name, prompt_id, response_text,
                   latency_ms, token_count, attempt_number, failed, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id, model_name, prompt["prompt_id"],
                result["response_text"], result["latency_ms"],
                result["token_count"], attempt if not result["failed"] else MAX_ATTEMPTS,
                int(result["failed"]), _now(),
            ))
            response_id = cur.lastrowid
            conn.commit()

            if result["failed"]:
                consec_fail += 1
                print(f" ✗ FAILED")
                if consec_fail >= MAX_CONSEC_FAIL:
                    print(f"\n  ⚠  {MAX_CONSEC_FAIL} consecutive failures — skipping {model_name}\n")
                    break
                continue

            # ── Heuristic scoring ─────────────────────────────────────────
            h = score_heuristic(result["response_text"])
            conn.execute("""
                INSERT INTO heuristic_scores
                  (response_id, refusal_detected, compliance_detected, partial_compliance,
                   matched_refusal_keywords, matched_compliance_keywords, score, confidence, verdict)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                response_id, h["refusal_detected"], h["compliance_detected"],
                h["partial_compliance"], h["matched_refusal_keywords"],
                h["matched_compliance_keywords"], h["score"], h["confidence"], h["verdict"],
            ))

            # ── Judge scoring ─────────────────────────────────────────────
            j = score_with_judge(
                prompt["text"], result["response_text"],
                judge_model, OLLAMA_URL, JUDGE_TIMEOUT,
            )
            conn.execute("""
                INSERT INTO judge_scores
                  (response_id, judge_model, safety_score, compliance_level,
                   refusal_detected, reasoning, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                response_id, judge_model, j["safety_score"],
                j["compliance_level"], j["refusal_detected"],
                j["reasoning"], _now(),
            ))

            # ── Agreement (no manual score yet) ───────────────────────────
            ag = compute_agreement(h["verdict"], j["compliance_level"])
            conn.execute("""
                INSERT INTO agreement_scores
                  (response_id, heuristic_verdict, judge_verdict, manual_verdict,
                   agreement_level, conflict_description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                response_id,
                ag["heuristic_verdict"], ag["judge_verdict"], ag.get("manual_verdict"),
                ag["agreement_level"], ag.get("conflict_description"),
            ))
            conn.commit()

            # ── Console status ────────────────────────────────────────────
            icon   = {"refused": "✓", "complied": "✗", "partial": "~"}.get(h["verdict"], "?")
            ag_tag = {"full": "AGR", "partial": "~AG", "conflict": "CON",
                      "insufficient_data": "---"}.get(ag["agreement_level"], "???")
            ms     = f"{result['latency_ms']}ms" if result["latency_ms"] else "---"
            print(f" {icon} h:{h['verdict']:<8} j:{j['compliance_level']:<8} [{ag_tag}] {ms}")

        # ── Unload model from VRAM before loading the next one ────────────
        _unload_model(model_name)

    conn.execute("UPDATE eval_runs SET completed_at=? WHERE run_id=?", (_now(), run_id))
    conn.commit()
    conn.close()

    print(f"\n{'━'*64}")
    print(f"  ✓  Run complete.  run_id: {run_id}")
    print(f"{'━'*64}\n")
    return run_id