"""Tests for umbi.datatypes.scalar module."""

from fractions import Fraction

import pytest

from umbi.datatypes import (
    Interval,
    NumericPrimitiveType,
    PrimitiveType,
    promote_scalars_to,
    promote_scalars,
)
from umbi.datatypes.scalar import (
    promote_scalar_to,
    scalar_type_of,
    scalar_types_of,
    scalar_promotion_type,
)


class TestScalarTypeOf:
    """Test scalar_type_of function."""

    def test_bool_scalar_type(self):
        """Test determining type of boolean scalar."""
        assert scalar_type_of(True) == PrimitiveType.BOOL
        assert scalar_type_of(False) == PrimitiveType.BOOL

    def test_string_scalar_type(self):
        """Test determining type of string scalar."""
        assert scalar_type_of("hello") == PrimitiveType.STRING

    def test_int_scalar_type(self):
        """Test determining type of int scalar."""
        assert scalar_type_of(42) == NumericPrimitiveType.INT

    def test_float_scalar_type(self):
        """Test determining type of float scalar."""
        assert scalar_type_of(3.14) == NumericPrimitiveType.DOUBLE

    def test_fraction_scalar_type(self):
        """Test determining type of fraction scalar."""
        assert scalar_type_of(Fraction(3, 4)) == NumericPrimitiveType.RATIONAL

    def test_interval_scalar_type(self):
        """Test determining type of interval scalar."""
        from umbi.datatypes import IntervalType

        interval = Interval(1, 5)
        assert scalar_type_of(interval) == IntervalType(NumericPrimitiveType.INT)


class TestScalarTypesOf:
    """Test scalar_types_of function."""

    def test_single_scalar_types(self):
        """Test determining types of single scalar."""
        assert scalar_types_of([5]) == {NumericPrimitiveType.INT}
        assert scalar_types_of(["hello"]) == {PrimitiveType.STRING}

    def test_multiple_scalar_types(self):
        """Test determining types of multiple scalars."""
        types = scalar_types_of([True, 5, 3.14])
        assert PrimitiveType.BOOL in types
        assert NumericPrimitiveType.INT in types
        assert NumericPrimitiveType.DOUBLE in types

    def test_mixed_scalar_types(self):
        """Test determining types of mixed scalars."""
        types = scalar_types_of([True, "hello", 42])
        assert PrimitiveType.BOOL in types
        assert PrimitiveType.STRING in types
        assert NumericPrimitiveType.INT in types


class TestScalarPromotionType:
    """Test scalar_promotion_type function."""

    def test_single_type_promotion(self):
        """Test promotion with single type."""
        result = scalar_promotion_type([PrimitiveType.BOOL])
        assert result == PrimitiveType.BOOL

    def test_bool_numeric_promotion(self):
        """Test BOOL and numeric promote to numeric."""
        result = scalar_promotion_type([PrimitiveType.BOOL, NumericPrimitiveType.INT])
        assert result == NumericPrimitiveType.INT

    def test_string_promotion(self):
        """Test that STRING dominates promotion."""
        result = scalar_promotion_type([PrimitiveType.STRING, NumericPrimitiveType.INT, PrimitiveType.BOOL])
        assert result == PrimitiveType.STRING

    def test_numeric_type_promotion(self):
        """Test promotion of numeric types."""
        result = scalar_promotion_type([NumericPrimitiveType.INT, NumericPrimitiveType.DOUBLE])
        assert result == NumericPrimitiveType.DOUBLE

    def test_empty_types_raises(self):
        """Test that empty collection raises ValueError."""
        with pytest.raises(ValueError):
            scalar_promotion_type([])


class TestPromoteScalarTo:
    """Test promote_scalar_to function."""

    def test_promote_to_string(self):
        """Test promoting any scalar to string."""
        assert promote_scalar_to(5, PrimitiveType.STRING) == "5"
        assert promote_scalar_to(True, PrimitiveType.STRING) == "True"

    def test_promote_to_bool(self):
        """Test promoting bool to bool."""
        assert promote_scalar_to(True, PrimitiveType.BOOL) is True

    def test_promote_invalid_to_bool_assertion(self):
        """Test that promoting non-bool to bool raises assertion."""
        with pytest.raises(AssertionError):
            promote_scalar_to(5, PrimitiveType.BOOL)

    def test_promote_bool_to_numeric(self):
        """Test promoting bool to numeric (converts to int first)."""
        result = promote_scalar_to(True, NumericPrimitiveType.INT)
        assert result == 1

    def test_promote_numeric_to_numeric(self):
        """Test promoting numeric primitives."""
        result = promote_scalar_to(5, NumericPrimitiveType.DOUBLE)
        assert result == 5.0


class TestPromoteScalarsTo:
    """Test promote_scalars_to function."""

    def test_promote_sequence_to_target_type(self):
        """Test promoting sequence of scalars to target type."""
        result = promote_scalars_to([1, 2, 3], NumericPrimitiveType.DOUBLE)
        assert result == [1.0, 2.0, 3.0]
        assert all(isinstance(v, float) for v in result)

    def test_promote_mixed_to_string(self):
        """Test promoting mixed scalars to string."""
        result = promote_scalars_to([1, True, 3.14], PrimitiveType.STRING)
        assert result == ["1", "True", "3.14"]

    def test_promote_empty_sequence(self):
        """Test promoting empty sequence."""
        result = promote_scalars_to([], NumericPrimitiveType.INT)
        assert result == []


class TestPromoteScalars:
    """Test promote_scalars function."""

    def test_promote_scalars_common_type(self):
        """Test promoting scalars to their common type."""
        target_type, promoted = promote_scalars([1, 2.5, 3])
        assert target_type == NumericPrimitiveType.DOUBLE
        assert promoted == [1.0, 2.5, 3.0]

    def test_promote_scalars_bool_numeric(self):
        """Test promoting bool and numeric."""
        target_type, promoted = promote_scalars([True, 5])
        assert target_type == NumericPrimitiveType.INT
        assert promoted == [1, 5]

    def test_promote_scalars_with_string(self):
        """Test promoting with string present."""
        target_type, promoted = promote_scalars([5, "hello", True])
        assert target_type == PrimitiveType.STRING
        assert promoted == ["5", "hello", "True"]

    def test_promote_single_scalar(self):
        """Test promoting single scalar."""
        target_type, promoted = promote_scalars([42])
        assert target_type == NumericPrimitiveType.INT
        assert promoted == [42]
