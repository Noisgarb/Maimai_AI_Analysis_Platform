from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.integrations.diving_fish_client import DivingFishClient, DivingFishError
from app.models.schemas import QueryPlayerRequest, TokenSetRequest
from app.services.token_store import TokenStore

router = APIRouter(prefix="/players", tags=["players"])
fish = DivingFishClient()
token_store = TokenStore()


@router.post("/query")
async def query_player(req: QueryPlayerRequest) -> dict:
    try:
        payload = await fish.query_player(req)
    except DivingFishError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return payload


@router.get("/records")
async def player_records(import_token: str | None = None) -> dict:
    try:
        payload = await fish.player_records(import_token=import_token or token_store.get_import_token())
    except DivingFishError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return payload


@router.post("/token/import")
async def save_import_token(req: TokenSetRequest) -> dict:
    token_store.set_import_token(req.token)
    return {"ok": True, "message": "import token 已保存到本地文件"}
