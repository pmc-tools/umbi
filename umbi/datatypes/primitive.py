"""
Primitive scalar datatypes.
#TODO: expand to JSONs?
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


# def is_of_atomic_type(value: object, type: PrimitiveType) -> bool:
#     """Check if a value is an instance of the given atomic type."""
#     return primitive_type_of(value) == type
