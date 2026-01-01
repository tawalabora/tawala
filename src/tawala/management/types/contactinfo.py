from typing import Literal, TypeAlias

ContactAddressKey: TypeAlias = Literal[
    "country",
    "state",
    "city",
    "street",
]

ContactEmailKey: TypeAlias = Literal[
    "primary",
    "additional",
]

ContactPhoneKey: TypeAlias = Literal[
    "primary",
    "additional",
]

__all__ = ["ContactAddressKey", "ContactEmailKey", "ContactPhoneKey"]
