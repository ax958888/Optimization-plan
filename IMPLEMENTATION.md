# 📋 Implementation Guide

OpenClaw Self-Improvement System 完整實施指南

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone and Install

```bash
# Clone repository
git clone https://github.com/ax958888/openclaw-self-improvement.git
cd openclaw-self-improvement

# Install dependencies
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Fill in SSH_HOST, SSH_KEY, etc.
```

### Step 2: Initialize for Your Agent

```bash
# For Alkaid agent
python3 scripts/setup.py --agent alkaid --path /root/.kiro

# This creates:
# - /root/.kiro/.learnings/
# - /root/.kiro/.learnings/ERRORS.md
# - /root/.kiro/.learnings/LEARNINGS.md
# - /root/.kiro/.learnings/config.json
```

### Step 3: Add to AGENTS.md

```bash
# Copy template content
cat templates/AGENTS_template.md >> ~/.kiro/steering/AGENTS.md

# Or manually add the Self-Improvement Protocol section
```

### Step 4: Deploy Skills

```bash
# Copy skills to Kiro
cp -r skills/* ~/.kiro/skills/

# Verify installation
ls ~/.kiro/skills/
# Should see: auto-troubleshoot/ error-logger/ pre-check/
```

### Step 5: Test

```bash
# Test auto-fix
python3 scripts/auto_fix.py --agent alkaid

# Test error logging (manual)
echo "Test error" >> ~/.kiro/.learnings/ERRORS.md
```

---

## 📦 Detailed Installation

### Prerequisites

- Python 3.9+
- SSH access to agent host
- Kiro Framework or OpenClaw installed
- sudo privileges (if needed)

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 2GB | 4GB |
| Disk | 100MB | 500MB |
| Python | 3.9 | 3.11+ |

### Dependencies

```txt
# Core
pyyaml>=6.0

# SSH (built-in)
paramiko  # If not using system ssh

# Optional
scikit-learn>=1.0  # For similarity detection
```

---

## 🔧 Configuration

### .env File

```bash
# SSH Configuration
SSH_HOST=hetzner
SSH_USER=root
SSH_KEY=~/.ssh/hetzner_key
SSH_PORT=22

# Agent Configuration
AGENT_NAME=alkaid
AGENT_PATH=/root/.kiro
OPENCLAW_NAMESPACE=openclaw

# Learning Configuration
LEARNINGS_PATH=.learnings
ERROR_RETENTION_DAYS=90
MAX_ERROR_ENTRIES=1000

# Auto-Fix Configuration
AUTO_FIX_ENABLED=true
AUTO_FIX_APPROVAL_REQUIRED=true
AUTO_FIX_MAX_ATTEMPTS=3

# Notification (Optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

### config.json (per agent)

```json
{
  "error_logging": {
    "enabled": true,
    "auto_format": true,
    "max_entries": 1000,
    "retention_days": 90,
    "severity_levels": ["critical", "error", "warning"]
  },
  "pre_check": {
    "enabled": true,
    "similarity_threshold": 0.8,
    "max_lookback": 100,
    "auto_apply_solutions": true
  },
  "auto_fix": {
    "enabled": true,
    "ssh_enabled": true,
    "max_attempts": 3,
    "require_approval": true,
    "safe_commands": ["restart", "status", "logs"]
  },
  "soul_optimization": {
    "style": "opinionated",
    "conciseness_level": "high",
    "hedge_removal": true
  }
}
```

---

## 📂 Directory Structure

After installation:

```
~/.kiro/  (or your agent path)
├── .learnings/
│   ├── README.md
│   ├── ERRORS.md
│   ├── LEARNINGS.md
│   ├── config.json
│   └── stats.json
│
├── skills/
│   ├── auto-troubleshoot/
│   │   ├── SKILL.md
│   │   └── troubleshoot.py
│   ├── error-logger/
│   │   ├── SKILL.md
│   │   └── logger.py
│   └── pre-check/
│       ├── SKILL.md
│       └── checker.py
│
└── steering/
    └── AGENTS.md  (modified)
```

---

## 🎯 Phase-by-Phase Implementation

### Phase 1: Error Logging (Week 1)

**Goal**: Capture all failures automatically

**Tasks**:
1. ✅ Create `.learnings/` directory
2. ✅ Deploy `error-logger` skill
3. ✅ Modify `AGENTS.md`
4. ✅ Test manual logging

**Verification**:
```bash
# Trigger an error (e.g., run non-existent command)
# Check if logged
cat ~/.kiro/.learnings/ERRORS.md
```

**Expected Outcome**:
- All failures logged
- Structured error entries
- Timestamp and context captured

---

### Phase 2: Pre-Execution Check (Week 2)

**Goal**: Prevent repeating past mistakes

**Tasks**:
1. ✅ Deploy `pre-check` skill
2. ✅ Configure similarity threshold
3. ✅ Test with past errors
4. ✅ Verify prevention

**Verification**:
```bash
# Run a previously failed command
# Should see: "⚠️ Similar task failed before..."
```

**Expected Outcome**:
- 80%+ error prevention rate
- Automatic solution application
- User warnings for new patterns

---

### Phase 3: Auto-Fix (Week 3)

**Goal**: Automatically recover from crashes

**Tasks**:
1. ✅ Deploy `auto-troubleshoot` skill
2. ✅ Configure SSH access
3. ✅ Test diagnostics
4. ✅ Test auto-fix

**Verification**:
```bash
# Manually stop agent
pkill -f kiro-telegram-bot

