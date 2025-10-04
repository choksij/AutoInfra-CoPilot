
CREATE DATABASE IF NOT EXISTS autoinfra;

USE autoinfra;

CREATE TABLE IF NOT EXISTS runs
(
    run_id           String,
    repo             String,
    pr_number        UInt32,
    commit_sha       String,
    status           LowCardinality(String),    -- running/completed/failed
    duration_ms      UInt32,
    cost_usd_month   Float64,
    created_at       DateTime DEFAULT now()
)
ENGINE = MergeTree
ORDER BY (created_at, run_id)
TTL created_at + INTERVAL 30 DAY
SETTINGS index_granularity = 8192;

CREATE TABLE IF NOT EXISTS findings
(
    run_id     String,
    idx        UInt32,                          -- position in list (for stable ordering)
    tool       LowCardinality(String),          -- "policy" | "checkov" | ...
    rule_id    String,
    severity   LowCardinality(String),          -- LOW/MEDIUM/HIGH/CRITICAL
    file       String,
    line       UInt32,
    message    String,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree
ORDER BY (run_id, idx)
TTL created_at + INTERVAL 30 DAY;

CREATE TABLE IF NOT EXISTS outcomes
(
    run_id         String,
    issues_before  UInt32,
    issues_after   UInt32,
    policy_before  UInt32,
    policy_after   UInt32,
    safe_to_merge  UInt8,                       -- 1 = true, 0 = false
    created_at     DateTime DEFAULT now()
)
ENGINE = MergeTree
ORDER BY (created_at, run_id)
TTL created_at + INTERVAL 30 DAY;

CREATE TABLE IF NOT EXISTS patch_library
(
    run_id        String,
    patch_md      String,
    accepted      Nullable(UInt8),              -- NULL = unknown, 1 = accepted, 0 = rejected
    created_at    DateTime DEFAULT now()
)
ENGINE = MergeTree
ORDER BY (created_at, run_id)
TTL created_at + INTERVAL 30 DAY;

CREATE VIEW IF NOT EXISTS recent_runs AS
SELECT
    run_id,
    repo,
    pr_number,
    commit_sha,
    status,
    duration_ms,
    cost_usd_month,
    created_at
FROM runs
ORDER BY created_at DESC;
