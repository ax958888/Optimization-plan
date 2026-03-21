#!/usr/bin/env python3
"""
Alkaid Self-Optimization System v2 — Learner
Drives Kiro CLI alkaid agent to analyze errors and write learnings.
Replaces v1's OpenAI API calls with native Kiro CLI.
"""
import asyncio
import json
import sqlite3
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any

TZ_TAIPEI = timezone(timedelta(hours=8))


class Learner:
    """Learning engine powered by Kiro CLI alkaid agent."""

    def __init__(self, insights_db_path: str, kiro_cli_path: str = "/root/.local/bin/kiro-cli",
                 kiro_agent: str = "alkaid", kiro_timeout: int = 300):
        self.db_path = Path(insights_db_path)
        self.kiro_cli = kiro_cli_path
        self.kiro_agent = kiro_agent
        self.kiro_timeout = kiro_timeout

    async def learn_from_analysis(self, analysis: Dict, formatted_prompt: str) -> str:
        """
        Send analysis to Kiro CLI alkaid agent for learning.
        The agent will autonomously:
        - Read .learnings/ via pre-check skill
        - QMD search for dedup
        - Write ERRORS.md and LEARNINGS.md
        - Output analysis report

        Returns:
            Kiro CLI output (analysis report)
        """
        prompt = (
            "You received a Daily Learning Digest. Execute the learning workflow:\n\n"
            "%s\n\n"
            "Steps:\n"
            "1. For each failed/timeout task, identify the root cause\n"
            "2. Run: qmd search \"{error_keyword}\" -c alkaid (check if already known)\n"
            "3. If NEW problem: append to /root/.kiro/.learnings/ERRORS.md\n"
            "4. Extract general solution: append to /root/.kiro/.learnings/LEARNINGS.md\n"
            "5. Run: qmd embed -c alkaid (update vector index)\n"
            "6. Output analysis report in Traditional Chinese:\n"
            "   - Today's statistics\n"
            "   - New learnings (what was learned)\n"
            "   - Known issues (already in .learnings/)\n"
            "   - Improvement suggestions\n"
        ) % formatted_prompt

        try:
            proc = await asyncio.create_subprocess_exec(
                self.kiro_cli, "chat",
                "--agent", self.kiro_agent,
                "--no-interactive", "--trust-all-tools",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/root",
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=prompt.encode("utf-8")),
                timeout=self.kiro_timeout,
            )
            output = stdout.decode("utf-8", errors="replace")
            clean = self._clean_kiro_output(output)
            return clean or "(No output from Kiro CLI)"
        except asyncio.TimeoutError:
            return "Kiro CLI timed out (%ds)" % self.kiro_timeout
        except Exception as e:
            return "Kiro CLI error: %s" % str(e)

    def save_errors_to_db(self, errors: List[Dict]):
        """Save detected errors to insights.db."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        for e in errors:
            cursor.execute(
                "INSERT INTO errors (timestamp, date, source, task_id, error_type, "
                "context, error_message, agent, user_correction, status) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'unprocessed')",
                (e.get("timestamp", ""), e.get("timestamp", "")[:10], e.get("source", "kanban"),
                 e.get("task_id", 0), e.get("error_type", "unknown"),
                 e.get("context", ""), e.get("error_message", ""),
                 e.get("agent", ""), e.get("user_correction", "")),
            )
        conn.commit()
        conn.close()

    def save_statistics(self, analysis: Dict):
        """Save daily statistics to insights.db."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO statistics "
            "(date, total_tasks, done_count, failed_count, timeout_count, "
            "error_count, success_rate, avg_duration_seconds) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (analysis.get("date", ""), analysis.get("total_tasks", 0),
             analysis.get("done", 0), analysis.get("failed", 0),
             analysis.get("timeout", 0), analysis.get("error_count", 0),
             analysis.get("success_rate", 0), analysis.get("avg_duration", 0)),
        )
        conn.commit()
        conn.close()

    def get_weekly_statistics(self) -> List[Dict]:
        """Get last 7 days of statistics."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM statistics ORDER BY date DESC LIMIT 7"
        )
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return list(reversed(rows))

    def count_pending_improvements(self) -> int:
        """Count pending improvements."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM improvements WHERE status = 'pending'")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def _clean_kiro_output(self, raw: str) -> str:
        """Clean ANSI codes and Kiro boilerplate from output."""
        ansi = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        clean = ansi.sub("", raw)
        lines = []
        skip = ["All tools are now trusted", "Learn more at",
                "Credits:", "Time:", "Successfully", "Completed in"]
        for line in clean.strip().split("\n"):
            s = line.strip()
            if not s:
                continue
            if any(p in line for p in skip):
                continue
            if line.startswith("> "):
                line = line[2:]
            lines.append(line)
        return "\n".join(lines).strip()
