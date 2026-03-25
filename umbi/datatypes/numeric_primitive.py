"""Numeric datatypes (integers, floats, rationals) that allow promotions."""

import enum
from collections.abc import Collection
from fractions import Fraction
from typing import TypeAlias


class NumericPrimitiveType(str, enum.Enum):
    """Numeric primitive types."""

    INT = "int"
    UINT = "uint"
    DOUBLE = "double"
    RATIONAL = "rational"

    @property
    def is_discrete(self) -> bool:
        """Check if the type is discrete."""
        return self in {NumericPrimitiveType.INT, NumericPrimitiveType.UINT}

    @property
    def is_continuous(self) -> bool:
        """Check if the type is continuous."""
        return self in {NumericPrimitiveType.DOUBLE, NumericPrimitiveType.RATIONAL}


#: Primitive numeric values (integers, floats, or rational numbers).
NumericPrimitive: TypeAlias = int | float | Fraction


def numeric_primitive_type_of(value: NumericPrimitive) -> NumericPrimitiveType:
    """Determine the numeric type of a given value."""
    if isinstance(value, int):
        return NumericPrimitiveType.INT
    elif isinstance(value, float):
        return NumericPrimitiveType.DOUBLE
    else:  # isinstance(value, Fraction):
        return NumericPrimitiveType.RATIONAL


def numeric_primitive_promotion_type(types: Collection[NumericPrimitiveType]) -> NumericPrimitiveType:
    """
    Determine the common numeric type from a set of numeric types. Used for type promotion.

    :raises ValueError: if the set of types is empty
    """
    assert len(types) > 0, "cannot determine common numeric type of empty set"
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
    :raises ValueError: if value cannot be promoted to target type (e.g., promoting to INT)
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
