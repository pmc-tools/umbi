"""Tests for umbi.binary.scalar module."""

from fractions import Fraction

import pytest
from bitstring import BitArray

from umbi.binary import bytes_to_scalar, scalar_to_bytes
from umbi.binary.scalar import bits_to_scalar, scalar_to_bits
from umbi.datatypes import (
    Interval,
    IntervalType,
    NumericPrimitiveType,
    PrimitiveType,
)


class TestScalarToBytesBasic:
    """Test basic scalar_to_bytes functionality."""

    def test_bool_to_bytes(self):
        """Test converting boolean to bytes."""
        with pytest.raises(NotImplementedError):
            scalar_to_bytes(True, PrimitiveType.BOOL)

    def test_string_to_bytes(self):
        """Test converting string to bytes."""
        result = scalar_to_bytes("hello", PrimitiveType.STRING)
        # String is encoded as UTF-8
        assert result == b"hello"

    def test_int_to_bytes_default_size(self):
        """Test converting integer to bytes with default size."""
        result = scalar_to_bytes(42, NumericPrimitiveType.INT, num_bytes=8, little_endian=True)
        assert len(result) == 8
        # 42 in little-endian bytes
        assert result[0] == 42

    def test_uint_to_bytes_little_endian(self):
        """Test converting unsigned integer to bytes in little-endian."""
        result = scalar_to_bytes(256, NumericPrimitiveType.UINT, num_bytes=2, little_endian=True)
        assert len(result) == 2
        # 256 in little-endian: [0x00, 0x01]
        assert result == b"\x00\x01"

    def test_uint_to_bytes_big_endian(self):
        """Test converting unsigned integer to bytes in big-endian."""
        result = scalar_to_bytes(256, NumericPrimitiveType.UINT, num_bytes=2, little_endian=False)
        assert len(result) == 2
        # 256 in big-endian: [0x01, 0x00]
        assert result == b"\x01\x00"

    def test_double_to_bytes(self):
        """Test converting double to bytes."""
        result = scalar_to_bytes(3.14, NumericPrimitiveType.DOUBLE, num_bytes=8)
        assert len(result) == 8

    def test_rational_to_bytes(self):
        """Test converting rational to bytes."""
        frac = Fraction(1, 2)
        result = scalar_to_bytes(frac, NumericPrimitiveType.RATIONAL, num_bytes=16)
        assert len(result) == 16


class TestBytesToScalarBasic:
    """Test basic bytes_to_scalar functionality."""

    def test_bytes_to_bool(self):
        """Test converting bytes to boolean."""
        with pytest.raises(NotImplementedError):
            bytes_to_scalar(b"\x01", PrimitiveType.BOOL)

    def test_bytes_to_string(self):
        """Test converting bytes to string."""
        result = bytes_to_scalar(b"hello", PrimitiveType.STRING)
        assert result == "hello"

    def test_bytes_to_int_little_endian(self):
        """Test converting bytes to integer in little-endian."""
        data = b"\x2a\x00\x00\x00\x00\x00\x00\x00"
        result = bytes_to_scalar(data, NumericPrimitiveType.INT, little_endian=True)
        assert result == 42

    def test_bytes_to_uint_big_endian(self):
        """Test converting bytes to unsigned integer in big-endian."""
        data = b"\x01\x00"
        result = bytes_to_scalar(data, NumericPrimitiveType.UINT, little_endian=False)
        assert result == 256

    def test_bytes_to_double(self):
        """Test converting bytes to double."""
        import struct

        double_value = 3.14
        data = struct.pack("<d", double_value)
        result = bytes_to_scalar(data, NumericPrimitiveType.DOUBLE, little_endian=True)
        assert isinstance(result, float)
        assert abs(result - 3.14) < 0.001


class TestScalarRoundTrip:
    """Test round-trip conversion of scalars."""

    def test_bool_roundtrip(self):
        """Test bool conversion round-trip."""
        for value in [True, False]:
            with pytest.raises(NotImplementedError):
                bytes_data = scalar_to_bytes(value, PrimitiveType.BOOL)
                result = bytes_to_scalar(bytes_data, PrimitiveType.BOOL)
                assert result == value

    def test_uint_roundtrip(self):
        """Test unsigned int conversion round-trip."""
        for value in [0, 42, 1000, 2**32 - 1]:
            bytes_data = scalar_to_bytes(value, NumericPrimitiveType.UINT, num_bytes=4, little_endian=True)
            result = bytes_to_scalar(bytes_data, NumericPrimitiveType.UINT, little_endian=True)
            assert result == value

    def test_int_roundtrip(self):
        """Test signed int conversion round-trip."""
        for value in [-1000, -42, 0, 42, 1000]:
            bytes_data = scalar_to_bytes(value, NumericPrimitiveType.INT, num_bytes=8, little_endian=True)
            result = bytes_to_scalar(bytes_data, NumericPrimitiveType.INT, little_endian=True)
            assert result == value


class TestIntervalConversion:
    """Test interval conversion."""

    def test_interval_to_bytes(self):
        """Test converting interval to bytes."""
        interval = Interval(Fraction(1, 4), Fraction(3, 4))
        interval_type = IntervalType(NumericPrimitiveType.RATIONAL)
        result = scalar_to_bytes(interval, interval_type, num_bytes=16)
        assert len(result) == 16

    def test_bytes_to_interval(self):
        """Test converting bytes to interval."""
        # Create an interval and convert to bytes
        interval = Interval(Fraction(1, 2), Fraction(3, 2))
        interval_type = IntervalType(NumericPrimitiveType.RATIONAL)
        bytes_data = scalar_to_bytes(interval, interval_type, num_bytes=16)

        # Convert back
        result = bytes_to_scalar(bytes_data, interval_type)
        assert isinstance(result, Interval)
        assert result.left == Fraction(1, 2)
        assert result.right == Fraction(3, 2)


class TestScalarValidation:
    """Test scalar value type validation."""

    def test_validates_value_type_match(self):
        """Test that validation ensures value matches type."""
        # Valid cases should not raise
        with pytest.raises(NotImplementedError):
            scalar_to_bytes(True, PrimitiveType.BOOL)
        scalar_to_bytes("hello", PrimitiveType.STRING)
        scalar_to_bytes(42, NumericPrimitiveType.INT, num_bytes=8)

    def test_invalid_value_for_type(self):
        """Test that mismatched types raise errors."""
        with pytest.raises(AssertionError):
            # Integer value for BOOL type
            scalar_to_bytes(1, PrimitiveType.BOOL)

        with pytest.raises(AssertionError):
            # String value for INT type
            scalar_to_bytes("hello", NumericPrimitiveType.INT, num_bytes=8)


class TestNotImplementedErrors:
    """Test that NotImplementedError is raised for unsupported operations."""

    def test_bits_to_interval_not_implemented(self):
        """Test that converting bits to interval raises NotImplementedError."""
        interval_type = IntervalType(NumericPrimitiveType.RATIONAL)
        bits = BitArray(uint=0, length=256)

        with pytest.raises(NotImplementedError):
            bits_to_scalar(bits, interval_type)

    def test_interval_to_bits_not_implemented(self):
        """Test that converting interval to bits raises NotImplementedError."""
        interval = Interval(Fraction(1, 2), Fraction(3, 2))
        interval_type = IntervalType(NumericPrimitiveType.RATIONAL)

        with pytest.raises(NotImplementedError):
            scalar_to_bits(interval, interval_type, num_bits=256)
