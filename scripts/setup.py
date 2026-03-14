#!/usr/bin/env python3
"""
Setup Script - Initialize Learning System
"""

import sqlite3
import sys
from pathlib import Path


def init_database(db_path: Path):
    """初始化 SQLite 資料庫"""
    print(f"📦 Initializing database at {db_path}")
    
    # 讀取 schema
    schema_path = Path(__file__).parent.parent / 'schema' / 'insights.sql'
    
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        return False
    
    try:
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executescript(schema)
        conn.commit()
        conn.close()
        
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False


def create_directories(base_path: Path):
    """創建必要的目錄結構"""
    dirs = [
        base_path,
        base_path / 'logs',
        base_path / 'drafts',
        base_path / 'backups',
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {d}")


def main():
    """主函數"""
    print("🚀 Alkaid Learning System Setup")
    print("="*60)
    
    # 確定基礎路徑
    base_path = Path.home() / '.kiro' / 'learning'
    
    # 創建目錄
    create_directories(base_path)
    
    # 初始化資料庫
    db_path = base_path / 'insights.db'
    if not init_database(db_path):
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")
    print(f"📂 Learning path: {base_path}")
    print(f"💾 Database: {db_path}")
    print("\nNext steps:")
    print("1. Configure .env file with API keys")
    print("2. Run: python3 src/analyzer.py --test")
    print("3. Install cron: python3 scripts/install_cron.py")


if __name__ == '__main__':
    main()
