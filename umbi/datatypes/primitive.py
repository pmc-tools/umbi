"""
Primitive datatypes.
#TODO: introduce StringType to include strings and jsons?
"""

import enum
from typing import TypeAlias


class PrimitiveType(str, enum.Enum):
    """Primitive types."""

    BOOL = "bool"
    STRING = "string"


#: Primitive values (boolean or string).
Primitive: TypeAlias = bool | str


def primitive_type_of(value: Primitive) -> PrimitiveType:
    """Determine the primitive type of a given value."""
    if isinstance(value, bool):
        return PrimitiveType.BOOL
    else:  # isinstance(value, str):
        return PrimitiveType.STRING
