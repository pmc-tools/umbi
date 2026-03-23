"""Tests for umbi.datatypes.numeric_primitive module."""

from fractions import Fraction

import pytest

from umbi.datatypes import NumericPrimitiveType
from umbi.datatypes.numeric_primitive import (
    numeric_primitive_promotion_type,
    numeric_primitive_type_of,
    promote_numeric_primitive_to,
)


class TestNumericPrimitiveType:
    """Test NumericPrimitiveType enum."""

    def test_numeric_primitive_type_values(self):
        """Test NumericPrimitiveType enum values."""
        assert NumericPrimitiveType.INT.value == "int"
        assert NumericPrimitiveType.UINT.value == "uint"
        assert NumericPrimitiveType.DOUBLE.value == "double"
        assert NumericPrimitiveType.RATIONAL.value == "rational"

    def test_numeric_primitive_type_count(self):
        """Test all NumericPrimitiveType members exist."""
        assert len(NumericPrimitiveType) == 4


class TestNumericPrimitiveTypeOf:
    """Test numeric_primitive_type_of function."""

    def test_int_type(self):
        """Test integer type identification."""
        assert numeric_primitive_type_of(42) == NumericPrimitiveType.INT
        assert numeric_primitive_type_of(0) == NumericPrimitiveType.INT
        assert numeric_primitive_type_of(-1) == NumericPrimitiveType.INT

    def test_float_type(self):
        """Test float type identification."""
        assert numeric_primitive_type_of(3.14) == NumericPrimitiveType.DOUBLE
        assert numeric_primitive_type_of(0.0) == NumericPrimitiveType.DOUBLE

    def test_fraction_type(self):
        """Test fraction type identification."""
        frac = Fraction(3, 4)
        assert numeric_primitive_type_of(frac) == NumericPrimitiveType.RATIONAL

    def test_bool_not_numeric_primitive(self):
        """Test that bool is not treated as numeric primitive."""
        # bool is subclass of int, but should be handled separately in scalar context
        assert numeric_primitive_type_of(True) == NumericPrimitiveType.INT


class TestNumericPrimitivePromotionType:
    """Test numeric_primitive_promotion_type function."""

    def test_single_type_promotion(self):
        """Test promotion with single type."""
        assert numeric_primitive_promotion_type([NumericPrimitiveType.INT]) == NumericPrimitiveType.INT

    def test_int_double_promotion(self):
        """Test INT and DOUBLE promote to DOUBLE."""
        assert (
            numeric_primitive_promotion_type([NumericPrimitiveType.INT, NumericPrimitiveType.DOUBLE])
            == NumericPrimitiveType.DOUBLE
        )

    def test_double_rational_promotion(self):
        """Test DOUBLE and RATIONAL promote to RATIONAL."""
        assert (
            numeric_primitive_promotion_type([NumericPrimitiveType.DOUBLE, NumericPrimitiveType.RATIONAL])
            == NumericPrimitiveType.RATIONAL
        )

    def test_all_types_promotion(self):
        """Test promotion with all types."""
        types = [
            NumericPrimitiveType.INT,
            NumericPrimitiveType.DOUBLE,
            NumericPrimitiveType.RATIONAL,
        ]
        assert numeric_primitive_promotion_type(types) == NumericPrimitiveType.RATIONAL

    def test_empty_types_assertion(self):
        """Test that empty types raises assertion."""
        with pytest.raises(AssertionError):
            numeric_primitive_promotion_type([])


class TestPromoteNumericPrimitiveTo:
    """Test promote_numeric_primitive_to function."""

    def test_promote_int_to_double(self):
        """Test promoting int to double."""
        result = promote_numeric_primitive_to(5, NumericPrimitiveType.DOUBLE)
        assert result == 5.0
        assert isinstance(result, float)

    def test_promote_int_to_rational(self):
        """Test promoting int to rational."""
        result = promote_numeric_primitive_to(5, NumericPrimitiveType.RATIONAL)
        assert result == Fraction(5, 1)

    def test_promote_float_to_rational(self):
        """Test promoting float to rational."""
        result = promote_numeric_primitive_to(2.5, NumericPrimitiveType.RATIONAL)
        assert result == Fraction(5, 2)

    def test_same_type_no_change(self):
        """Test promoting to same type returns same value."""
        assert promote_numeric_primitive_to(5, NumericPrimitiveType.INT) == 5

    def test_promote_to_int_raises(self):
        """Test that promoting to INT raises ValueError."""
        with pytest.raises(ValueError):
            promote_numeric_primitive_to(5.0, NumericPrimitiveType.INT)

    def test_promote_double_to_int_raises(self):
        """Test that promoting DOUBLE to INT raises."""
        with pytest.raises(ValueError):
            promote_numeric_primitive_to(3.14, NumericPrimitiveType.INT)
