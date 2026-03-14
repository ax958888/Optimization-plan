#!/usr/bin/env python3
"""
Install Cron Jobs for Alkaid Learning System
"""

import os
import sys
from pathlib import Path


def get_cron_entries():
    """生成 cron 條目"""
    project_path = Path(__file__).parent.parent.absolute()
    scheduler_path = project_path / 'src' / 'scheduler.py'
    python_path = sys.executable
    
    entries = [
        # 每天凌晨 3:00 執行日常分析
        f"0 3 * * * {python_path} {scheduler_path} --mode daily >> ~/.kiro/learning/logs/daily.log 2>&1",
        
        # 每週日凌晨 4:00 執行週報告
        f"0 4 * * 0 {python_path} {scheduler_path} --mode weekly >> ~/.kiro/learning/logs/weekly.log 2>&1",
    ]
    
    return entries


def install_cron():
    """安裝 cron 任務"""
    print("📅 Installing cron jobs for Alkaid Learning System")
    print("="*60)
    
    entries = get_cron_entries()
    
    # 顯示即將安裝的任務
    print("\nCron entries to be installed:")
    for entry in entries:
        print(f"  {entry}")
    
    # 確認
    response = input("\nProceed with installation? (y/n): ")
    if response.lower() != 'y':
        print("❌ Installation cancelled")
        return
    
    # 創建日誌目錄
    log_dir = Path.home() / '.kiro' / 'learning' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 獲取現有 crontab
    from subprocess import run, PIPE
    
    result = run(['crontab', '-l'], stdout=PIPE, stderr=PIPE, text=True)
    existing_cron = result.stdout if result.returncode == 0 else ""
    
    # 移除舊的 Alkaid 條目
    lines = [line for line in existing_cron.split('\n') 
             if 'scheduler.py' not in line]
    
    # 添加新條目
    lines.extend(entries)
    
    # 寫入新的 crontab
    new_cron = '\n'.join(lines) + '\n'
    
    result = run(['crontab', '-'], input=new_cron, text=True, 
                 stdout=PIPE, stderr=PIPE)
    
    if result.returncode == 0:
        print("✅ Cron jobs installed successfully")
        print("\nVerify with: crontab -l | grep scheduler")
    else:
        print(f"❌ Failed to install cron jobs: {result.stderr}")
        sys.exit(1)


def main():
    """主函數"""
    try:
        install_cron()
    except KeyboardInterrupt:
        print("\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
