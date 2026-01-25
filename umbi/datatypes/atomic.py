"""
Atomic datatypes. "Atomic" is an umbrella term for primitive types that are neither numeric nor interval types.
#TODO: expand to JSONs?
"""

import enum

""" Atomic types. """


class AtomicType(str, enum.Enum):
    BOOL = "bool"
    STRING = "string"


""" Alias for atomic objects. """
Atomic = bool | str


def atomic_type_of(value: Atomic) -> AtomicType:
    """Determine the primitive type of a given value."""
    if isinstance(value, bool):
        return AtomicType.BOOL
    else:  # isinstance(value, str):
        return AtomicType.STRING


# def is_of_atomic_type(value: object, type: AtomicType) -> bool:
#     """Check if a value is an instance of the given atomic type."""
#     return atomic_type_of(value) == type
