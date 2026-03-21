#!/usr/bin/env python3
"""
Alkaid Self-Optimization System v2 — Notifier
Sends learning digests and reports to Discord channels.
Replaces v1 Telegram notifier.
"""
import discord
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

TZ_TAIPEI = timezone(timedelta(hours=8))


class DiscordNotifier:
    """Sends embeds to #archive and messages to #alkaid."""

    def __init__(self, bot, archive_channel_id: int, alkaid_channel_id: int):
        self.bot = bot
        self.archive_channel_id = archive_channel_id
        self.alkaid_channel_id = alkaid_channel_id

    async def send_daily_digest_embed(self, analysis: Dict, learning_output: str = ""):
        """Send Daily Learning Digest embed to #archive."""
        channel = self.bot.get_channel(self.archive_channel_id)
        if not channel:
            return

        date = analysis.get("date", "?")
        done = analysis.get("done", 0)
        failed = analysis.get("failed", 0)
        timeout = analysis.get("timeout", 0)
        total = analysis.get("total_tasks", 0)
        error_count = analysis.get("error_count", 0)
        rate = analysis.get("success_rate", 0)

        if failed > 0 or timeout > 0:
            color = 0xF39C12  # orange
        elif total == 0:
            color = 0x95A5A6  # gray
        else:
            color = 0x2ECC71  # green

        desc_lines = []
        if learning_output:
            # Take first 300 chars of learning output as summary
            desc_lines.append(learning_output[:300])
        if not desc_lines:
            desc_lines.append("No tasks to analyze today." if total == 0 else "All tasks completed successfully.")

        embed = discord.Embed(
            title="Daily Learning Digest -- %s" % date,
            description="\n".join(desc_lines),
            color=color,
        )
        embed.add_field(name="Tasks", value="%d total" % total, inline=True)
        embed.add_field(name="Done", value=str(done), inline=True)
        embed.add_field(name="Failed", value=str(failed), inline=True)
        embed.add_field(name="Timeout", value=str(timeout), inline=True)
        embed.add_field(name="Errors", value=str(error_count), inline=True)
        embed.add_field(name="Success Rate", value="%.1f%%" % (rate * 100), inline=True)

        now = datetime.now(TZ_TAIPEI).strftime("%Y-%m-%d %H:%M")
        embed.set_footer(text="%s (Taipei)" % now)

        try:
            msg = await channel.send(embed=embed)
            return str(msg.id)
        except Exception:
            return None

    async def send_weekly_report_embed(self, weekly_stats: List[Dict], summary: str):
        """Send Weekly Report embed to #archive."""
        channel = self.bot.get_channel(self.archive_channel_id)
        if not channel:
            return

        now = datetime.now(TZ_TAIPEI)
        week_end = now.strftime("%Y-%m-%d")

        total_tasks = sum(s.get("total_tasks", 0) for s in weekly_stats)
        total_done = sum(s.get("done_count", 0) for s in weekly_stats)
        total_failed = sum(s.get("failed_count", 0) for s in weekly_stats)
        overall_rate = total_done / max(total_tasks, 1)

        embed = discord.Embed(
            title="Weekly Learning Report -- w/e %s" % week_end,
            description=summary[:400] if summary else "Weekly summary",
            color=0x3498DB,  # blue
        )
        embed.add_field(name="Total Tasks", value=str(total_tasks), inline=True)
        embed.add_field(name="Done", value=str(total_done), inline=True)
        embed.add_field(name="Failed", value=str(total_failed), inline=True)
        embed.add_field(name="Success Rate", value="%.1f%%" % (overall_rate * 100), inline=True)

        # Per-day breakdown
        if weekly_stats:
            day_lines = []
            for s in weekly_stats:
                day_lines.append("%s: %d tasks, %.0f%%" % (
                    s.get("date", "?")[-5:],
                    s.get("total_tasks", 0),
                    s.get("success_rate", 0) * 100))
            embed.add_field(name="Daily Breakdown", value="\n".join(day_lines), inline=False)

        embed.set_footer(text="%s (Taipei)" % now.strftime("%Y-%m-%d %H:%M"))

        try:
            await channel.send(embed=embed)
        except Exception:
            pass
