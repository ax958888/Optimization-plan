# 📋 實施計劃

## 項目時間線

```
Week 1-2: 基礎設施搭建
Week 3-4: 錯誤學習循環
Week 5-6: Prompt 自動優化
Week 7+:  任務自主分解
```

---

## 階段 1：基礎設施 (Week 1-2)

### 目標
建立資料庫、解析器、基礎工具鏈

### 任務清單

#### Day 1-2: 環境準備
- [ ] 在 VPS 創建 `~/.kiro/learning/` 目錄
- [ ] 安裝 Python 依賴：`pip install openai pyyaml`
- [ ] 初始化 SQLite 資料庫：`python scripts/setup.py`
- [ ] 測試讀取 `conversations.jsonl`

```bash
# 執行命令
ssh hetzner "mkdir -p ~/.kiro/learning"
scp -r src/ hetzner:~/.kiro/learning/
ssh hetzner "cd ~/.kiro/learning && python3 scripts/setup.py"
```

#### Day 3-5: 開發 Analyzer
- [ ] 實現 JSONL 解析器
- [ ] 編寫錯誤檢測邏輯
  - SSH 超時檢測
  - Kubectl 錯誤識別
  - 用戶修正信號（"不對"、"錯了"）
- [ ] 實現模式統計功能

**測試命令**：
```bash
python3 src/analyzer.py --test --input sample.jsonl
```

**預期輸出**：
```json
{
  "errors_found": 5,
  "patterns": [
    {"type": "ssh_timeout", "count": 3},
    {"type": "kubectl_not_found", "count": 2}
  ]
}
```

#### Day 6-7: 建立存儲層
- [ ] 創建 SQLite Schema（`schema/insights.sql`）
- [ ] 實現 DAO 層（Database Access Object）
- [ ] 編寫資料庫遷移腳本

**測試命令**：
```bash
python3 scripts/migrate_db.py --init
sqlite3 ~/.kiro/learning/insights.db ".schema"
```

---

## 階段 2：錯誤學習循環 (Week 3-4)

### 目標
實現從錯誤中自動學習並生成改進建議

### 任務清單

#### Day 8-10: 開發 Learner
- [ ] 整合 OpenAI API
- [ ] 編寫 LLM Prompt 模板
- [ ] 實現批次處理邏輯
- [ ] 開發語義去重功能

**核心代碼**：
```python
# src/learner.py
class Learner:
    def analyze_errors(self, errors: List[dict]) -> List[Insight]:
        prompt = self.build_prompt(errors)
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        return self.parse_insights(response)
```

#### Day 11-12: 實現 Notifier
- [ ] Telegram Bot 整合
- [ ] 通知模板設計
- [ ] 測試消息發送

**測試命令**：
```bash
python3 src/notifier.py --test --message "測試通知"
```

#### Day 13-14: 端到端測試
- [ ] 運行完整分析流程
- [ ] 驗證 insights 存入資料庫
- [ ] 確認 Telegram 通知發送

**執行流程**：
```bash
# 1. 手動觸發分析
python3 src/scheduler.py --mode daily

# 2. 查看生成的建議
python3 src/learner.py --review

# 3. 批准一個建議
python3 src/learner.py --approve 1
```

---

## 階段 3：Prompt 自動優化 (Week 5-6)

### 目標
分析成功對話，優化 IDENTITY.md

### 任務清單

#### Day 15-17: 開發 Optimizer
- [ ] 實現文件讀寫模組
- [ ] 編寫 diff 生成邏輯
- [ ] 開發草稿管理系統

**核心功能**：
```python
# src/optimizer.py
class Optimizer:
    def optimize_identity(self, patterns: List[Pattern]) -> Draft:
        # 1. 讀取現有 IDENTITY.md
        current = self.read_file("~/.kiro/steering/IDENTITY.md")
        
        # 2. 調用 LLM 生成優化版本
        optimized = self.generate_optimized_version(current, patterns)
        
        # 3. 生成 diff
        diff = self.create_diff(current, optimized)
        
        # 4. 保存草稿
        return self.save_draft(optimized, diff)
```

#### Day 18-19: GitHub 整合
- [ ] 配置 GitHub API Token
- [ ] 實現自動 PR 創建
- [ ] 測試 PR 工作流

