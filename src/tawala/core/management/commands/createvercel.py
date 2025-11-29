"""Management command: createvercel"""

import json
from pathlib import Path
from typing import Any, List, TypedDict

from django.conf import settings
from django.core.management.base import BaseCommand


class RewriteRule(TypedDict):
    source: str
    destination: str


VercelConfig = TypedDict(
    "VercelConfig",
    {
        "$schema": str,
        "buildCommand": str,
        "rewrites": List[RewriteRule],
    },
)
# Using the dict-style TypedDict because $schema is not a valid Python identifier.


class Command(BaseCommand):
    help = "Create a vercel.json file at BASE_DIR with Vercel config."

    def handle(self, *args: Any, **options: Any) -> None:
        base_dir: Path = Path(settings.BASE_DIR)
        vercel_path: Path = base_dir / "vercel.json"

        content: VercelConfig = {
            "$schema": "https://openapi.vercel.sh/vercel.json",
            "buildCommand": "export UV_LINK_MODE=copy; uv run tawala build",
            "rewrites": [{"source": "/(.*)", "destination": "/api/asgi"}],
        }

        try:
            json_text: str = json.dumps(content, indent=2)
            vercel_path.write_text(json_text, encoding="utf-8")

            self.stdout.write(
                self.style.SUCCESS(f"vercel.json created at: {vercel_path}")
            )
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Failed to create vercel.json: {exc}"))
