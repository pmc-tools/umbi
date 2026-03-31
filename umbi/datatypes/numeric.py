"""
Numeric type: union of numeric primitive types and intervals.
"""

from collections.abc import Collection
from typing import TypeAlias

from .interval import Interval, IntervalType, interval_promotion_type, promote_interval_to
from .numeric_primitive import (
    NumericPrimitive,
    NumericPrimitiveType,
    numeric_primitive_promotion_type,
    numeric_primitive_type_of,
    promote_numeric_primitive_to,
)

#: Numeric type: either a primitive numeric type or an interval.
NumericType: TypeAlias = NumericPrimitiveType | IntervalType

#: Numeric value: either a primitive numeric value or an interval.
Numeric: TypeAlias = NumericPrimitive | Interval


def numeric_type_of(value: Numeric) -> NumericType:
    """Determine the numeric type of a given value."""
    if isinstance(value, NumericPrimitive):
        return numeric_primitive_type_of(value)
    else:  # isinstance(value, Interval):
        return value.type


def numeric_promotion_type(types: Collection[NumericType]) -> NumericType:
    """Determine the common numeric type from a set of numeric types. Used for type promotion."""
    assert len(types) > 0, "cannot determine common numeric type of empty set"
    assert all(isinstance(t, (NumericPrimitiveType, IntervalType)) for t in types), (
        f"non-numeric types found in set: {types}"
    )
    if any(isinstance(t, IntervalType) for t in types):
        # convert all primitive types to intervals
        interval_types = list({IntervalType(t) if isinstance(t, NumericPrimitiveType) else t for t in types})
        return interval_promotion_type(interval_types)
    return numeric_primitive_promotion_type(types)  # type: ignore[arg-type]


def promote_numeric_to(value: Numeric, target_type: NumericType) -> Numeric:
    """Promote a numeric value to the target type."""
    if isinstance(target_type, NumericPrimitiveType):
        assert isinstance(value, NumericPrimitive), f"cannot promote {value} to primitive type {target_type}"
        return promote_numeric_primitive_to(value, target_type)
    else:  # isinstance(target_type, IntervalType):
        if not isinstance(value, Interval):
            value = Interval(value, value)
        return promote_interval_to(value, target_type)


def is_numeric_a_probability(value: Numeric) -> bool:
    """Check if a numeric value is in the interval [0, 1]."""
    if isinstance(value, NumericPrimitive):
        return 0 <= value <= 1
    else:  # isinstance(value, Interval):
        return value.left >= 0 and value.right <= 1
