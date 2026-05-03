from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "docker" / "compose.local.yml"
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

    def test_compose_keeps_p3_1_scope_to_backend_frontend(self) -> None:
        text = self.read_compose().lower()
        self.assertIn("  backend:", text)
        self.assertIn("  frontend:", text)
        for forbidden in ["webhook:", "email:", "mailer:", "broker:", "billing:", "credits:", "postgres:", "mysql:"]:
            self.assertNotIn(forbidden, text)
        self.assertNotIn("/var/run/docker.sock", text)

    def test_compose_has_safety_default_environment(self) -> None:
        text = self.read_compose()
        for marker in [
            'QG_LOCAL_ONLY: "1"',
            'QG_DRY_RUN: "1"',
            'QG_KILL_SWITCH_LOCKED: "1"',
            'QG_ORDER_SEND_ALLOWED: "0"',
            'QG_LIVE_PRESET_MUTATION_ALLOWED: "0"',
            'QG_CREDENTIAL_STORAGE_ALLOWED: "0"',
            'QG_TELEGRAM_COMMANDS_ALLOWED: "0"',
            'condition: service_healthy',
        ]:
            self.assertIn(marker, text)
        for forbidden in ["TELEGRAM_BOT_TOKEN", "OPENROUTER_API_KEY", "BROKER_API_KEY", "MT5_PASSWORD", "HFM_PASSWORD"]:
            self.assertNotIn(forbidden, text)

    def test_static_check_function_passes(self) -> None:
        spec = importlib.util.spec_from_file_location("qg_docker_local", SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        self.assertEqual(module.static_check(), [])


if __name__ == "__main__":
    unittest.main()
