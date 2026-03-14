-- Alkaid Learning System Database Schema

-- 錯誤記錄表
CREATE TABLE IF NOT EXISTS errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    conversation_id TEXT,
    error_type TEXT NOT NULL,
    context TEXT,
    error_message TEXT,
    user_correction TEXT,
    status TEXT DEFAULT 'unprocessed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_errors_timestamp ON errors(timestamp);
CREATE INDEX IF NOT EXISTS idx_errors_status ON errors(status);
CREATE INDEX IF NOT EXISTS idx_errors_type ON errors(error_type);

-- 模式記錄表
CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL,
    description TEXT,
    frequency INTEGER DEFAULT 1,
    success_rate REAL,
    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    example_conversations TEXT,
    learned_response TEXT
);

CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_patterns_frequency ON patterns(frequency DESC);

-- 改進建議表
CREATE TABLE IF NOT EXISTS improvements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    problem TEXT,
    solution TEXT,
    expected_impact TEXT,
    impact_score REAL DEFAULT 0.0,
    source_error_ids TEXT,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME,
    applied_at DATETIME
);

CREATE INDEX IF NOT EXISTS idx_improvements_status ON improvements(status);
CREATE INDEX IF NOT EXISTS idx_improvements_score ON improvements(impact_score DESC);
CREATE INDEX IF NOT EXISTS idx_improvements_created ON improvements(created_at DESC);

-- 變更記錄表
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

CREATE INDEX IF NOT EXISTS idx_changes_improvement ON changes(improvement_id);
CREATE INDEX IF NOT EXISTS idx_changes_applied ON changes(applied_at DESC);

-- 統計數據表
CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    total_conversations INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    correction_count INTEGER DEFAULT 0,
    avg_response_time REAL DEFAULT 0.0,
    success_rate REAL DEFAULT 0.0,
    llm_cost REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_statistics_date ON statistics(date);

-- 任務分解模板表
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
