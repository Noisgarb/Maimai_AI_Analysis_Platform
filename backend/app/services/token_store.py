from __future__ import annotations

import json
from pathlib import Path


class TokenStore:
    def __init__(self, root: str | Path = ".") -> None:
        self._path = Path(root).resolve() / "backend" / "data" / "tokens.local.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text(json.dumps({}, ensure_ascii=False), encoding="utf-8")

    def set_import_token(self, token: str) -> None:
        data = self._read()
        data["import_token"] = token
        self._write(data)

    def get_import_token(self) -> str | None:
        data = self._read()
        return data.get("import_token")

    def _read(self) -> dict:
        return json.loads(self._path.read_text(encoding="utf-8"))

    def _write(self, data: dict) -> None:
        self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