# Run auto-fix
python3 scripts/auto_fix.py --agent alkaid --auto

# Verify agent restarted
ps aux | grep kiro-telegram-bot
```

**Expected Outcome**:
- 90%+ auto-recovery rate
- <5 minute recovery time
- Full diagnostic logs

---

### Phase 4: Soul Optimization (Week 4)

**Goal**: Transform agent to opinionated style

**Tasks**:
1. ✅ Analyze current `SOUL.md`
2. ✅ Generate optimized version
3. ✅ A/B test (keep backup)
4. ✅ Rollout to all agents

**Verification**:
```bash
# Compare response styles
# Before: "你想要 A 還是 B？"
# After: "執行 A（推薦）。需要 B？"
```

**Expected Outcome**:
- 50%+ faster task completion
- 30%+ higher user satisfaction
- 80%+ reduction in clarifying questions

---

## 🧪 Testing

### Unit Tests

```bash
# Test error logging
python3 -m pytest tests/test_error_logger.py

# Test pre-check
python3 -m pytest tests/test_pre_check.py

# Test auto-fix
python3 -m pytest tests/test_auto_fix.py
```

### Integration Tests

```bash
# End-to-end test
python3 tests/e2e_test.py

# Should:
# 1. Trigger an error
# 2. Log to ERRORS.md
# 3. Fix manually
# 4. Log to LEARNINGS.md
# 5. Repeat same task
# 6. Verify prevention
```

### Manual Testing Checklist

- [ ] Error logging works
- [ ] Pre-check detects similar tasks
- [ ] Auto-fix diagnoses correctly
- [ ] SSH connection works
- [ ] Solutions applied successfully
- [ ] LEARNINGS.md updated
- [ ] Stats tracked correctly

---

## 📊 Monitoring

### Dashboard

```bash
# View statistics
python3 scripts/stats.py

# Output:
📊 Learning Statistics (Last 30 Days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Errors Logged:        47
🔄 Repeated Errors:       2 (4%)
💡 Solutions Applied:    45
⏱️  Average Fix Time:     8 minutes
🛡️  Prevention Rate:     96%
💾 Database Size:        2.3 MB
```

### Alerts

Configure alerts in `config.json`:
```json
{
  "alerts": {
    "on_repeated_error": true,
    "on_fix_failure": true,
    "on_high_error_rate": true,
    "threshold": 5
  }
}
```

---

## 🔍 Troubleshooting

### Issue 1: SSH Connection Failed

**Symptoms**: auto_fix.py cannot connect

**Solutions**:
```bash
# 1. Verify SSH key
ssh -i ~/.ssh/hetzner_key root@178.156.239.62 "uptime"

# 2. Check SSH config
cat ~/.ssh/config

# 3. Test with verbose
ssh -vvv -i ~/.ssh/hetzner_key root@178.156.239.62
```

### Issue 2: Skills Not Loading

**Symptoms**: Skills not found by agent

**Solutions**:
```bash
# 1. Check skill path
ls -la ~/.kiro/skills/

# 2. Verify SKILL.md format
cat ~/.kiro/skills/error-logger/SKILL.md | head -5

# 3. Check Kiro config
cat ~/.kiro/agents/alkaid.json | grep skills
```

### Issue 3: ERRORS.md Not Updating

**Symptoms**: Errors not logged automatically

**Solutions**:
```bash
# 1. Check if error-logger skill is active
# In agent conversation:
"List all active skills"

# 2. Manually test logging
python3 ~/.kiro/skills/error-logger/logger.py --test

# 3. Check permissions
ls -la ~/.kiro/.learnings/
```

---

## 🚀 Production Deployment

### Backup

```bash
# Before deployment
tar -czf kiro-backup-$(date +%Y%m%d).tar.gz ~/.kiro/
```

### Rollout Strategy

1. **Single Agent Test** (Alkaid)
2. **Monitor 1 week**
3. **Expand to 2-3 agents**
4. **Monitor 1 week**
5. **Full rollout** (all 5 agents)

### Rollback Plan

```bash
# If issues occur
tar -xzf kiro-backup-YYYYMMDD.tar.gz -C ~/
systemctl restart kiro-telegram-bot
```

---

## 📈 Success Metrics

Track these KPIs:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Error Prevention Rate | >85% | Repeated errors / Total errors |
| Auto-Fix Success | >90% | Successful fixes / Total attempts |
| Average Recovery Time | <5 min | Time from crash to recovery |
| User Satisfaction | >4.5/5 | User feedback score |
| Task Completion Speed | +50% | Time comparison |

---

## 🔄 Maintenance

### Weekly Tasks

```bash
# Clean old logs
python3 scripts/cleanup.py --days 90

# Export stats
python3 scripts/export_stats.py --format csv

# Backup learnings
cp -r ~/.kiro/.learnings/ ~/backups/learnings-$(date +%Y%m%d)
```

### Monthly Tasks

- Review top errors
- Update solutions
- Share learnings across agents
- Performance tuning

---

## 📚 Next Steps

After successful implementation:

1. **Expand to Other Agents**
   - Astra, Lumix, Vera, Blaze, Forge
   - Share learnings database

2. **Advanced Features**
   - Predictive error prevention
   - ML-based similarity detection
   - Cross-agent knowledge transfer

3. **Community Contribution**
   - Share your learnings
   - Contribute to skill library
   - Help others implement

---

**Need Help?** [Open an Issue](https://github.com/ax958888/openclaw-self-improvement/issues)