**測試命令**：
```bash
python3 src/optimizer.py --create-pr --draft-id 5
```

#### Day 20-21: 週報生成
- [ ] 統計本週學習數據
- [ ] 生成 Markdown 報告
- [ ] 自動發送到 Telegram

**報告示例**：
```markdown
# 📊 Alkaid 學習週報 (2026-03-10 ~ 2026-03-16)

## 統計數據
- 總對話數: 127
- 錯誤次數: 18 (-25% vs 上週)
- 用戶修正: 5 (-50% vs 上週)
- 成功率: 85.8% (+3.2% vs 上週)

## 本週學習成果
- 新增規則: 3 條
- 優化 Prompt: 1 次
- 創建 Skill: 1 個

## Top 改進建議
1. SSH 連線檢查規則 (已應用，錯誤率 -80%)
2. OpenClaw 狀態檢查 Skill (待審核)
3. 簡化回應風格 (已應用，用戶滿意度 +15%)
```

---

## 階段 4：任務自主分解 (Week 7+)

### 目標
識別複雜任務，自動拆解並追蹤執行

### 任務清單

#### Week 7: 任務識別
- [ ] 開發複雜任務檢測邏輯
- [ ] 建立任務分解模板庫
- [ ] 實現依賴關係分析

**示例任務分解**：
```yaml
# 原始任務
task: "優化 OpenClaw 資源使用"

# 自動分解
subtasks:
  - id: 1
    name: "分析當前資源使用"
    tools: ["kubectl top pods"]
    depends_on: []
  
  - id: 2
    name: "檢查 PVC 存儲"
    tools: ["df -h"]
    depends_on: []
  
  - id: 3
    name: "分析日誌瓶頸"
    tools: ["kubectl logs"]
    depends_on: [1]
  
  - id: 4
    name: "生成優化建議"
    tools: ["llm analysis"]
    depends_on: [1, 2, 3]
  
  - id: 5
    name: "執行安全優化"
    tools: ["kubectl apply"]
    depends_on: [4]
```

#### Week 8: 執行追蹤
- [ ] 實現任務狀態機
- [ ] 開發執行進度監控
- [ ] 建立失敗重試機制

**狀態轉換**：
```
pending → running → completed
        ↓
    failed → retry (3x) → permanent_failure
```

#### Week 9: 模板學習
- [ ] 記錄成功的分解模板
- [ ] 實現模板匹配算法
- [ ] 測試模板重用

**模板存儲**：
```python
# 存入資料庫
template = {
    "task_type": "resource_optimization",
    "keywords": ["優化", "資源", "性能"],
    "subtask_template": subtasks,
    "success_count": 5,
    "avg_completion_time": "15min"
}
db.save_template(template)
```

---

## 部署檢查清單

### 生產環境部署

#### 前置檢查
- [ ] VPS 可用內存 > 1GB
- [ ] Python 版本 >= 3.9
- [ ] OpenAI API Key 有效
- [ ] Telegram Bot Token 配置正確
- [ ] SSH Key 訪問 GitHub

#### 安裝步驟
```bash
# 1. 克隆項目
cd ~
git clone https://github.com/ax958888/Optimization-plan.git
cd Optimization-plan

# 2. 安裝依賴
pip3 install -r requirements.txt

# 3. 配置環境變量
cp .env.example .env
nano .env  # 填入 API Keys

# 4. 初始化系統
python3 scripts/setup.py

# 5. 測試運行
python3 src/analyzer.py --test

# 6. 安裝定時任務
python3 scripts/install_cron.py

# 7. 驗證 cron
crontab -l | grep "scheduler.py"
```

#### 驗證測試
```bash
# 測試分析器
python3 -m pytest tests/test_analyzer.py

# 測試學習器
python3 -m pytest tests/test_learner.py

# 測試優化器
python3 -m pytest tests/test_optimizer.py

# 端到端測試
python3 tests/e2e_test.py
```

---

## 監控與維護

### 日常運維

#### 每日檢查
```bash
# 查看今日分析日誌
tail -f ~/.kiro/learning/logs/daily_$(date +%Y%m%d).log

# 檢查待審核建議數
python3 src/learner.py --count-pending

# 查看資料庫大小
du -h ~/.kiro/learning/insights.db
```

