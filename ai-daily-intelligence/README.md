# AI Industry Daily Intelligence System

完全免费的AI行业每日情报自动化系统。成本：**$0/月**。

## 系统状态

| 项目 | 状态 |
|------|------|
| 定时运行 | ✅ GitHub Actions (公共仓库免费) |
| 数据来源 | ✅ arXiv + GitHub + HN + RSS (全免费) |
| 去重 | ✅ 本地Python规则引擎 |
| 评分 | ✅ 多维度规则评分 |
| 报告生成 | ✅ Markdown自动输出 |
| 历史数据库 | ✅ JSON Lines本地存储 |

## 部署步骤（5分钟完成）

### 第1步：创建GitHub仓库
1. 访问 https://github.com/new
2. Repository name: `ai-daily-intelligence`
3. 选择 **Public**（公共仓库Actions完全免费）
4. 勾选 "Add a README file"
5. 点击 **Create repository**

### 第2步：上传代码
1. 在你的仓库页面，点击 "Add file" → "Upload files"
2. 将本项目的所有文件和文件夹拖拽上传
3. 确保目录结构正确：
   ```
   ai-daily-intelligence/
   ├── .github/workflows/daily.yml
   ├── src/
   ├── data/
   ├── reports/
   ├── main.py
   └── requirements.txt
   ```
4. Commit changes

### 第3步：验证运行
1. 进入仓库的 **Actions** 标签页
2. 点击左侧 "AI Daily Intelligence"
3. 点击 "Run workflow" → 选择分支 `main` → **Run workflow**
4. 等待2-3分钟，查看运行结果

### 第4步：查看报告
- 报告自动生成在 `reports/YYYY-MM-DD.md`
- 历史数据保存在 `data/events.jsonl`

## 每天什么时候运行？

- **默认**: 每天 UTC 02:00（北京时间 10:00）
- **手动**: 随时在Actions页面点击 "Run workflow"
- **注意**: 新仓库的schedule可能有8-14小时延迟，属GitHub正常机制，运行几次后会稳定

## 信息源覆盖

| 领域 | 来源 |
|------|------|
| 前沿模型 | GitHub Trending, RSS |
| AI Agent | GitHub Search, HN |
| AI编程 | GitHub Search |
| 开源 | HuggingFace Blog RSS, GitHub |
| AI研究 | arXiv cs.AI/LG/CL/CV/RO |
| AI硬件 | HN, RSS |
| 基础设施 | GitHub, RSS |
| 机器人 | arXiv cs.RO, GitHub |
| 商业 | TechCrunch, The Verge, VentureBeat RSS |

## 免费限制说明

| 服务 | 免费额度 | 是否足够 |
|------|---------|---------|
| GitHub Actions (Public) | 无限分钟 | ✅ 足够 |
| GitHub API | 60次/小时 (无Token) / 5000次/小时 (有Token) | ✅ 足够 |
| arXiv API | 无限制 | ✅ 足够 |
| Hacker News API | 无限制 | ✅ 足够 |
| RSS | 无限制 | ✅ 足够 |

**注意**: 系统会自动使用 `GITHUB_TOKEN`（GitHub自动提供，无需手动配置），获得5000次/小时的API额度。

## 如果任务失败

1. 进入仓库 **Actions** 标签页
2. 点击失败的运行记录
3. 查看日志中的错误信息
4. 常见问题：
   - 网络超时：重新运行即可
   - API限制：等待1小时后重试
   - 无输出：当天数据源确实无重大更新

## 自定义配置

编辑 `src/config.py`：
- `RSS_SOURCES`: 添加/删除RSS源
- `IMPACT_KEYWORDS`: 调整重要性关键词
- `MIN_SCORE_FOR_REPORT`: 调整报道阈值（默认40分）
- `DAYS_HISTORY`: 历史保留天数

## 成本确认

- **月成本**: $0
- **隐藏收费**: 无
- **需要信用卡**: 否
- **需要API Key**: 否（GitHub Token自动提供）
