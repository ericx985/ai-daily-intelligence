"""
AI Industry Daily Intelligence System - Configuration
完全免费配置，所有数据源均为免费API或公开RSS
"""

import os
from datetime import datetime, timedelta

# === 基础配置 ===
DATA_DIR = os.environ.get("DATA_DIR", "data")
REPORTS_DIR = os.environ.get("REPORTS_DIR", "reports")
DAYS_HISTORY = 30  # 保留历史天数
MIN_SCORE_FOR_REPORT = 40  # 最低报道分数

# === 分类配置 ===
CATEGORIES = {
    "frontier_models": "前沿模型",
    "ai_agents": "AI Agent",
    "ai_coding": "AI 编程",
    "open_source": "开源 AI",
    "ai_research": "AI 研究",
    "ai_hardware": "AI 硬件",
    "ai_infrastructure": "AI 基础设施",
    "robotics": "机器人",
    "ai_business": "AI 商业",
}

# === 来源权重 (S=1.0, A=0.8, B=0.5, C=0.3) ===
SOURCE_TIERS = {
    # S级：第一手来源
    "openai.com": 1.0,
    "anthropic.com": 1.0,
    "deepmind.google": 1.0,
    "research.google": 1.0,
    "ai.meta.com": 1.0,
    "x.ai": 1.0,
    "arxiv.org": 1.0,
    "github.com": 1.0,
    "huggingface.co": 1.0,
    "nvidia.com": 1.0,
    "apple.com": 1.0,
    "microsoft.com": 1.0,
    "amazon.com": 1.0,

    # A级：专业媒体
    "reuters.com": 0.8,
    "bloomberg.com": 0.8,
    "ft.com": 0.8,
    "technologyreview.com": 0.8,
    "ieee.org": 0.8,
    "techcrunch.com": 0.8,
    "theverge.com": 0.8,
    "venturebeat.com": 0.8,
    "arstechnica.com": 0.8,
    "wired.com": 0.8,
    "zdnet.com": 0.8,

    # B级：技术媒体
    "medium.com": 0.5,
    "dev.to": 0.5,
    "towardsdatascience.com": 0.5,
    "analyticsvidhya.com": 0.5,

    # C级：社区
    "reddit.com": 0.3,
    "news.ycombinator.com": 0.4,  # HN略高于一般社区
    "twitter.com": 0.3,
    "x.com": 0.3,
}

# === 重要性评分关键词 ===
IMPACT_KEYWORDS = {
    "critical": [
        "发布新模型", "new model", "model release", "GPT", "Claude", "Gemini", "Llama",
        "融资", "funding", "IPO", "收购", "acquisition", "merger",
        "突破", "breakthrough", "里程碑", "milestone", "SOTA", "state of the art",
        "开源", "open source", "open-source",
        "安全", "safety", "alignment", "监管", "regulation",
    ],
    "high": [
        "更新", "update", "升级", "upgrade",
        "API", "launch", "发布", "release",
        "合作", "partnership", "collaboration",
        "基准测试", "benchmark", "leaderboard",
        "论文", "paper", "研究", "research",
        "推理", "reasoning", "agent", "多模态", "multimodal",
        "机器人", "robot", "人形", "humanoid",
        "芯片", "chip", "GPU", "TPU", "NPU",
    ],
    "medium": [
        "工具", "tool", "框架", "framework",
        "教程", "tutorial", "指南", "guide",
        "分析", "analysis", "报告", "report",
        "趋势", "trend", "预测", "prediction",
    ],
}

# === RSS 源配置 (全免费) ===
RSS_SOURCES = [
    # AI研究
    {"url": "http://export.arxiv.org/rss/cs.AI", "category": "ai_research", "tier": "S"},
    {"url": "http://export.arxiv.org/rss/cs.LG", "category": "ai_research", "tier": "S"},
    {"url": "http://export.arxiv.org/rss/cs.CL", "category": "ai_research", "tier": "S"},
    {"url": "http://export.arxiv.org/rss/cs.CV", "category": "ai_research", "tier": "S"},
    {"url": "http://export.arxiv.org/rss/cs.RO", "category": "robotics", "tier": "S"},

    # 技术媒体
    {"url": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "ai_business", "tier": "A"},
    {"url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml", "category": "ai_business", "tier": "A"},
    {"url": "https://venturebeat.com/category/ai/feed/", "category": "ai_business", "tier": "A"},
    {"url": "https://www.wired.com/tag/artificial-intelligence/feed/", "category": "ai_business", "tier": "A"},
    {"url": "https://arstechnica.com/tag/artificial-intelligence/feed/", "category": "ai_business", "tier": "A"},

    # 开源/HuggingFace
    {"url": "https://huggingface.co/blog/feed.xml", "category": "open_source", "tier": "S"},
]

# === GitHub 搜索配置 ===
GITHUB_SEARCHES = [
    {"query": "AI agent OR agentic AI OR autonomous agent", "category": "ai_agents"},
    {"query": "AI coding OR code generation OR SWE-bench", "category": "ai_coding"},
    {"query": "LLM OR large language model OR foundation model", "category": "frontier_models"},
    {"query": "robotics OR humanoid OR embodied AI", "category": "robotics"},
    {"query": "GPU OR TPU OR AI chip OR inference hardware", "category": "ai_hardware"},
]

# === Hacker News 配置 ===
HN_MIN_SCORE = 50  # 最低分数

# === 公司关键词映射 (用于分类和去重) ===
COMPANY_KEYWORDS = {
    "OpenAI": ["openai", "gpt", "chatgpt", "o1", "o3", "sora", "dall-e"],
    "Anthropic": ["anthropic", "claude", "sonnet", "opus", "haiku"],
    "Google": ["google", "deepmind", "gemini", "bard", "alphabet", "deepmind.google"],
    "Meta": ["meta", "llama", "facebook", "fair", "ai.meta"],
    "xAI": ["xai", "grok", "elon musk ai"],
    "Microsoft": ["microsoft", "copilot", "azure ai", "openai partnership"],
    "Amazon": ["amazon", "aws", "bedrock", "titan", "alexa"],
    "NVIDIA": ["nvidia", "geforce", "cuda", "hopper", "blackwell", "h100", "h200"],
    "Apple": ["apple", "apple intelligence", "siri", "on-device"],
    "Mistral": ["mistral", "mixtral"],
    "DeepSeek": ["deepseek"],
    "Qwen": ["qwen", "alibaba"],
    "Stability AI": ["stability ai", "stable diffusion"],
    "Midjourney": ["midjourney"],
}

# === 报告模板 ===
REPORT_TEMPLATE = """# AI Industry Daily Intelligence Report

**日期**: {date}
**生成时间**: {generated_at}
**数据来源**: arXiv, GitHub, Hacker News, RSS feeds, 官方网站
**今日事件总数**: {total_events}
**重要事件**: {important_events}

---

## Executive Summary

{executive_summary}

---

{sections}

---

## Today's Top 5

{top5}

---

## Emerging Trends

{trends}

---

*本报告由 AI Industry Daily Intelligence System 自动生成*
*系统架构: GitHub Actions + Python + 免费数据源 | 成本: $0*
"""

SECTION_TEMPLATE = """## {category_name}

{events}

"""

EVENT_TEMPLATE = """### {importance} {title}

**发生了什么**: {summary}

**技术意义**: {technical_significance}

**为什么重要**: {why_important}

**行业影响**: {industry_impact}

**可信度**: {confidence}

**来源**:
{sources}

---

"""
