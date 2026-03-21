# 系統架構設計

## 四層架構模型

```
┌──────────────────────────────────────────────────────────────────┐
│                     收集層 (Collection Layer)                    │
│                     Kanban Bot (每日 23:30 Taipei)               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐   │
│  │  Kanban SQLite      │  │  Kiro conversations.jsonl       │   │
│  │  (kanban.db)        │  │  (/root/.kiro/memory/)          │   │
│  │                     │  │                                 │   │
│  │  tasks:             │  │  Recent 24h conversations:      │   │
│  │  - done             │  │  - user_message                 │   │
│  │  - failed           │  │  - assistant_response           │   │
│  │  - timeout          │  │  - context (tools, errors)      │   │
│  │  - result_summary   │  │  - timestamp                    │   │
│  │  - duration         │  │                                 │   │
│  │  - agent            │  │                                 │   │
│  └────────┬────────────┘  └──────────────┬──────────────────┘   │
│           │                              │                       │
│           └──────────┬───────────────────┘                       │
│                      ▼                                           │
│           ┌──────────────────────┐                               │
│           │   collector.py       │                               │
│           │   → daily_digest.json│                               │
│           └──────────┬───────────┘                               │
│                      │                                           │
└──────────────────────┼───────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                     分析層 (Analysis Layer)                      │
│                     Kanban Bot 內執行                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  analyzer.py                                             │    │
│  │                                                          │    │
│  │  1. Error Pattern Detection                              │    │
│  │     ├── SSH timeout / connection refused                 │    │
│  │     ├── kubectl error / pod crash                        │    │
│  │     ├── helm upgrade failure                             │    │
│  │     ├── permission denied                                │    │
│  │     └── Kiro CLI timeout                                 │    │
│  │                                                          │    │
│  │  2. User Correction Signals                              │    │
│  │     ├── "不對"、"錯了"、"應該是"                         │    │
│  │     ├── Repeated questions                               │    │
│  │     └── Manual task re-assignment                        │    │
│  │                                                          │    │
│  │  3. Task Statistics                                      │    │
│  │     ├── Success rate by agent                            │    │
│  │     ├── Average duration by task type                    │    │
│  │     └── Failure pattern clustering                       │    │
│  │                                                          │    │
│  │  → analysis_result.json                                  │    │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Kanban Bot @mention Alkaid in #alkaid                           │
│  (attach analysis_result summary)                                │
│                                                                  │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                     學習層 (Learning Layer)                      │
│                     Alkaid Bot → Kiro CLI                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Kiro CLI alkaid agent (claude-sonnet-4.5)               │    │
│  │                                                          │    │
│  │  Automatic (Kiro native):                                │    │
│  │  ├── pre-check skill (auto)                              │    │
│  │  │   └── 讀取 .learnings/ 歷史，避免重複錯誤            │    │
│  │  ├── error-logger skill (always)                         │    │
│  │  │   └── 自動記錄失敗到 ERRORS.md                       │    │
│  │  └── memory protocol                                     │    │
│  │      └── 每次互動前讀取、互動後寫入 conversations.jsonl  │    │
│  │                                                          │    │
│  │  QMD Dedup (qmd_dedup.py):                               │    │
│  │  ├── qmd search "error description" -c alkaid            │    │
│  │  ├── If similarity > 0.85 → skip (already known)         │    │
│  │  └── If new → proceed to learn                           │    │
│  │                                                          │    │
│  │  Write Outputs:                                          │    │
│  │  ├── /root/.kiro/.learnings/ERRORS.md (append)           │    │
│  │  ├── /root/.kiro/.learnings/LEARNINGS.md (append)        │    │
│  │  ├── /root/.kiro/memory/conversations.jsonl (auto)       │    │
│  │  └── /root/.kiro/learning/insights.db (improvements)     │    │
│  │                                                          │    │
│  │  Update Index:                                           │    │
│  │  └── qmd embed -c alkaid (refresh vectors)               │    │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                     應用層 (Application Layer)                   │
│                     Discord + GitHub                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Daily (每日 23:30):                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  #alkaid: Analysis report + improvement suggestions     │     │
│  │  #archive: Daily Learning Digest embed                  │     │
│  │  insights.db: statistics table updated                  │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Weekly (每週日 23:30):                                          │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  #archive: Weekly Report embed                          │     │
│  │  GitHub Issue: Weekly learning report                   │     │
│  │  .learnings/LEARNINGS.md: consolidated update           │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  Prompt Optimization (trigger: improvements >= 5 pending):       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  GitHub PR: IDENTITY.md optimization draft              │     │
│  │  → Manual review & merge by user                        │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 資料庫設計

### insights.db (SQLite)

位置: `/root/.kiro/learning/insights.db`

```sql
-- 見 schema/insights.sql 完整定義
```

| 表 | 用途 | 寫入者 |
|---|------|--------|
| errors | 錯誤記錄 (from analyzer) | Kanban Bot (collector) |
| patterns | 任務模式統計 | Kanban Bot (analyzer) |
| improvements | 改進建議 (from Kiro CLI) | Alkaid Bot (learner) |
| changes | 變更歷史 (rollback 支援) | Alkaid Bot (optimizer) |
| statistics | 每日/週統計 | Kanban Bot (collector) |
| daily_digests | 每日摘要 JSON | Kanban Bot (collector) |
| task_templates | 任務分解模板 | Alkaid Bot (learner) |

### kanban.db (SQLite, 只讀)

位置: `/root/kanban-kiro-bot/data/kanban.db`

| 表 | 讀取欄位 |
|---|---------|
| tasks | id, title, status, assigned_agent, duration_seconds, result_summary, github_issue_number |
| task_logs | task_id, event, message, timestamp |

---

## 資料流

### 學習閉環 (核心)

```
Task Completed/Failed
       │
       ▼
