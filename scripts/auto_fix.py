#!/usr/bin/env python3
"""
Auto-Fix Script - Automatically diagnose and fix agent issues
"""

import sys
import subprocess
import argparse
from datetime import datetime


class AutoFix:
    """自動修復系統"""
    
    def __init__(self, agent_name, ssh_host="hetzner", ssh_key="~/.ssh/hetzner_key"):
        self.agent_name = agent_name
        self.ssh_host = ssh_host
        self.ssh_key = ssh_key
    
    def run_ssh(self, command):
        """執行 SSH 命令"""
        full_cmd = f"ssh -i {self.ssh_key} -o BatchMode=yes {self.ssh_host} \"{command}\""
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    
    def check_process(self):
        """檢查 Agent 進程狀態"""
        print(f"🔍 Checking {self.agent_name} process...")
        
        stdout, stderr, code = self.run_ssh(f"ps aux | grep {self.agent_name} | grep -v grep")
        
        if code == 0 and stdout:
            print(f"✅ Process running")
            return True, stdout
        else:
            print(f"❌ Process not found")
            return False, None
    
    def check_memory(self):
        """檢查記憶體使用"""
        print("🔍 Checking memory usage...")
        
        stdout, _, _ = self.run_ssh("free -m | grep Mem")
        if stdout:
            parts = stdout.split()
            total = int(parts[1])
            used = int(parts[2])
            percent = (used / total) * 100
            
            print(f"📊 Memory: {used}MB / {total}MB ({percent:.1f}%)")
            
            if percent > 90:
                print(f"⚠️  High memory usage detected!")
                return False, percent
            return True, percent
        return True, 0
    
    def check_logs(self):
        """檢查最近的日誌"""
        print("🔍 Checking recent logs...")
        
        stdout, _, _ = self.run_ssh(f"tail -50 ~/.kiro/learning/logs/daily.log 2>/dev/null || echo 'No logs found'")
        
        # 檢查常見錯誤模式
        errors = []
        if "MemoryError" in stdout:
            errors.append("Memory allocation error")
        if "Connection refused" in stdout:
            errors.append("Connection issues")
        if "timeout" in stdout.lower():
            errors.append("Timeout errors")
        
        if errors:
            print(f"❌ Found errors: {', '.join(errors)}")
            return False, errors
        else:
            print(f"✅ No errors in recent logs")
            return True, []
    
    def diagnose(self):
        """完整診斷"""
        print("="*60)
        print(f"🏥 Diagnosing {self.agent_name} Agent")
        print("="*60)
        
        issues = []
        
        # 檢查進程
        process_ok, process_info = self.check_process()
        if not process_ok:
            issues.append(("process", "Process not running"))
        
        # 檢查記憶體
        memory_ok, memory_usage = self.check_memory()
        if not memory_ok:
            issues.append(("memory", f"Memory usage at {memory_usage:.1f}%"))
        
        # 檢查日誌
        logs_ok, errors = self.check_logs()
        if not logs_ok:
            for error in errors:
                issues.append(("log_error", error))
        
        return issues
    
    def suggest_fixes(self, issues):
        """建議修復方案"""
        print("\n" + "="*60)
        print("💡 Recommended Solutions")
        print("="*60)
        
        solutions = []
        
        for issue_type, description in issues:
            if issue_type == "process":
                solutions.append({
                    "id": 1,
                    "title": "Restart Agent",
                    "command": f"systemctl restart {self.agent_name} || pkill -f {self.agent_name} && python3 /root/kiro-telegram-bot/bot.py &",
                    "risk": "low"
                })
            
            elif issue_type == "memory":
                solutions.append({
                    "id": 2,
                    "title": "Restart to Free Memory",
                    "command": f"systemctl restart {self.agent_name}",
                    "risk": "low"
                })
                solutions.append({
                    "id": 3,
                    "title": "Check Memory Leaks",
                    "command": f"ps aux --sort=-%mem | head -10",
                    "risk": "none"
                })
            
            elif issue_type == "log_error":
                if "Memory" in description:
                    solutions.append({
                        "id": 4,
                        "title": "Implement Batch Processing",
                        "command": "echo 'See LEARNINGS.md [2026-03-14 16:45]'",
                        "risk": "none"
                    })
        
        for sol in solutions:
            print(f"\n[{sol['id']}] {sol['title']}")
            print(f"    Command: {sol['command']}")
            print(f"    Risk: {sol['risk']}")
        
        return solutions
    
    def apply_fix(self, solution):
        """應用修復方案"""
        print(f"\n⚙️  Applying: {solution['title']}")
        
        stdout, stderr, code = self.run_ssh(solution['command'])
        
        if code == 0:
            print(f"✅ Fix applied successfully")
            print(f"Output: {stdout[:200]}")
            return True
        else:
            print(f"❌ Fix failed")
            print(f"Error: {stderr[:200]}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Auto-fix agent issues')
    parser.add_argument('--agent', default='alkaid', help='Agent name')
    parser.add_argument('--ssh-host', default='hetzner', help='SSH host')
    parser.add_argument('--ssh-key', default='~/.ssh/hetzner_key', help='SSH key path')
    parser.add_argument('--auto', action='store_true', help='Auto-apply first solution')
    
    args = parser.parse_args()
    
    fixer = AutoFix(args.agent, args.ssh_host, args.ssh_key)
    
    # 診斷
    issues = fixer.diagnose()
    
    if not issues:
        print("\n✅ No issues found! Agent is healthy.")
        return 0
    
    # 建議修復
    solutions = fixer.suggest_fixes(issues)
    
    if not solutions:
        print("\n⚠️  Issues found but no automated solutions available.")
        return 1
    
    # 應用修復
    if args.auto:
        fixer.apply_fix(solutions[0])
    else:
        choice = input("\nSelect solution to apply (number), or 'q' to quit: ")
        if choice.lower() == 'q':
            return 0
        
        try:
            sol_id = int(choice)
            solution = next(s for s in solutions if s['id'] == sol_id)
            fixer.apply_fix(solution)
        except (ValueError, StopIteration):
            print("Invalid choice")
            return 1


if __name__ == '__main__':
    sys.exit(main())
