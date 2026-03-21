#!/usr/bin/env python3
"""
Alkaid Self-Optimization System v2 — Configuration
Reads from environment or uses CPX31 defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
KIRO_PATH = Path(os.getenv("KIRO_PATH", "/root/.kiro"))
MEMORY_PATH = Path(os.getenv("MEMORY_PATH", "/root/.kiro/memory/conversations.jsonl"))
LEARNING_PATH = Path(os.getenv("LEARNING_PATH", "/root/.kiro/learning"))
LEARNINGS_PATH = Path(os.getenv("LEARNINGS_PATH", "/root/.kiro/.learnings"))
KANBAN_DB_PATH = Path(os.getenv("KANBAN_DB_PATH", "/root/kanban-kiro-bot/data/kanban.db"))
INSIGHTS_DB_PATH = Path(os.getenv("INSIGHTS_DB_PATH", "/root/.kiro/learning/insights.db"))
DAILY_DIR = LEARNING_PATH / "daily"

# Discord
ALKAID_CHANNEL_ID = int(os.getenv("ALKAID_CHANNEL_ID", "1484560345405063289"))
ARCHIVE_CHANNEL_ID = int(os.getenv("ARCHIVE_CHANNEL_ID", "1484434683528744980"))
ALKAID_BOT_ID = int(os.getenv("ALKAID_BOT_ID", "1484557430443610163"))
KANBAN_BOT_ID = int(os.getenv("KANBAN_BOT_ID", "1484372402078093352"))

# GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "ax958888/VPS-Kanban-Agent")

# QMD
QMD_BINARY = os.getenv("QMD_BINARY", "/usr/bin/qmd")
QMD_COLLECTION = os.getenv("QMD_COLLECTION", "alkaid")
QMD_DEDUP_THRESHOLD = float(os.getenv("QMD_DEDUP_THRESHOLD", "0.85"))

# Kiro CLI
KIRO_CLI_PATH = os.getenv("KIRO_CLI_PATH", "/root/.local/bin/kiro-cli")
KIRO_AGENT = os.getenv("KIRO_AGENT", "alkaid")
KIRO_TIMEOUT = int(os.getenv("KIRO_TIMEOUT", "300"))

# Schedule
DAILY_ANALYSIS_HOUR = int(os.getenv("DAILY_ANALYSIS_HOUR", "23"))
DAILY_ANALYSIS_MINUTE = int(os.getenv("DAILY_ANALYSIS_MINUTE", "30"))
WEEKLY_REPORT_DAY = int(os.getenv("WEEKLY_REPORT_DAY", "6"))  # 0=Mon, 6=Sun
PROMPT_OPTIMIZE_THRESHOLD = int(os.getenv("PROMPT_OPTIMIZE_THRESHOLD", "5"))

# Limits
MAX_TASKS_PER_ANALYSIS = int(os.getenv("MAX_TASKS_PER_ANALYSIS", "50"))
MAX_CONVERSATIONS_PER_ANALYSIS = int(os.getenv("MAX_CONVERSATIONS_PER_ANALYSIS", "100"))
MAX_DAILY_DIGEST_RETENTION_DAYS = int(os.getenv("MAX_DAILY_DIGEST_RETENTION_DAYS", "30"))
