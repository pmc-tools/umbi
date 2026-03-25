"""Tests for umbi.datatypes.interval module."""

from fractions import Fraction

import pytest

from umbi.datatypes import Interval, IntervalType, NumericPrimitiveType
from umbi.datatypes.interval import (
    interval_promotion_type,
    promote_interval_to,
)


class TestIntervalType:
    """Test IntervalType class."""

    def test_interval_type_creation(self):
        """Test creating IntervalType."""
        it = IntervalType(NumericPrimitiveType.INT)
        assert it.base_type == NumericPrimitiveType.INT

    def test_interval_type_str(self):
        """Test IntervalType string representation."""
        it = IntervalType(NumericPrimitiveType.INT)
        assert str(it) == "int-interval"

        it_double = IntervalType(NumericPrimitiveType.DOUBLE)
        assert str(it_double) == "double-interval"

    def test_interval_type_from_string(self):
        """Test parsing IntervalType from string."""
        it = IntervalType.from_string("int-interval")
        assert it.base_type == NumericPrimitiveType.INT

        it_double = IntervalType.from_string("double-interval")
        assert it_double.base_type == NumericPrimitiveType.DOUBLE

    def test_interval_type_from_string_invalid(self):
        """Test parsing invalid interval type string."""
        with pytest.raises(ValueError):
            IntervalType.from_string("invalid")

        with pytest.raises(ValueError):
            IntervalType.from_string("int-invalid")


class TestInterval:
    """Test Interval class."""

    def test_interval_creation(self):
        """Test creating Interval."""
        interval = Interval(1, 5)
        assert interval.left == 1
        assert interval.right == 5

    def test_interval_with_floats(self):
        """Test Interval with float endpoints."""
        interval = Interval(1.5, 3.5)
        assert interval.left == 1.5
        assert interval.right == 3.5

    def test_interval_with_fractions(self):
        """Test Interval with fraction endpoints."""
        left = Fraction(1, 2)
        right = Fraction(3, 2)
        interval = Interval(left, right)
        assert interval.left == left
        assert interval.right == right

    def test_interval_invalid_bounds(self):
        """Test that invalid interval bounds raise error."""
        with pytest.raises(ValueError):
            Interval(5, 1)

    def test_interval_equal_bounds(self):
        """Test interval with equal endpoints."""
        interval = Interval(5, 5)
        assert interval.left == 5
        assert interval.right == 5


class TestIntervalTypeClassification:
    """Test IntervalType classification properties."""

    def test_is_discrete_for_int_interval(self):
        """Test that int-interval is discrete."""
        it = IntervalType(NumericPrimitiveType.INT)
        assert it.is_discrete

    def test_is_discrete_for_uint_interval(self):
        """Test that uint-interval is discrete."""
        it = IntervalType(NumericPrimitiveType.UINT)
        assert it.is_discrete

    def test_is_discrete_for_continuous_intervals(self):
        """Test that double-interval and rational-interval are not discrete."""
        double_it = IntervalType(NumericPrimitiveType.DOUBLE)
        rational_it = IntervalType(NumericPrimitiveType.RATIONAL)
        assert not double_it.is_discrete
        assert not rational_it.is_discrete

    def test_is_continuous_for_double_interval(self):
        """Test that double-interval is continuous."""
        it = IntervalType(NumericPrimitiveType.DOUBLE)
        assert it.is_continuous

    def test_is_continuous_for_rational_interval(self):
        """Test that rational-interval is continuous."""
        it = IntervalType(NumericPrimitiveType.RATIONAL)
        assert it.is_continuous

    def test_is_continuous_for_discrete_intervals(self):
        """Test that int-interval and uint-interval are not continuous."""
        int_it = IntervalType(NumericPrimitiveType.INT)
        uint_it = IntervalType(NumericPrimitiveType.UINT)
        assert not int_it.is_continuous
        assert not uint_it.is_continuous

    def test_interval_str_repr(self):
        """Test Interval string representation."""
        interval = Interval(1, 5)
        assert str(interval) == "interval[1,5]"
        assert repr(interval) == "interval[1,5]"

    def test_interval_contains(self):
        """Test interval membership."""
        interval = Interval(1, 5)
        assert 1 in interval
        assert 3 in interval
        assert 5 in interval
        assert 0 not in interval
        assert 6 not in interval

    def test_interval_type_property(self):
        """Test interval.type property."""
        interval = Interval(1, 5)
        assert interval.type == IntervalType(NumericPrimitiveType.INT)

        interval_float = Interval(1.0, 5.0)
        assert interval_float.type == IntervalType(NumericPrimitiveType.DOUBLE)

    def test_interval_equality(self):
        """Test interval equality."""
        i1 = Interval(1, 5)
        i2 = Interval(1, 5)
        assert i1 == i2

        i3 = Interval(1, 6)
        assert i1 != i3

    def test_interval_equality_with_numeric(self):
        """Test interval equality with numeric primitives."""
        interval = Interval(5, 5)
        assert interval == 5  # point interval equals the value

        interval2 = Interval(1, 5)
        assert interval2 != 3  # non-point interval not equal to value


class TestIntervalPromotionType:
    """Test interval_promotion_type function."""

    def test_single_interval_type_promotion(self):
        """Test promotion with single interval type."""
        it = IntervalType(NumericPrimitiveType.INT)
        result = interval_promotion_type([it])
        assert result == it

    def test_mixed_interval_types_promotion(self):
        """Test promotion with mixed interval types."""
        it_int = IntervalType(NumericPrimitiveType.INT)
        it_double = IntervalType(NumericPrimitiveType.DOUBLE)
        result = interval_promotion_type([it_int, it_double])
        assert result == IntervalType(NumericPrimitiveType.DOUBLE)


class TestPromoteIntervalTo:
    """Test promote_interval_to function."""

    def test_promote_interval_same_type(self):
        """Test promoting interval to same type."""
        interval = Interval(1, 5)
        target = IntervalType(NumericPrimitiveType.INT)
        result = promote_interval_to(interval, target)
        assert result.left == 1
        assert result.right == 5

    def test_promote_interval_to_double(self):
        """Test promoting interval to double type."""
        interval = Interval(1, 5)
        target = IntervalType(NumericPrimitiveType.DOUBLE)
        result = promote_interval_to(interval, target)
        assert result.left == 1.0
        assert result.right == 5.0
        assert isinstance(result.left, float)
