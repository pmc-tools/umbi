"""Tests for umbi.datatypes.numeric module."""

from fractions import Fraction

import pytest

from umbi.datatypes import (
    Interval,
    IntervalType,
    NumericPrimitiveType,
)
from umbi.datatypes.numeric import (
    numeric_promotion_type,
    numeric_type_of,
    promote_numeric_to,
)


class TestNumericTypeOf:
    """Test numeric_type_of function."""

    def test_numeric_primitive_type(self):
        """Test determining type of numeric primitives."""
        assert numeric_type_of(5) == NumericPrimitiveType.INT
        assert numeric_type_of(3.14) == NumericPrimitiveType.DOUBLE
        assert numeric_type_of(Fraction(3, 4)) == NumericPrimitiveType.RATIONAL

    def test_interval_type(self):
        """Test determining type of intervals."""
        interval = Interval(1, 5)
        assert numeric_type_of(interval) == IntervalType(NumericPrimitiveType.INT)

        interval_float = Interval(1.0, 5.0)
        assert numeric_type_of(interval_float) == IntervalType(NumericPrimitiveType.DOUBLE)


class TestNumericPromotionType:
    """Test numeric_promotion_type function."""

    def test_single_primitive_type(self):
        """Test promotion with single primitive type."""
        result = numeric_promotion_type([NumericPrimitiveType.INT])
        assert result == NumericPrimitiveType.INT

    def test_mixed_primitive_types(self):
        """Test promotion with mixed primitive types."""
        result = numeric_promotion_type([NumericPrimitiveType.INT, NumericPrimitiveType.DOUBLE])
        assert result == NumericPrimitiveType.DOUBLE

    def test_interval_type_promotion(self):
        """Test promotion with interval types."""
        int_interval = IntervalType(NumericPrimitiveType.INT)
        double_interval = IntervalType(NumericPrimitiveType.DOUBLE)
        result = numeric_promotion_type([int_interval, double_interval])
        assert result == IntervalType(NumericPrimitiveType.DOUBLE)

    def test_mixed_primitive_and_interval_types(self):
        """Test promotion with both primitive and interval types."""
        # When mixing primitives and intervals, all primitives convert to intervals
        result = numeric_promotion_type([NumericPrimitiveType.INT, IntervalType(NumericPrimitiveType.DOUBLE)])
        assert isinstance(result, IntervalType)
        assert result.base_type == NumericPrimitiveType.DOUBLE

    def test_empty_types_assertion(self):
        """Test that empty types raises assertion."""
        with pytest.raises(AssertionError):
            numeric_promotion_type([])

    def test_invalid_types_assertion(self):
        """Test that invalid types raise assertion."""
        with pytest.raises(AssertionError):
            numeric_promotion_type(["invalid"])  # type: ignore


class TestPromoteNumericTo:
    """Test promote_numeric_to function."""

    def test_promote_primitive_to_primitive(self):
        """Test promoting numeric primitive to primitive type."""
        result = promote_numeric_to(5, NumericPrimitiveType.DOUBLE)
        assert result == 5.0
        assert isinstance(result, float)

    def test_promote_primitive_to_interval(self):
        """Test promoting numeric primitive to interval type."""
        target = IntervalType(NumericPrimitiveType.INT)
        result = promote_numeric_to(5, target)
        assert isinstance(result, Interval)
        assert result.left == 5
        assert result.right == 5

    def test_promote_interval_to_interval(self):
        """Test promoting interval to another interval type."""
        interval = Interval(1, 5)
        target = IntervalType(NumericPrimitiveType.DOUBLE)
        result = promote_numeric_to(interval, target)
        assert isinstance(result, Interval)
        assert result.left == 1.0
        assert result.right == 5.0

    def test_promote_incompatible_primitive_assertion(self):
        """Test that promoting incompatible primitive raises assertion."""
        with pytest.raises(AssertionError):
            promote_numeric_to(Interval(1, 5), NumericPrimitiveType.INT)  # type: ignore
