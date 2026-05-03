from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "docker" / "compose.local.yml"
ENV_EXAMPLE = ROOT / "docker" / ".env.local.example"
SCRIPT = ROOT / "scripts" / "qg-docker-local.py"


class DockerLocalStackTests(unittest.TestCase):
    def read_compose(self) -> str:
        return COMPOSE.read_text(encoding="utf-8")

    def test_compose_binds_host_ports_to_loopback_only(self) -> None:
        text = self.read_compose()
        self.assertIn('"127.0.0.1:${QG_BACKEND_PORT:-8080}:8080"', text)
        self.assertIn('"127.0.0.1:${QG_FRONTEND_PORT:-5173}:5173"', text)
        self.assertNotIn('"8080:8080"', text)
        self.assertNotIn('"5173:5173"', text)
        self.assertNotIn('0.0.0.0:${QG_BACKEND_PORT', text)
        self.assertNotIn('0.0.0.0:${QG_FRONTEND_PORT', text)

    def test_compose_keeps_scope_to_backend_frontend_and_no_webhook_email(self) -> None:
        text = self.read_compose()
        self.assertIn("  backend:", text)
        self.assertIn("  frontend:", text)
        forbidden = ["webhook:", "email:", "mailer:", "broker:", "billing:", "credits:", "postgres:", "mysql:", "/var/run/docker.sock"]
        for marker in forbidden:
            self.assertNotIn(marker, text.lower())

    def test_compose_has_safety_default_environment(self) -> None:
        text = self.read_compose()
        required = [
            'QG_LOCAL_ONLY: "1"',
            'QG_DRY_RUN: "1"',
            'QG_KILL_SWITCH_LOCKED: "1"',
            'QG_ORDER_SEND_ALLOWED: "0"',
            'QG_LIVE_PRESET_MUTATION_ALLOWED: "0"',
            'QG_CREDENTIAL_STORAGE_ALLOWED: "0"',
            'QG_TELEGRAM_PUSH_ALLOWED: "${QG_TELEGRAM_PUSH_ALLOWED:-0}"',
            'QG_TELEGRAM_COMMANDS_ALLOWED: "0"',
            "condition: service_healthy",
        ]
        for marker in required:
            self.assertIn(marker, text)
        for forbidden in ["OPENROUTER_API_KEY", "BROKER_API_KEY", "MT5_PASSWORD", "HFM_PASSWORD"]:
            self.assertNotIn(forbidden, text)

    def test_telegram_token_and_chat_id_are_pass_through_only(self) -> None:
        text = self.read_compose()
        env_text = ENV_EXAMPLE.read_text(encoding="utf-8")
        self.assertIn('QG_TELEGRAM_BOT_TOKEN: "${QG_TELEGRAM_BOT_TOKEN:-}"', text)
        self.assertIn('QG_TELEGRAM_CHAT_ID: "${QG_TELEGRAM_CHAT_ID:-}"', text)
        self.assertIn('QG_TELEGRAM_API_BASE_URL: "${QG_TELEGRAM_API_BASE_URL:-https://api.telegram.org}"', text)
        self.assertNotRegex(text, re.compile(r"[0-9]{5,}:[A-Za-z0-9_-]{20,}"))
        self.assertIn("QG_TELEGRAM_PUSH_ALLOWED=0", env_text)
        self.assertIn("QG_TELEGRAM_COMMANDS_ALLOWED=0", env_text)
        self.assertRegex(env_text, re.compile(r"^QG_TELEGRAM_BOT_TOKEN=\s*$", re.MULTILINE))
        self.assertRegex(env_text, re.compile(r"^QG_TELEGRAM_CHAT_ID=\s*$", re.MULTILINE))

    def test_static_check_function_passes(self) -> None:
        spec = importlib.util.spec_from_file_location("qg_docker_local", SCRIPT)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        assert spec and spec.loader
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        self.assertEqual([], module.static_check())


if __name__ == "__main__":
    unittest.main()
