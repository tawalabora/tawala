from pathlib import Path

TAWALA = "tawala"

UI = "ui"

UI_PATH = Path(__file__).resolve().parent.parent / UI

DJANGO_SETTINGS_MODULE = f"{TAWALA}.management.settings"
