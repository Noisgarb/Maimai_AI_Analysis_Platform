from __future__ import annotations

from fastapi import APIRouter, Query

from app.integrations.diving_fish_client import DivingFishClient, DivingFishError
from app.kb.repository import SongRepository
from app.kb.tagging import collect_tag_distribution

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
repo = SongRepository()
fish = DivingFishClient()


@router.get("/songs")
async def list_songs(
    tags: list[str] | None = Query(default=None),
    min_ds: float | None = None,
    max_ds: float | None = None,
    version: str | None = None,
) -> dict:
    filtered = repo.list_all()
    if version:
        filtered = repo.filter_by_version(version)
    if tags:
        tagged = repo.filter_by_tags(tags)
        tagged_ids = {item.song_id for item in tagged}
        filtered = [song for song in filtered if song.song_id in tagged_ids]
    if min_ds is not None or max_ds is not None:
        filtered = [
            song
            for song in filtered
            if (min_ds is None or song.ds >= min_ds) and (max_ds is None or song.ds <= max_ds)
        ]
    return {"count": len(filtered), "items": [item.model_dump() for item in filtered]}


@router.get("/tags/distribution")
async def tag_distribution() -> dict:
    dist = collect_tag_distribution(repo.list_all())
    return {"distribution": dist}


@router.post("/sync/music-data")
async def sync_music_data() -> dict:
    try:
        music_data = await fish.music_data()
        count = repo.upsert_from_music_data(music_data)
    except DivingFishError as exc:
        return {"ok": False, "message": str(exc)}
    return {"ok": True, "count": count, "path": str(repo.path)}
