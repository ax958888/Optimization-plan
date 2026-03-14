#!/usr/bin/env python3
"""
Alkaid Learning System - Scheduler Module
調度器：管理定時任務和工作流編排
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加 src 到 Python path
sys.path.insert(0, str(Path(__file__).parent))

from analyzer import Analyzer
from learner import Learner
from config import Config


class Scheduler:
    """任務調度器"""
    
    def __init__(self):
        """初始化調度器"""
        if not Config.validate():
            raise ValueError("Configuration validation failed")
        
        self.analyzer = Analyzer()
        self.learner = Learner()
    
    def daily_analysis(self):
        """每日分析流程"""
        print("="*60)
        print(f"🔍 Daily Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 1. 分析最近 24 小時對話
        print("\n[1/3] Analyzing conversations...")
        results = self.analyzer.analyze_recent(hours=24)
        
        if not results['errors'] and not results['patterns']:
            print("✅ No errors found - system running smoothly!")
            return
        
        # 2. 調用學習引擎
        print("\n[2/3] Generating insights...")
        insights = self.learner.analyze(results)
        
        # 3. 發送通知
        print("\n[3/3] Sending notification...")
        if insights:
            self._send_notification(insights)
        
        print("\n✅ Daily analysis completed")
        print(f"   Generated {len(insights)} improvement suggestions")
        print("   Run `python3 src/learner.py --review` to review")
    
    def weekly_optimization(self):
        """每週優化流程"""
        print("="*60)
        print(f"📊 Weekly Optimization - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 1. 統計本週數據
        print("\n[1/3] Collecting weekly statistics...")
        results = self.analyzer.analyze_recent(hours=24*7)
        
        # 2. 生成週報
        print("\n[2/3] Generating weekly report...")
        self._generate_weekly_report(results)
        
        # 3. 發送通知
        print("\n[3/3] Sending weekly summary...")
        print("✅ Weekly optimization completed")
    
    def _send_notification(self, insights: list):
        """發送 Telegram 通知"""
        # TODO: 實現 Telegram 通知
        print(f"📱 [Mock] Telegram notification sent: {len(insights)} new insights")
    
    def _generate_weekly_report(self, results: dict):
        """生成週報"""
        stats = results['statistics']
        
        report = f"""
# 📊 Alkaid 學習週報

**時間**: {datetime.now().strftime('%Y-%m-%d')}

## 統計數據
- 總對話數: {stats['total_conversations']}
- 錯誤次數: {stats['error_count']}
- 用戶修正: {stats['correction_count']}
- 成功率: {stats['success_rate']:.1%}

## 發現的模式
{len(results['patterns'])} 個常見任務類型

## 下週建議
繼續觀察錯誤模式，優化高頻任務處理流程。
"""
        
        print(report)
        
        # 保存到文件
        report_path = Config.LEARNING_PATH / 'reports' / f'weekly_{datetime.now().strftime("%Y%m%d")}.md'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report)
        print(f"📄 Report saved to: {report_path}")


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Alkaid Task Scheduler')
    parser.add_argument('--mode', choices=['daily', 'weekly'], default='daily',
                       help='Execution mode')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run without saving')
    
    args = parser.parse_args()
    
    try:
        scheduler = Scheduler()
        
        if args.mode == 'daily':
            scheduler.daily_analysis()
        elif args.mode == 'weekly':
            scheduler.weekly_optimization()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
