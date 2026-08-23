"""报告生成器"""
import os
from datetime import datetime
from typing import List, Dict
from src.config import CATEGORIES, REPORT_TEMPLATE, SECTION_TEMPLATE, EVENT_TEMPLATE, REPORTS_DIR

class Reporter:
    """生成Markdown日报"""

    def __init__(self):
        os.makedirs(REPORTS_DIR, exist_ok=True)

    def generate(self, events: List[Dict]) -> str:
        """生成日报"""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        significant = [e for e in events if e.get("total_score", 0) >= 40]
        top_events = significant[:5]

        report = REPORT_TEMPLATE.format(
            date=today,
            generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            total_events=len(events),
            important_events=len(significant),
            executive_summary=self._gen_executive_summary(top_events),
            sections=self._gen_sections(significant),
            top5=self._gen_top5(significant[:5]),
            trends=self._gen_trends(significant),
        )

        filename = f"{today}.md"
        filepath = os.path.join(REPORTS_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)

        return filepath

    def _gen_executive_summary(self, events: List[Dict]) -> str:
        if not events:
            return "今日AI行业无重大突破性动态。"
        lines = []
        for i, e in enumerate(events[:5], 1):
            lines.append(f"{i}. **{e.get('title', '')}** ({e.get('importance', '')})")
            lines.append(f"   - {e.get('why_important', '')[:120]}...")
        return "\n".join(lines)

    def _gen_sections(self, events: List[Dict]) -> str:
        sections = []
        for cat_key, cat_name in CATEGORIES.items():
            cat_events = [e for e in events if e.get("category") == cat_key]
            if not cat_events:
                continue

            events_md = []
            for e in cat_events[:10]:
                sources = e.get("sources", [e.get("source", "")])
                sources_str = "\n".join([f"- {s}" for s in sources if s])

                event_md = EVENT_TEMPLATE.format(
                    importance=e.get("importance", "★★☆☆☆"),
                    title=e.get("title", ""),
                    summary=e.get("summary", ""),
                    technical_significance=e.get("technical_significance", ""),
                    why_important=e.get("why_important", ""),
                    industry_impact=e.get("industry_impact", ""),
                    confidence=e.get("confidence", "Medium"),
                    sources=sources_str,
                )
                events_md.append(event_md)

            section = SECTION_TEMPLATE.format(
                category_name=cat_name,
                events="".join(events_md),
            )
            sections.append(section)

        return "\n".join(sections)

    def _gen_top5(self, events: List[Dict]) -> str:
        if not events:
            return "今日无足够重要事件入选Top 5。"
        lines = []
        for i, e in enumerate(events[:5], 1):
            lines.append(f"### {i}. {e.get('title', '')}")
            lines.append(f"**发生了什么**: {e.get('summary', '')[:200]}...")
            lines.append(f"**为什么重要**: {e.get('why_important', '')}")
            lines.append(f"**未来可能**: {self._gen_future(e)}")
            lines.append("")
        return "\n".join(lines)

    def _gen_future(self, event: Dict) -> str:
        cat = event.get("category", "")
        futures = {
            "frontier_models": "可能引发新一轮模型能力竞赛，推动API降价或新应用爆发。",
            "ai_agents": "更多产品将集成自主执行能力，改变人机协作模式。",
            "ai_coding": "开发者工具链加速重构，初级编码岗位需求可能下降。",
            "open_source": "闭源厂商可能被迫调整定价策略或加速开源自身模型。",
            "ai_research": "6-12个月内可能看到基于该研究的工程化产品。",
            "ai_hardware": "训练和推理成本曲线变化，影响AI创业门槛。",
            "ai_infrastructure": "企业AI部署成本下降，边缘推理场景扩展。",
            "robotics": "工业和服务业自动化加速，人形机器人进入更多试点。",
            "ai_business": "资本向头部集中，并购活动可能增加。",
        }
        return futures.get(cat, "建议持续关注后续产品化和市场反馈。")

    def _gen_trends(self, events: List[Dict]) -> str:
        if len(events) < 3:
            return "数据不足，暂无法形成可靠趋势判断。"

        cat_counts = {}
        company_counts = {}
        for e in events:
            cat = e.get("category", "unknown")
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
            comp = e.get("company", "Unknown")
            if comp:
                company_counts[comp] = company_counts.get(comp, 0) + 1

        lines = ["### 近期信号统计"]
        lines.append(f"- 今日覆盖事件: {len(events)}条")
        lines.append(f"- 最活跃领域: {max(cat_counts, key=cat_counts.get, default='N/A')}")
        if company_counts:
            lines.append(f"- 最活跃公司: {max(company_counts, key=company_counts.get, default='N/A')}")

        lines.append("\n### 观察要点")
        lines.append("基于今日数据，建议关注以下方向是否形成持续趋势：")
        lines.append("1. 模型发布密度是否持续走高")
        lines.append("2. Agent产品化是否从Demo走向实用")
        lines.append("3. 开源社区是否出现新的技术范式")
        lines.append("4. 硬件供应链是否有重大变化信号")

        return "\n".join(lines)
