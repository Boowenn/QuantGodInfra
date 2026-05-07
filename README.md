# QuantGodInfra

QuantGodInfra owns the local workspace automation, deployment support, dist synchronization, macOS LaunchAgent setup, and split-repository validation for QuantGod.

It does not own trading logic, Vue components, MT5 presets, or product documentation. Its role is to keep the four repositories operating as one controlled local system.

## Repository Role

| Area | Path | Responsibility |
|---|---|---|
| Workspace helper | `scripts/qg-workspace.py` | Multi-repository status, tests, frontend build, dist sync, closed-loop verification |
| macOS automation | `scripts/qg-macos-launchd.py` | LaunchAgent generation for API, Vite, Agent v2.5, and AI Telegram monitor |
| Local Docker | `docker/`, `scripts/qg-docker-local.py` | Optional local backend/frontend Compose stack |
| Cloud sync | `scripts/cloud-sync/` | Optional dashboard snapshot uploader |
| Guards | `scripts/qg-split-path-guard.py`, tests | Split-repo path and boundary validation |

Related repositories:

- Backend: `../QuantGodBackend`
- Frontend: `../QuantGodFrontend`
- Docs: `../QuantGodDocs`

## Workspace Configuration

Create a local workspace file:

```bash
cd /Users/bowen/Desktop/Quard/QuantGodInfra
cp workspace/quantgod.workspace.example.json workspace/quantgod.workspace.json
```

Recommended macOS layout:

```text
/Users/bowen/Desktop/Quard/QuantGodBackend
/Users/bowen/Desktop/Quard/QuantGodFrontend
/Users/bowen/Desktop/Quard/QuantGodInfra
/Users/bowen/Desktop/Quard/QuantGodDocs
```

Windows layouts are supported through the same workspace JSON.

## Workspace Commands

```bash
python3 scripts/qg-workspace.py --workspace workspace/quantgod.workspace.json status
python3 scripts/qg-workspace.py --workspace workspace/quantgod.workspace.json test
python3 scripts/qg-workspace.py --workspace workspace/quantgod.workspace.json build-frontend
python3 scripts/qg-workspace.py --workspace workspace/quantgod.workspace.json sync-frontend-dist
python3 scripts/qg-workspace.py --workspace workspace/quantgod.workspace.json verify
python3 scripts/qg-workspace.py --workspace workspace/quantgod.workspace.json closed-loop
```

`closed-loop` performs the local operator-workbench path:

1. Run frontend guards.
2. Build Vue.
3. Sync `dist/` into backend `Dashboard/vue-dist/`.
4. Run backend and docs verification.

It does not modify MT5 live presets, credentials, wallet state, or trading configuration.

## macOS LaunchAgents

Install local background services:

```bash
cd /Users/bowen/Desktop/Quard/QuantGodInfra
python3 scripts/qg-macos-launchd.py --workspace workspace/quantgod.workspace.json doctor
python3 scripts/qg-macos-launchd.py --workspace workspace/quantgod.workspace.json install
python3 scripts/qg-macos-launchd.py status
```

Generated agents:

| Agent | Purpose |
|---|---|
| `com.quantgod.backend-api` | Backend `/api/*` and static `/vue/` server |
| `com.quantgod.frontend-dev` | Vite workbench at `http://127.0.0.1:5173/vue/` |
| `com.quantgod.daily-autopilot` | Agent v2.5 USDJPY live-loop, policy, daily todo, daily review |
| `com.quantgod.ai-telegram-monitor` | DeepSeek-assisted MT5 advisory push-only monitor |

Private environment values live in `~/.quantgod/launchd.env`. Logs are written to `~/.quantgod/logs/`.

Uninstall:

```bash
python3 scripts/qg-macos-launchd.py uninstall
```

## Agent v2.5 Launch Policy

Infra intentionally starts Agent v2.5, not the legacy daily autopilot loop.

Default launchd environment:

```text
QG_FOCUS_SYMBOL=USDJPYc
QG_ALLOWED_SYMBOLS=USDJPYc
QG_DISABLE_NON_FOCUS_SYMBOLS=1
QG_ACCOUNT_MODE=cent
QG_ACCOUNT_CURRENCY_UNIT=USC
QG_CENT_ACCOUNT_ACCELERATION=1
QG_LEGACY_DAILY_AUTOPILOT_ENABLED=0
QG_AGENT_V25_INTERVAL_SECONDS=300
```

Telegram and DeepSeek credentials remain in backend-local `.env.*.local` files and must not be committed.

## Local Docker

Docker is optional and is intended for local backend/frontend development only:

```bash
python3 scripts/qg-docker-local.py static-check
python3 scripts/qg-docker-local.py doctor
python3 scripts/qg-docker-local.py config
python3 scripts/qg-docker-local.py up
```

The local Docker stack does not introduce broker execution, public ingress, billing, user accounts, or credential storage.

## Cloudflare and Cloud Sync

Cloudflare deployment and Cloud Sync are optional. Local MT5/HFM operation does not depend on them.

Cloud Sync reads backend dashboard evidence and uploads selected snapshots when explicitly configured. Tokens must live in environment variables, Wrangler secrets, or ignored local config.

## Validation

```bash
cd /Users/bowen/Desktop/Quard/QuantGodInfra
python3 -m unittest discover tests -v
python3 scripts/qg-split-path-guard.py --root /Users/bowen/Desktop/Quard --include-codex-automations
```

Focused launchd tests:

```bash
python3 -m unittest tests.test_macos_launchd -v
```

## Safety Boundaries

Infra may start processes and synchronize static assets. It must not:

- Write MT5 live trading decisions.
- Store Telegram, DeepSeek, broker, wallet, or private-key secrets in Git.
- Add Telegram command execution.
- Add Polymarket wallet execution.
- Mutate live preset risk settings.
- Convert optional Cloudflare tooling into a required runtime dependency.
