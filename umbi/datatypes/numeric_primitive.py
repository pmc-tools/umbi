"""
Numeric datatypes (integers, floats, rationals) that allow promotions.
"""

import enum
from fractions import Fraction

""" Numeric primitive types. """


class NumericPrimitiveType(str, enum.Enum):
    INT = "int"
    UINT = "uint"
    DOUBLE = "double"
    RATIONAL = "rational"


""" Alias for primitive numeric objects. """
NumericPrimitive = int | float | Fraction


def is_integer_type(type: NumericPrimitiveType) -> bool:
    return type in [NumericPrimitiveType.INT, NumericPrimitiveType.UINT]


def assert_integer_type(type: NumericPrimitiveType):
    assert is_integer_type(type), f"not an integer type: {type}"


def integer_type_signed(type: NumericPrimitiveType) -> bool:
    assert_integer_type(type)
    return type == NumericPrimitiveType.INT


def numeric_primitive_type_of(value: NumericPrimitive) -> NumericPrimitiveType:
    """Determine the numeric type of a given value."""
    if isinstance(value, int):
        return NumericPrimitiveType.INT
    elif isinstance(value, float):
        return NumericPrimitiveType.DOUBLE
    else:  # isinstance(value, Fraction):
        return NumericPrimitiveType.RATIONAL


def common_numeric_primitive_type(types: set[NumericPrimitiveType]) -> NumericPrimitiveType:
    """Determine the common numeric type from a set of numeric types. Used for type promotion."""
    assert len(types) > 0, "cannot determine common numeric type of empty set"
    assert all(isinstance(t, NumericPrimitiveType) for t in types), f"non-numeric types found in set: {types}"
    if NumericPrimitiveType.RATIONAL in types:
        return NumericPrimitiveType.RATIONAL
    elif NumericPrimitiveType.DOUBLE in types:
        return NumericPrimitiveType.DOUBLE
    elif NumericPrimitiveType.INT in types:
        return NumericPrimitiveType.INT
    else:  # only NumericPrimitiveType.UINT in types
        return NumericPrimitiveType.UINT


def promote_numeric_primitive_to(value: NumericPrimitive, target_type: NumericPrimitiveType) -> NumericPrimitive:
    """
    Promote a primitive numeric value to the target type.
    Promotion rules: int -> double -> rational
    """
    if numeric_primitive_type_of(value) == target_type:
        return value
    if target_type == NumericPrimitiveType.INT:
        raise ValueError(f"cannot promote value {value} to int")
    elif target_type == NumericPrimitiveType.DOUBLE:
        assert isinstance(value, int), f"cannot promote value {value} to double"
        return float(value)
    else:
        assert target_type == NumericPrimitiveType.RATIONAL, f"unexpected target type: {target_type}"
        if isinstance(value, int):
            return Fraction(value, 1)
        elif isinstance(value, float):
            return Fraction.from_float(value)
        else:
            raise ValueError(f"cannot promote value {value} to rational")