┌─ Kanban Bot ──────────────┐
│  kanban.db → collector.py  │
│  → daily_digest.json       │
│  → analyzer.py             │
│  → analysis_result         │
│  → @mention Alkaid         │
└────────────┬───────────────┘
             │
             ▼
┌─ Alkaid Bot ──────────────┐
│  Kiro CLI alkaid agent     │
│  ├─ pre-check → 查歷史    │
│  ├─ QMD search → 去重     │
│  ├─ LLM 分析 → 新知識     │
│  ├─ .learnings/ 寫入      │
│  └─ qmd embed → 更新索引  │
└────────────┬───────────────┘
             │
             ▼
┌─ 下次相同任務 ────────────┐
│  alkaid agent 接到任務     │
│  ├─ pre-check → 命中!     │
│  ├─ QMD search → 命中!    │
│  └─ 直接用學到的方式解決  │
└───────────────────────────┘
```

### Discord 頻道分工

```
#kanban    → Board 即時狀態
#agent-hub → 工作 thread (完成後 archived)
#logs      → 即時事件通知 (start/complete/fail)
#archive   → 永久歸檔: 任務記錄 + Daily/Weekly Learning Digest
#alkaid    → Alkaid 對話 + 每日分析報告 + CONFIRM 交互
#lumix     → Lumix 對話 + 排程新聞
#astra     → Astra 直接對話
```

---

## 安全機制

### 數據隱私
- 所有分析在本地執行 (QMD 本地模型，Kiro CLI 本地呼叫)
- 不上傳原始對話到第三方服務
- GitHub PR 只包含通用改進規則，不含敏感資料

### 審核機制
- 改進建議存入 insights.db `status=pending`
- Prompt 優化透過 GitHub PR，需要手動 review & merge
- .learnings/ 寫入由 Kiro CLI 原生 skill 管理，有 pre-check 防護

### 資源限制
- 每日分析最多處理 50 筆任務 + 100 條對話
- Kiro CLI timeout 300 秒
- QMD embed 更新限制 CPU 20 秒
- insights.db 每月 VACUUM 一次

---

## 與 v1 架構對比

| 層次 | v1 (原方案) | v2 (本方案) |
|------|------------|------------|
| 收集 | conversations.jsonl only | **Kanban SQLite + JSONL + #archive** |
| 分析 | 獨立 Python analyzer | **Kanban Bot 內建 + @mention Alkaid** |
| 學習 | OpenAI API call | **Kiro CLI alkaid agent (原生)** |
| 去重 | OpenAI Embedding + cosine | **QMD 本地向量搜尋 (免費)** |
| 儲存 | insights.db only | **insights.db + .learnings/ + QMD index** |
| 通知 | Telegram | **Discord #archive + #alkaid embed** |
| 審核 | Telegram 手動 | **GitHub PR (IDENTITY.md)** |
| 排程 | crontab | **discord.ext.tasks (Bot 內建)** |
