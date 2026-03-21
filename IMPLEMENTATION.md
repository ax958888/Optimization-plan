# 實施計畫

## 時間線

```
Phase 1 (Week 1):   收集 + 分析基礎
Phase 2 (Week 2-3): 學習閉環 + QMD 整合
Phase 3 (Week 4):   週報 + GitHub PR
Phase 4 (Week 5+):  任務分解模板
```

---

## Phase 1: 收集 + 分析 (Week 1)

### 目標
Kanban Bot 每日 23:30 自動收集當日任務資料，分析錯誤模式，觸發 Alkaid 學習。

### 需修改的檔案

| 檔案 | 修改內容 |
|------|----------|
| `/root/kanban-kiro-bot/services/orchestrator.py` | 加入 daily digest scheduler + collector 邏輯 |
| `/root/kanban-kiro-bot/models/database.py` | 新增 `get_tasks_by_date()` 查詢方法 |
| `/root/kanban-kiro-bot/bot.py` | 啟動 daily_digest_scheduler task loop |
| `/root/alkaid-bot/bot.py` | 在 on_message 中識別 Kanban Bot 的 @mention digest，觸發 Kiro CLI 分析 |

### 新增的檔案

| 檔案 | 內容 |
|------|------|
| `/root/.kiro/learning/insights.db` | SQLite 學習資料庫 (由 setup.py 初始化) |
| `/root/.kiro/learning/daily/` | 每日 digest JSON 存放目錄 |

### Kanban Bot 新增功能

```python
# orchestrator.py 新增
@tasks.loop(seconds=30)
async def daily_digest_scheduler(self):
    now = datetime.now(TZ_TAIPEI)
    if now.hour == 23 and now.minute == 30:
        await self._generate_daily_digest()

async def _generate_daily_digest(self):
    # 1. Query today's tasks from kanban.db
    today = datetime.now(TZ_TAIPEI).strftime("%Y-%m-%d")
    tasks = await self.db.get_tasks_by_date(today)

    if not tasks:
        return  # 無任務，跳過

    # 2. Read recent conversations.jsonl
    conversations = read_recent_conversations(hours=24)

    # 3. Run analyzer
    analysis = analyze(tasks, conversations)

    # 4. Save daily digest JSON
    save_digest(today, analysis)

    # 5. Save to insights.db
    save_statistics(today, analysis)

    # 6. @mention Alkaid in #alkaid with summary
    channel = self.bot.get_channel(ALKAID_CHANNEL_ID)
    await channel.send(
        f"<@{ALKAID_BOT_ID}> Daily Learning Digest — {today}\n"
        f"Tasks: {analysis['done']} done, {analysis['failed']} failed\n"
        f"Errors detected: {analysis['error_count']}\n"
        f"Please analyze and update .learnings/"
    )
```

### 驗收標準
- [ ] 23:30 Taipei 自動觸發收集
- [ ] Kanban SQLite 查詢正確回傳當日任務
- [ ] daily_digest.json 寫入 `/root/.kiro/learning/daily/`
- [ ] Discord API `channel.history()` 正確拉取 #alkaid 最近 24h 對話
- [ ] 用戶糾正/Bot 錯誤/❌ reaction 偵測正確
- [ ] insights.db errors 表有 source='alkaid_chat' 記錄
- [ ] #alkaid 收到 @mention + 摘要 (含 Chat Analysis 區塊)
- [ ] Alkaid Kiro CLI 被觸發，輸出分析報告
- [ ] #archive 收到 Daily Learning Digest embed

---

## Phase 2: 學習閉環 + QMD (Week 2-3)

### 目標
Alkaid 接收分析結果後，自動：
1. 透過 QMD 搜尋去重（避免重複學習）
2. 寫入 `.learnings/` (ERRORS.md, LEARNINGS.md)
3. 更新 QMD 向量索引
4. 記錄改進建議到 insights.db

### Alkaid Bot 修改

