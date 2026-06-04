from __future__ import annotations

import json
from pathlib import Path

from app.kb.models import default_song_seed, kb_data_path
from app.models.schemas import SongEntry


class SongRepository:
    def __init__(self, root: str | Path = ".") -> None:
        self._path = kb_data_path(root)
        self._songs: list[SongEntry] = []
        self._ensure_seed()
        self._load()

    @property
    def path(self) -> Path:
        return self._path

    def _ensure_seed(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if self._path.exists():
            return
        seed = [item.model_dump() for item in default_song_seed()]
        self._path.write_text(json.dumps(seed, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load(self) -> None:
        data = json.loads(self._path.read_text(encoding="utf-8"))
        self._songs = [SongEntry.model_validate(item) for item in data]

    def list_all(self) -> list[SongEntry]:
        return self._songs

    def filter_by_tags(self, tags: list[str]) -> list[SongEntry]:
        if not tags:
            return self.list_all()
        pairs = [tuple(t.split(":", 1)) for t in tags if ":" in t]
        out: list[SongEntry] = []
        for song in self._songs:
            song_pairs = {(t.key, t.value) for t in song.tags}
            if all(pair in song_pairs for pair in pairs):
                out.append(song)
        return out

    def filter_by_ds(self, min_ds: float | None = None, max_ds: float | None = None) -> list[SongEntry]:
        out: list[SongEntry] = []
        for song in self._songs:
            if min_ds is not None and song.ds < min_ds:
                continue
            if max_ds is not None and song.ds > max_ds:
                continue
            out.append(song)
        return out

    def filter_by_version(self, version: str | None = None) -> list[SongEntry]:
        if not version:
            return self.list_all()
        return [song for song in self._songs if song.version.lower() == version.lower()]
