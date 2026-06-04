from __future__ import annotations

from app.analysis.ai_advisor import AIAdvisor
from app.analysis.six_dim_engine import SixDimEngine
from app.integrations.diving_fish_client import DivingFishClient
from app.kb.repository import SongRepository
from app.kb.tagging import suggest_training_tags
from app.models.schemas import AnalyzeResponse, B50Item, QueryPlayerRequest


class AnalysisService:
    def __init__(self) -> None:
        self.song_repo = SongRepository()
        self.fish = DivingFishClient()
        self.engine = SixDimEngine(self.song_repo)
        self.advisor = AIAdvisor()

    async def analyze_b50(self, req: QueryPlayerRequest) -> AnalyzeResponse:
        payload = await self.fish.query_player(req)
        player_id = req.username or req.qq or "unknown"
        radar = self.engine.score(player_id=player_id, payload=payload)
        advice = await self.advisor.generate_advice(radar, payload)
        b50_items = self._extract_b50(payload)
        b35 = b50_items[:35]
        b15 = b50_items[35:50]
        return AnalyzeResponse(
            player_id=player_id,
            rating=payload.get("rating"),
            b50=b50_items,
            b35=b35,
            b15=b15,
            radar=radar,
            advice=advice,
            debug={"source": "diving-fish", "charts_count": len(payload.get("charts", {}).get("sd", [])) + len(payload.get("charts", {}).get("dx", []))},
        )

    @staticmethod
    def _extract_b50(payload: dict) -> list[B50Item]:
        charts = payload.get("charts", {})
        sd = charts.get("sd", []) or []
        dx = charts.get("dx", []) or []
        all_items = sd + dx

        out: list[B50Item] = []
        for idx, item in enumerate(all_items):
            song_id = item.get("song_id")
            cover_url = f"https://www.diving-fish.com/covers/{song_id}.png" if song_id is not None else None
            segment = "B35" if idx < 35 else "B15"
            out.append(
                B50Item(
                    song_id=song_id,
                    title=item.get("title", "unknown"),
                    type=item.get("type"),
                    level_label=item.get("level_label"),
                    ds=item.get("ds"),
                    ra=item.get("ra"),
                    achievements=item.get("achievements"),
                    dx_score=item.get("dxScore"),
                    rate=item.get("rate"),
                    fc=item.get("fc"),
                    fs=item.get("fs"),
                    cover_url=cover_url,
                    segment=segment,
                )
            )
        return out

    def recommend_songs_by_shortfall(self, shortfalls: list[str], limit: int = 6):
        tags = suggest_training_tags(shortfalls)
        results = []
        seen_ids = set()
        for tag in tags:
            songs = self.song_repo.filter_by_tags([tag])
            for song in songs:
                if song.song_id in seen_ids:
                    continue
                seen_ids.add(song.song_id)
                results.append(song)
                if len(results) >= limit:
                    return results
        if len(results) < limit:
            for song in self.song_repo.list_all():
                if song.song_id in seen_ids:
                    continue
                results.append(song)
                if len(results) >= limit:
                    break
        return results
