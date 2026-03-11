"""
Primitive scalar datatypes.
#TODO: introduce StringType to include strings and jsons?
"""

import enum

""" Primitive scalar type names. """


class PrimitiveType(str, enum.Enum):
    BOOL = "bool"
    STRING = "string"


""" Alias for primitive scalar objects. """
Primitive = bool | str


def primitive_type_of(value: Primitive) -> PrimitiveType:
    """Determine the primitive type of a given value."""
    if isinstance(value, bool):
        return PrimitiveType.BOOL
    else:  # isinstance(value, str):
        return PrimitiveType.STRING
