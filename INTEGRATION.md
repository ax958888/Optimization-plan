# CPX31 系統整合指南

## 系統全景

本方案不是獨立系統，而是嵌入以下現有服務的自我優化層：

```
┌─────────────────────────────────────────────────────────┐
│  CPX31 — 178.156.239.62                                 │
│                                                          │
│  ┌─ k3s Cluster ──────────────────────────────────────┐ │
│  │  OpenClaw Pod (2/2)                                 │ │
│  │  ├── Astra (Discord Bot #1)                         │ │
│  │  └── Lumix (sessions)                               │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ systemd Services ─────────────────────────────────┐ │
│  │                                                     │ │
│  │  kanban-kiro-bot  ←── 收集層 + 分析層 (本方案新增)  │ │
│  │  ├── SQLite (kanban.db)                             │ │
│  │  ├── Orchestrator (自動閉環)                        │ │
│  │  ├── #archive embed (已啟用)                        │ │
│  │  ├── collector.py (NEW: 每日 23:30 收集)            │ │
│  │  └── analyzer.py (NEW: 錯誤模式分析)               │ │
│  │                                                     │ │
│  │  alkaid-bot  ←── 學習層 (本方案新增)                │ │
│  │  ├── Kiro CLI (claude-sonnet-4.5)                   │ │
│  │  ├── Daily digest handler (NEW)                     │ │
│  │  ├── GitHub Issue/PR creation (已有)                │ │
│  │  └── CONFIRM UPDATE flow (已有)                     │ │
│  │                                                     │ │
│  │  lumix-bot (不受影響)                               │ │
│  │  qmd-mcp ←── 向量搜尋引擎 (已有，本方案利用)       │ │
│  │                                                     │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ Kiro CLI Ecosystem ──────────────────────────────┐  │
│  │                                                    │  │
│  │  Agents:                                           │  │
│  │  ├── alkaid (claude-sonnet-4.5) ←── 學習執行者     │  │
│  │  └── lumix (auto)                                  │  │
│  │                                                    │  │
│  │  Skills:                                           │  │
│  │  ├── error-logger (always) ←── 自動錯誤記錄        │  │
│  │  ├── pre-check (auto) ←── 執行前查歷史            │  │
│  │  ├── openclaw-update                               │  │
│  │  ├── auto-troubleshoot                             │  │
│  │  └── skill-analyzer                                │  │
│  │                                                    │  │
│  │  Memory:                                           │  │
│  │  ├── conversations.jsonl ←── 對話記錄來源          │  │
│  │  └── .learnings/ ←── 學習寫入目標                  │  │
│  │                                                    │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ QMD (本地向量搜尋) ──────────────────────────────┐  │
│  │  Port: 8181 (localhost)                            │  │
│  │  Collections:                                      │  │
│  │  ├── alkaid (17 files) ←── 學習去重 + 知識搜尋     │  │
│  │  ├── astra (191 files)                             │  │
│  │  ├── lumix (12 files)                              │  │
│  │  └── ... (7 total)                                 │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ Storage ─────────────────────────────────────────┐  │
│  │  /root/.kiro/learning/ (NEW)                       │  │
│  │  ├── insights.db ←── 學習資料庫                    │  │
│  │  └── daily/ ←── 每日 digest JSON                   │  │
│  │                                                    │  │
│  │  /root/.kiro/.learnings/ (已有)                     │  │
│  │  ├── ERRORS.md ←── 錯誤記錄                        │  │
│  │  └── LEARNINGS.md ←── 學習筆記                     │  │
│  │                                                    │  │
│  │  /root/kanban-kiro-bot/data/kanban.db (已有)       │  │
│  │  └── tasks, task_logs ←── 任務資料來源             │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 整合點

### 1. Kanban Bot → collector.py

**觸發**: discord.ext.tasks loop, 每日 23:30 Taipei

**讀取**:
- `kanban.db` → 當日 tasks (done/failed/timeout)
- `conversations.jsonl` → 最近 24h 對話

**寫入**:
- `/root/.kiro/learning/daily/YYYY-MM-DD.json`
- `insights.db` → errors, patterns, statistics

**通知**:
- `#alkaid` @mention Alkaid Bot (附 digest 摘要)

### 2. Alkaid Bot → Kiro CLI 學習

**觸發**: 收到 Kanban Bot 的 @mention (Daily Learning Digest)

**讀取**:
- Daily digest 摘要 (from #alkaid message)

**執行** (Kiro CLI alkaid agent):
- pre-check skill → `.learnings/` 查歷史
- QMD search → alkaid collection 去重
- LLM 分析 → 根因識別 + 知識提煉

**寫入** (Kiro CLI 自主):
- `.learnings/ERRORS.md` (error-logger skill, always)
- `.learnings/LEARNINGS.md` (新知識)
- `conversations.jsonl` (自動)
- `insights.db` → improvements (pending)
- `qmd embed -c alkaid` (更新向量索引)

**通知**:
- `#alkaid` 分析報告
- `#archive` Daily Learning Digest embed

### 3. Kanban Bot → 週報 + GitHub

**觸發**: 每週日 23:30 Taipei

**讀取**:
- `insights.db` → 本週 statistics, improvements

**寫入**:
- GitHub Issue (VPS-Kanban-Agent repo)
- `#archive` Weekly Report embed

### 4. Alkaid Bot → GitHub PR

**觸發**: `insights.db` pending improvements >= 5

**執行**:
- Kiro CLI 生成 IDENTITY.md 優化草稿
- GitHub API 建立 PR

---

## Bot ID 映射

| Bot | ID | 用途 |
|-----|-----|------|
| OpenClaw Astra | 1484367437402210344 | Bot #1, 不涉及 |
| Kanban Kiro Bridge | 1484372402078093352 | Bot #2, 收集+分析+通知 |
| ALKAID | 1484557430443610163 | Bot #3, 學習+寫入+PR |
| Lumix | 1484594588722135111 | Bot #4, 不涉及 |

---

## 不受影響的現有功能

| 功能 | 確認 |
|------|------|
| Kanban /task create, /board, /stats | 不受影響 |
| GitHub Webhook → Issue → Task → Agent | 不受影響 |
| Orchestrator 自動閉環 (TODO → DONE) | 不受影響 |
| #archive embed (任務完成歸檔) | 不受影響，額外增加學習 digest |
| Alkaid #alkaid 自由對話 | 不受影響 |
| Alkaid 每日 09:00 版本檢查 | 不受影響 |
| Alkaid CONFIRM UPDATE 流程 | 不受影響 |
| Lumix 排程任務 (08/09/10:00) | 不受影響 |
| QMD MCP Server | 不受影響，被學習層利用 |
