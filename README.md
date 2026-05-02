# QuantGodInfra

Infrastructure and workspace automation for the QuantGod four-repo setup.

This repo owns:

- Cloudflare worker/static deployment files
- local multi-repo workspace scripts
- frontend dist → backend served-static sync
- repo linkage verification
- deployment runbooks that are not product documentation

It does **not** own backend business logic, Vue source, or canonical docs.

## Workspace bootstrap

Copy the example workspace file and adjust paths:

```powershell
Copy-Item workspace\quantgod.workspace.example.json workspace\quantgod.workspace.json
notepad workspace\quantgod.workspace.json
```

Typical layout:

```text
C:\QuantGod\QuantGodBackend
C:\QuantGod\QuantGodFrontend
C:\QuantGod\QuantGodInfra
C:\QuantGod\QuantGodDocs
```

## Common commands

```powershell
python scripts\qg-workspace.py --workspace workspace\quantgod.workspace.json status
python scripts\qg-workspace.py --workspace workspace\quantgod.workspace.json pull
python scripts\qg-workspace.py --workspace workspace\quantgod.workspace.json test
python scripts\qg-workspace.py --workspace workspace\quantgod.workspace.json build-frontend
python scripts\qg-workspace.py --workspace workspace\quantgod.workspace.json sync-frontend-dist
```

## Cloudflare

Cloudflare remains optional. Local HFM/MT5 operation does not require it. Keep tokens and secrets in Wrangler secrets or environment variables, not Git.
