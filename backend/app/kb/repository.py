from __future__ import annotations

import json
from pathlib import Path

from app.kb.models import default_song_seed, kb_data_path, kb_music_data_path
from app.models.schemas import SongEntry


class SongRepository:
    def __init__(self, root: str | Path = ".") -> None:
        self._seed_path = kb_data_path(root)
        self._music_data_path = kb_music_data_path(root)
        self._path = self._music_data_path if self._music_data_path.exists() else self._seed_path
        self._songs: list[SongEntry] = []
        self._ensure_seed()
        self._load()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def using_music_data(self) -> bool:
        return self._path == self._music_data_path

    @property
    def using_seed_data(self) -> bool:
        return self._path == self._seed_path

    def _ensure_seed(self) -> None:
        self._seed_path.parent.mkdir(parents=True, exist_ok=True)
        if self._seed_path.exists():
            return
        seed = [item.model_dump() for item in default_song_seed()]
        self._seed_path.write_text(json.dumps(seed, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load(self) -> None:
        data = json.loads(self._path.read_text(encoding="utf-8"))
        self._songs = [SongEntry.model_validate(item) for item in data]

    def upsert_from_music_data(self, music_data: list[dict]) -> int:
        """
        将水鱼 /music_data 的完整曲库扁平化为 SongEntry 列表并落盘。
        每首歌按每个难度展开为一条 SongEntry，确保推荐只来源于真实曲库。
        """
        converted: list[SongEntry] = []
        for music in music_data:
            song_id = int(music.get("id", 0))
            title = str(music.get("title") or music.get("basic_info", {}).get("title") or "unknown")
            version = str(music.get("basic_info", {}).get("from") or "unknown")
            ds_list = music.get("ds", []) or []
            level_list = music.get("level", []) or []
            chart_list = music.get("charts", []) or []
            type_name = str(music.get("type") or "DX")
            for idx, ds in enumerate(ds_list):
                level = str(level_list[idx]) if idx < len(level_list) else "-"
                chart = chart_list[idx] if idx < len(chart_list) else {}
                charter = str(chart.get("charter", "unknown"))
                difficulty_name = ["Basic", "Advanced", "Expert", "Master", "Re:Master"]
                difficulty = difficulty_name[idx] if idx < len(difficulty_name) else f"Diff-{idx}"
                tags = self._infer_tags(level=level, ds=float(ds), title=title)
                converted.append(
                    SongEntry(
                        song_id=song_id,
                        title=title,
                        version=version,
                        difficulty=f"{type_name}-{difficulty}",
                        level=level,
                        ds=float(ds),
                        charter=charter,
                        tags=tags,
                    )
                )

        self._music_data_path.parent.mkdir(parents=True, exist_ok=True)
        self._music_data_path.write_text(
            json.dumps([item.model_dump() for item in converted], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self._path = self._music_data_path
        self._songs = converted
        return len(converted)

    @staticmethod
    def _infer_tags(level: str, ds: float, title: str):
        from app.models.schemas import SongTag

        title_l = title.lower()
        style = "balance"
        if any(k in title_l for k in ["break", "rage", "conflict", "chaos"]):
            style = "tech"
        elif any(k in title_l for k in ["night", "silent", "dream", "sky"]):
            style = "flow"
        elif any(k in title_l for k in ["jack", "loop", "rush"]):
            style = "jack"
        stamina = "high" if ds >= 14 else "mid" if ds >= 13 else "low"
        reading = "high" if "+" in level or ds >= 14.2 else "mid" if ds >= 13 else "low"
        return [
            SongTag(key="style", value=style),
            SongTag(key="stamina", value=stamina),
            SongTag(key="reading", value=reading),
        ]

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
