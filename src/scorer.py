"""重要性评分引擎"""
import re
from typing import Dict, List
from src.config import SOURCE_TIERS, IMPACT_KEYWORDS, CATEGORIES

class Scorer:
    """基于规则的重要性评分"""

    def score(self, events: List[Dict]) -> List[Dict]:
        """为每个事件计算重要性分数"""
        for event in events:
            scores = {
                "technical_impact": self._technical_impact(event),
                "industry_impact": self._industry_impact(event),
                "novelty": self._novelty(event),
                "source_reliability": self._source_reliability(event),
                "community_signal": self._community_signal(event),
            }

            total = (
                scores["technical_impact"] * 0.25 +
                scores["industry_impact"] * 0.25 +
                scores["novelty"] * 0.20 +
                scores["source_reliability"] * 0.15 +
                scores["community_signal"] * 0.15
            )

            event["scores"] = scores
            event["total_score"] = round(total, 1)
            event["importance"] = self._score_to_stars(total)
            event["confidence"] = self._confidence_level(event)
            event["technical_significance"] = self._gen_technical_sig(event)
            event["why_important"] = self._gen_why_important(event)
            event["industry_impact"] = self._gen_industry_impact(event)

        events.sort(key=lambda x: x.get("total_score", 0), reverse=True)
        return events

    def _technical_impact(self, event: Dict) -> float:
        score = 0
        text = (event.get("title", "") + " " + event.get("summary", "")).lower()
        if any(k in text for k in ["new model", "模型发布", "architecture", "架构", "sota", "state of the art"]):
            score += 40
        if any(k in text for k in ["reasoning", "推理", "rlhf", "distillation", "test-time", "合成数据"]):
            score += 30
        if any(k in text for k in ["agent", "autonomous", "tool use", "mcp", "computer use"]):
            score += 25
        if any(k in text for k in ["multimodal", "多模态", "vision", "video", "audio"]):
            score += 20
        return min(score + event.get("raw_score", 0) * 0.3, 100)

    def _industry_impact(self, event: Dict) -> float:
        score = 0
        text = (event.get("title", "") + " " + event.get("summary", "")).lower()
        major = ["openai", "google", "deepmind", "anthropic", "meta", "microsoft", "nvidia", "apple", "amazon"]
        if any(c in text for c in major):
            score += 30
        if any(k in text for k in ["funding", "融资", "ipo", "acquisition", "收购", "billion", "million"]):
            score += 35
        if any(k in text for k in ["api", "launch", "product", "发布", "推出"]):
            score += 25
        return min(score, 100)

    def _novelty(self, event: Dict) -> float:
        score = 50
        text = (event.get("title", "") + " " + event.get("summary", "")).lower()
        if any(k in text for k in ["first", "首次", "novel", "new approach", "breakthrough", "突破"]):
            score += 30
        if "arxiv" in text:
            score += 10
        return min(score, 100)

    def _source_reliability(self, event: Dict) -> float:
        source = event.get("source", "").lower()
        for domain, weight in SOURCE_TIERS.items():
            if domain in source:
                return weight * 100
        return 40

    def _community_signal(self, event: Dict) -> float:
        score = 30
        stars = event.get("stars", 0)
        if stars > 1000: score += 40
        elif stars > 500: score += 30
        elif stars > 100: score += 20
        hn = event.get("hn_score", 0)
        if hn > 200: score += 30
        elif hn > 100: score += 20
        elif hn > 50: score += 10
        return min(score, 100)

    def _score_to_stars(self, score: float) -> str:
        if score >= 85: return "★★★★★ Critical"
        elif score >= 70: return "★★★★☆ Important"
        elif score >= 55: return "★★★☆☆ Worth Watching"
        elif score >= 40: return "★★☆☆☆ Minor"
        else: return "★☆☆☆☆ Low"

    def _confidence_level(self, event: Dict) -> str:
        sources = event.get("sources", [event.get("source", "")])
        tier = event.get("source_tier", "C")
        if len(sources) >= 3 and tier in ["S", "A"]:
            return "High"
        elif len(sources) >= 2 and tier in ["S", "A", "B"]:
            return "Medium"
        elif tier == "S":
            return "High"
        elif tier == "C":
            return "Low"
        return "Medium"

    def _gen_technical_sig(self, event: Dict) -> str:
        cat = event.get("category", "")
        sigs = {
            "frontier_models": "涉及大语言模型或基础模型的能力边界扩展，可能改变行业技术路线。",
            "ai_agents": "代表AI从对话工具向自主执行体的演进，是通往通用人工智能的关键路径。",
            "ai_coding": "直接影响软件工程生产力，可能重塑开发者工具生态和编程范式。",
            "open_source": "降低技术门槛，加速社区创新，可能挑战闭源模型的商业壁垒。",
            "ai_research": "基础理论或算法创新，长期影响模型能力和效率上限。",
            "ai_hardware": "算力是AI发展的物理基础，硬件突破直接决定训练和推理成本曲线。",
            "ai_infrastructure": "支撑AI规模化部署的关键层，影响企业采用成本和延迟。",
            "robotics": "连接数字智能与物理世界，是AI落地的终极场景之一。",
            "ai_business": "反映市场信心和资源配置方向，影响技术转化速度和产业格局。",
        }
        return sigs.get(cat, "AI领域重要动态，具体技术影响需进一步观察。")

    def _gen_why_important(self, event: Dict) -> str:
        score = event.get("total_score", 0)
        if score >= 85:
            return "该事件可能重新定义行业竞争格局或技术路线，建议持续关注后续发展。"
        elif score >= 70:
            return "对特定领域有显著影响，可能加速相关技术或产品的成熟与普及。"
        elif score >= 55:
            return "代表值得关注的技术或市场信号，建议跟踪其后续演进。"
        return "行业常规动态，可作为背景信息了解。"

    def _gen_industry_impact(self, event: Dict) -> str:
        company = event.get("company", "")
        cat = event.get("category", "")
        cat_name = CATEGORIES.get(cat, cat)
        if company:
            return f"{company}在{cat_name}领域的动作，可能引发竞争对手跟进或市场重新定价。"
        return f"该{cat_name}动态反映了行业当前的发展重心和资源配置趋势。"
