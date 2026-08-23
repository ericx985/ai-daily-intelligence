"""GitHub 采集器 - 使用免费API额度"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import time
import os

class GitHubCollector:
    """采集GitHub上的AI相关趋势仓库和讨论"""

    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AI-Daily-Intelligence/1.0",
            "Accept": "application/vnd.github.v3+json"
        })

        # 如果有GITHUB_TOKEN，使用它获得更高额度(5000/hr vs 60/hr)
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            self.session.headers["Authorization"] = f"token {token}"

    def fetch(self, days_back: int = 1) -> List[Dict]:
        """获取GitHub上的AI相关内容"""
        events = []

        # 计算日期
        since_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        # 搜索热门仓库
        searches = [
            {"query": "AI agent stars:>50 pushed:>" + since_date, "category": "ai_agents"},
            {"query": "LLM OR "large language model" stars:>50 pushed:>" + since_date, "category": "frontier_models"},
            {"query": "AI coding OR "code generation" stars:>30 pushed:>" + since_date, "category": "ai_coding"},
            {"query": "robotics OR humanoid stars:>20 pushed:>" + since_date, "category": "robotics"},
            {"query": "open source AI model stars:>50 pushed:>" + since_date, "category": "open_source"},
        ]

        for search in searches:
            try:
                params = {
                    "q": search["query"],
                    "sort": "updated",
                    "order": "desc",
                    "per_page": 20
                }

                response = self.session.get(
                    f"{self.BASE_URL}/search/repositories",
                    params=params,
                    timeout=30
                )

                if response.status_code == 403:
                    # 速率限制，等待后重试
                    reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                    if reset_time:
                        wait = max(reset_time - int(time.time()), 0) + 5
                        print(f"[GitHub] Rate limited, waiting {wait}s...")
                        time.sleep(min(wait, 60))
                        continue

                response.raise_for_status()
                data = response.json()

                for item in data.get("items", []):
                    event = {
                        "id": f"github_repo_{item['id']}",
                        "title": f"[{item['full_name']}] {item['name']}",
                        "summary": item.get("description", "")[:300] or "无描述",
                        "url": item["html_url"],
                        "source": "github.com",
                        "source_tier": "S",
                        "published_at": item.get("pushed_at", datetime.utcnow().isoformat()),
                        "category": search["category"],
                        "company": self._detect_company(item.get("description", "") + " " + item["full_name"]),
                        "stars": item.get("stargazers_count", 0),
                        "language": item.get("language", ""),
                        "raw_score": min(50 + item.get("stargazers_count", 0) // 100, 80),
                    }
                    events.append(event)

                time.sleep(2)

            except Exception as e:
                print(f"[GitHub] Error: {e}")
                continue

        return events

    def _detect_company(self, text: str) -> str:
        """检测公司名"""
        text_lower = text.lower()
        companies = {
            "OpenAI": ["openai"],
            "Anthropic": ["anthropic"],
            "Google": ["google", "deepmind"],
            "Meta": ["meta", "llama"],
            "Microsoft": ["microsoft"],
            "NVIDIA": ["nvidia"],
            "Hugging Face": ["huggingface"],
        }
        for company, keywords in companies.items():
            if any(kw in text_lower for kw in keywords):
                return company
        return ""
