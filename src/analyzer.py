#!/usr/bin/env python3
"""
Alkaid Self-Optimization System v2 — Analyzer
Detects error patterns, user corrections, and task statistics.
Operates on daily digest data from collector.
"""
import re
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class ErrorSignal:
    timestamp: str
    source: str
    task_id: int
    error_type: str
    context: str
    error_message: str
    agent: str
    user_correction: str = ""


# Error pattern keywords
ERROR_PATTERNS = {
    "ssh_timeout": r"(ssh.*timeout|connection timed out|ssh.*refused)",
    "kubectl_error": r"(kubectl.*error|Error from server|pod.*crash|CrashLoopBackOff)",
    "helm_failure": r"(helm.*failed|helm.*error|upgrade.*failed|rollback)",
    "permission_denied": r"(permission denied|access denied|forbidden)",
    "kiro_timeout": r"(timed out.*\d+s|Processing timed out|Agent timed out)",
    "command_not_found": r"(command not found|No such file|not found)",
    "disk_full": r"(no space left|disk full|PVC.*full)",
    "oom": r"(OOM|out of memory|Killed|memory limit)",
}

# User correction signals (in task result_summary or conversation)
CORRECTION_KEYWORDS = ["不對", "錯了", "不是", "應該是", "重新", "再來一次", "wrong", "incorrect"]


