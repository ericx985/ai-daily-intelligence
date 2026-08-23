"""数据采集器模块"""
from .arxiv import ArxivCollector
from .github import GitHubCollector
from .hackernews import HNCollector
from .rss import RSSCollector

__all__ = ["ArxivCollector", "GitHubCollector", "HNCollector", "RSSCollector"]
