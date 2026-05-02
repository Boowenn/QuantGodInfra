param(
  [string]$Workspace = "workspace\quantgod.workspace.json",
  [ValidateSet("status", "pull", "test", "build-frontend", "sync-frontend-dist", "verify")]
  [string]$Command = "status"
)
python "$PSScriptRoot\qg-workspace.py" --workspace $Workspace $Command
