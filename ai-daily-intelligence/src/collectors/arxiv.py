"""arXiv 论文采集器 - 完全免费"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict
import time

class ArxivCollector:
    """采集arXiv最新AI相关论文"""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AI-Daily-Intelligence/1.0 (Research Bot)"
        })

    def fetch(self, days_back: int = 1) -> List[Dict]:
        """获取过去N天的论文"""
        events = []

        # 计算日期范围
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)

        # arXiv搜索AI相关论文
        search_queries = [
            "cat:cs.AI",
            "cat:cs.LG",
            "cat:cs.CL",
            "cat:cs.CV",
            "cat:cs.RO",
        ]

        for query in search_queries:
            try:
                params = {
                    "search_query": query,
                    "start": 0,
                    "max_results": 50,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                }

                response = self.session.get(self.BASE_URL, params=params, timeout=30)
                response.raise_for_status()

                # 解析XML
                root = ET.fromstring(response.content)

                # arXiv Atom命名空间
                ns = {
                    "atom": "http://www.w3.org/2005/Atom",
                    "arxiv": "http://arxiv.org/schemas/atom"
                }

                for entry in root.findall("atom:entry", ns):
                    title = entry.find("atom:title", ns)
                    summary = entry.find("atom:summary", ns)
                    published = entry.find("atom:published", ns)
                    link = entry.find("atom:link[@rel='alternate']", ns)
                    authors = entry.findall("atom:author/atom:name", ns)

                    if title is None or published is None:
                        continue

                    pub_date = datetime.fromisoformat(published.text.replace("Z", "+00:00"))

                    # 只保留指定日期范围内的
                    if pub_date < start_date.replace(tzinfo=pub_date.tzinfo):
                        continue

                    event = {
                        "id": f"arxiv_{link.get('href', '').split('/')[-1] if link is not None else ''}",
                        "title": self._clean_text(title.text),
                        "summary": self._clean_text(summary.text[:500] + "..." if summary is not None else ""),
                        "url": link.get("href") if link is not None else "",
                        "source": "arxiv.org",
                        "source_tier": "S",
                        "published_at": pub_date.isoformat(),
                        "category": self._map_category(query),
                        "company": self._detect_company(title.text or ""),
                        "authors": [a.text for a in authors[:3]],
                        "raw_score": 60,  # 学术论文基础分较高
                    }
                    events.append(event)

                time.sleep(3)  # 尊重arXiv速率限制

            except Exception as e:
                print(f"[arXiv] Error fetching {query}: {e}")
                continue

        return events

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        return " ".join(text.replace("
", " ").split())

    def _map_category(self, query: str) -> str:
        """映射arXiv分类到系统分类"""
        mapping = {
            "cat:cs.AI": "ai_research",
            "cat:cs.LG": "ai_research",
            "cat:cs.CL": "ai_research",
            "cat:cs.CV": "ai_research",
            "cat:cs.RO": "robotics",
        }
        return mapping.get(query, "ai_research")

    def _detect_company(self, text: str) -> str:
        """检测论文中提到的公司"""
        text_lower = text.lower()
        companies = {
            "OpenAI": ["openai"],
            "Anthropic": ["anthropic"],
            "Google": ["google", "deepmind"],
            "Meta": ["meta", "facebook"],
            "Microsoft": ["microsoft"],
            "NVIDIA": ["nvidia"],
        }
        for company, keywords in companies.items():
            if any(kw in text_lower for kw in keywords):
                return company
        return ""