```python
# alkaid-bot/bot.py on_message 新增
async def on_message(self, message):
    # ... 既有邏輯 ...

    # 偵測 Kanban Bot 的 Daily Digest @mention
    if message.author.id == KANBAN_BOT_ID and "Daily Learning Digest" in message.content:
        await self._process_daily_digest(message)
        return

async def _process_daily_digest(self, message):
    # 1. 提取 digest 內容
    # 2. 構建 Kiro CLI prompt:
    prompt = """
    分析以下每日任務摘要，執行學習流程：

    {digest_content}

    步驟：
    1. 對每個 failed/timeout 任務，識別根因
    2. 執行 `qmd search "{error_keyword}" -c alkaid` 檢查是否已知問題
    3. 如果是新問題，寫入 /root/.kiro/.learnings/ERRORS.md
    4. 提煉通用解決方案，寫入 /root/.kiro/.learnings/LEARNINGS.md
    5. 執行 `qmd embed -c alkaid` 更新向量索引
    6. 輸出分析報告（繁體中文）：
       - 今日統計
       - 新學到的知識
       - 改進建議
    """
    output = await self.kiro.run(prompt, timeout=300)

    # 3. 發送到 #alkaid
    # 4. 發送 embed 到 #archive
    # 5. 記錄到 insights.db
```

### QMD 去重邏輯

```python
# src/qmd_dedup.py
async def is_known_error(error_description: str) -> bool:
    """Check if this error pattern is already in QMD index."""
    proc = await asyncio.create_subprocess_exec(
        "qmd", "search", error_description, "-c", "alkaid", "--limit", "3",
        stdout=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    results = parse_qmd_output(stdout)
    # If top result similarity > 0.85, consider it known
    return any(r.score > 0.85 for r in results)
```

### 驗收標準
- [ ] Alkaid 接收 Kanban digest 後自動觸發 Kiro CLI
- [ ] QMD search 去重正確運作（不重複記錄已知問題）
- [ ] `.learnings/ERRORS.md` 有新內容追加
- [ ] `.learnings/LEARNINGS.md` 有新知識寫入
- [ ] `qmd embed -c alkaid` 成功更新索引
- [ ] insights.db improvements 表有新記錄
- [ ] #archive 有 Daily Learning Digest embed

---

## Phase 3: 週報 + GitHub PR (Week 4)

### 目標
每週日自動彙整一週學習成果，發送到 #archive + GitHub Issue。
當 pending improvements >= 5 時，自動建立 IDENTITY.md 優化 PR。

### 週報生成

```python
# 每週日 23:30 觸發 (Kanban Bot scheduler)
async def _generate_weekly_report(self):
    # 1. Query insights.db: 本週 statistics
    # 2. Query insights.db: 本週 improvements (pending + applied)
    # 3. 生成 Markdown 報告
    # 4. 發送 #archive Weekly Report embed
    # 5. GitHub Issue: weekly learning report
```

### 週報格式

```markdown
## Weekly Learning Report — 2026-03-17 ~ 2026-03-23

### Statistics
| Day | Tasks | Done | Failed | Timeout | Success Rate |
|-----|-------|------|--------|---------|--------------|
| Mon | 3     | 2    | 1      | 0       | 66.7%        |
| Tue | 5     | 5    | 0      | 0       | 100%         |
| ... |       |      |        |         |              |
| **Total** | **21** | **18** | **2** | **1** | **85.7%** |

### New Learnings This Week
1. helm upgrade 前需檢查 PVC 空間 (from Task #15)
2. Kiro CLI timeout 對大型 repo 需提高至 900s (from Task #18)

### Pending Improvements
- [#3] rule: SSH 連線前 uptime 檢查 (score: 0.8)
- [#5] prompt: 複雜任務先列計畫再執行 (score: 0.7)

### QMD Index
- alkaid collection: 17 → 21 files (+4)
- 新增向量: 8

### Error Rate Trend
Week 1: 35% → Week 2: 28% → Week 3: 22% → **This Week: 14.3%**
```

