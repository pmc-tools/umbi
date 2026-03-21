"""Tests for umbi.binary.sized_type module."""

import pytest

from umbi.binary import SizedType, BOOL1, UINT32, UINT64
from umbi.datatypes import PrimitiveType, NumericPrimitiveType


class TestSizedTypeBasics:
    """Test basic SizedType functionality."""

    def test_create_sized_type_bool(self):
        """Test creating a SizedType for boolean."""
        sized_type = SizedType(PrimitiveType.BOOL, 1)
        assert sized_type.type == PrimitiveType.BOOL
        assert sized_type.size_bits == 1

    def test_create_sized_type_uint(self):
        """Test creating a SizedType for unsigned integer."""
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)
        assert sized_type.type == NumericPrimitiveType.UINT
        assert sized_type.size_bits == 32

    def test_create_sized_type_int(self):
        """Test creating a SizedType for signed integer."""
        sized_type = SizedType(NumericPrimitiveType.INT, 64)
        assert sized_type.type == NumericPrimitiveType.INT
        assert sized_type.size_bits == 64

    def test_create_sized_type_double(self):
        """Test creating a SizedType for double."""
        sized_type = SizedType(NumericPrimitiveType.DOUBLE, 64)
        assert sized_type.type == NumericPrimitiveType.DOUBLE
        assert sized_type.size_bits == 64

    def test_create_sized_type_string(self):
        """Test creating a SizedType for string."""
        sized_type = SizedType(PrimitiveType.STRING, 64)
        assert sized_type.type == PrimitiveType.STRING
        assert sized_type.size_bits == 64


class TestSizedTypeConversion:
    """Test size conversion properties."""

    def test_size_bytes_aligned(self):
        """Test size_bytes for byte-aligned sizes."""
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)
        assert sized_type.size_bytes == 4

    def test_size_bytes_not_aligned(self):
        """Test size_bytes with ceiling division for non-aligned sizes."""
        sized_type = SizedType(PrimitiveType.BOOL, 5)
        # (5 + 7) // 8 = 1
        assert sized_type.size_bytes == 1

    def test_is_byte_aligned(self):
        """Test byte alignment check."""
        aligned = SizedType(NumericPrimitiveType.UINT, 32)
        not_aligned = SizedType(PrimitiveType.BOOL, 5)
        assert aligned.is_byte_aligned
        assert not not_aligned.is_byte_aligned


class TestSizedTypeValidation:
    """Test SizedType validation."""

    def test_positive_size_required(self):
        """Test that size must be positive."""
        with pytest.raises(AssertionError):
            SizedType(NumericPrimitiveType.UINT, 0)

        with pytest.raises(AssertionError):
            SizedType(NumericPrimitiveType.UINT, -1)

    def test_string_must_be_64_bits(self):
        """Test that STRING type must be 64 bits."""
        # Valid
        SizedType(PrimitiveType.STRING, 64)

        # Invalid
        with pytest.raises(ValueError):
            SizedType(PrimitiveType.STRING, 32)

    def test_double_must_be_64_bits(self):
        """Test that DOUBLE type must be 64 bits."""
        # Valid
        SizedType(NumericPrimitiveType.DOUBLE, 64)

        # Invalid
        with pytest.raises(ValueError):
            SizedType(NumericPrimitiveType.DOUBLE, 32)

    def test_rational_must_be_multiple_of_2(self):
        """Test that RATIONAL type must have size as multiple of 2."""
        # Valid
        SizedType(NumericPrimitiveType.RATIONAL, 128)

        # Invalid
        with pytest.raises(ValueError):
            SizedType(NumericPrimitiveType.RATIONAL, 127)


class TestPredefinedConstants:
    """Test predefined SizedType constants."""

    def test_bool1(self):
        """Test BOOL1 constant."""
        assert BOOL1.type == PrimitiveType.BOOL
        assert BOOL1.size_bits == 1

    def test_uint32(self):
        """Test UINT32 constant."""
        assert UINT32.type == NumericPrimitiveType.UINT
        assert UINT32.size_bits == 32

    def test_uint64(self):
        """Test UINT64 constant."""
        assert UINT64.type == NumericPrimitiveType.UINT
        assert UINT64.size_bits == 64


class TestForTypeClassMethod:
    """Test SizedType.for_type() class method."""

    def test_bool_default_size(self):
        """Test default size for BOOL."""
        sized_type = SizedType.for_type(PrimitiveType.BOOL)
        assert sized_type.size_bits == 1

    def test_string_default_size(self):
        """Test default size for STRING."""
        sized_type = SizedType.for_type(PrimitiveType.STRING)
        assert sized_type.size_bits == 64

    def test_uint_default_size(self):
        """Test default size for UINT."""
        sized_type = SizedType.for_type(NumericPrimitiveType.UINT)
        assert sized_type.size_bits == 64

    def test_int_default_size(self):
        """Test default size for INT."""
        sized_type = SizedType.for_type(NumericPrimitiveType.INT)
        assert sized_type.size_bits == 64

    def test_double_default_size(self):
        """Test default size for DOUBLE."""
        sized_type = SizedType.for_type(NumericPrimitiveType.DOUBLE)
        assert sized_type.size_bits == 64
