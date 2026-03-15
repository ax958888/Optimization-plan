---
name: pre-check
description: Check .learnings/ before executing tasks to avoid repeating past errors
inclusion: auto
---

# 🔍 Pre-Check Skill

Automatically checks `.learnings/` history before executing tasks to prevent repeating past mistakes.

## When It Runs

**Automatically** before any task execution (`inclusion: auto`)

Activates when:
- About to execute a command
- Similar to past failed tasks
- User requests high-risk operations

## How It Works

### 1. Task Similarity Detection

```python
current_task = "Check OpenClaw pod status"
past_errors = load_errors_from(".learnings/ERRORS.md")

for error in past_errors:
    similarity = calculate_similarity(current_task, error.task)
    if similarity > 0.8:
        warn_user(error)
        suggest_solution(error)
```

### 2. Solution Application

If a solution exists in `LEARNINGS.md`:
```
⚠️  Similar task failed before: [2026-03-15 14:30]
Error: kubectl not found

✅ Solution available:
   Pre-install check added (see LEARNINGS.md)
   
🤖 Applying learned solution...
   [Checking kubectl availability...]
   ❌ kubectl not found
   📦 Installing kubectl...
   ✅ kubectl installed successfully
   
✅ Ready to proceed with original task
```

### 3. Prevention

If no solution exists:
```
⚠️  Warning: Similar task failed before
Error: SSH connection timeout (3 times)
No automated solution yet.

Suggestions:
1. Check network connectivity first
2. Verify SSH key permissions
3. Try alternative host

Proceed? (y/n)
```

## Example Scenarios

### Scenario 1: kubectl Command

**First Time** (no check):
```
User: "List all pods"
Agent: kubectl get pods
Error: command not found
→ Logged to ERRORS.md
```

**Second Time** (with pre-check):
```
User: "List all pods"
Agent: [Pre-check triggered]
  ⚠️  kubectl failed before
  ✅ Applying solution: Install kubectl
  ✅ kubectl now available
Agent: kubectl get pods
Success: 3 pods listed
```

### Scenario 2: SSH Timeout

**First Time**:
```
User: "SSH to server"
Agent: ssh hetzner
Error: Connection timed out
→ Logged to ERRORS.md
```

**Second Time** (with pre-check):
```
User: "SSH to server"
Agent: [Pre-check triggered]
  ⚠️  SSH timeout happened before
  ✅ Applying solution: Pre-connection check
  → Running: ssh -o ConnectTimeout=5 hetzner "uptime"
  ✅ Connection OK (responded in 1.2s)
Agent: ssh hetzner
Success: Connected
```

## Configuration

### Similarity Threshold

`.learnings/config.json`:
```json
{
  "pre_check": {
    "enabled": true,
    "similarity_threshold": 0.8,
    "max_lookback": 100,
    "auto_apply_solutions": true,
    "require_approval_for": ["destructive", "system-wide"]
  }
}
```

### Similarity Algorithm

Uses TF-IDF + cosine similarity:
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(task1, task2):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([task1, task2])
    return cosine_similarity(vectors[0], vectors[1])[0][0]
```

## Integration

### With error-logger
```
Error occurs → error-logger logs it
                     ↓
Next similar task → pre-check reads log
                     ↓
                 Prevents repeat
```

### With auto-troubleshoot
```
Pre-check detects issue → Calls auto-troubleshoot
                                    ↓
                              Auto-fix applied
                                    ↓
                            Task proceeds safely
```

## Bypass

For urgent cases:
```
User: "List pods --force-skip-precheck"
Agent: [Skipping pre-check as requested]
```

## Statistics

Track prevention success:
```
📊 Pre-Check Statistics (Last 30 Days)
✅ Errors prevented: 47
⏱️  Time saved: 6.5 hours
🎯 Prevention rate: 94%
```

## Benefits

✅ Zero repeated errors  
✅ Automatic solution application  
✅ Faster task execution  
✅ Reduced user frustration  
✅ Continuous learning
