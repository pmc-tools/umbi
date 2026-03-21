"""Tests for umbi.binary.numeric_primitive module."""

import pytest
from fractions import Fraction
from bitstring import BitArray

from umbi.binary.numeric_primitive import (
    bytes_to_double,
    double_to_bytes,
    bits_to_double,
    double_to_bits,
    bytes_to_integer,
    integer_to_bytes,
    bits_to_integer,
    integer_to_bits,
    bytes_to_rational,
    rational_to_bytes,
    bits_to_rational,
    rational_to_bits,
    normalize_rational,
    bytes_to_numeric_primitive,
    numeric_primitive_to_bytes,
    bits_to_numeric_primitive,
    numeric_primitive_to_bits,
)
from umbi.datatypes import NumericPrimitiveType


class TestDoubleConversion:
    """Test double (float) conversion functions."""

    def test_double_to_bytes_little_endian(self):
        """Test converting double to bytes in little-endian."""
        value = 3.14
        result = double_to_bytes(value, little_endian=True)
        assert len(result) == 8
        assert isinstance(result, bytes)

    def test_double_to_bytes_big_endian(self):
        """Test converting double to bytes in big-endian."""
        value = 3.14
        result = double_to_bytes(value, little_endian=False)
        assert len(result) == 8

    def test_bytes_to_double_little_endian(self):
        """Test converting bytes to double in little-endian."""
        original = 3.14159
        data = double_to_bytes(original, little_endian=True)
        result = bytes_to_double(data, little_endian=True)
        assert abs(result - original) < 0.00001

    def test_bytes_to_double_big_endian(self):
        """Test converting bytes to double in big-endian."""
        original = 2.71828
        data = double_to_bytes(original, little_endian=False)
        result = bytes_to_double(data, little_endian=False)
        assert abs(result - original) < 0.00001

    def test_double_to_bits(self):
        """Test converting double to bits."""
        value = 1.5
        bits = double_to_bits(value)
        assert len(bits) == 64

    def test_bits_to_double(self):
        """Test converting bits to double."""
        original = 2.5
        bits = double_to_bits(original)
        result = bits_to_double(bits)
        assert abs(result - original) < 0.00001

    def test_double_roundtrip(self):
        """Test roundtrip conversion for doubles."""
        test_values = [0.0, 1.0, -1.0, 3.14159, -2.71828, 1e-10, 1e10]
        for value in test_values:
            data = double_to_bytes(value, little_endian=True)
            result = bytes_to_double(data, little_endian=True)
            assert abs(result - value) < 1e-10


class TestIntegerConversion:
    """Test integer conversion functions."""

    def test_integer_to_bytes_unsigned(self):
        """Test converting unsigned integer to bytes."""
        result = integer_to_bytes(256, num_bytes=2, signed=False, little_endian=True)
        assert result == b"\x00\x01"

    def test_integer_to_bytes_signed_positive(self):
        """Test converting positive signed integer to bytes."""
        result = integer_to_bytes(42, num_bytes=1, signed=True, little_endian=True)
        assert len(result) == 1

    def test_integer_to_bytes_signed_negative(self):
        """Test converting negative signed integer to bytes."""
        result = integer_to_bytes(-1, num_bytes=1, signed=True, little_endian=True)
        assert result == b"\xff"

    def test_bytes_to_integer_unsigned_little_endian(self):
        """Test converting bytes to unsigned integer in little-endian."""
        result = bytes_to_integer(b"\x00\x01", signed=False, little_endian=True)
        assert result == 256

    def test_bytes_to_integer_unsigned_big_endian(self):
        """Test converting bytes to unsigned integer in big-endian."""
        result = bytes_to_integer(b"\x01\x00", signed=False, little_endian=False)
        assert result == 256

    def test_bytes_to_integer_signed(self):
        """Test converting bytes to signed integer."""
        result = bytes_to_integer(b"\xff", signed=True, little_endian=True)
        assert result == -1

    def test_integer_to_bits_signed(self):
        """Test converting signed integer to bits."""
        bits = integer_to_bits(42, num_bits=8, signed=True)
        assert len(bits) == 8
        assert bits_to_integer(bits, signed=True) == 42

    def test_integer_to_bits_unsigned(self):
        """Test converting unsigned integer to bits."""
        bits = integer_to_bits(255, num_bits=8, signed=False)
        assert len(bits) == 8
        assert bits_to_integer(bits, signed=False) == 255

    def test_bits_to_integer_signed(self):
        """Test converting bits to signed integer."""
        bits = BitArray(int=-42, length=8)
        result = bits_to_integer(bits, signed=True)
        assert result == -42

    def test_bits_to_integer_unsigned(self):
        """Test converting bits to unsigned integer."""
        bits = BitArray(uint=200, length=8)
        result = bits_to_integer(bits, signed=False)
        assert result == 200

    def test_integer_roundtrip(self):
        """Test roundtrip conversion for integers."""
        test_values = [0, 1, -1, 127, -128, 255, 256, -256, 1000000]
        for value in test_values:
            signed = value < 0 or value > 255
            num_bytes = 8 if signed else 4
            data = integer_to_bytes(value, num_bytes, signed=True, little_endian=True)
            result = bytes_to_integer(data, signed=True, little_endian=True)
            assert result == value

    def test_integer_overflow(self):
        """Test that integer overflow is caught."""
        with pytest.raises(OverflowError):
            integer_to_bytes(256, num_bytes=1, signed=False)


