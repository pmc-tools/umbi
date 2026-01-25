"""
Numeric type: union of numeric primitive types and intervals.
"""

from .numeric_primitive import (
    NumericPrimitive,
    NumericPrimitiveType,
    common_numeric_primitive_type,
    numeric_primitive_type_of,
    promote_numeric_primitive_to,
)
from .interval import Interval, IntervalType, base_to_interval_type, common_interval_type, promote_interval_to

""" Alias for all numeric objects. """
NumericType = NumericPrimitiveType | IntervalType

""" Alias for all numeric types. """
Numeric = NumericPrimitive | Interval


def is_numeric_primitive_type(type: NumericType) -> bool:
    return isinstance(type, NumericPrimitiveType)


def is_interval_type(type: NumericType) -> bool:
    return isinstance(type, IntervalType)


def numeric_type_of(value: Numeric) -> NumericType:
    """Determine the numeric type of a given value."""
    if isinstance(value, NumericPrimitive):
        return numeric_primitive_type_of(value)
    else:  # isinstance(value, Interval):
        return value.type


def common_numeric_type(types: set[NumericType]) -> NumericType:
    """Determine the common numeric type from a set of numeric types. Used for type promotion."""
    assert len(types) > 0, "cannot determine common numeric type of empty set"
    assert all(isinstance(t, (NumericPrimitiveType, IntervalType)) for t in types), (
        f"non-numeric types found in set: {types}"
    )
    if any(isinstance(t, IntervalType) for t in types):
        # convert all primitive types to intervals
        interval_types = {base_to_interval_type(t) if isinstance(t, NumericPrimitiveType) else t for t in types}
        return common_interval_type(interval_types)
    # assert all(isinstance(t, NumericPrimitiveType) for t in types), f"non-primitive types found in set: {types}"
    return common_numeric_primitive_type(types)  # type: ignore


def promote_numeric_to(value: Numeric, target_type: NumericType) -> Numeric:
    """Promote a numeric value to the target type."""
    if isinstance(target_type, NumericPrimitiveType):
        assert isinstance(value, NumericPrimitive), f"cannot promote {value} to primitive type {target_type}"
        return promote_numeric_primitive_to(value, target_type)
    else:  # is_interval_type(target_type):
        if not isinstance(value, Interval):
            value = Interval(value, value)
        return promote_interval_to(value, target_type)
