# QuantGodInfra 工作区联动修复

这次修复用于拆分后四仓库联动测试的加固，目标是让 `qg-workspace.py test` 真的能拦住 backend API contract、CI guard、前端构建和文档检查里的失败。

## 修复内容

- `scripts/qg-workspace.py` 从压缩脚本整理成可维护的 Python 模块。
- workspace 配置支持 `workspaceRoot`，提交进 Git 的 example 不再写死个人机器路径。
- `cmd_test` 对 backend Node/API contract 测试使用硬失败，不再允许 `check=False` 静默放过。
- backend Node 测试由 Python 枚举 `tests/node/*.mjs`，避免依赖 shell glob，在 Windows、macOS、Linux 上行为一致。
- `cmd_test` 会继续运行 backend `tools/ci_guard.py`。
- `cmd_verify` 会检查 backend/frontend/infra/docs 的拆分边界。
- Infra CI 增加 workspace helper 单元测试。
- `.gitignore` 忽略本地 workspace 配置，例如 `workspace/quantgod.workspace.json` 和 `workspace/*.local.json`。

## 本地验证

```powershell
cd C:\QuantGod\QuantGodInfra
python -m py_compile scripts\qg-workspace.py
python -m unittest discover tests -v
python -m json.tool workspace\quantgod.workspace.example.json > $null
```

如果还没有本机 workspace 配置，可以从示例复制：

```powershell
Copy-Item workspace\quantgod.workspace.example.json workspace\quantgod.workspace.json
```

再执行四仓库联动检查：

```powershell
python scripts\qg-workspace.py --workspace workspace\quantgod.workspace.json verify
python scripts\qg-workspace.py --workspace workspace\quantgod.workspace.json test
```

## 安全边界

这个 helper 只做本地仓库联动、测试、构建和前端 dist 同步。它不会下单、平仓、修改 MT5 preset、保存凭据，也不会绕过 backend 的 `ci_guard.py`、Kill Switch、authorization lock 或 dry-run 边界。
