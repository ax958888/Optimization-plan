# 🤝 Multi-Agent Collaboration

協作規範和自我改進協議

---

## 🧠 Self-Improvement Protocol

### 執行規則

**關鍵原則**：永不重複同樣的錯誤

#### 1. 任務完成後
```
✅ Check .learnings/ERRORS.md for similar past failures
✅ Review .learnings/LEARNINGS.md for relevant solutions
✅ Update your knowledge base
```

#### 2. 任務失敗後
```
❌ IMMEDIATELY log to .learnings/ERRORS.md
📝 Include: error message, context, impact, environment
🔍 Search for similar past errors
💡 Check if solution already exists in LEARNINGS.md
```

#### 3. 任務執行前
```
🔍 Pre-check: Is this similar to past failures?
📚 If yes, apply learned solution automatically
⚠️  If no solution exists, warn user and proceed cautiously
```

---

## 📝 Error Logging Format

### ERRORS.md Entry

```markdown
## [YYYY-MM-DD HH:MM] Task: <Brief Description>

**Error**: `<Exact error message>`

**Context**: 
- User request: "<original user message>"
- Command attempted: `<command>`
- System: <host/environment>

**Impact**: 
- Task completion: Failed / Partial / Delayed
- Time lost: <minutes>
- User experience: <description>

**Environment**:
- OS: <version>
- Tools: <relevant tools and versions>
- Resources: <memory, CPU, network status>
```

### LEARNINGS.md Entry

```markdown
## [YYYY-MM-DD HH:MM] Solution: <Problem Solved>

**Original Error**: See ERRORS.md [Date Time]

**Root Cause**: 
<Why the error occurred>

**Solution**:
\`\`\`bash
<Commands or code that fixed it>
\`\`\`

**Prevention**:
1. <What checks to add>
2. <What rules to implement>
3. <What documentation to update>

**Verification**:
<How to confirm it's fixed>

✅ **Status**: Deployed / Testing / Pending
```

---

## 🔍 Pre-Execution Checklist

Before executing any task:

```python
# Pseudocode
def before_task_execution(task):
    # 1. Check past errors
    similar_errors = search_learnings_errors(task)
    
    if similar_errors:
        print(f"⚠️  Warning: Similar task failed {len(similar_errors)} times before")
        
        # 2. Check if solution exists
        solution = search_learnings_solutions(similar_errors)
        
        if solution:
            print(f"✅ Solution found in LEARNINGS.md")
            apply_solution(solution)
        else:
            print(f"⚠️  No solution yet. Proceed with caution.")
            ask_user_confirmation()
    
    # 3. Proceed with task
    execute_task(task)
```

---

## 🛡️ Failure Handling

### When Task Fails

```python
def on_task_failure(task, error):
    # 1. Log immediately
    log_to_errors_md(task, error)
    
    # 2. Notify user
    tell_user(f"Task failed: {error}")
    
    # 3. Check if known issue
    if error in known_issues:
        suggest_solution(known_issues[error])
    
    # 4. Ask for manual fix
    user_fix = ask_user_how_to_fix()
    
    # 5. Log the solution
    log_to_learnings_md(task, error, user_fix)
```

---

## 🤖 Auto-Troubleshoot

When agent crashes or becomes unresponsive:

```bash
# Automatic recovery
python3 scripts/auto_fix.py --agent <name> --auto

# Or describe the issue naturally:
"My agent is not responding. SSH to server and troubleshoot."
```

### Auto-fix will:
1. ✅ SSH into server
2. ✅ Check process status
3. ✅ Read recent logs
4. ✅ Identify root cause
5. ✅ Propose solutions
6. ✅ Apply fix (with approval)
7. ✅ Verify recovery
8. ✅ Log to LEARNINGS.md

---

## 📊 Learning Statistics

Track your improvement:

```markdown
### Last 30 Days
- Total Errors: 15
- Repeated Errors: 0 ✅
- Solutions Applied: 15
- Fix Rate: 100%
- Average Fix Time: 12 minutes
- Time Saved by Pre-Check: 4.5 hours
```

---

## 🔄 Continuous Improvement Cycle

```
Execute Task
     ↓
  Success? ──No──→ Log Error → Manual Fix → Log Solution
     │                                           ↓
     Yes                                   Add to Knowledge
     ↓                                           ↓
Check Learnings ←──────────────────────────────┘
     ↓
Apply Past Solutions
     ↓
Never Repeat Mistakes ✅
```

---

## 🎯 Goals

- **Zero repeated errors**
- **100% error documentation**
- **90%+ auto-fix success rate**
- **<5 minute average recovery time**

---

## 📚 Resources

- Error Log: `.learnings/ERRORS.md`
- Solution Log: `.learnings/LEARNINGS.md`
- Auto-Fix Script: `scripts/auto_fix.py`
- Skills: `skills/error-logger/`, `skills/pre-check/`, `skills/auto-troubleshoot/`

---

**Remember**: Every failure is a learning opportunity. Log it, fix it, never repeat it. 🚀
