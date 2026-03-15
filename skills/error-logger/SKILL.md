---
name: error-logger
description: Automatically log all failures and errors to .learnings/ERRORS.md
inclusion: always
---

# 📝 Error Logger Skill

Automatically captures and logs every failure to `.learnings/ERRORS.md` for future learning.

## When It Runs

**Automatically** - This skill is ALWAYS active (`inclusion: always`)

Triggers on:
- Command execution failures (exit code != 0)
- Python exceptions
- API errors
- Timeout errors
- User corrections ("不對", "錯了", "重新")

## What It Logs

### Error Entry Format

```markdown
## [YYYY-MM-DD HH:MM] Task: <description>

**Error**: `<error message>`

**Context**: 
- What command/action was attempted
- What the user requested
- System environment details

**Impact**: 
- User experience impact
- Time wasted
- Task completion status

**Environment**:
- OS, tools, versions
- Network conditions
- Resource availability
```

## Example

### User Interaction
```
User: "檢查 OpenClaw Pod 狀態"
Agent: [Executes] kubectl get pods -n openclaw
Error: kubectl: command not found
```

### Auto-Generated Log Entry

````markdown
## [2026-03-15 14:30] Task: Check OpenClaw Pod Status

**Error**: `kubectl: command not found`

**Context**: 
- User requested: "檢查 OpenClaw Pod 狀態"
- Attempted command: `kubectl get pods -n openclaw`
- System: Hetzner VPS root@178.156.239.62

**Impact**: 
- Task completely failed
- User waited 5 minutes for manual resolution
- Had to switch to alternate method

**Environment**:
- OS: Ubuntu 22.04
- Shell: bash
- User: root
- kubectl: NOT INSTALLED
````

## Integration with Pre-Check

After logging an error, the `pre-check` skill can:
1. Read `.learnings/ERRORS.md`
2. Check if current task is similar
3. Warn: "This task failed before - see [Date] entry"
4. Suggest: Apply solution from LEARNINGS.md

## Configuration

In `.learnings/config.json`:
```json
{
  "error_logging": {
    "enabled": true,
    "auto_format": true,
    "max_entries": 1000,
    "retention_days": 90,
    "severity_levels": ["critical", "error", "warning"]
  }
}
```

## Maintenance

Auto-cleanup runs weekly:
- Archives entries older than 90 days
- Exports statistics
- Compresses old logs

## Benefits

✅ Complete error history  
✅ Pattern recognition  
✅ Knowledge base building  
✅ Team learning  
✅ Debugging efficiency +500%
