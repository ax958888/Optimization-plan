# 🧠 Alkaid AI Self-Optimization System

**Alkaid 自我優化系統** - 為 VPS 環境設計的輕量級 AI Agent 自我學習與優化框架

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> 基於 Stanford/SambaNova 的 Agentic Context Engineering (ACE) 研究理念，為資源受限的 VPS 環境量身打造

---

## 📋 項目概述

本方案為運行在 **Hetzner CPX31 VPS** (4 vCPU / 8GB RAM) 上的 Kiro Agent **Alkaid** 設計，實現：

- ✅ **零框架依賴**：僅使用 Python 標準庫 + SQLite + OpenAI API
- ✅ **多維度學習**：錯誤檢測、模式識別、Prompt 優化
- ✅ **資源友好**：平時零開銷，每日分析僅需 200MB RAM
- ✅ **漸進式部署**：4 個階段逐步實施，可隨時中止
- ✅ **人工審核**：所有改進方案需手動批准後生效

---

## 🎯 核心功能

### 1. 🔍 智能錯誤檢測

- 自動識別失敗的 SSH 指令、Kubectl 錯誤
- 檢測用戶修正行為（"不對"、"錯了"、重複提問）
- 追蹤工具執行失敗模式

### 2. 🧠 自動學習引擎

- 調用 LLM 分析對話記錄，提取 insights
- 生成新的 steering files 和 skills 草稿
- 語義去重，避免重複學習

### 3. ✍️ Prompt 自動優化

- 分析成功對話，提煉有效溝通模式
- 生成優化後的 `IDENTITY.md` 草稿
- 自動提交 GitHub PR 供審核

### 4. 📊 任務自主分解

- 識別複雜任務，自動拆解成子任務
- 記錄成功的分解模板，供未來重用
- 追蹤執行狀態，生成報告

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────┐
│                   Alkaid (主 Agent)                      │
│  - 正常對話執行                                          │
│  - 記錄到 conversations.jsonl                            │
└──────────────┬──────────────────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────────────────┐
│         自我優化系統 (每日觸發)                           │
├─────────────────────────────────────────────────────────┤
│  📊 Analyzer   - 解析對話，檢測錯誤模式                   │
│  🧠 Learner    - LLM 提取 insights，生成改進方案          │
│  ✍️ Optimizer  - 優化 Prompt，更新 Skills                │
│  📡 Scheduler  - 定時任務，通知管理                       │
└─────────────────────────────────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────────────────┐
│  存儲層                                                  │
│  ├─ conversations.jsonl  (現有對話記錄)                   │
│  ├─ insights.db          (學習資料庫)                     │
│  └─ changelog.md         (變更日誌)                       │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 技術棧

### 最小化依賴

```
Python 3.9+       (運行時)
openai>=1.0.0     (LLM API)
pyyaml>=6.0       (配置文件)
SQLite3           (內建，無需安裝)
```

### 資源消耗

| 模式 | RAM | CPU | LLM 成本 |
|------|-----|-----|----------|
| **待機** | 0 MB | 0% | $0 |
| **每日分析** | ~200 MB | 20-40% | ~$0.50 |
| **每週優化** | ~300 MB | 30-50% | ~$1.50 |

---

## 🚀 快速開始

### 1. 環境準備

```bash
# 克隆項目
git clone https://github.com/ax958888/Optimization-plan.git
cd Optimization-plan

# 安裝依賴
pip install -r requirements.txt

# 配置環境變量
cp .env.example .env
# 編輯 .env，填入 OPENAI_API_KEY
```

### 2. 初始化系統

```bash
# 創建學習目錄
python3 scripts/setup.py

# 測試分析器
python3 src/analyzer.py --test

# 配置定時任務
python3 scripts/install_cron.py
```

### 3. 手動觸發分析

```bash
# 分析最近 24 小時對話
python3 src/scheduler.py --mode daily

# 查看發現的改進建議
python3 src/learner.py --review

# 批准並應用建議
python3 src/optimizer.py --apply <suggestion_id>
```

---

## 📂 項目結構

```
Optimization-plan/
├── README.md                 # 本文件
├── ARCHITECTURE.md           # 詳細架構設計
├── IMPLEMENTATION.md         # 實施計劃
├── requirements.txt          # Python 依賴
├── .env.example              # 環境變量模板
│
├── src/                      # 核心代碼
│   ├── analyzer.py           # 對話分析器
│   ├── learner.py            # 學習引擎
│   ├── optimizer.py          # 優化器
│   ├── scheduler.py          # 定時任務
│   ├── notifier.py           # Telegram 通知
│   └── config.py             # 配置管理
│
├── scripts/                  # 工具腳本
│   ├── setup.py              # 初始化腳本
│   ├── install_cron.py       # 安裝定時任務
│   └── migrate_db.py         # 資料庫遷移
│
├── schema/                   # 資料庫結構
│   └── insights.sql          # SQLite Schema
│
├── docs/                     # 文檔
│   ├── API.md                # API 文檔
│   ├── EXAMPLES.md           # 使用示例
│   └── TROUBLESHOOTING.md    # 故障排除
│
└── tests/                    # 測試
    ├── test_analyzer.py
    ├── test_learner.py
    └── test_optimizer.py
```

---

## 📈 實施階段

### 階段 1：基礎設施 (Week 1)

