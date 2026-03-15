# 🧠 Learning Log

記錄所有修正方案，累積智慧

---

## [2026-03-15 14:35] Solution: Install kubectl CLI

**Original Error**: See ERRORS.md [2026-03-15 14:30]

**Root Cause**: 
kubectl was not installed on the system. Agent assumed it was available.

**Solution**:
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
mv kubectl /usr/local/bin/
```

**Prevention**:
1. Add pre-execution check for kubectl
2. Update TOOLS.md with installation guide
3. Add to system requirements documentation

**Code Added**:
```python
# In pre-check script
def check_kubectl():
    if not shutil.which('kubectl'):
        raise ToolNotFoundError("kubectl not installed")
```

**Verification**:
```bash
$ kubectl version --client
Client Version: v1.28.0
```

✅ **Status**: Deployed and tested successfully

---

## [2026-03-15 10:20] Solution: SSH Connection Pre-Check

**Original Error**: See ERRORS.md [2026-03-15 10:15]

**Root Cause**:
Agent directly attempted SSH without checking network connectivity first.

**Solution**:
Added connection pre-check:
```bash
# Always check before SSH
ssh -o BatchMode=yes -o ConnectTimeout=5 hetzner "uptime" || {
    echo "Connection unavailable, retrying in 10s..."
    sleep 10
    ssh -o BatchMode=yes hetzner "uptime"
}
```

**Prevention**:
1. Updated AGENTS.md with new rule
2. Created ssh-precheck skill
3. Added to all SSH-related tasks

**Rule Added to AGENTS.md**:
```markdown
## SSH 連線規則
執行任何 SSH 指令前，必須先執行：
`ssh -o BatchMode=yes -o ConnectTimeout=5 <host> "uptime"`
```

✅ **Status**: Zero timeouts since implementation (5 days)

---

## [2026-03-14 16:45] Solution: Batch Processing for Large Datasets

**Original Error**: See ERRORS.md [2026-03-14 16:20]

**Root Cause**:
Tried to load 10,000 records into memory at once. System has limited RAM.

**Solution**:
Implemented batch processing:
```python
BATCH_SIZE = 100

def process_conversations(total):
    for i in range(0, total, BATCH_SIZE):
        batch = read_batch(i, BATCH_SIZE)
        process(batch)
        del batch  # Free memory
```

**Prevention**:
1. Set maximum batch size to 100
2. Add memory monitoring
3. Implement progressive processing

**Performance Impact**:
- Before: 10,000 records = crash
- After: 10,000 records = 5 minutes, stable

✅ **Status**: Running smoothly for 2 days

---

## 📋 Template for New Learnings

```markdown
## [YYYY-MM-DD HH:MM] Solution: <Brief Title>

**Original Error**: See ERRORS.md [Date Time]

**Root Cause**: 
Why did the error occur?

**Solution**:
\`\`\`bash
# Command or code that fixed it
\`\`\`

**Prevention**:
1. What rules/checks to add?
2. What documentation to update?
3. What code to write?

**Code/Config Added**:
\`\`\`python
# Relevant code snippet
\`\`\`

**Verification**:
How to confirm it's fixed?

✅ **Status**: Deployed / Testing / Pending
```

---

## 📊 Statistics

- Total Errors Logged: 3
- Total Solutions: 3
- Fix Rate: 100%
- Average Time to Fix: 15 minutes
- Zero Repeated Errors: ✅
