from typing import Literal

VALID_CASTS = ("str_cast", "bool_cast", "int_cast", "float_cast", "list_cast")

CastType = Literal["str_cast", "bool_cast", "int_cast", "float_cast", "list_cast"]
