from typing import Literal, TypeAlias

OrgKey: TypeAlias = Literal[
    "name",
    "short-name",
    "description",
]

__all__ = ["OrgKey"]
