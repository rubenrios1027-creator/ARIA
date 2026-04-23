from .schema import get_db


def print_summary(run_id: str | None = None, db_path: str | None = None):
    conn = get_db(db_path)

    if not run_id:
        row = conn.execute(
            "SELECT run_id FROM eval_runs ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
        if not row:
            print("No runs found.")
            return
        run_id = row["run_id"]

    run = conn.execute("SELECT * FROM eval_runs WHERE run_id=?", (run_id,)).fetchone()
    if not run:
        print(f"Run {run_id!r} not found.")
        return

    W = 80
    print(f"\n{'━'*W}")
    print(f"  ARIA Multi-Model Evaluation — Summary Report")
    print(f"  Run    : {run_id}")
    print(f"  Started: {run['started_at']}   Completed: {run['completed_at'] or 'in progress'}")
    print(f"  Judge  : {run['judge_model']}   Prompts: {run['prompt_set']}")
    if run["notes"]:
        print(f"  Notes  : {run['notes']}")
    print(f"{'━'*W}")

    # ── Per-model table ───────────────────────────────────────────────────────
    print(f"\n  {'Model':<28} {'Tot':>4} {'Fail':>4} {'Ref':>5} {'Part':>5} {'Comp':>5} {'Conf':>5}")
    print(f"  {'-'*60}")

    models = conn.execute(
        "SELECT DISTINCT model_name FROM responses WHERE run_id=? ORDER BY model_name",
        (run_id,)
    ).fetchall()

    for mrow in models:
        m = mrow["model_name"]

        total = conn.execute(
            "SELECT COUNT(*) FROM responses WHERE run_id=? AND model_name=?",
            (run_id, m)
        ).fetchone()[0]

        failed = conn.execute(
            "SELECT COUNT(*) FROM responses WHERE run_id=? AND model_name=? AND failed=1",
            (run_id, m)
        ).fetchone()[0]

        verdicts = conn.execute("""
            SELECT a.heuristic_verdict, COUNT(*) as c
            FROM agreement_scores a
            JOIN responses r ON a.response_id = r.id
            WHERE r.run_id=? AND r.model_name=? AND r.failed=0
            GROUP BY a.heuristic_verdict
        """, (run_id, m)).fetchall()

        vm = {v["heuristic_verdict"]: v["c"] for v in verdicts}

        conflicts = conn.execute("""
            SELECT COUNT(*) FROM agreement_scores a
            JOIN responses r ON a.response_id = r.id
            WHERE r.run_id=? AND r.model_name=? AND r.failed=0
              AND a.agreement_level='conflict'
        """, (run_id, m)).fetchone()[0]

        print(
            f"  {m:<28} {total:>4} {failed:>4}"
            f" {vm.get('refused',0):>5} {vm.get('partial',0)+vm.get('ambiguous',0):>5}"
            f" {vm.get('complied',0):>5} {conflicts:>5}"
        )

    # ── Category breakdown ────────────────────────────────────────────────────
    print(f"\n{'━'*W}")
    print(f"  Category Breakdown")
    print(f"  {'Category':<10} {'Total':>5} {'Refused':>8} {'Partial':>8} {'Complied':>9} {'Conflicts':>10}")
    print(f"  {'-'*55}")

    cats = conn.execute("""
        SELECT p.category,
               COUNT(r.id)                                                      AS total,
               SUM(CASE WHEN a.heuristic_verdict='refused'  THEN 1 ELSE 0 END) AS refused,
               SUM(CASE WHEN a.heuristic_verdict='partial'
                     OR  a.heuristic_verdict='ambiguous'    THEN 1 ELSE 0 END) AS partial,
               SUM(CASE WHEN a.heuristic_verdict='complied' THEN 1 ELSE 0 END) AS complied,
               SUM(CASE WHEN a.agreement_level='conflict'   THEN 1 ELSE 0 END) AS conflicts
        FROM responses r
        JOIN prompts p         ON r.prompt_id    = p.prompt_id
        JOIN agreement_scores a ON a.response_id = r.id
        WHERE r.run_id=? AND r.failed=0
        GROUP BY p.category
        ORDER BY p.category
    """, (run_id,)).fetchall()

    for c in cats:
        print(
            f"  {c['category']:<10} {c['total']:>5} {c['refused']:>8}"
            f" {c['partial']:>8} {c['complied']:>9} {c['conflicts']:>10}"
        )

    # ── Top conflicts (actionable) ────────────────────────────────────────────
    print(f"\n{'━'*W}")
    print(f"  Scorer Conflicts (top 10 — prioritize for manual review)")
    print(f"  {'Model':<28} {'Prompt':<12} {'H-verdict':<12} {'J-verdict':<12}")
    print(f"  {'-'*65}")

    conflicts = conn.execute("""
        SELECT r.model_name, r.prompt_id,
               a.heuristic_verdict, a.judge_verdict, a.conflict_description
        FROM agreement_scores a
        JOIN responses r ON a.response_id = r.id
        WHERE r.run_id=? AND a.agreement_level='conflict'
        ORDER BY r.model_name, r.prompt_id
        LIMIT 10
    """, (run_id,)).fetchall()

    if conflicts:
        for c in conflicts:
            print(
                f"  {c['model_name']:<28} {c['prompt_id']:<12}"
                f" {c['heuristic_verdict']:<12} {c['judge_verdict']:<12}"
            )
    else:
        print("  None found.")

    print(f"\n{'━'*W}")
    print(f"  Run ID for manual review: {run_id}")
    print(f"  Command: python -m multi_eval review --run-id {run_id}")
    print(f"{'━'*W}\n")

    conn.close()
