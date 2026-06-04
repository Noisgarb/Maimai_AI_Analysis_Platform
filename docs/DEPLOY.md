# 部署说明（Windows 本地）

## 环境变量

复制 `.env.example` 为 `.env`，按需填写：

- `DIVING_FISH_IMPORT_TOKEN`
- `AI_PROVIDER` / `AI_API_BASE` / `AI_API_KEY`（如要接入真实模型）

## 启动顺序

1. `powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap.ps1 -InstallFrontendDeps`
2. 后端：`powershell -ExecutionPolicy Bypass -File .\scripts\run_backend.ps1`
3. 前端：`powershell -ExecutionPolicy Bypass -File .\scripts\run_frontend.ps1`
4. Bot：`powershell -ExecutionPolicy Bypass -File .\scripts\run_bot.ps1`

## 备份建议

- 数据目录：`backend/data/`
  - `songs_seed.json`
  - `tokens.local.json`

建议每天备份一次该目录。

## 常见故障

1) `python` 命令不存在  
请先安装 Python 并勾选 PATH，或直接使用 `py` 启动。

2) 无法查询玩家  
检查对方是否开启隐私限制；或尝试 `username/qq` 切换。

3) Bot 无响应  
检查 OneBot 端口、token 与 `.env` 中配置是否一致。
