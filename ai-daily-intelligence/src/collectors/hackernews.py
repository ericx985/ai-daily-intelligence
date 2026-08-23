"""Hacker News 采集器 - 完全免费"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import time

class HNCollector:
    """采集Hacker News上的AI相关内容"""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AI-Daily-Intelligence/1.0"
        })

    def fetch(self, days_back: int = 1, min_score: int = 50) -> List[Dict]:
        """获取HN热门AI内容"""
        events = []

        # AI相关关键词
        ai_keywords = [
            "AI", "LLM", "GPT", "Claude", "OpenAI", "Anthropic", "Gemini",
            "machine learning", "deep learning", "neural network",
            "agent", "autonomous", "robot", "NVIDIA", "GPU",
            "model", "training", "inference", "transformer",
        ]

        try:
            # 获取热门故事ID
            top_response = self.session.get(
                f"{self.BASE_URL}/topstories.json",
                timeout=30
            )
            top_response.raise_for_status()
            top_ids = top_response.json()[:100]

            # 获取每个故事的详情
            for story_id in top_ids:
                try:
                    story_response = self.session.get(
                        f"{self.BASE_URL}/item/{story_id}.json",
                        timeout=10
                    )
                    story_response.raise_for_status()
                    story = story_response.json()

                    if not story or story.get("deleted") or story.get("dead"):
                        continue

                    title = story.get("title", "")
                    score = story.get("score", 0)

                    # 过滤低分和无关内容
                    if score < min_score:
                        continue

                    # 检查是否AI相关
                    title_lower = title.lower()
                    if not any(kw.lower() in title_lower for kw in ai_keywords):
                        continue

                    # 确定分类
                    category = self._categorize(title)

                    event = {
                        "id": f"hn_{story_id}",
                        "title": title,
                        "summary": f"Hacker News热门讨论，{score}分，{story.get('descendants', 0)}条评论",
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        "source": "news.ycombinator.com",
                        "source_tier": "C",
                        "published_at": datetime.fromtimestamp(story.get("time", 0)).isoformat(),
                        "category": category,
                        "company": self._detect_company(title),
                        "hn_score": score,
                        "hn_comments": story.get("descendants", 0),
                        "raw_score": min(score // 2, 70),
                    }
                    events.append(event)

                    time.sleep(0.1)  # 尊重API

                except Exception as e:
                    continue

        except Exception as e:
            print(f"[HN] Error: {e}")

        return events

    def _categorize(self, title: str) -> str:
        """分类"""
        t = title.lower()
        if any(k in t for k in ["agent", "autonomous", "browser", "computer use"]):
            return "ai_agents"
        elif any(k in t for k in ["code", "coding", "programming", "software", "developer"]):
            return "ai_coding"
        elif any(k in t for k in ["robot", "humanoid", "embodied"]):
            return "robotics"
        elif any(k in t for k in ["open source", "llama", "mistral", "huggingface", "github"]):
            return "open_source"
        elif any(k in t for k in ["gpu", "chip", "hardware", "nvidia", "tpu", "npu"]):
            return "ai_hardware"
        elif any(k in t for k in ["model", "gpt", "claude", "gemini", "llm", "foundation"]):
            return "frontier_models"
        else:
            return "ai_research"

    def _detect_company(self, text: str) -> str:
        """检测公司"""
        text_lower = text.lower()
        companies = {
            "OpenAI": ["openai", "gpt", "chatgpt"],
            "Anthropic": ["anthropic", "claude"],
            "Google": ["google", "deepmind", "gemini"],
            "Meta": ["meta", "llama"],
            "xAI": ["xai", "grok"],
            "Microsoft": ["microsoft", "copilot"],
            "NVIDIA": ["nvidia"],
        }
        for company, keywords in companies.items():
            if any(kw in text_lower for kw in keywords):
                return company
        return ""
