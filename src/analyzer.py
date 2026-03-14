#!/usr/bin/env python3
"""
Alkaid Learning System - Analyzer Module
對話分析器：解析 conversations.jsonl，識別錯誤模式和學習信號
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ErrorSignal:
    """錯誤信號數據類"""
    timestamp: str
    conversation_id: str
    error_type: str
    context: str
    error_message: str
    user_correction: Optional[str] = None


@dataclass
class Pattern:
    """模式數據類"""
    pattern_type: str
    description: str
    frequency: int
    success_rate: float
    examples: List[str]


class Analyzer:
    """對話分析器"""
    
    # 錯誤關鍵詞匹配
    ERROR_PATTERNS = {
        'ssh_timeout': r'(ssh.*timeout|connection timed out)',
        'kubectl_error': r'(kubectl.*error|Error from server)',
        'command_not_found': r'(command not found|No such file)',
        'permission_denied': r'(permission denied|access denied)',
        'connection_refused': r'(connection refused|unable to connect)',
    }
    
    # 用戶修正信號
    CORRECTION_KEYWORDS = ['不對', '錯了', '不是', '應該是', '重新', '再來一次']
    
    def __init__(self, memory_path: str = None):
        """
        初始化分析器
        
        Args:
            memory_path: conversations.jsonl 文件路徑
        """
        if memory_path is None:
            memory_path = Path.home() / '.kiro' / 'memory' / 'conversations.jsonl'
        self.memory_path = Path(memory_path)
        
    def read_conversations(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        讀取最近 N 小時的對話記錄
        
        Args:
            hours: 讀取最近多少小時的對話
            
        Returns:
            對話記錄列表
        """
        if not self.memory_path.exists():
            print(f"⚠️  Memory file not found: {self.memory_path}")
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        conversations = []
        
        try:
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        conv = json.loads(line)
                        # 檢查時間戳
                        conv_time = datetime.fromisoformat(conv.get('timestamp', ''))
                        if conv_time >= cutoff_time:
                            conversations.append(conv)
        except Exception as e:
            print(f"❌ Error reading conversations: {e}")
            return []
        
        return conversations
    
    def detect_errors(self, conversations: List[Dict[str, Any]]) -> List[ErrorSignal]:
        """
        檢測對話中的錯誤信號
        
        Args:
            conversations: 對話記錄列表
            
        Returns:
            錯誤信號列表
        """
        errors = []
        
        for conv in conversations:
            conv_id = conv.get('id', str(datetime.now().timestamp()))
            timestamp = conv.get('timestamp', datetime.now().isoformat())
            user_msg = conv.get('user_message', '')
            assistant_resp = conv.get('assistant_response', '')
            context = conv.get('context', {})
            
            # 檢查錯誤模式
            for error_type, pattern in self.ERROR_PATTERNS.items():
                if re.search(pattern, assistant_resp, re.IGNORECASE):
                    errors.append(ErrorSignal(
                        timestamp=timestamp,
                        conversation_id=conv_id,
                        error_type=error_type,
                        context=json.dumps(context),
                        error_message=assistant_resp[:500],  # 截取前 500 字符
                        user_correction=None
                    ))
            
            # 檢查用戶修正信號
            if any(keyword in user_msg for keyword in self.CORRECTION_KEYWORDS):
                errors.append(ErrorSignal(
                    timestamp=timestamp,
                    conversation_id=conv_id,
                    error_type='user_correction',
                    context=json.dumps(context),
                    error_message=assistant_resp[:500],
                    user_correction=user_msg[:300]
                ))
        
        return errors
    
    def identify_patterns(self, conversations: List[Dict[str, Any]]) -> List[Pattern]:
        """
        識別對話模式
        
        Args:
            conversations: 對話記錄列表
            
        Returns:
            模式列表
        """
        patterns = []
        
        # 統計任務類型
        task_types = {}
        for conv in conversations:
            user_msg = conv.get('user_message', '')
            
            # 簡單的任務分類
            if 'openclaw' in user_msg.lower():
                task_type = 'openclaw_management'
            elif 'ssh' in user_msg.lower():
                task_type = 'ssh_command'
            elif 'kubectl' in user_msg.lower():
                task_type = 'kubectl_command'
            else:
                task_type = 'general_query'
            
            if task_type not in task_types:
                task_types[task_type] = {'count': 0, 'examples': []}
            
            task_types[task_type]['count'] += 1
            if len(task_types[task_type]['examples']) < 3:
                task_types[task_type]['examples'].append(user_msg[:100])
        
        # 生成模式
        for task_type, data in task_types.items():
            patterns.append(Pattern(
                pattern_type=task_type,
                description=f"Task type: {task_type}",
                frequency=data['count'],
                success_rate=0.9,  # TODO: 實際計算成功率
                examples=data['examples']
            ))
        
        return patterns
    
    def analyze_recent(self, hours: int = 24) -> Dict[str, Any]:
        """
        分析最近 N 小時的對話
        
        Args:
            hours: 分析最近多少小時
            
        Returns:
            分析結果字典
        """
        print(f"📊 Analyzing conversations from the last {hours} hours...")
        
        conversations = self.read_conversations(hours)
        print(f"📝 Found {len(conversations)} conversations")
        
        if not conversations:
            return {'errors': [], 'patterns': [], 'statistics': {}}
        
        errors = self.detect_errors(conversations)
        print(f"🔍 Detected {len(errors)} error signals")
        
        patterns = self.identify_patterns(conversations)
        print(f"🧩 Identified {len(patterns)} patterns")
        
        # 統計數據
        statistics = {
            'total_conversations': len(conversations),
            'error_count': len(errors),
            'correction_count': sum(1 for e in errors if e.error_type == 'user_correction'),
            'success_rate': 1 - (len(errors) / len(conversations)) if conversations else 0
        }
        
        return {
            'errors': [vars(e) for e in errors],
            'patterns': [vars(p) for p in patterns],
            'statistics': statistics
        }


def main():
    """命令行測試入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Alkaid Conversation Analyzer')
    parser.add_argument('--hours', type=int, default=24, help='Analyze last N hours')
    parser.add_argument('--test', action='store_true', help='Run test mode')
    parser.add_argument('--input', type=str, help='Custom input file')
    
    args = parser.parse_args()
    
    analyzer = Analyzer(memory_path=args.input)
    results = analyzer.analyze_recent(hours=args.hours)
    
    # 輸出結果
    print("\n" + "="*60)
    print("📊 Analysis Results")
    print("="*60)
    print(f"Total Conversations: {results['statistics']['total_conversations']}")
    print(f"Errors Found: {results['statistics']['error_count']}")
    print(f"User Corrections: {results['statistics']['correction_count']}")
    print(f"Success Rate: {results['statistics']['success_rate']:.1%}")
    
    if results['errors']:
        print("\n🔴 Top Errors:")
        for i, error in enumerate(results['errors'][:5], 1):
            print(f"  {i}. {error['error_type']} at {error['timestamp']}")
    
    if results['patterns']:
        print("\n🧩 Patterns:")
        for pattern in results['patterns']:
            print(f"  • {pattern['pattern_type']}: {pattern['frequency']} occurrences")


if __name__ == '__main__':
    main()
