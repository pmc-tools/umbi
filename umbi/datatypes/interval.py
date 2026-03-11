"""
Interval datatypes.
"""

from dataclasses import dataclass
from fractions import Fraction
from collections.abc import Collection
from .numeric_primitive import (
    NumericPrimitiveType,
    NumericPrimitive,
    numeric_primitive_promotion_type,
    promote_numeric_primitive_to,
)


@dataclass(frozen=True)
class IntervalType:
    base_type: NumericPrimitiveType

    def __str__(self) -> str:
        return f"{self.base_type.value}-interval"

    @classmethod
    def from_string(cls, s: str) -> "IntervalType":
        """Parse an interval type from a string s of type <base-type>-interval."""
        if not s.endswith("-interval"):
            raise ValueError(f"invalid interval type string: {s}")
        base_type_string = s.removesuffix("-interval")
        base_type = NumericPrimitiveType(base_type_string)
        return cls(base_type)


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
        return IntervalType(self.base_type)


def interval_promotion_type(types: Collection[IntervalType]) -> IntervalType:
    """Determine the common interval type from a set of interval types. Used for type promotion."""
    assert len(types) > 0, "cannot determine common numeric type of empty sequence"
    assert all(isinstance(t, IntervalType) for t in types), f"non-interval types found in set: {types}"
    base_types = {t.base_type for t in types}
    common_base_type = numeric_primitive_promotion_type(base_types)
    return IntervalType(common_base_type)


def promote_interval_to(value: Interval, target_type: IntervalType) -> Interval:
    """Promote an interval to the target interval type."""
    target_base_type = target_type.base_type
    return Interval(
        promote_numeric_primitive_to(value.left, target_base_type),
        promote_numeric_primitive_to(value.right, target_base_type),
    )