- [x] 創建 SQLite 資料庫結構
- [x] 實現對話解析器
- [x] 建立錯誤檢測邏輯
- [ ] 部署到 VPS 測試

**產出**：能夠解析 `conversations.jsonl` 並識別錯誤

---

### 階段 2：錯誤學習 (Week 2-3)

- [ ] 整合 OpenAI API
- [ ] 實現 LLM 分析流程
- [ ] 生成改進建議草稿
- [ ] 配置 Telegram 通知

**產出**：每日收到「發現 N 個改進建議」通知

---

### 階段 3：Prompt 優化 (Week 4-5)

- [ ] 統計成功對話模式
- [ ] 生成 IDENTITY.md 草稿
- [ ] 實現 GitHub PR 自動提交
- [ ] 對比優化前後效果

**產出**：每週自動生成 Prompt 優化 PR

---

### 階段 4：任務分解 (Week 6+)

- [ ] 識別複雜任務類型
- [ ] 構建任務分解模板庫
- [ ] 追蹤執行狀態
- [ ] 自動生成執行報告

**產出**：能夠自主處理複雜多步驟任務

---

## 🔧 配置說明

### 環境變量 (.env)

```bash
# OpenAI API 配置
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Telegram Bot 配置
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...

# 路徑配置
KIRO_PATH=/root/.kiro
MEMORY_PATH=/root/.kiro/memory/conversations.jsonl
LEARNING_PATH=/root/.kiro/learning

# 學習參數
ANALYSIS_INTERVAL=daily       # daily/weekly
MAX_INSIGHTS_PER_DAY=10
DEDUP_THRESHOLD=0.85
AUTO_APPLY=false              # 是否自動應用改進（建議 false）
```

### 定時任務配置

```bash
# 每天凌晨 3:00 執行日常分析
0 3 * * * /usr/bin/python3 /root/.kiro/learning/src/scheduler.py --mode daily

# 每週日凌晨 4:00 執行週報告
0 4 * * 0 /usr/bin/python3 /root/.kiro/learning/src/scheduler.py --mode weekly
```

---

## 📊 預期效果

### 性能指標

| 指標 | 首月 | 三個月 | 半年 |
|------|------|--------|------|
| **錯誤率下降** | -15% | -40% | -60% |
| **響應準確度** | +10% | +25% | +40% |
| **重複任務時間** | -20% | -40% | -50% |

### 學習曲線

```
成功率 (%)
100 ┤                                    ╭─────
 90 ┤                           ╭────────╯
 80 ┤                  ╭────────╯
 70 ┤         ╭────────╯
 60 ┤ ────────╯
    └─────────────────────────────────────────> 時間 (週)
    0        4        8       12       16      20
```

---

## 🛡️ 安全性考慮

### 數據隱私

- ✅ 所有對話記錄**本地存儲**，不上傳第三方
- ✅ LLM 分析時**脫敏處理**敏感信息（API Key、密碼）
- ✅ GitHub PR 僅包含**通用改進規則**，不含私密數據

### 審核機制

- ✅ 所有改進建議**先存草稿**，不自動應用
- ✅ Telegram 通知**人工審核**後手動批准
- ✅ 每次優化**記錄 changelog**，可回滾

### 資源限制

- ✅ 單次分析**最多處理 100 條對話**，防止 RAM 爆炸
- ✅ LLM 調用**設置超時 30 秒**，避免卡死
- ✅ 錯誤達到**閾值自動暫停**，發送警報

---

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 開發環境設置

```bash
# 克隆倉庫
git clone https://github.com/ax958888/Optimization-plan.git
cd Optimization-plan

# 創建虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝開發依賴
pip install -r requirements-dev.txt

# 運行測試
pytest tests/
```

### 代碼風格

- 遵循 PEP 8
- 使用 Black 格式化
- 100% 類型註解（mypy）

---

## 📚 相關資源

### 學術論文

- [Agentic Context Engineering (ACE)](https://arxiv.org/abs/2510.04618) - Stanford/SambaNova, 2024

### 參考專案

- [claude-coach-plugin](https://github.com/netresearch/claude-coach-plugin) - Claude Code 自我改進系統
- [llmace](https://github.com/kvyb/llmace) - ACE 論文的 Python 實現
- [open-agent-studio](https://github.com/open-agent-studio/agent) - 自主 Agent 運行時

### 技術文檔

- [Kiro Framework](https://kiro.dev/docs/) - Agent 框架官方文檔
- [Agent Skills Standard](https://agentskills.io) - Agent 技能標準

---

## 📄 授權協議

MIT License

Copyright (c) 2026 ax958888

---

## 🙏 致謝

- **Stanford University & SambaNova Systems** - ACE 研究團隊
- **Kiro Framework** - 提供優秀的 Agent 基礎設施
- **OpenClaw Community** - 多 Agent 協作靈感來源

---

## 📞 聯繫方式

- **GitHub Issues**: [提交問題](https://github.com/ax958888/Optimization-plan/issues)
- **Email**: 見 GitHub Profile
- **Telegram**: @Pojun_kirobot (Alkaid Bot)

---

**⭐ 如果這個方案對你有幫助，請給個 Star！**

---

## 📝 更新日誌

### v0.1.0 (2026-03-14)

- 🎉 初始版本發布
- 📐 完整架構設計
- 📋 4 階段實施計劃
- 🔧 核心代碼框架

---

**Made with ❤️ for Alkaid Agent**
