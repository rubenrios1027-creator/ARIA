-- ARIA Multi-Eval Analysis Queries
-- Run these in any SQLite client (DB Browser for SQLite, DBeaver, etc.)
-- or from Python: conn.execute(query).fetchall()
--
-- All queries are parameterized by :run_id or return latest-run data.


-- ── Overview ──────────────────────────────────────────────────────────────────

-- Compliance rate per model (heuristic verdict)
SELECT
    r.model_name,
    COUNT(*)                                                      AS total,
    ROUND(AVG(CASE WHEN a.heuristic_verdict='refused'  THEN 1.0 ELSE 0.0 END)*100,1) AS refused_pct,
    ROUND(AVG(CASE WHEN a.heuristic_verdict='partial'  THEN 1.0 ELSE 0.0 END)*100,1) AS partial_pct,
    ROUND(AVG(CASE WHEN a.heuristic_verdict='complied' THEN 1.0 ELSE 0.0 END)*100,1) AS complied_pct
FROM responses r
JOIN agreement_scores a ON a.response_id = r.id
WHERE r.run_id = :run_id AND r.failed = 0
GROUP BY r.model_name
ORDER BY complied_pct DESC;


-- Average heuristic score per model (0=safe, 1=harmful)
SELECT
    r.model_name,
    ROUND(AVG(h.score), 3)      AS avg_harm_score,
    ROUND(AVG(h.confidence), 3) AS avg_confidence,
    COUNT(*)                    AS n
FROM responses r
JOIN heuristic_scores h ON h.response_id = r.id
WHERE r.run_id = :run_id AND r.failed = 0
GROUP BY r.model_name
ORDER BY avg_harm_score DESC;


-- Average judge safety score per model (1=safe, 5=harmful)
SELECT
    r.model_name,
    ROUND(AVG(j.safety_score), 2) AS avg_judge_score,
    COUNT(*)                      AS n
FROM responses r
JOIN judge_scores j ON j.response_id = r.id
WHERE r.run_id = :run_id AND r.failed = 0 AND j.safety_score IS NOT NULL
GROUP BY r.model_name
ORDER BY avg_judge_score DESC;


-- ── Category breakdown ─────────────────────────────────────────────────────────

-- Compliance by category across all models
SELECT
    p.category,
    p.severity,
    COUNT(*)                                                            AS total,
    SUM(CASE WHEN a.heuristic_verdict='complied' THEN 1 ELSE 0 END)   AS complied,
    SUM(CASE WHEN a.agreement_level='conflict'   THEN 1 ELSE 0 END)   AS scorer_conflicts,
    ROUND(AVG(h.score)*100,1)                                          AS avg_harm_pct
FROM responses r
JOIN prompts          p ON r.prompt_id    = p.prompt_id
JOIN agreement_scores a ON a.response_id  = r.id
JOIN heuristic_scores h ON h.response_id  = r.id
WHERE r.run_id = :run_id AND r.failed = 0
GROUP BY p.category
ORDER BY avg_harm_pct DESC;


-- Heatmap data: model × category compliance rate
SELECT
    r.model_name,
    p.category,
    COUNT(*)                                                            AS n,
    ROUND(AVG(CASE WHEN a.heuristic_verdict='complied' THEN 1.0 ELSE 0.0 END)*100,1) AS complied_pct
FROM responses r
JOIN prompts          p ON r.prompt_id    = p.prompt_id
JOIN agreement_scores a ON a.response_id  = r.id
WHERE r.run_id = :run_id AND r.failed = 0
GROUP BY r.model_name, p.category
ORDER BY r.model_name, p.category;


-- ── Scoring agreement ──────────────────────────────────────────────────────────

-- Agreement level distribution
SELECT
    a.agreement_level,
    COUNT(*) AS n,
    ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM agreement_scores a2
        JOIN responses r2 ON a2.response_id=r2.id
        WHERE r2.run_id=:run_id AND r2.failed=0), 1) AS pct
FROM agreement_scores a
JOIN responses r ON a.response_id = r.id
WHERE r.run_id = :run_id AND r.failed = 0
GROUP BY a.agreement_level;


-- All conflict rows (heuristic says refused, judge says complied or vice versa)
SELECT
    r.model_name,
    r.prompt_id,
    p.category,
    p.severity,
    a.heuristic_verdict,
    a.judge_verdict,
    a.manual_verdict,
    a.conflict_description,
    h.score            AS h_score,
    j.safety_score     AS j_score,
    LEFT(r.response_text, 200) AS response_preview
FROM agreement_scores a
JOIN responses        r ON a.response_id = r.id
JOIN prompts          p ON r.prompt_id   = p.prompt_id
JOIN heuristic_scores h ON h.response_id = r.id
JOIN judge_scores     j ON j.response_id = r.id
WHERE r.run_id=:run_id AND a.agreement_level='conflict'
ORDER BY p.severity, r.model_name;


-- ── Family / size analysis ─────────────────────────────────────────────────────

-- Compliance rate by model family
SELECT
    m.family,
    COUNT(DISTINCT r.model_name)                                        AS model_count,
    COUNT(r.id)                                                         AS total_responses,
    ROUND(AVG(CASE WHEN a.heuristic_verdict='complied' THEN 1.0 ELSE 0.0 END)*100,1) AS complied_pct,
    ROUND(AVG(CASE WHEN a.heuristic_verdict='refused'  THEN 1.0 ELSE 0.0 END)*100,1) AS refused_pct
FROM responses r
JOIN models           m ON m.model_name  = r.model_name
JOIN agreement_scores a ON a.response_id = r.id
WHERE r.run_id = :run_id AND r.failed = 0
GROUP BY m.family
ORDER BY complied_pct DESC;


-- Coder vs general-purpose compliance
SELECT
    CASE m.is_coder WHEN 1 THEN 'coder' ELSE 'general' END AS model_type,
    COUNT(r.id)                                             AS total,
    ROUND(AVG(CASE WHEN a.heuristic_verdict='complied' THEN 1.0 ELSE 0.0 END)*100,1) AS complied_pct
FROM responses r
JOIN models           m ON m.model_name  = r.model_name
JOIN agreement_scores a ON a.response_id = r.id
WHERE r.run_id = :run_id AND r.failed = 0
GROUP BY m.is_coder;


-- ── Performance ────────────────────────────────────────────────────────────────

-- Average latency and token count per model
SELECT
    model_name,
    ROUND(AVG(latency_ms))  AS avg_latency_ms,
    ROUND(AVG(token_count)) AS avg_tokens,
    MAX(latency_ms)         AS max_latency_ms,
    COUNT(*)                AS n
FROM responses
WHERE run_id = :run_id AND failed = 0
GROUP BY model_name
ORDER BY avg_latency_ms DESC;


-- ── Manual review progress ─────────────────────────────────────────────────────

-- How many responses still need manual review
SELECT
    r.model_name,
    COUNT(r.id)                                      AS total,
    COUNT(ms.id)                                     AS manually_scored,
    COUNT(r.id) - COUNT(ms.id)                       AS remaining
FROM responses r
LEFT JOIN manual_scores ms ON ms.response_id = r.id
WHERE r.run_id = :run_id AND r.failed = 0
GROUP BY r.model_name
ORDER BY remaining DESC;
