# QuantGodInfra

QuantGod 四仓库工作区的基础设施与联动自动化仓库。

## 仓库职责

- Cloudflare worker/static deployment 文件。
- 多仓库 workspace helper。
- `QuantGodFrontend/dist` 到 `QuantGodBackend/Dashboard/vue-dist` 的同步。
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
```

## Cloudflare

Cloudflare 是可选能力，本地 HFM/MT5 运行不依赖它。所有 token 和 secret 必须放在 Wrangler secrets 或本机环境变量里，不能进入 Git。
