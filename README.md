# QuantGodInfra

QuantGod 四仓库工作区的基础设施与联动自动化仓库。

## 仓库职责

- Cloudflare worker/static deployment 文件。
- 多仓库 workspace helper。
- `QuantGodFrontend/dist` 到 `QuantGodBackend/Dashboard/vue-dist` 的同步。
- 可选 Cloud Sync 上传器；脚本在 Infra，读取 backend 的 `Dashboard/QuantGod_Dashboard.json`。
- 四仓库状态、构建、验证联动。
- 与部署相关的脚本和说明。

本仓库不拥有后端业务逻辑、Vue 组件源码或完整产品文档。

## 初始化工作区

复制示例配置并按本机路径调整：

```powershell
Copy-Item workspace\quantgod.workspace.example.json workspace\quantgod.workspace.json
notepad workspace\quantgod.workspace.json
```

推荐目录结构：

```text
C:\QuantGod\QuantGodBackend
C:\QuantGod\QuantGodFrontend
C:\QuantGod\QuantGodInfra
C:\QuantGod\QuantGodDocs
```

macOS 本机当前对应结构通常是：

```text
/Users/bowen/Desktop/Quard/QuantGodBackend
/Users/bowen/Desktop/Quard/QuantGodFrontend
/Users/bowen/Desktop/Quard/QuantGodInfra
/Users/bowen/Desktop/Quard/QuantGodDocs
```

## 常用命令

```powershell
python scripts\qg-workspace.py --workspace workspace\quantgod.workspace.json status
python scripts\qg-workspace.py --workspace workspace\quantgod.workspace.json pull
python scripts\qg-workspace.py --workspace workspace\quantgod.workspace.json test
python scripts\qg-workspace.py --workspace workspace\quantgod.workspace.json build-frontend
python scripts\qg-workspace.py --workspace workspace\quantgod.workspace.json sync-frontend-dist
python scripts\qg-workspace.py --workspace workspace\quantgod.workspace.json verify
python scripts\qg-workspace.py --workspace workspace\quantgod.workspace.json closed-loop
```

`closed-loop` 是本地最小闭环：先跑前端 API/拆包/单元 guard，再编译 Vue，随后把 `dist/`
同步到 `QuantGodBackend/Dashboard/vue-dist`，最后跑 backend Python/Node 检查和 Docs 链接检查。
它不会改 MT5 实盘配置、不会保存凭据，也不会触发任何交易动作。

## Cloudflare

Cloudflare 是可选能力，本地 HFM/MT5 运行不依赖它。所有 token 和 secret 必须放在 Wrangler secrets 或本机环境变量里，不能进入 Git。

## Cloud Sync 上传器

历史上 Cloud Sync 脚本曾放在 backend 的 `Dashboard/` 目录；拆分后已经迁到 Infra，避免 backend 混入部署脚本。使用时显式指定 backend Dashboard 运行目录：

```powershell
$env:QG_BACKEND_DASHBOARD_DIR="C:\QuantGod\QuantGodBackend\Dashboard"
node scripts\cloud-sync\cloud_sync_uploader.js

powershell -ExecutionPolicy Bypass -File scripts\cloud-sync\cloud_sync_uploader.ps1 `
  -DashboardDir C:\QuantGod\QuantGodBackend\Dashboard
```

启用配置请从 `scripts/cloud-sync/quantgod_cloud_sync.example.json` 复制为 backend Dashboard 运行目录下的 `quantgod_cloud_sync.enabled.json`，不要提交 token。
