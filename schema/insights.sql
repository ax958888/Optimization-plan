-- Alkaid Self-Optimization System v2 — Database Schema
-- Location: /root/.kiro/learning/insights.db

-- 錯誤記錄表 (from analyzer)
CREATE TABLE IF NOT EXISTS errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    date TEXT NOT NULL,
    source TEXT DEFAULT 'kanban',
    task_id INTEGER,
    conversation_id TEXT,
    error_type TEXT NOT NULL,
    context TEXT,
    error_message TEXT,
    user_correction TEXT,
    agent TEXT,
    status TEXT DEFAULT 'unprocessed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_errors_date ON errors(date);
CREATE INDEX IF NOT EXISTS idx_errors_status ON errors(status);
CREATE INDEX IF NOT EXISTS idx_errors_type ON errors(error_type);

-- 模式記錄表 (from analyzer)
CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL,
    description TEXT,
    frequency INTEGER DEFAULT 1,
    success_rate REAL,
    agent TEXT,
    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    example_tasks TEXT,
    learned_response TEXT
);

CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type);

-- 改進建議表 (from Kiro CLI learner)
CREATE TABLE IF NOT EXISTS improvements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    problem TEXT,
    solution TEXT,
    expected_impact TEXT,
    impact_score REAL DEFAULT 0.0,
    source_error_ids TEXT,
    source_task_ids TEXT,
    agent TEXT DEFAULT 'alkaid',
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME,
    applied_at DATETIME
);

CREATE INDEX IF NOT EXISTS idx_improvements_status ON improvements(status);
CREATE INDEX IF NOT EXISTS idx_improvements_score ON improvements(impact_score DESC);

-- 變更記錄表 (rollback support)
CREATE TABLE IF NOT EXISTS changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    improvement_id INTEGER,
    change_type TEXT NOT NULL,
    target_file TEXT,
    diff TEXT,
    rollback_data TEXT,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (improvement_id) REFERENCES improvements(id)
);

CREATE INDEX IF NOT EXISTS idx_changes_applied ON changes(applied_at DESC);

-- 每日統計表
CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    total_tasks INTEGER DEFAULT 0,
    done_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    timeout_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    correction_count INTEGER DEFAULT 0,
    avg_duration_seconds REAL DEFAULT 0.0,
    success_rate REAL DEFAULT 0.0,
    new_learnings INTEGER DEFAULT 0,
    qmd_files_added INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_statistics_date ON statistics(date);

-- 每日摘要表
CREATE TABLE IF NOT EXISTS daily_digests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    digest_json TEXT NOT NULL,
    analysis_json TEXT,
    learning_output TEXT,
    archive_message_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_digests_date ON daily_digests(date);

-- 任務分解模板表 (Phase 4)
CREATE TABLE IF NOT EXISTS task_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL,
    keywords TEXT,
    subtask_template TEXT,
    success_count INTEGER DEFAULT 0,
    avg_completion_time REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used DATETIME
);

CREATE INDEX IF NOT EXISTS idx_templates_type ON task_templates(task_type);
CREATE INDEX IF NOT EXISTS idx_templates_success ON task_templates(success_count DESC);
