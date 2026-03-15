---
name: auto-troubleshoot
description: Automatically diagnose and fix OpenClaw agent crashes and errors via SSH
inclusion: manual
---

# 🔧 Auto-Troubleshoot Skill

Automatically diagnose and fix OpenClaw/Kiro agent issues by SSH into the server, analyzing logs, and proposing solutions.

## When to Use

Invoke this skill when:
- Agent is not responding
- Performance is degraded
- Error messages appear
- Pod/process crashes
- Memory/CPU issues

## Usage

```
/troubleshoot <agent-name>
```

Or naturally:
```
"My Alkaid agent stopped responding. Please troubleshoot."
"OpenClaw pod keeps restarting. Diagnose the issue."
```

## What It Does

1. **SSH into the server**
   - Uses configured SSH key
   - Connects to specified host

2. **Collect diagnostics**
   - Check process status (ps, systemctl)
   - Read recent logs (journalctl, tail)
   - Check resources (top, df, free)
   - Check network (netstat, ss)

3. **Analyze patterns**
   - Common error signatures
   - Resource constraints
   - Configuration issues

4. **Propose solutions**
   - Restart commands
   - Configuration fixes
   - Resource adjustments

5. **Execute fix (with approval)**
   - Apply the solution
   - Verify recovery
   - Log to LEARNINGS.md

## Configuration

In your `.env`:
```bash
SSH_HOST=hetzner
SSH_KEY=~/.ssh/hetzner_key
SSH_USER=root
AGENT_PATH=/root/.kiro
```

## Example Output

```
🔍 Diagnosing Alkaid agent...

✅ SSH connection: OK
✅ Process status: Running (PID 830525)
⚠️  Memory usage: 95% (7.2GB / 7.6GB)
❌ Error in logs: "MemoryError: Unable to allocate"

🧠 Analysis:
Root cause: Memory exhaustion
Pattern: Large conversation history analysis

💡 Recommended Solutions:
1. Restart agent to free memory
2. Implement batch processing (see LEARNINGS.md [2026-03-14])
3. Add memory limit monitoring

Would you like me to:
[1] Restart agent
[2] Apply batch processing fix
[3] Both
```

## Requirements

- SSH access to agent host
- Sufficient permissions (sudo if needed)
- SSH key configured

## Safety

- Always asks for approval before executing fixes
- Logs all actions to LEARNINGS.md
- Creates backup before config changes
- Verifies fix before marking complete
