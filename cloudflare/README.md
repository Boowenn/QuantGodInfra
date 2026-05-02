# Cloudflare 边缘同步

本目录保存 QuantGod 的 Cloudflare worker/static deployment 相关文件。它属于可选远程展示能力，不是本地 HFM/MT5 运行的必要条件。

## 文件说明

- `src/index.js`：Cloudflare Worker 入口。
- `wrangler.jsonc`：Wrangler 配置。
- `.dev.vars.example`：本地开发变量示例，只能放占位符。
- `package.json`：Cloudflare worker 相关依赖与脚本。

## 安全规则

不要提交真实 `QG_INGEST_TOKEN`、Cloudflare token、Telegram token、OpenRouter key 或任何交易凭据。生产值应通过 Wrangler secrets 或平台环境变量配置。

## 与四仓库的关系

- 前端源码在 `QuantGodFrontend`。
- 后端 API 和运行证据在 `QuantGodBackend`。
- 详细运维文档在 `QuantGodDocs`。
- 本目录只负责 Cloudflare 侧的部署材料。
