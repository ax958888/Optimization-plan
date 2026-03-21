#!/usr/bin/env python3
"""
Alkaid Self-Optimization System v2 — Collector
Collects daily task data from Kanban SQLite + Kiro conversations.
Also collects #alkaid Discord channel conversations via channel.history() API.
Runs inside Kanban Bot at 23:30 Taipei.

Note: The Discord API chat collection (_collect_alkaid_conversations) is
implemented directly in orchestrator.py since it requires the Bot instance
for channel.history() access. This module handles the file-based sources.
"""
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any

TZ_TAIPEI = timezone(timedelta(hours=8))


class Collector:
    """Collects daily task and conversation data."""

    def __init__(self, kanban_db_path: str, memory_path: str, output_dir: str):
        self.kanban_db_path = Path(kanban_db_path)
        self.memory_path = Path(memory_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def collect_daily(self, date: str = None) -> Dict[str, Any]:
        """
        Collect all data for a given date.

        Args:
            date: YYYY-MM-DD string, defaults to today (Taipei)

        Returns:
            Daily digest dict
        """
        if date is None:
            date = datetime.now(TZ_TAIPEI).strftime("%Y-%m-%d")

        tasks = self._get_tasks_by_date(date)
        conversations = self._get_recent_conversations(hours=24)

        done = [t for t in tasks if t["status"] == "done"]
        failed = [t for t in tasks if t["status"] == "failed"]
        timeout = [t for t in tasks if t["status"] in ("review", "timeout")]

        digest = {
            "date": date,
            "collected_at": datetime.now(TZ_TAIPEI).isoformat(),
            "total_tasks": len(tasks),
            "done": len(done),
            "failed": len(failed),
            "timeout": len(timeout),
            "total_conversations": len(conversations),
            "tasks": [self._task_summary(t) for t in tasks],
            "failed_tasks": [self._task_detail(t) for t in failed],
            "timeout_tasks": [self._task_detail(t) for t in timeout],
            "avg_duration": self._avg_duration(done),
        }

        # Save to file
        output_file = self.output_dir / ("%s.json" % date)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(digest, f, ensure_ascii=False, indent=2)

        return digest

    def _get_tasks_by_date(self, date: str) -> List[Dict]:
        """Query Kanban SQLite for tasks completed/failed on a given date."""
        if not self.kanban_db_path.exists():
            return []
        conn = sqlite3.connect(str(self.kanban_db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE date(completed_at) = ? OR date(created_at) = ? "
            "ORDER BY id",
            (date, date),
        )
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def _get_recent_conversations(self, hours: int = 24) -> List[Dict]:
        """Read recent conversations from Kiro JSONL."""
        if not self.memory_path.exists():
            return []
        cutoff = datetime.now(TZ_TAIPEI) - timedelta(hours=hours)
        conversations = []
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        conv = json.loads(line)
                        ts = conv.get("timestamp", "")
                        if ts and ts >= cutoff.isoformat():
                            conversations.append(conv)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        return conversations

    def _task_summary(self, task: Dict) -> Dict:
        return {
            "id": task.get("id"),
            "title": task.get("title", ""),
            "status": task.get("status", ""),
            "agent": task.get("assigned_agent", ""),
            "duration": task.get("duration_seconds", 0),
        }

    def _task_detail(self, task: Dict) -> Dict:
        summary = self._task_summary(task)
        summary["result_summary"] = (task.get("result_summary") or "")[:500]
        summary["github_issue"] = task.get("github_issue_number")
        return summary

    def _avg_duration(self, tasks: List[Dict]) -> float:
        durations = [t.get("duration_seconds", 0) for t in tasks if t.get("duration_seconds")]
        return sum(durations) / len(durations) if durations else 0.0


if __name__ == "__main__":
    from config import KANBAN_DB_PATH, MEMORY_PATH, DAILY_DIR

    collector = Collector(str(KANBAN_DB_PATH), str(MEMORY_PATH), str(DAILY_DIR))
    digest = collector.collect_daily()
    print(json.dumps(digest, ensure_ascii=False, indent=2))
