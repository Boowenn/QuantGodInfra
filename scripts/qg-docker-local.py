#!/usr/bin/env python3
"""QuantGod P3-1/P3-2 Docker/local-dev stack helper."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

INFRA_ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = INFRA_ROOT / "docker" / "compose.local.yml"
ENV_FILE = INFRA_ROOT / "docker" / ".env.local"
ENV_EXAMPLE = INFRA_ROOT / "docker" / ".env.local.example"
PROJECT_NAME = "quantgod-local-dev"

REQUIRED_LOCAL_PORTS = [
    '"127.0.0.1:${QG_BACKEND_PORT:-8080}:8080"',
    '"127.0.0.1:${QG_FRONTEND_PORT:-5173}:5173"',
]
REQUIRED_GUARD_MARKERS = [
    'QG_LOCAL_ONLY: "1"',
    'QG_DRY_RUN: "1"',
    'QG_KILL_SWITCH_LOCKED: "1"',
    'QG_ORDER_SEND_ALLOWED: "0"',
    'QG_LIVE_PRESET_MUTATION_ALLOWED: "0"',
    'QG_CREDENTIAL_STORAGE_ALLOWED: "0"',
    'QG_TELEGRAM_PUSH_ALLOWED: "${QG_TELEGRAM_PUSH_ALLOWED:-0}"',
    'QG_TELEGRAM_COMMANDS_ALLOWED: "0"',
]
REQUIRED_TELEGRAM_PASS_THROUGH = [
    'QG_TELEGRAM_BOT_TOKEN: "${QG_TELEGRAM_BOT_TOKEN:-}"',
    'QG_TELEGRAM_CHAT_ID: "${QG_TELEGRAM_CHAT_ID:-}"',
    'QG_TELEGRAM_API_BASE_URL: "${QG_TELEGRAM_API_BASE_URL:-https://api.telegram.org}"',
]
FORBIDDEN_MARKERS = [
    "0.0.0.0:${QG_BACKEND_PORT",
    "0.0.0.0:${QG_FRONTEND_PORT",
    '"8080:8080"',
    '"5173:5173"',
    "/var/run/docker.sock",
    "OPENROUTER_API_KEY",
    "BROKER_API_KEY",
    "MT5_PASSWORD",
    "HFM_PASSWORD",
]
FORBIDDEN_SERVICE_WORDS = [
    "webhook:",
    "email:",
    "mailer:",
    "broker:",
    "billing:",
    "credits:",
    "postgres:",
    "mysql:",
]


def read_compose() -> str:
    if not COMPOSE_FILE.exists():
        raise FileNotFoundError(f"missing compose file: {COMPOSE_FILE}")
    return COMPOSE_FILE.read_text(encoding="utf-8")


def _telegram_secret_literal_errors(text: str) -> list[str]:
    errors: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("QG_TELEGRAM_BOT_TOKEN:") and '${QG_TELEGRAM_BOT_TOKEN:-}' not in stripped:
            errors.append("QG_TELEGRAM_BOT_TOKEN must be pass-through only, not a literal token")
        if stripped.startswith("QG_TELEGRAM_CHAT_ID:") and '${QG_TELEGRAM_CHAT_ID:-}' not in stripped:
            errors.append("QG_TELEGRAM_CHAT_ID must be pass-through only, not a literal chat id")
    return errors


def static_check() -> list[str]:
    errors: list[str] = []
    text = read_compose()
    for marker in REQUIRED_LOCAL_PORTS:
        if marker not in text:
            errors.append(f"missing host-local port binding: {marker}")
    for marker in REQUIRED_GUARD_MARKERS:
        if marker not in text:
            errors.append(f"missing safety guard marker: {marker}")
    for marker in REQUIRED_TELEGRAM_PASS_THROUGH:
        if marker not in text:
            errors.append(f"missing Telegram pass-through marker: {marker}")
    lower = text.lower()
    for marker in FORBIDDEN_MARKERS:
        if marker.lower() in lower:
            errors.append(f"forbidden compose marker present: {marker}")
    for marker in FORBIDDEN_SERVICE_WORDS:
        if marker in lower:
            errors.append(f"forbidden local-dev service present: {marker}")
    if "services:" not in text or "  backend:" not in text or "  frontend:" not in text:
        errors.append("compose.local.yml must define backend and frontend services")
    if "condition: service_healthy" not in text:
        errors.append("frontend must wait for backend service_healthy")
    errors.extend(_telegram_secret_literal_errors(text))
    return errors


def compose_base_command() -> list[str]:
    env_file = ENV_FILE if ENV_FILE.exists() else ENV_EXAMPLE
    return [
        "docker",
        "compose",
        "--project-name",
        PROJECT_NAME,
        "--env-file",
        str(env_file),
        "-f",
        str(COMPOSE_FILE),
    ]


def run_compose(args: list[str]) -> int:
    errors = static_check()
    if errors:
        print("QuantGod Docker local static check FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    command = compose_base_command() + args
    print("+ " + " ".join(command))
    return subprocess.call(command, cwd=INFRA_ROOT)


def command_static_check(_args: argparse.Namespace) -> int:
    errors = static_check()
    if errors:
        print("QuantGod Docker local static check FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("QuantGod Docker local static check OK")
    return 0


def command_doctor(_args: argparse.Namespace) -> int:
    rc = command_static_check(_args)
    docker = shutil.which("docker")
    print(f"docker: {docker or 'not found'}")
    print(f"compose file: {COMPOSE_FILE}")
    print(f"env file: {ENV_FILE if ENV_FILE.exists() else ENV_EXAMPLE}")
    print("backend URL: http://127.0.0.1:8080")
    print("frontend URL: http://127.0.0.1:5173")
    print("telegram push: pass-through only, disabled unless QG_TELEGRAM_PUSH_ALLOWED=1")
    return rc


def command_config(_args: argparse.Namespace) -> int:
    return run_compose(["config"])


def command_build(_args: argparse.Namespace) -> int:
    return run_compose(["build"])


def command_ps(_args: argparse.Namespace) -> int:
    return run_compose(["ps"])


def command_up(args: argparse.Namespace) -> int:
    compose_args = ["up", "--build"]
    if args.detach:
        compose_args.append("--detach")
    return run_compose(compose_args)


def command_down(args: argparse.Namespace) -> int:
    compose_args = ["down"]
    if args.volumes:
        compose_args.append("--volumes")
    return run_compose(compose_args)


def command_logs(args: argparse.Namespace) -> int:
    compose_args = ["logs"]
    if args.follow:
        compose_args.append("--follow")
    return run_compose(compose_args)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QuantGod local Docker Compose helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("static-check", help="Run local-only static guard checks").set_defaults(
        func=command_static_check
    )
    subparsers.add_parser("doctor", help="Show local Docker readiness").set_defaults(func=command_doctor)
    subparsers.add_parser("config", help="Render Docker Compose config").set_defaults(func=command_config)
    subparsers.add_parser("build", help="Build local backend/frontend images").set_defaults(func=command_build)

    up = subparsers.add_parser("up", help="Start the local stack")
    up.add_argument("--no-detach", dest="detach", action="store_false", help="Run in foreground")
    up.set_defaults(func=command_up, detach=True)

    down = subparsers.add_parser("down", help="Stop the local stack")
    down.add_argument("--volumes", action="store_true", help="Also remove local state volume")
    down.set_defaults(func=command_down)

    subparsers.add_parser("ps", help="Show stack containers").set_defaults(func=command_ps)

    logs = subparsers.add_parser("logs", help="Show stack logs")
    logs.add_argument("--follow", action="store_true", help="Follow logs")
    logs.set_defaults(func=command_logs)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
