"""Vercel entry point for the existing Israptama HTTP API."""
from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Vercel loads this file from api/; the shared app modules live at the project root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import Handler  # noqa: E402


class handler(Handler):
    """Preserve the local API implementation behind explicit Vercel rewrites."""

    def _select_route(self) -> None:
        route = parse_qs(urlparse(self.path).query).get("route", [None])[0]
        if route in {"sample", "research", "sample.csv", "template.csv",
                     "analyze", "review"}:
            self.path = f"/api/{route}"

    def do_GET(self) -> None:
        self._select_route()
        super().do_GET()

    def do_POST(self) -> None:
        self._select_route()
        super().do_POST()