class TestRationalConversion:
    """Test rational (fraction) conversion functions."""

    def test_normalize_rational_positive(self):
        """Test normalizing a rational with positive denominator."""
        frac = Fraction(1, 2)
        result = normalize_rational(frac)
        assert result.denominator > 0

    def test_normalize_rational_negative_denominator(self):
        """Test normalizing a rational with negative denominator."""
        frac = Fraction(1, -2)
        result = normalize_rational(frac)
        assert result.denominator > 0
        assert result == Fraction(-1, 2)

    def test_rational_to_bytes(self):
        """Test converting rational to bytes."""
        frac = Fraction(1, 2)
        result = rational_to_bytes(frac, num_bytes=16, little_endian=True)
        assert len(result) == 16

    def test_bytes_to_rational(self):
        """Test converting bytes to rational."""
        original = Fraction(3, 4)
        data = rational_to_bytes(original, num_bytes=16, little_endian=True)
        result = bytes_to_rational(data, little_endian=True)
        assert result == original

    def test_rational_to_bits(self):
        """Test converting rational to bits."""
        frac = Fraction(2, 3)
        bits = rational_to_bits(frac, num_bits=64)
        assert len(bits) == 64

    def test_bits_to_rational(self):
        """Test converting bits to rational."""
        original = Fraction(5, 7)
        bits = rational_to_bits(original, num_bits=64)
        result = bits_to_rational(bits)
        assert result == original

    def test_rational_roundtrip(self):
        """Test roundtrip conversion for rationals."""
        test_values = [
            Fraction(0, 1),
            Fraction(1, 1),
            Fraction(1, 2),
            Fraction(-1, 2),
            Fraction(22, 7),
            Fraction(1, 3),
        ]
        for value in test_values:
            data = rational_to_bytes(value, num_bytes=16, little_endian=True)
            result = bytes_to_rational(data, little_endian=True)
            assert result == value

    def test_rational_even_bytes_required(self):
        """Test that even number of bytes is required."""
        frac = Fraction(1, 2)
        with pytest.raises(AssertionError):
            rational_to_bytes(frac, num_bytes=15, little_endian=True)


class TestNumericPrimitiveAPI:
    """Test the public API functions."""

    def test_bytes_to_numeric_primitive_int(self):
        """Test converting bytes to numeric primitive INT."""
        data = integer_to_bytes(42, 8, signed=True, little_endian=True)
        result = bytes_to_numeric_primitive(data, NumericPrimitiveType.INT, little_endian=True)
        assert result == 42

    def test_bytes_to_numeric_primitive_uint(self):
        """Test converting bytes to numeric primitive UINT."""
        data = integer_to_bytes(42, 8, signed=False, little_endian=True)
        result = bytes_to_numeric_primitive(data, NumericPrimitiveType.UINT, little_endian=True)
        assert result == 42

    def test_bytes_to_numeric_primitive_double(self):
        """Test converting bytes to numeric primitive DOUBLE."""
        data = double_to_bytes(3.14, little_endian=True)
        result = bytes_to_numeric_primitive(data, NumericPrimitiveType.DOUBLE, little_endian=True)
        assert abs(result - 3.14) < 0.01

    def test_bytes_to_numeric_primitive_rational(self):
        """Test converting bytes to numeric primitive RATIONAL."""
        frac = Fraction(1, 2)
        data = rational_to_bytes(frac, num_bytes=16, little_endian=True)
        result = bytes_to_numeric_primitive(data, NumericPrimitiveType.RATIONAL, little_endian=True)
        assert result == frac

    def test_numeric_primitive_to_bytes_int(self):
        """Test converting numeric primitive INT to bytes."""
        result = numeric_primitive_to_bytes(42, NumericPrimitiveType.INT, num_bytes=8, little_endian=True)
        assert len(result) == 8

    def test_numeric_primitive_to_bytes_uint(self):
        """Test converting numeric primitive UINT to bytes."""
        result = numeric_primitive_to_bytes(42, NumericPrimitiveType.UINT, num_bytes=8, little_endian=True)
        assert len(result) == 8

    def test_numeric_primitive_to_bytes_double(self):
        """Test converting numeric primitive DOUBLE to bytes."""
        result = numeric_primitive_to_bytes(3.14, NumericPrimitiveType.DOUBLE, num_bytes=8, little_endian=True)
        assert len(result) == 8

    def test_numeric_primitive_to_bytes_rational(self):
        """Test converting numeric primitive RATIONAL to bytes."""
        frac = Fraction(1, 2)
        result = numeric_primitive_to_bytes(frac, NumericPrimitiveType.RATIONAL, num_bytes=16, little_endian=True)
        assert len(result) == 16

    def test_bits_to_numeric_primitive_int(self):
        """Test converting bits to numeric primitive INT."""
        bits = BitArray(int=42, length=64)
        result = bits_to_numeric_primitive(bits, NumericPrimitiveType.INT)
        assert result == 42

    def test_numeric_primitive_to_bits_int(self):
        """Test converting numeric primitive INT to bits."""
        bits = numeric_primitive_to_bits(42, NumericPrimitiveType.INT, num_bits=64)
        assert len(bits) == 64
        assert bits_to_numeric_primitive(bits, NumericPrimitiveType.INT) == 42
