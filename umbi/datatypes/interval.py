"""
Interval datatypes.
"""

from fractions import Fraction
from .numeric_primitive import (
    NumericPrimitiveType,
    NumericPrimitive,
    common_numeric_primitive_type,
    promote_numeric_primitive_to,
)
import enum

""" Interval types. """


class IntervalType(str, enum.Enum):
    INT = "int-interval"
    UINT = "uint-interval"
    DOUBLE = "double-interval"
    RATIONAL = "rational-interval"


def interval_base_type(type: IntervalType) -> NumericPrimitiveType:
    return {
        IntervalType.INT: NumericPrimitiveType.INT,
        IntervalType.UINT: NumericPrimitiveType.UINT,
        IntervalType.DOUBLE: NumericPrimitiveType.DOUBLE,
        IntervalType.RATIONAL: NumericPrimitiveType.RATIONAL,
    }[type]


def base_to_interval_type(type: NumericPrimitiveType) -> IntervalType:
    return {
        NumericPrimitiveType.INT: IntervalType.INT,
        NumericPrimitiveType.UINT: IntervalType.UINT,
        NumericPrimitiveType.DOUBLE: IntervalType.DOUBLE,
        NumericPrimitiveType.RATIONAL: IntervalType.RATIONAL,
    }[type]


class Interval:
    """Represents a numeric interval where left <= right."""

    def __init__(self, left: NumericPrimitive, right: NumericPrimitive) -> None:
        self.left = left
        self.right = right
        self.validate()

    def validate(self) -> None:
        if not self.left <= self.right:
            raise ValueError(f"expected {self.left} <=  {self.right}")

    def __str__(self) -> str:
        return f"interval[{self.left},{self.right}]"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, NumericPrimitive):
            other = Interval(other, other)
        if not isinstance(other, Interval):
            return False
        return self.left == other.left and self.right == other.right

    def __contains__(self, value: NumericPrimitive) -> bool:
        """Check if a numeric value is within the interval."""
        return self.left <= value <= self.right

    @property
    def base_type(self) -> NumericPrimitiveType:
        """Get the base numeric type of the interval."""
        if isinstance(self.left, Fraction) or isinstance(self.right, Fraction):
            return NumericPrimitiveType.RATIONAL
        elif isinstance(self.left, float) or isinstance(self.right, float):
            return NumericPrimitiveType.DOUBLE
        else:  # isinstance(self.left, int) and isinstance(self.right, int):
            return NumericPrimitiveType.INT

    @property
    def type(self) -> IntervalType:
        """Get the interval type of the interval."""
        return base_to_interval_type(self.base_type)


def common_interval_type(types: set[IntervalType]) -> IntervalType:
    """Determine the common interval type from a set of interval types. Used for type promotion."""
    assert len(types) > 0, "cannot determine common numeric type of empty set"
    assert all(isinstance(t, IntervalType) for t in types), f"non-interval types found in set: {types}"
    base_types = {interval_base_type(t) for t in types}
    common_base_type = common_numeric_primitive_type(base_types)
    return base_to_interval_type(common_base_type)


def promote_interval_to(value: Interval, target_type: IntervalType) -> Interval:
    """Promote an interval to the target interval type."""
    target_base_type = interval_base_type(target_type)
    return Interval(
        promote_numeric_primitive_to(value.left, target_base_type),
        promote_numeric_primitive_to(value.right, target_base_type),
    )
