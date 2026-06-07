# 舞萌平台 MVP

本项目实现了一周计划中的核心能力：水鱼查分接入、本地谱面知识库、六维实力分析、Bot 与 Web 双端展示。

## 1. 目录结构

- `backend/`: FastAPI 后端（数据接入、评分、AI建议）
- `bot/`: NoneBot2 机器人插件
- `frontend/`: Vue3 前端页面
- `scripts/`: 启动与初始化脚本

## 2. 环境准备（Windows）

1) 执行初始化脚本（会创建虚拟环境，并使用国内源安装 Python 依赖）：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap.ps1
```

2) 如需前端依赖：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap.ps1 -InstallFrontendDeps
```

## 3. 运行服务

### 后端 API

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_backend.ps1
```

健康检查：`GET http://127.0.0.1:8000/health`

### Bot

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_bot.ps1
```

Bot 指令：
- `舞萌帮助`
- `舞萌ping`
- `b50分析 用户名`
- `b50分析 qq:123456789`

### 前端

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_frontend.ps1
```

打开 `http://127.0.0.1:5173`。

## 4. API 说明

- `POST /players/query`：查询玩家 b50/rating 简略信息
- `GET /players/records?import_token=...`：使用导入 token 查询完整成绩
- `GET /knowledge/songs`：查询本地谱面，支持 `tags`, `min_ds`, `max_ds`
- `GET /knowledge/tags/distribution`：标签分布统计
- `POST /knowledge/sync/music-data`：从水鱼同步完整曲库到本地
- `POST /analysis/b50`：生成六维分析与建议

## 5. 水鱼接入说明

请先在水鱼查分器个人资料页生成 `Import-Token`，并配置到环境变量 `DIVING_FISH_IMPORT_TOKEN`。

查询 b50 通常可直接使用用户名/QQ（取决于对方隐私设置）。

## 6. 六维模型（首版）

- 定数突破力
- 稳定率
- 准度
- 覆盖面
- 成长性
- 短板韧性

评分结果映射到 0-100 区间，前端展示雷达图，并生成短中长期建议。

## 7. 完整曲库同步（避免虚构曲目）

推荐曲目应基于真实曲库。可通过以下方式同步：

```powershell
& .\.venv\Scripts\python.exe .\scripts\sync_music_data.py
```

或调用后端接口：

```http
POST /knowledge/sync/music-data
```

同步后曲库文件默认写入 `backend/data/songs_music_data.json`，推荐仅从该真实曲库中筛选；若命中不足，将返回不足数量，不再伪造/补齐曲名。
