from typing import Optional, TypeAlias
from pathlib import Path

ValueType: TypeAlias = Optional[str | bool | list[str] | Path | int]


__all__ = ["ValueType"]
