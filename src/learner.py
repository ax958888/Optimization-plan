#!/usr/bin/env python3
"""
Alkaid Learning System - Learner Module
學習引擎：調用 LLM 分析錯誤，生成改進建議
"""

import json
import sqlite3
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path


class Learner:
    """學習引擎"""
    
    SYSTEM_PROMPT = """你是 Alkaid AI Agent 的學習系統。
你的任務是分析對話記錄中的錯誤和模式，提取可操作的改進建議。

輸出格式（JSON）：
{
  "insights": [
    {
      "type": "rule|skill|prompt|script",
      "title": "簡短標題",
      "problem": "具體描述當前問題",
      "solution": "具體的改進措施",
      "expected_impact": "量化的預期效果",
      "impact_score": 0.0-1.0
    }
  ]
}

要求：
1. 每個建議必須具體、可執行
2. 優先解決高頻錯誤
3. 避免過於通用的建議
4. impact_score 基於錯誤頻率和影響範圍計算
"""
    
    def __init__(self, db_path: Path = None):
        """初始化學習器"""
        if db_path is None:
            db_path = Path.home() / '.kiro' / 'learning' / 'insights.db'
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
    
    def analyze(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        分析錯誤並生成改進建議
        
        Args:
            analysis_results: Analyzer 的輸出結果
            
        Returns:
            改進建議列表
        """
        errors = analysis_results.get('errors', [])
        
        if not errors:
            print("✅ No errors to analyze")
            return []
        
        print(f"🧠 Analyzing {len(errors)} errors...")
        
        # 構建 LLM prompt
        prompt = self._build_analysis_prompt(errors)
        
        # TODO: 調用 OpenAI API
        # 這裡先返回模擬數據
        insights = self._mock_llm_analysis(errors)
        
        # 保存到資料庫
        for insight in insights:
            self._save_insight(insight)
        
        print(f"✅ Generated {len(insights)} improvement suggestions")
        return insights
    
    def _build_analysis_prompt(self, errors: List[Dict]) -> str:
        """構建分析 Prompt"""
        error_summary = []
        for e in errors[:10]:  # 最多分析 10 個錯誤
            error_summary.append(f"- {e['error_type']}: {e['error_message'][:100]}")
        
        return f"""
請分析以下錯誤記錄，提取改進建議：

## 錯誤列表
{chr(10).join(error_summary)}

## 統計
總錯誤數: {len(errors)}

請生成 3-5 條改進建議。
"""
    
    def _mock_llm_analysis(self, errors: List[Dict]) -> List[Dict[str, Any]]:
        """模擬 LLM 分析（用於測試）"""
        # 統計錯誤類型
        error_types = {}
        for e in errors:
            error_type = e['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        insights = []
        
        # 針對最常見錯誤生成建議
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:3]:
            if error_type == 'ssh_timeout':
                insights.append({
                    'type': 'rule',
                    'title': 'SSH 連線檢查規則',
                    'problem': f'SSH 超時錯誤出現 {count} 次',
                    'solution': '在執行 SSH 指令前先運行 `ssh -o BatchMode=yes hetzner "uptime"` 檢查連線狀態',
                    'expected_impact': f'預計減少 {int(count * 0.8)} 次超時錯誤（80%）',
                    'impact_score': min(count / len(errors), 1.0)
                })
            
            elif error_type == 'kubectl_error':
                insights.append({
                    'type': 'skill',
                    'title': 'Kubectl 錯誤處理 Skill',
                    'problem': f'Kubectl 命令失敗 {count} 次',
                    'solution': '創建新 skill 處理常見 kubectl 錯誤，包含重試邏輯和友好錯誤提示',
                    'expected_impact': f'提升 kubectl 操作成功率 20%',
                    'impact_score': min(count / len(errors), 1.0)
                })
            
            elif error_type == 'user_correction':
                insights.append({
                    'type': 'prompt',
                    'title': '優化回應準確性',
                    'problem': f'用戶修正 {count} 次',
                    'solution': '在 IDENTITY.md 中添加：回答前先確認理解用戶意圖，複雜任務需列出執行計劃',
                    'expected_impact': f'減少用戶修正次數 50%',
                    'impact_score': min(count / len(errors) * 1.2, 1.0)
                })
        
        return insights
    
    def _save_insight(self, insight: Dict[str, Any]):
        """保存改進建議到資料庫"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO improvements (type, title, problem, solution, expected_impact, impact_score, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
        """, (
            insight['type'],
            insight['title'],
            insight['problem'],
            insight['solution'],
            insight['expected_impact'],
            insight['impact_score'],
            datetime.now().isoformat()
        ))
        self.conn.commit()
    
    def get_pending_insights(self) -> List[Dict[str, Any]]:
        """獲取待審核的改進建議"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM improvements 
            WHERE status = 'pending' 
            ORDER BY impact_score DESC, created_at DESC
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        
        return results
    
    def approve_insight(self, insight_id: int):
        """批准改進建議"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE improvements 
            SET status = 'approved', approved_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), insight_id))
        self.conn.commit()
        print(f"✅ Insight #{insight_id} approved")
    
    def reject_insight(self, insight_id: int, reason: str = ""):
        """拒絕改進建議"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE improvements 
            SET status = 'rejected'
            WHERE id = ?
        """, (insight_id,))
        self.conn.commit()
        print(f"❌ Insight #{insight_id} rejected")
    
    def __del__(self):
        """清理連接"""
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Alkaid Learning Engine')
    parser.add_argument('--review', action='store_true', help='Review pending insights')
    parser.add_argument('--approve', type=int, help='Approve insight by ID')
    parser.add_argument('--reject', type=int, help='Reject insight by ID')
    parser.add_argument('--count-pending', action='store_true', help='Count pending insights')
    
    args = parser.parse_args()
    
    learner = Learner()
    
    if args.review:
        insights = learner.get_pending_insights()
        print(f"\n📋 Pending Insights: {len(insights)}")
        print("="*60)
        for ins in insights:
            print(f"\n[#{ins['id']}] {ins['title']} ({ins['type']})")
            print(f"  Impact Score: {ins['impact_score']:.2f}")
            print(f"  Problem: {ins['problem']}")
            print(f"  Solution: {ins['solution'][:100]}...")
    
    elif args.approve:
        learner.approve_insight(args.approve)
    
    elif args.reject:
        learner.reject_insight(args.reject)
    
    elif args.count_pending:
        count = len(learner.get_pending_insights())
        print(f"Pending insights: {count}")


if __name__ == '__main__':
    main()
