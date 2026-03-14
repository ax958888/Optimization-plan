#!/usr/bin/env python3
"""
Configuration Management
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """配置管理類"""
    
    # OpenAI API
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    OPENAI_TIMEOUT: int = int(os.getenv('OPENAI_TIMEOUT', '60'))
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # Paths
    KIRO_PATH: Path = Path(os.getenv('KIRO_PATH', Path.home() / '.kiro'))
    MEMORY_PATH: Path = Path(os.getenv('MEMORY_PATH', KIRO_PATH / 'memory' / 'conversations.jsonl'))
    LEARNING_PATH: Path = Path(os.getenv('LEARNING_PATH', KIRO_PATH / 'learning'))
    
    # Learning Parameters
    ANALYSIS_INTERVAL: str = os.getenv('ANALYSIS_INTERVAL', 'daily')
    MAX_INSIGHTS_PER_DAY: int = int(os.getenv('MAX_INSIGHTS_PER_DAY', '10'))
    DEDUP_THRESHOLD: float = float(os.getenv('DEDUP_THRESHOLD', '0.85'))
    AUTO_APPLY: bool = os.getenv('AUTO_APPLY', 'false').lower() == 'true'
    
    # GitHub
    GITHUB_TOKEN: str = os.getenv('GITHUB_TOKEN', '')
    GITHUB_REPO: str = os.getenv('GITHUB_REPO', '')
    
    @classmethod
    def validate(cls) -> bool:
        """驗證必需的配置是否存在"""
        if not cls.OPENAI_API_KEY:
            print("❌ OPENAI_API_KEY not set")
            return False
        return True
