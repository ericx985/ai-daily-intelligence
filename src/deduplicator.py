"""去重引擎 - 核心功能"""
import re
from difflib import SequenceMatcher
from typing import List, Dict
import hashlib

class Deduplicator:
    """事件去重引擎"""
    
    def __init__(self, similarity_threshold: float = 0.72):
        self.similarity_threshold = similarity_threshold
    
    def deduplicate(self, events: List[Dict]) -> List[Dict]:
        """去重并合并事件"""
        if not events:
            return []
        
        events = self._dedup_by_url(events)
        events = self._dedup_by_title(events)
        events = self._dedup_by_company_event(events)
        
        for e in events:
            if "urls" not in e:
                e["urls"] = [e.get("url", "")] if e.get("url") else []
        
        return events
    
    def _dedup_by_url(self, events: List[Dict]) -> List[Dict]:
        """基于URL去重"""
        seen_urls = {}
        unique = []
        
        for event in events:
            url = event.get("url", "")
            normalized = self._normalize_url(url)
            
            if normalized in seen_urls:
                existing = seen_urls[normalized]
                self._merge_events(existing, event)
            else:
                event["sources"] = [event.get("source", "")]
                event["urls"] = [url] if url else []
                seen_urls[normalized] = event
                unique.append(event)
        
        return unique
    
    def _dedup_by_title(self, events: List[Dict]) -> List[Dict]:
        """基于标题相似度去重"""
        unique = []
        
        for event in events:
            title = self._normalize_title(event.get("title", ""))
            is_duplicate = False
            
            for existing in unique:
                existing_title = self._normalize_title(existing.get("title", ""))
                similarity = SequenceMatcher(None, title, existing_title).ratio()
                
                if similarity >= self.similarity_threshold:
                    self._merge_events(existing, event)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                if "urls" not in event:
                    event["urls"] = [event.get("url", "")] if event.get("url") else []
                unique.append(event)
        
        return unique
    
    def _dedup_by_company_event(self, events: List[Dict]) -> List[Dict]:
        """基于公司+事件类型去重"""
        unique = []
        
        for event in events:
            company = event.get("company", "")
            if not company:
                if "urls" not in event:
                    event["urls"] = [event.get("url", "")] if event.get("url") else []
                unique.append(event)
                continue
            
            event_type = self._extract_event_type(event.get("title", ""))
            key = f"{company}_{event_type}"
            
            is_duplicate = False
            for existing in unique:
                existing_key = f"{existing.get('company', '')}_{self._extract_event_type(existing.get('title', ''))}"
                if key == existing_key and key != "_":
                    self._merge_events(existing, event)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                if "urls" not in event:
                    event["urls"] = [event.get("url", "")] if event.get("url") else []
                unique.append(event)
        
        return unique
    
    def _merge_events(self, existing: Dict, new: Dict):
        """合并两个事件"""
        if "sources" not in existing:
            existing["sources"] = [existing.get("source", "")]
        
        new_source = new.get("source", "")
        if new_source and new_source not in existing["sources"]:
            existing["sources"].append(new_source)
        
        # 关键修复：合并具体URL
        if "urls" not in existing:
            existing["urls"] = [existing.get("url", "")] if existing.get("url") else []
        
        new_url = new.get("url", "")
        if new_url and new_url not in existing["urls"]:
            existing["urls"].append(new_url)
        
        if new.get("raw_score", 0) > existing.get("raw_score", 0):
            existing["raw_score"] = new["raw_score"]
        
        if len(new.get("summary", "")) > len(existing.get("summary", "")):
            existing["summary"] = new["summary"]
        
        existing_pub = existing.get("published_at", "")
        new_pub = new.get("published_at", "")
        if new_pub and (not existing_pub or new_pub < existing_pub):
            existing["published_at"] = new_pub
    
    def _normalize_url(self, url: str) -> str:
        url = url.lower().strip()
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        url = re.sub(r'[?#].*$', '', url)
        url = re.sub(r'/+$', '', url)
        return url
    
    def _normalize_title(self, title: str) -> str:
        title = title.lower()
        title = re.sub(r'[^\w\s]', '', title)
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                     "being", "have", "has", "had", "do", "does", "did", "will",
                     "would", "could", "should", "may", "might", "must", "shall",
                     "can", "need", "dare", "ought", "used", "to", "of", "in",
                     "for", "on", "with", "at", "by", "from", "as", "into",
                     "through", "during", "before", "after", "above", "below",
                     "between", "under", "again", "further", "then", "once",
                     "here", "there", "when", "where", "why", "how", "all",
                     "each", "few", "more", "most", "other", "some", "such",
                     "no", "nor", "not", "only", "own", "same", "so", "than",
                     "too", "very", "just", "and", "but", "if", "or", "because",
                     "until", "while", "this", "that", "these", "those"}
        words = [w for w in title.split() if w not in stopwords and len(w) > 2]
        return " ".join(words)
    
    def _extract_event_type(self, title: str) -> str:
        title_lower = title.lower()
        
        if any(w in title_lower for w in ["release", "发布", "launch", "推出", "introduce"]):
            return "release"
        elif any(w in title_lower for w in ["funding", "融资", "invest", "投资", "million", "billion"]):
            return "funding"
        elif any(w in title_lower for w in ["acquisition", "收购", "merge", "合并", "buy"]):
            return "mna"
        elif any(w in title_lower for w in ["paper", "论文", "research", "研究", "arxiv"]):
            return "research"
        elif any(w in title_lower for w in ["update", "升级", "new version", "v2", "v3"]):
            return "update"
        elif any(w in title_lower for w in ["partnership", "合作", "collaborate", "team up"]):
            return "partnership"
        elif any(w in title_lower for w in ["benchmark", "测试", "leaderboard", "sota"]):
            return "benchmark"
        elif any(w in title_lower for w in ["open source", "开源", "github", "release model"]):
            return "opensource"
        else:
            return "general"
