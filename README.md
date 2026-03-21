# Alkaid Self-Optimization System v2

**CPX31 系統整合版** — 基於現有 Kanban + Alkaid + QMD 生態的 AI Agent 自我學習與優化框架

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

> 基於 Stanford/SambaNova ACE 研究理念，針對 Hetzner CPX31 VPS 現有系統量身整合

---

## 項目概述

本方案為運行在 **Hetzner CPX31** (4 vCPU / 8GB RAM) 上的多 Agent 系統設計，**不是獨立的新系統，而是嵌入現有 Kanban Bot + Alkaid Bot + QMD 生態的自我優化層**。

### 與 v1 的核心差異

| 項目 | v1 (原方案) | v2 (本方案) |
|------|------------|------------|
| 架構 | 獨立 Python 系統 | **嵌入現有 Bot 生態** |
| LLM | OpenAI API (額外費用) | **Kiro CLI claude-sonnet-4.5 (已有)** |
| 通知 | Telegram | **Discord (#archive + #alkaid)** |
| 向量搜尋 | OpenAI Embedding (付費) | **QMD 本地向量搜尋 (免費)** |
| 去重 | 自建 cosine similarity | **QMD BM25 + semantic search** |
| 資料來源 | conversations.jsonl only | **Kanban SQLite + conversations.jsonl + #archive** |
| 學習寫入 | 自建 insights.db | **Kiro .learnings/ (原生) + insights.db (擴充)** |
| 排程 | crontab | **Bot 內建 discord.ext.tasks** |
| 審核 | Telegram 手動 | **Discord CONFIRM + GitHub PR** |

### 核心功能

1. **每日自動收集** — Kanban Bot 從 SQLite 收集當日完成/失敗/超時任務
2. **智能錯誤分析** — Alkaid agent (claude-sonnet-4.5) 分析根因並識別模式
3. **自動學習寫入** — 新知識寫入 `.learnings/`，QMD 更新向量索引
4. **學習閉環** — 下次 alkaid 接到類似任務時，pre-check skill 自動命中歷史解決方案
5. **週報 + GitHub Issue** — 每週日自動彙整學習成果，發到 #archive 和 GitHub
6. **Prompt 優化 PR** — 累積足夠改進建議後，自動建立 IDENTITY.md 優化 PR

---

## 系統架構

```
┌─ 收集層 (Kanban Bot, 23:30 Taipei) ─────────────────┐
│                                                       │
│  Kanban SQLite: done/failed/timeout tasks             │
│  conversations.jsonl: Kiro 對話 (last 24h)            │
│  → daily_digest.json                                  │
│                                                       │
└───────────────────┬───────────────────────────────────┘
                    │
                    ▼
┌─ 分析層 (Kanban Bot → @mention Alkaid) ──────────────┐
│                                                       │
│  Error pattern detection + 用戶修正信號               │
│  Task statistics (成功率, 耗時, agent 分布)           │
│  → analysis_result → 發送到 #alkaid                   │
│                                                       │
└───────────────────┬───────────────────────────────────┘
                    │
                    ▼
┌─ 學習層 (Alkaid Kiro CLI, claude-sonnet-4.5) ────────┐
│                                                       │
│  pre-check skill → 查詢 .learnings/ 歷史             │
│  QMD search → 比對既有知識 (alkaid collection)        │
│  LLM 推理 → 識別新問題 vs 已知問題                   │
│  error-logger skill → 寫入 ERRORS.md                  │
│  → LEARNINGS.md + conversations.jsonl + insights.db   │
│  → qmd embed -c alkaid (更新向量索引)                 │
│                                                       │
└───────────────────┬───────────────────────────────────┘
                    │
                    ▼
┌─ 應用層 (Discord + GitHub) ──────────────────────────┐
│                                                       │
│  即時: #alkaid 分析報告 + #archive embed              │
│  每週: #archive 週報 + GitHub Issue                   │
│  Prompt 優化: GitHub PR (IDENTITY.md)                 │
│                                                       │
└──────────────────────────────────────────────────────┘
```

詳見 [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 技術棧

### 零額外依賴 — 全部利用現有系統

| 組件 | 已有 | 用途 |
|------|------|------|
| Kanban Bot (discord.py) | kanban-kiro-bot.service | 收集任務資料、觸發分析 |
| Alkaid Bot (discord.py) | alkaid-bot.service | 接收分析結果、Kiro CLI 學習 |
| Kiro CLI 1.27.1 | /root/.local/bin/kiro-cli | LLM 推理 (claude-sonnet-4.5) |
| QMD 1.0.7 | qmd-mcp.service :8181 | 本地向量搜尋 + 去重 |
| SQLite | kanban.db + insights.db | 結構化資料儲存 |
| GitHub API | github_pat (已配置) | Issue + PR 自動建立 |
| aiohttp | 已安裝 | GitHub API 呼叫 |

### 資源消耗

| 模式 | RAM | CPU | LLM 成本 |
|------|-----|-----|----------|
| 待機 | 0 MB | 0% | $0 |
| 每日分析 (23:30) | ~50 MB (collector) + Kiro CLI (~300 MB peak) | 10-30% | $0 (Kiro CLI 已有) |
| QMD embed 更新 | ~200 MB (10-20s) | 30-50% | $0 (本地) |
| 週報生成 | ~50 MB | 5% | $0 |

---

## 實施階段

### Phase 1: 收集 + 分析 (Week 1)
- Kanban Bot 加入 daily digest collector
- 在 #alkaid @mention Alkaid 觸發分析
- 結果發到 #archive

### Phase 2: 學習閉環 (Week 2-3)
- Alkaid Kiro CLI 自動寫入 .learnings/
- QMD 向量索引更新
- insights.db 記錄改進建議

### Phase 3: 週報 + GitHub (Week 4)
- 每週日自動彙整
- GitHub Issue 週報
- Prompt 優化 PR (累積 5+ 建議時)

### Phase 4: 任務分解模板 (Week 5+)
- 記錄成功的任務分解模式
- 模板重用機制

詳見 [IMPLEMENTATION.md](IMPLEMENTATION.md)

---

## 學習閉環示意

```
Day 1: Task #15 "helm upgrade" → failed (PVC full)
                                    │
                    ┌───────────────┘
                    ▼
        23:30 Daily Analysis
        → Alkaid 分析根因: "PVC 空間不足導致 helm upgrade 失敗"
        → 寫入 .learnings/ERRORS.md: "helm upgrade 前需檢查 PVC 空間"
        → qmd embed -c alkaid → 向量索引更新
        → #archive: Daily Learning Digest embed

Day 5: Task #20 "helm upgrade" → alkaid agent 接到任務
                                    │
                    ┌───────────────┘
                    ▼
        pre-check skill (auto) 自動觸發
        → 讀取 .learnings/ERRORS.md → 命中 "helm upgrade PVC"
        → qmd search "helm upgrade" -c alkaid → 命中 Day 1 學習
        → alkaid 自動在 upgrade 前先檢查 PVC 空間
        → Task #20 成功！
```

---

## 項目結構

```
Optimization-plan/
├── README.md                    # 本文件
├── ARCHITECTURE.md              # 四層架構設計
├── IMPLEMENTATION.md            # 4 Phase 實施計畫
├── INTEGRATION.md               # CPX31 系統整合指南
├── requirements.txt             # Python 依賴
├── .env.example                 # 配置模板
├── LICENSE                      # MIT License
│
├── src/
│   ├── config.py                # 配置管理
│   ├── collector.py             # 資料收集器 (Kanban SQLite + JSONL)
│   ├── analyzer.py              # 錯誤模式分析器
│   ├── learner.py               # 學習引擎 (Kiro CLI 驅動)
│   ├── optimizer.py             # Prompt 優化器 (GitHub PR)
│   ├── notifier.py              # Discord 通知器 (#archive + #alkaid)
│   └── qmd_dedup.py             # QMD 向量搜尋去重
│
├── schema/
│   └── insights.sql             # SQLite Schema
│
├── scripts/
│   ├── setup.py                 # 初始化腳本
│   └── migrate_db.py            # 資料庫遷移
│
└── docs/
    ├── FLOW.md                  # 完整流程圖
    └── TROUBLESHOOTING.md       # 故障排除
```

---

## 相關系統

| 系統 | 關聯 |
|------|------|
| [VPS-Kanban-Agent](https://github.com/ax958888/VPS-Kanban-Agent) | Kanban Bot 主 repo + 系統架構文件 |
| Kanban Kiro Bridge (Bot #2) | 任務收集源 + 分析觸發器 |
| ALKAID Bot (Bot #3) | 學習引擎執行者 |
| QMD MCP Server (:8181) | 向量搜尋 + 去重引擎 |
| Kiro CLI (.learnings/) | 原生學習寫入機制 |

---

## 授權

MIT License — Copyright (c) 2026 ax958888

---

## 更新日誌

### v2.0.0 (2026-03-21)
- 完全重構：從獨立系統 → 嵌入現有 CPX31 Bot 生態
- 移除 Telegram，改用 Discord (#archive + #alkaid)
- 移除 OpenAI API，改用 Kiro CLI (claude-sonnet-4.5)
- 移除 OpenAI Embedding，改用 QMD 本地向量搜尋
- 加入 Kanban SQLite 作為資料來源
- 加入 GitHub Issue 週報 + Prompt 優化 PR
- 加入 #archive embed 永久學習記錄

### v0.1.0 (2026-03-14)
- 初始版本：獨立 Python 學習系統框架