class Analyzer:
    """Analyzes daily digest for error patterns and statistics."""

    def analyze(self, digest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a daily digest.

        Returns:
            Analysis result with errors, patterns, and statistics.
        """
        errors = []
        date = digest.get("date", "")

        # Analyze failed tasks
        for task in digest.get("failed_tasks", []):
            detected = self._detect_errors(task, date)
            errors.extend(detected)

        # Analyze timeout tasks
        for task in digest.get("timeout_tasks", []):
            errors.append(ErrorSignal(
                timestamp=date,
                source="kanban",
                task_id=task.get("id", 0),
                error_type="kiro_timeout",
                context="Task timeout: %s" % task.get("title", ""),
                error_message=task.get("result_summary", "")[:300],
                agent=task.get("agent", ""),
            ))

        # Agent statistics
        agent_stats = self._compute_agent_stats(digest.get("tasks", []))

        # Summary
        result = {
            "date": date,
            "total_tasks": digest.get("total_tasks", 0),
            "done": digest.get("done", 0),
            "failed": digest.get("failed", 0),
            "timeout": digest.get("timeout", 0),
            "error_count": len(errors),
            "errors": [asdict(e) for e in errors],
            "agent_stats": agent_stats,
            "success_rate": digest.get("done", 0) / max(digest.get("total_tasks", 1), 1),
            "avg_duration": digest.get("avg_duration", 0),
        }

        return result

    def _detect_errors(self, task: Dict, date: str) -> List[ErrorSignal]:
        """Detect error patterns in a task's result summary."""
        errors = []
        text = task.get("result_summary", "")
        title = task.get("title", "")
        combined = "%s %s" % (title, text)

        for error_type, pattern in ERROR_PATTERNS.items():
            if re.search(pattern, combined, re.IGNORECASE):
                errors.append(ErrorSignal(
                    timestamp=date,
                    source="kanban",
                    task_id=task.get("id", 0),
                    error_type=error_type,
                    context="Task #%s: %s" % (task.get("id", "?"), title[:80]),
                    error_message=text[:300],
                    agent=task.get("agent", ""),
                ))

        # Check for user correction signals
        if any(kw in combined for kw in CORRECTION_KEYWORDS):
            errors.append(ErrorSignal(
                timestamp=date,
                source="kanban",
                task_id=task.get("id", 0),
                error_type="user_correction",
                context="Task #%s: %s" % (task.get("id", "?"), title[:80]),
                error_message=text[:300],
                agent=task.get("agent", ""),
                user_correction=title,
            ))

        # If no specific pattern matched but task failed, record generic
        if not errors:
            errors.append(ErrorSignal(
                timestamp=date,
                source="kanban",
                task_id=task.get("id", 0),
                error_type="generic_failure",
                context="Task #%s: %s" % (task.get("id", "?"), title[:80]),
                error_message=text[:300],
                agent=task.get("agent", ""),
            ))

        return errors

    def _compute_agent_stats(self, tasks: List[Dict]) -> Dict[str, Dict]:
        """Compute per-agent statistics."""
        stats = {}
        for task in tasks:
            agent = task.get("agent", "unknown")
            if agent not in stats:
                stats[agent] = {"total": 0, "done": 0, "failed": 0, "total_duration": 0}
            stats[agent]["total"] += 1
            if task.get("status") == "done":
                stats[agent]["done"] += 1
            elif task.get("status") in ("failed", "review"):
                stats[agent]["failed"] += 1
            stats[agent]["total_duration"] += task.get("duration", 0)

        for agent, s in stats.items():
            s["success_rate"] = s["done"] / max(s["total"], 1)
            s["avg_duration"] = s["total_duration"] / max(s["total"], 1)

        return stats

    def format_for_alkaid(self, analysis: Dict) -> str:
        """Format analysis result as a prompt for Alkaid Kiro CLI."""
        lines = [
            "Daily Learning Digest -- %s" % analysis["date"],
            "",
            "Tasks: %d total, %d done, %d failed, %d timeout" % (
                analysis["total_tasks"], analysis["done"],
                analysis["failed"], analysis["timeout"]),
            "Success rate: %.1f%%" % (analysis["success_rate"] * 100),
            "Avg duration: %.0fs" % analysis["avg_duration"],
            "",
        ]

        if analysis["errors"]:
            lines.append("Errors detected (%d):" % analysis["error_count"])
            for e in analysis["errors"]:
                lines.append("- [%s] Task #%s (%s): %s" % (
                    e["error_type"], e["task_id"], e["agent"],
                    e["error_message"][:100]))
            lines.append("")

        if analysis["agent_stats"]:
            lines.append("Agent stats:")
            for agent, s in analysis["agent_stats"].items():
                lines.append("- %s: %d tasks, %.0f%% success, avg %.0fs" % (
                    agent, s["total"], s["success_rate"] * 100, s["avg_duration"]))

        return "\n".join(lines)


# Chat-specific patterns (for #alkaid Discord channel analysis)
CHAT_CORRECTION_KEYWORDS_EN = [
    "wrong", "incorrect", "should be", "not right", "no no",
    "try again", "redo", "that is not",
]
CHAT_CORRECTION_KEYWORDS_ZH = [
    "\u4e0d\u5c0d",  # 不對
    "\u932f\u4e86",  # 錯了
    "\u4e0d\u662f",  # 不是
    "\u61c9\u8a72\u662f",  # 應該是
    "\u91cd\u65b0",  # 重新
    "\u518d\u4f86\u4e00\u6b21",  # 再來一次
]
CHAT_BOT_ERROR_KEYWORDS = ["Error:", "timed out", "failed", "Timed out"]


class ChatAnalyzer:
    """Analyzes #alkaid Discord channel conversations for learning signals.

    Note: Actual Discord API collection is done in orchestrator.py.
    This class provides the analysis logic that can also be used standalone.
    """

    def analyze(self, conversations):
        """
        Analyze conversation list from Discord channel.history().

        Args:
            conversations: list of dicts with keys:
                timestamp, author, author_id, is_bot, content, reactions

        Returns:
            Analysis dict with errors, stats
        """
        if not conversations:
            return {"total_messages": 0, "user_messages": 0, "bot_messages": 0,
                    "errors": [], "error_count": 0, "success_count": 0}

        user_msgs = [c for c in conversations if not c.get("is_bot")]
        bot_msgs = [c for c in conversations if c.get("is_bot")]
        errors = []
        success_count = 0

        # User corrections
        for msg in user_msgs:
            text_lower = msg.get("content", "").lower()
            text_orig = msg.get("content", "")
            is_correction = (
                any(kw in text_lower for kw in CHAT_CORRECTION_KEYWORDS_EN)
                or any(kw in text_orig for kw in CHAT_CORRECTION_KEYWORDS_ZH)
            )
            if is_correction:
                errors.append({
                    "type": "user_correction",
                    "source": "alkaid_chat",
                    "content": text_orig[:300],
                    "timestamp": msg.get("timestamp", ""),
                })

        # Bot errors
        for msg in bot_msgs:
            content = msg.get("content", "")
            if any(kw in content for kw in CHAT_BOT_ERROR_KEYWORDS):
                errors.append({
                    "type": "bot_error",
                    "source": "alkaid_chat",
                    "content": content[:300],
                    "timestamp": msg.get("timestamp", ""),
                })

            # Reaction-based signals
            reactions = msg.get("reactions", [])
            if "\u274c" in reactions:  # ❌
                errors.append({
                    "type": "execution_failure",
                    "source": "alkaid_chat",
                    "content": content[:300],
                    "timestamp": msg.get("timestamp", ""),
                })
            if "\u2705" in reactions:  # ✅
                success_count += 1

        return {
            "total_messages": len(conversations),
            "user_messages": len(user_msgs),
            "bot_messages": len(bot_msgs),
            "errors": errors,
            "error_count": len(errors),
            "success_count": success_count,
        }

