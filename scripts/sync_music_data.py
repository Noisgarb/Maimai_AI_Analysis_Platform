import json
import urllib.request
from pathlib import Path


def infer_tags(level: str, ds: float, title: str) -> list[dict]:
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
        {"key": "style", "value": style},
        {"key": "stamina", "value": stamina},
        {"key": "reading", "value": reading},
    ]


def main() -> None:
    url = "https://www.diving-fish.com/api/maimaidxprober/music_data"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    converted = []
    for music in data:
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
            converted.append(
                {
                    "song_id": song_id,
                    "title": title,
                    "version": version,
                    "difficulty": f"{type_name}-{difficulty}",
                    "level": level,
                    "ds": float(ds),
                    "charter": charter,
                    "tags": infer_tags(level=level, ds=float(ds), title=title),
                }
            )

    out_path = Path("d:/知识库/backend/data/songs_music_data.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(converted, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"synced_count={len(converted)} path={out_path}")


if __name__ == "__main__":
    main()