#### 每週檢查
```bash
# 查看本週統計
python3 src/scheduler.py --mode weekly --dry-run

# 檢查 GitHub PR 狀態
python3 src/optimizer.py --list-prs

# 清理舊日誌（保留 30 天）
find ~/.kiro/learning/logs -mtime +30 -delete
```

#### 每月維護
```bash
# 資料庫優化
sqlite3 ~/.kiro/learning/insights.db "VACUUM;"

# 備份資料庫
cp ~/.kiro/learning/insights.db ~/.kiro/learning/backups/insights_$(date +%Y%m).db

# 生成月度報告
python3 src/scheduler.py --mode monthly-report
```

---

## 故障排除

### 常見問題

#### Q1: OpenAI API 超時
```bash
# 檢查網絡連接
curl -I https://api.openai.com

# 增加超時時間
export OPENAI_TIMEOUT=60

# 或在代碼中配置
client = OpenAI(timeout=60.0)
```

#### Q2: 資料庫鎖定錯誤
```bash
# 檢查是否有多個進程同時寫入
ps aux | grep scheduler.py

# 殺死舊進程
pkill -f scheduler.py

# 清理資料庫鎖
rm -f ~/.kiro/learning/insights.db-wal
rm -f ~/.kiro/learning/insights.db-shm
```

#### Q3: Telegram 通知失敗
```bash
# 測試 Bot Token
curl -X POST https://api.telegram.org/bot<TOKEN>/getMe

# 測試發送消息
python3 src/notifier.py --test

# 檢查 Chat ID
python3 src/notifier.py --get-chat-id
```

#### Q4: Cron 任務未執行
```bash
# 檢查 cron 服務狀態
systemctl status cron

# 查看 cron 日誌
grep CRON /var/log/syslog | tail -20

# 手動測試執行
/usr/bin/python3 ~/.kiro/learning/src/scheduler.py --mode daily
```

---

## 性能調優

### 優化建議

#### 1. 減少 LLM 調用次數
```python
# 批次處理（10 條錯誤一次分析）
for batch in chunk(errors, size=10):
    insights = learner.analyze_batch(batch)
```

#### 2. 啟用 Embedding 緩存
```python
from functools import lru_cache

@lru_cache(maxsize=256)
def get_embedding(text: str):
    return openai.embeddings.create(input=text)
```

#### 3. 資料庫索引優化
```sql
-- 創建複合索引
CREATE INDEX idx_errors_ts_status ON errors(timestamp, status);
CREATE INDEX idx_improvements_status_score ON improvements(status, impact_score DESC);
```

#### 4. 增量分析
```python
# 只分析上次運行後的新對話
last_run = db.get_last_run_timestamp()
new_conversations = read_since(last_run)
```

---

## 成功指標

### KPI 定義

| 指標 | 目標值 | 測量方法 |
|------|--------|---------|
| **錯誤率下降** | 首月 -15% | `SELECT COUNT(*) FROM errors WHERE date > ?` |
| **響應準確度** | 每週 +2% | 用戶反饋 + 修正次數 |
| **重複任務時間** | -30% | 對比同類任務執行時間 |
| **LLM 成本** | < $2/天 | OpenAI API 使用統計 |
| **系統可用性** | > 99% | Cron 任務成功率 |

### 數據收集

```python
# 每日統計
stats = {
    'date': today,
    'total_conversations': count_conversations(),
    'error_count': count_errors(),
    'correction_count': count_corrections(),
    'success_rate': calculate_success_rate(),
    'llm_cost': get_openai_cost()
}
db.save_statistics(stats)
```

### 報表生成

```bash
# 生成 30 天趨勢圖
python3 src/analytics.py --report monthly --output report.png
```

---

## 下一步規劃

### 未來功能

#### Phase 5: 多 Agent 協作
- 與 OpenClaw 其他 Agents（Astra, Lumix, Vera, Blaze, Forge）共享學習成果
- 建立中央學習資料庫
- 實現跨 Agent 知識遷移

#### Phase 6: 強化學習
- 引入獎勵機制（用戶點讚 = +1，修正 = -1）
- 實現 A/B 測試（兩種 Prompt 對比）
- 自動選擇最優策略

#### Phase 7: 預測性維護
- 預測可能出現的錯誤
- 主動發送警告通知
- 自動執行預防措施

---

**本實施計劃支持靈活調整，可根據實際情況調整優先級和時間線。**
