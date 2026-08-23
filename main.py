#!/usr/bin/env python3
"""AI Industry Daily Intelligence System - Main Entry"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import RSS_SOURCES, MIN_SCORE_FOR_REPORT
from src.collectors import ArxivCollector, GitHubCollector, HNCollector, RSSCollector
from src.deduplicator import Deduplicator
from src.scorer import Scorer
from src.database import Database
from src.reporter import Reporter

def main():
    print(f"🚀 AI Daily Intelligence System starting at {datetime.utcnow().isoformat()}")

    all_events = []

    print("[1/5] Collecting from arXiv...")
    try:
        arxiv = ArxivCollector()
        all_events.extend(arxiv.fetch(days_back=1))
    except Exception as e:
        print(f"  ⚠️ arXiv error: {e}")

    print("[2/5] Collecting from GitHub...")
    try:
        github = GitHubCollector()
        all_events.extend(github.fetch(days_back=1))
    except Exception as e:
        print(f"  ⚠️ GitHub error: {e}")

    print("[3/5] Collecting from Hacker News...")
    try:
        hn = HNCollector()
        all_events.extend(hn.fetch(days_back=1, min_score=50))
    except Exception as e:
        print(f"  ⚠️ HN error: {e}")

    print("[4/5] Collecting from RSS feeds...")
    try:
        rss = RSSCollector()
        all_events.extend(rss.fetch(RSS_SOURCES, days_back=1))
    except Exception as e:
        print(f"  ⚠️ RSS error: {e}")

    print(f"  📊 Total raw events: {len(all_events)}")

    if not all_events:
        print("⚠️ No events collected today. Exiting.")
        return

    print("[5/5] Deduplicating...")
    dedup = Deduplicator()
    events = dedup.deduplicate(all_events)
    print(f"  📊 After dedup: {len(events)}")

    print("Scoring events...")
    scorer = Scorer()
    events = scorer.score(events)

    print("Checking history...")
    db = Database()
    history = db.load_recent(days=30)
    new_events = [e for e in events if not db.is_duplicate(e, history)]
    print(f"  📊 New events: {len(new_events)}")

    db.save(new_events)
    db.cleanup()

    print("Generating report...")
    reporter = Reporter()
    report_path = reporter.generate(new_events)
    print(f"  ✅ Report saved: {report_path}")

    print("Done.")

if __name__ == "__main__":
    main()
