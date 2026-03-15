# 🔴 Error Log

記錄所有失敗案例，確保不重複犯錯

---

## [2026-03-15 14:30] Task: Check OpenClaw Pod Status

**Error**: `kubectl: command not found`

**Context**: 
- User asked: "檢查 OpenClaw 狀態"
- Tried to execute: `kubectl get pods -n openclaw`
- System: Hetzner VPS (178.156.239.62)

**Impact**: 
- Task failed completely
- User had to wait for manual fix
- Lost 5 minutes

**Environment**:
- OS: Ubuntu 22.04
- Shell: bash
- User: root

---

## [2026-03-15 10:15] Task: SSH Connection Timeout

**Error**: `ssh: connect to host 178.156.239.62 port 22: Connection timed out`

**Context**:
- User asked: "SSH 到 Hetzner 查看日誌"
- Did not check connection status first
- Directly tried SSH without verification

**Impact**:
- Wasted 30 seconds waiting for timeout
- Had to retry 3 times

**Environment**:
- Network: Unstable during morning hours
- SSH Key: ~/.ssh/hetzner_key

---

## [2026-03-14 16:20] Task: Memory Overflow in Analysis

**Error**: `MemoryError: Unable to allocate array`

**Context**:
- Analyzing 10,000 conversation records at once
- Tried to load everything into memory
- System only has 8GB RAM

**Impact**:
- Process crashed
- Lost 15 minutes of work
- Had to restart daemon

**Environment**:
- Python 3.10
- RAM: 7.6GB available
- Script: src/analyzer.py

---

## 📋 Template for New Errors

```markdown
## [YYYY-MM-DD HH:MM] Task: <Brief Description>

**Error**: `<Error message>`

**Context**: 
- What were you trying to do?
- What command/action triggered it?
- What was the environment?

**Impact**: 
- How did this affect the user?
- How much time was lost?

**Environment**:
- Relevant system info
- Tools/versions involved
```