### Prompt 優化 PR

```python
# optimizer.py
async def check_and_create_pr(self):
    pending = db.count_pending_improvements()
    if pending >= 5:
        # 1. Read current IDENTITY.md
        # 2. Build Kiro CLI prompt with pending improvements
        # 3. Generate optimized IDENTITY.md draft
        # 4. Create GitHub PR via API
        # 5. Notify #alkaid
```

### 驗收標準
- [ ] 每週日 23:30 自動生成週報
- [ ] #archive 有 Weekly Report embed
- [ ] GitHub Issue 週報自動建立
- [ ] 累積 5+ pending improvements 時自動建 PR
- [ ] PR 包含 IDENTITY.md diff 和改進理由

---

## Phase 4: 任務分解模板 (Week 5+)

### 目標
記錄成功的複雜任務分解模式，建立模板庫，未來遇到相似任務時自動套用。

### 模板記錄

```python
# 任務完成時記錄分解模式
async def record_task_template(self, task, subtasks, duration):
    template = {
        "task_type": classify_task(task.title),
        "keywords": extract_keywords(task.title + task.description),
        "subtask_template": subtasks,
        "success_count": 1,
        "avg_completion_time": duration,
    }
    db.save_or_update_template(template)
```

### 模板匹配

```python
# 新任務進來時搜尋模板
async def find_matching_template(self, task_title):
    # 1. QMD search in task_templates
    # 2. Keyword matching
    # 3. Return best match (if confidence > 0.7)
    templates = db.search_templates(keywords)
    if templates and templates[0].confidence > 0.7:
        return templates[0]
    return None
```

### 驗收標準
- [ ] 完成的複雜任務自動記錄分解模式
- [ ] 新任務可以搜尋到匹配的模板
- [ ] 模板使用次數和成功率有追蹤

---

## 部署檢查清單

### 前置條件 (全部已滿足)
- [x] Kanban Bot 運行中 (kanban-kiro-bot.service)
- [x] Alkaid Bot 運行中 (alkaid-bot.service)
- [x] Kiro CLI 1.27.1 已安裝
- [x] QMD MCP Server 運行中 (qmd-mcp.service :8181)
- [x] GitHub PAT 已配置 (kanban-bot + alkaid-bot 共用)
- [x] .learnings/ 目錄存在且有 error-logger + pre-check skill
- [x] #archive 頻道已啟用歸檔功能
- [x] 磁碟空間充足 (35GB/75GB, 49%)

### 初始化步驟

```bash
# 1. 建立 learning 目錄
mkdir -p /root/.kiro/learning/daily

# 2. 初始化 insights.db
sqlite3 /root/.kiro/learning/insights.db < schema/insights.sql

# 3. 修改 Kanban Bot (加入 collector + scheduler)
# 4. 修改 Alkaid Bot (加入 digest handler)
# 5. 重啟 Bot services
systemctl restart kanban-kiro-bot alkaid-bot

# 6. 驗證
curl http://localhost:9000/health  # Kanban webhook OK
```

---

## 監控與維護

### 每日自動
- 23:30: daily digest 收集 + 分析 + 學習 + #archive embed

### 每週自動 (週日)
- 23:30: weekly report + GitHub Issue

### 每月手動
```bash
# 資料庫優化
sqlite3 /root/.kiro/learning/insights.db "VACUUM;"

# 清理 30 天前的 daily digest JSON
find /root/.kiro/learning/daily -name "*.json" -mtime +30 -delete

# 檢查 QMD 索引大小
qmd list
```

---

## 成功指標

| 指標 | 首月目標 | 三月目標 |
|------|----------|----------|
| 錯誤率下降 | -15% | -40% |
| 重複任務耗時 | -20% | -40% |
| QMD 知識量 | +20 files | +60 files |
| .learnings/ 條目 | +10 | +30 |
| 週報連續產出 | 4 週 | 12 週 |
