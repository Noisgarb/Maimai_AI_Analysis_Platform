from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings
from app.models.schemas import QueryPlayerRequest


class DivingFishError(RuntimeError):
    pass


class DivingFishClient:
    def __init__(self) -> None:
        self.base_url = settings.diving_fish_base_url.rstrip("/")
        self.timeout = settings.diving_fish_timeout_seconds

    async def query_player(self, req: QueryPlayerRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {"b50": req.b50}
        if req.username:
            payload["username"] = req.username
        if req.qq:
            payload["qq"] = req.qq
        if "username" not in payload and "qq" not in payload:
            raise DivingFishError("username 与 qq 不能同时为空")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/query/player", json=payload)
            except httpx.HTTPError as exc:
                raise DivingFishError(f"请求失败: {exc}") from exc

        if resp.status_code != 200:
            detail = resp.text
            if resp.status_code == 400:
                raise DivingFishError("玩家信息不存在或隐私设置拒绝查询")
            if resp.status_code == 403:
                raise DivingFishError("访问被拒绝，可能触发限制策略")
            raise DivingFishError(f"水鱼接口错误 {resp.status_code}: {detail}")
        return resp.json()

    async def player_records(self, import_token: str | None = None) -> dict[str, Any]:
        token = import_token or settings.diving_fish_import_token
        if not token:
            raise DivingFishError("缺少 Import-Token，无法访问 /player/records")
        headers = {"Import-Token": token}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/player/records", headers=headers)
            except httpx.HTTPError as exc:
                raise DivingFishError(f"请求失败: {exc}") from exc
        if resp.status_code != 200:
            raise DivingFishError(f"/player/records 错误 {resp.status_code}: {resp.text}")
        return resp.json()
