# 📚 .learnings/ Directory

This directory contains your agent's learning history - all errors and their solutions.

## Structure

```
.learnings/
├── ERRORS.md       # Log of all failures with context
├── LEARNINGS.md    # Log of all corrections and solutions
└── stats.json      # Statistics and metrics
```

## Usage

### Automatic Logging

When your agent fails, it automatically logs to `ERRORS.md`:

```markdown
## [2026-03-15 14:30] Task: Check OpenClaw Pod Status
**Error**: `kubectl command not found`
**Context**: Trying to execute `kubectl get pods -n openclaw`
**Impact**: Unable to check pod status, user had to wait
```

### Manual Correction

After you fix the error, log the solution to `LEARNINGS.md`:

```markdown
## [2026-03-15 14:35] Solution: Install kubectl
**Original Error**: See ERRORS.md [2026-03-15 14:30]
**Root Cause**: kubectl not installed on system
**Solution**: Ran `apt install kubectl`
**Prevention**: Add kubectl check in pre-execution validation
```

### Pre-Execution Check

Before executing similar tasks, agent automatically checks `.learnings/`:

```python
# Pseudocode
if task_similar_to_past_error():
    apply_learned_solution()
    avoid_repeating_mistake()
```

## Benefits

✅ **Never repeat the same mistake**  
✅ **Faster debugging** - Solutions are documented  
✅ **Knowledge accumulation** - Agent gets smarter over time  
✅ **Team learning** - Share learnings across agents  

## Maintenance

- Clean old entries (>90 days) periodically
- Export learnings for analysis
- Share successful patterns with other agents
