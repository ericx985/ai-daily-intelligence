"""历史数据库 - JSON Lines格式"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict
from src.config import DATA_DIR

class Database:
    """简单JSON历史数据库"""

    def __init__(self):
        self.db_path = os.path.join(DATA_DIR, "events.jsonl")
        os.makedirs(DATA_DIR, exist_ok=True)

    def load_recent(self, days: int = 30) -> List[Dict]:
        """加载最近N天的事件"""
        events = []
        cutoff = datetime.utcnow() - timedelta(days=days)

        if not os.path.exists(self.db_path):
            return events

        with open(self.db_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    pub = event.get("published_at", "")
                    if pub:
                        pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                        if pub_dt >= cutoff:
                            events.append(event)
                except Exception:
                    continue

        return events

    def is_duplicate(self, event: Dict, history: List[Dict]) -> bool:
        """检查事件是否已在历史中"""
        event_title = event.get("title", "").lower()
        event_company = event.get("company", "").lower()

        for old in history:
            if old.get("title", "").lower() == event_title:
                return True
            if (old.get("company", "").lower() == event_company and 
                event_company and 
                old.get("category") == event.get("category")):
                old_score = old.get("total_score", 0)
                new_score = event.get("total_score", 0)
                if new_score <= old_score * 1.2:
                    return True

        return False

    def save(self, events: List[Dict]):
        """保存事件到数据库"""
        with open(self.db_path, "a", encoding="utf-8") as f:
            for event in events:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def cleanup(self):
        """清理过期数据（保留最近90天）"""
        if not os.path.exists(self.db_path):
            return

        cutoff = datetime.utcnow() - timedelta(days=90)
        valid_lines = []

        with open(self.db_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line)
                    pub = event.get("published_at", "")
                    if pub:
                        pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                        if pub_dt >= cutoff:
                            valid_lines.append(line)
                except Exception:
                    continue

        with open(self.db_path, "w", encoding="utf-8") as f:
            f.writelines(valid_lines)
