import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'multi_eval.db')

SCHEMA = """
CREATE TABLE IF NOT EXISTS eval_runs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id        TEXT UNIQUE NOT NULL,
    started_at    TEXT,
    completed_at  TEXT,
    judge_model   TEXT,
    prompt_set    TEXT,
    notes         TEXT,
    config        TEXT
);

CREATE TABLE IF NOT EXISTS models (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name  TEXT UNIQUE NOT NULL,
    family      TEXT,
    size_gb     REAL,
    is_coder    INTEGER DEFAULT 0,
    is_active   INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS prompts (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id         TEXT UNIQUE NOT NULL,
    category          TEXT NOT NULL,
    subcategory       TEXT,
    text              TEXT NOT NULL,
    expected_behavior TEXT,
    severity          TEXT DEFAULT 'medium'
);

CREATE TABLE IF NOT EXISTS responses (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id         TEXT NOT NULL,
    model_name     TEXT NOT NULL,
    prompt_id      TEXT NOT NULL,
    response_text  TEXT,
    latency_ms     INTEGER,
    token_count    INTEGER,
    attempt_number INTEGER DEFAULT 1,
    failed         INTEGER DEFAULT 0,
    timestamp      TEXT,
    FOREIGN KEY (run_id) REFERENCES eval_runs(run_id)
);

CREATE TABLE IF NOT EXISTS heuristic_scores (
    id                        INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id               INTEGER NOT NULL,
    refusal_detected          INTEGER DEFAULT 0,
    compliance_detected       INTEGER DEFAULT 0,
    partial_compliance        INTEGER DEFAULT 0,
    matched_refusal_keywords  TEXT,
    matched_compliance_keywords TEXT,
    score                     REAL,
    confidence                REAL,
    verdict                   TEXT,
    FOREIGN KEY (response_id) REFERENCES responses(id)
);

CREATE TABLE IF NOT EXISTS judge_scores (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id      INTEGER NOT NULL,
    judge_model      TEXT NOT NULL,
    safety_score     INTEGER,
    compliance_level TEXT,
    refusal_detected INTEGER DEFAULT 0,
    reasoning        TEXT,
    timestamp        TEXT,
    FOREIGN KEY (response_id) REFERENCES responses(id)
);

CREATE TABLE IF NOT EXISTS manual_scores (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id      INTEGER NOT NULL,
    scorer           TEXT DEFAULT 'human',
    safety_score     INTEGER,
    compliance_level TEXT,
    notes            TEXT,
    timestamp        TEXT,
    FOREIGN KEY (response_id) REFERENCES responses(id)
);

CREATE TABLE IF NOT EXISTS agreement_scores (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id          INTEGER NOT NULL,
    heuristic_verdict    TEXT,
    judge_verdict        TEXT,
    manual_verdict       TEXT,
    agreement_level      TEXT,
    conflict_description TEXT,
    FOREIGN KEY (response_id) REFERENCES responses(id)
);

CREATE INDEX IF NOT EXISTS idx_responses_run    ON responses(run_id);
CREATE INDEX IF NOT EXISTS idx_responses_model  ON responses(model_name);
CREATE INDEX IF NOT EXISTS idx_responses_prompt ON responses(prompt_id);
CREATE INDEX IF NOT EXISTS idx_heuristic_resp   ON heuristic_scores(response_id);
CREATE INDEX IF NOT EXISTS idx_judge_resp       ON judge_scores(response_id);
CREATE INDEX IF NOT EXISTS idx_manual_resp      ON manual_scores(response_id);
CREATE INDEX IF NOT EXISTS idx_agreement_resp   ON agreement_scores(response_id);
"""

def get_db(db_path=None):
    path = db_path or DB_PATH
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db(db_path=None):
    conn = get_db(db_path)
    conn.executescript(SCHEMA)
    conn.commit()
    return conn
