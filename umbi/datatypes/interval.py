"""
Interval datatypes.
"""

from collections.abc import Collection
from dataclasses import dataclass

from .numeric_primitive import (
    NumericPrimitive,
    NumericPrimitiveType,
    numeric_primitive_promotion_type,
    numeric_primitive_type_of,
    promote_numeric_primitive_to,
)


@dataclass(frozen=True)
class IntervalType:
    """Interval type, parameterized by a base numeric primitive type."""

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

    @property
    def is_discrete(self) -> bool:
        """Check if the interval type is discrete."""
        return self.base_type.is_discrete

    @property
    def is_continuous(self) -> bool:
        """Check if the interval type is continuous."""
        return self.base_type.is_continuous


@dataclass(frozen=False)
class Interval:
    """A numeric interval with left <= right."""

    #: Left endpoint of the interval.
    left: NumericPrimitive
    #: Right endpoint of the interval.
    right: NumericPrimitive

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not self.left <= self.right:
            raise ValueError(f"expected {self.left} <=  {self.right}")

    def __str__(self) -> str:
        return f"interval[{self.left},{self.right}]"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another interval or numeric primitive. Numeric primitives are treated as point intervals
        [value, value].
        """
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
        types = {numeric_primitive_type_of(self.left), numeric_primitive_type_of(self.right)}
        return numeric_primitive_promotion_type(types)

    @property
    def type(self) -> IntervalType:
        """Get the interval type of the interval."""
        return IntervalType(self.base_type)


def interval_promotion_type(types: Collection[IntervalType]) -> IntervalType:
    """Determine the interval type to which all interval types in the set can be promoted."""
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
