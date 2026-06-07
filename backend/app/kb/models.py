from __future__ import annotations

from pathlib import Path

from app.models.schemas import SongEntry, SongTag


def default_song_seed() -> list[SongEntry]:
    # 初版种子数据，用于快速验证流程，后续可替换为全量曲库导入。
    return [
        SongEntry(
            song_id=1001,
            title="MAXRAGE",
            version="PRiSM",
            difficulty="Master",
            level="14+",
            ds=14.7,
            charter="TechMapper",
            tags=[
                SongTag(key="style", value="tech"),
                SongTag(key="stamina", value="high"),
                SongTag(key="reading", value="mid"),
            ],
        ),
        SongEntry(
            song_id=1002,
            title="SILENT VOICE",
            version="UNiVERSE",
            difficulty="Master",
            level="13+",
            ds=13.8,
            charter="FlowMapper",
            tags=[
                SongTag(key="style", value="flow"),
                SongTag(key="stamina", value="mid"),
                SongTag(key="reading", value="high"),
            ],
        ),
        SongEntry(
            song_id=1003,
            title="NEXUS LOOP",
            version="FESTiVAL",
            difficulty="Re:Master",
            level="14",
            ds=14.3,
            charter="PatternLab",
            tags=[
                SongTag(key="style", value="jack"),
                SongTag(key="stamina", value="high"),
                SongTag(key="reading", value="high"),
            ],
        ),
        SongEntry(
            song_id=1004,
            title="Aqua Pulse",
            version="BUDDiES",
            difficulty="Expert",
            level="12+",
            ds=12.9,
            charter="SwingMapper",
            tags=[
                SongTag(key="style", value="swing"),
                SongTag(key="stamina", value="low"),
                SongTag(key="reading", value="mid"),
            ],
        ),
        SongEntry(
            song_id=1005,
            title="Skyline Drive",
            version="FESTiVAL PLUS",
            difficulty="Master",
            level="13",
            ds=13.2,
            charter="ClassicMapper",
            tags=[
                SongTag(key="style", value="balance"),
                SongTag(key="stamina", value="mid"),
                SongTag(key="reading", value="low"),
            ],
        ),
    ]


def kb_data_path(root: str | Path = ".") -> Path:
    return Path(root).resolve() / "backend" / "data" / "songs_seed.json"


def kb_music_data_path(root: str | Path = ".") -> Path:
    return Path(root).resolve() / "backend" / "data" / "songs_music_data.json"
