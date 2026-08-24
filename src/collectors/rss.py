"""RSS 采集器 - 完全免费"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict
import time
import re

class RSSCollector:
    """采集RSS源"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AI-Daily-Intelligence/1.0 (Research Bot; Contact: research@example.com)"
        })
    
    def fetch(self, sources: List[Dict], days_back: int = 1) -> List[Dict]:
        """获取RSS源内容"""
        events = []
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        
        for source in sources:
            try:
                url = source["url"]
                category = source.get("category", "ai_business")
                tier = source.get("tier", "B")
                
                response = self.session.get(url, timeout=30)
                if response.status_code != 200:
                    continue
                
                root = ET.fromstring(response.content)
                
                if root.tag == "rss" or root.tag.endswith("rss"):
                    items = self._parse_rss(root)
                else:
                    items = self._parse_atom(root)
                
                for item in items:
                    try:
                        pub_date = self._parse_date(item.get("pub_date", ""))
                        if pub_date and pub_date < cutoff:
                            continue
                        
                        title = item.get("title", "")
                        if not title:
                            continue
                        
                        if not self._is_ai_related(title + " " + item.get("summary", "")):
                            continue
                        
                        event = {
                            "id": f"rss_{self._hash_url(item.get('url', ''))}",
                            "title": title[:200],
                            "summary": item.get("summary", "")[:400],
                            "url": item.get("url", ""),
                            "source": self._extract_domain(url),
                            "source_tier": tier,
                            "published_at": pub_date.isoformat() if pub_date else datetime.utcnow().isoformat(),
                            "category": category,
                            "company": self._detect_company(title + " " + item.get("summary", "")),
                            "raw_score": self._source_tier_to_score(tier),
                        }
                        events.append(event)
                        
                    except Exception:
                        continue
                
                time.sleep(1)
                
            except Exception as e:
                print(f"[RSS] Error fetching {source.get('url', '')}: {e}")
                continue
        
        return events
    
    def _parse_rss(self, root) -> List[Dict]:
        """解析RSS格式"""
        items = []
        channel = root.find("channel")
        if channel is None:
            return items
        
        for item in channel.findall("item"):
            title = item.find("title")
            link = item.find("link")
            desc = item.find("description")
            pub_date = item.find("pubDate")
            
            items.append({
                "title": title.text if title is not None else "",
                "url": link.text if link is not None else "",
                "summary": self._strip_html(desc.text if desc is not None else ""),
                "pub_date": pub_date.text if pub_date is not None else "",
            })
        
        return items
    
    def _parse_atom(self, root) -> List[Dict]:
        """解析Atom格式"""
        items = []
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            link = entry.find("atom:link", ns)
            summary = entry.find("atom:summary", ns)
            content = entry.find("atom:content", ns)
            published = entry.find("atom:published", ns)
            
            text = summary.text if summary is not None else (content.text if content is not None else "")
            
            items.append({
                "title": title.text if title is not None else "",
                "url": link.get("href") if link is not None else "",
                "summary": self._strip_html(text or ""),
                "pub_date": published.text if published is not None else "",
            })
        
        return items
    
    def _strip_html(self, text: str) -> str:
        """去除HTML标签"""
        if not text:
            return ""
        clean = re.sub(r'<[^>]+>', '', text)
        return " ".join(clean.split())
    
    def _parse_date(self, date_str: str):
        """解析日期"""
        if not date_str:
            return None
        
        formats = [
            "%a, %d %b %Y %H:%M:%S %Z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _is_ai_related(self, text: str) -> bool:
        """检查是否AI相关"""
        ai_terms = [
            "AI", "artificial intelligence", "machine learning", "deep learning",
            "LLM", "large language model", "GPT", "Claude", "Gemini", "Llama",
            "neural network", "transformer", "agent", "autonomous",
            "OpenAI", "Anthropic", "Google", "DeepMind", "Meta", "xAI",
            "NVIDIA", "GPU", "training", "inference", "model",
            "robot", "humanoid", "embodied", "coding", "code generation",
            "开源", "open source", "Hugging Face", "GitHub",
        ]
        text_lower = text.lower()
        return any(term.lower() in text_lower for term in ai_terms)
    
    def _extract_domain(self, url: str) -> str:
        """提取域名"""
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        return match.group(1) if match else url
    
    def _detect_company(self, text: str) -> str:
        """检测公司"""
        text_lower = text.lower()
        companies = {
            "OpenAI": ["openai"],
            "Anthropic": ["anthropic"],
            "Google": ["google", "deepmind"],
            "Meta": ["meta", "llama"],
            "xAI": ["xai"],
            "Microsoft": ["microsoft"],
            "NVIDIA": ["nvidia"],
            "Apple": ["apple"],
            "Amazon": ["amazon"],
            "Hugging Face": ["huggingface"],
        }
        for company, keywords in companies.items():
            if any(kw in text_lower for kw in keywords):
                return company
        return ""
    
    def _source_tier_to_score(self, tier: str) -> int:
        """来源等级转分数"""
        mapping = {"S": 60, "A": 50, "B": 35, "C": 20}
        return mapping.get(tier, 25)
    
    def _hash_url(self, url: str) -> str:
        """简单URL哈希"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:12]
