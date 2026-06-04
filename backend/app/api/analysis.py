from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.integrations.diving_fish_client import DivingFishError
from app.models.schemas import AnalyzeResponse, QueryPlayerRequest
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analysis", tags=["analysis"])
service = AnalysisService()


@router.post("/b50", response_model=AnalyzeResponse)
async def analyze_b50(req: QueryPlayerRequest) -> AnalyzeResponse:
    try:
        return await service.analyze_b50(req)
    except DivingFishError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/recommend")
async def recommend_from_player(req: QueryPlayerRequest) -> dict:
    try:
        analyzed = await service.analyze_b50(req)
        shortfalls = analyzed.radar.shortfalls
        player_id = analyzed.player_id
        source = "player-shortfall"
        warning = None
    except DivingFishError as exc:
        shortfalls = ["coverage", "resilience"]
        player_id = req.username or req.qq or "unknown"
        source = "fallback-default"
        warning = str(exc)

    items = service.recommend_songs_by_shortfall(shortfalls, limit=6)
    return {
        "player_id": player_id,
        "shortfalls": shortfalls,
        "items": [item.model_dump() for item in items],
        "source": source,
        "warning": warning,
    }
