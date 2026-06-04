from __future__ import annotations

from typing import Any

from app.kb.tagging import suggest_training_tags
from app.models.schemas import AdviceItem, RadarOutput


class AIAdvisor:
    def build_prompt(self, radar: RadarOutput, raw_payload: dict[str, Any]) -> str:
        dim_text = ", ".join(f"{item.name}:{item.score}" for item in radar.dimensions)
        return (
            "你是舞萌训练教练。请根据玩家B50给出分阶段建议。\n"
            f"玩家: {raw_payload.get('nickname', radar.player_id)}\n"
            f"六维: {dim_text}\n"
            f"短板: {','.join(radar.shortfalls)}\n"
            "输出结构: 问题诊断/练习优先级/推荐曲目类别/预计提升区间。"
        )

    async def generate_advice(self, radar: RadarOutput, raw_payload: dict[str, Any]) -> list[AdviceItem]:
        # 首版使用规则引擎兜底，保证离线与无Key时可工作。
        weak_tags = suggest_training_tags(radar.shortfalls)
        player_name = raw_payload.get("nickname", radar.player_id)
        _prompt = self.build_prompt(radar, raw_payload)

        return [
            AdviceItem(
                horizon="short",
                title=f"{player_name} 的短期修复重点",
                detail="先优先修复最低两个维度，每天30-45分钟专练同类标签谱面并保留复盘记录。",
                songs=weak_tags[:3],
            ),
            AdviceItem(
                horizon="middle",
                title="中期提分策略",
                detail="采用 2+1 训练节奏：两天冲高定数，一天做稳定率回收；以周为单位观察B50底部分数抬升。",
                songs=weak_tags[:5],
            ),
            AdviceItem(
                horizon="long",
                title="长期能力构建",
                detail="通过跨风格曲目轮换减少偏科，目标是将六维最低项提升至60分以上后再冲总体Rating。",
                songs=weak_tags,
            ),
        ]
