#!/usr/bin/env python3
"""
Alkaid Self-Optimization System v2 — Scheduler
Designed to run inside Kanban Bot as a discord.ext.tasks loop.
NOT a standalone cron job.

This module provides the scheduling logic that should be integrated
into kanban-kiro-bot/services/orchestrator.py
"""


INTEGRATION_GUIDE = """
# Integration into Kanban Bot

Add the following to kanban-kiro-bot/services/orchestrator.py:

```python
from discord.ext import tasks
from datetime import datetime, timezone, timedelta

TZ_TAIPEI = timezone(timedelta(hours=8))

class Orchestrator:
    # ... existing code ...

    @tasks.loop(seconds=30)
    async def daily_digest_scheduler(self):
        now = datetime.now(TZ_TAIPEI)
        # Daily at 23:30 Taipei
        if now.hour == 23 and now.minute == 30:
            await self._generate_daily_digest()
        # Weekly report on Sunday at 23:30
        if now.hour == 23 and now.minute == 30 and now.weekday() == 6:
            await self._generate_weekly_report()

    @daily_digest_scheduler.before_loop
    async def before_digest_scheduler(self):
        await self.bot.wait_until_ready()

    async def _generate_daily_digest(self):
        from src.collector import Collector
        from src.analyzer import Analyzer
        from src.notifier import DiscordNotifier

        collector = Collector(
            kanban_db_path=DB_PATH,
            memory_path=MEMORY_PATH,
            output_dir=DAILY_DIR,
        )
        digest = collector.collect_daily()

        if digest['total_tasks'] == 0:
            return  # Skip if no tasks today

        analyzer = Analyzer()
        analysis = analyzer.analyze(digest)

        # @mention Alkaid in #alkaid with digest
        alkaid_channel = self.bot.get_channel(ALKAID_CHANNEL_ID)
        formatted = analyzer.format_for_alkaid(analysis)
        await alkaid_channel.send(
            "<@%d> Daily Learning Digest\\n```\\n%s\\n```"
            % (ALKAID_BOT_ID, formatted)
        )

    async def _generate_weekly_report(self):
        from src.learner import Learner
        from src.notifier import DiscordNotifier

        learner = Learner(insights_db_path=INSIGHTS_DB_PATH)
        stats = learner.get_weekly_statistics()

        notifier = DiscordNotifier(
            self.bot, ARCHIVE_CHANNEL_ID, ALKAID_CHANNEL_ID)
        await notifier.send_weekly_report_embed(stats, "Weekly auto-report")

        # Create GitHub Issue
        # ... (use GitHubAPI from alkaid-bot or aiohttp directly)
```

Then in bot.py, start the scheduler:
```python
bot.orchestrator.daily_digest_scheduler.start()
```
"""

if __name__ == "__main__":
    print(INTEGRATION_GUIDE)
