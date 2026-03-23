"""(De)serializers for numeric primitive types."""

import struct
from fractions import Fraction

from bitstring import BitArray

from umbi.datatypes import NumericPrimitive, NumericPrimitiveType

from .utils import split_bits_half, split_bytes_half

# Floats


def bytes_to_double(data: bytes, little_endian: bool = True) -> float:
    """Convert a bytestring to a double."""
    ef = "<" if little_endian else ">"
    return struct.unpack(f"{ef}d", data)[0]


def double_to_bytes(value: float, little_endian: bool = True) -> bytes:
    """Convert a double to a bytestring."""
    ef = "<" if little_endian else ">"
    return struct.pack(f"{ef}d", value)


def bits_to_double(bits: BitArray) -> float:
    """Convert bitstring to a double."""
    assert len(bits) == 64, "double must be represented with 64 bits"
    return bits.float


def double_to_bits(value: float) -> BitArray:
    """Convert a double to a bitstring."""
    return BitArray(float=value, length=64)


# Integers


def bytes_to_integer(data: bytes, signed: bool = True, little_endian: bool = True) -> int:
    """Convert a bytestring to an integer."""
    return int.from_bytes(data, byteorder="little" if little_endian else "big", signed=signed)


def integer_to_bytes(value: int, num_bytes: int, signed: bool = True, little_endian: bool = True) -> bytes:
    """
    Convert an integer to a bytestring.
    :raises OverflowError if the integer cannot be represented in the given number of bytes.
    """
    return value.to_bytes(num_bytes, byteorder="little" if little_endian else "big", signed=signed)


def bits_to_integer(bits: BitArray, signed: bool = True) -> int:
    """Convert a bitstring to an integer."""
    if signed:
        return bits.int
    else:
        return bits.uint


def integer_to_bits(value: int, num_bits: int, signed: bool = True) -> BitArray:
    """
    Convert an integer to a bitstring.
    :raises ValueError if the integer cannot be represented in the given number of bits.
    """
    if signed:
        return BitArray(int=value, length=num_bits)
    else:
        return BitArray(uint=value, length=num_bits)


# Rationals
# Convention: a normalized rational has a non-negative denominator.
# Rationals are represented as two integers of equal lengths: a signed numerator and an unsigned denominator.


def normalize_rational(value: Fraction) -> Fraction:
    """Ensure that the denominator of a fraction is non-negative."""
    if value.denominator < 0:
        value = Fraction(-value.numerator, -value.denominator)
    return value


def bytes_to_rational(data: bytes, little_endian: bool = True) -> Fraction:
    """Convert a bytestring to a fraction."""
    numerator_bytes, denominator_bytes = split_bytes_half(data)
    numerator = bytes_to_integer(numerator_bytes, signed=True, little_endian=little_endian)
    denominator = bytes_to_integer(denominator_bytes, signed=False, little_endian=little_endian)
    return Fraction(numerator, denominator)


def rational_to_bytes(value: Fraction, num_bytes: int, little_endian: bool = True) -> bytes:
    """Convert a fraction to a bytestring."""
    value = normalize_rational(value)
    assert num_bytes % 2 == 0, "num_bytes must be even to encode both numerator and denominator"
    term_size_bytes = num_bytes // 2
    numerator_bytes = integer_to_bytes(
        value.numerator, num_bytes=term_size_bytes, signed=True, little_endian=little_endian
    )
    denominator_bytes = integer_to_bytes(
        value.denominator,
        num_bytes=term_size_bytes,
        signed=False,
        little_endian=little_endian,
    )
    return numerator_bytes + denominator_bytes


def bits_to_rational(bits: BitArray) -> Fraction:
    """Convert a bitstring to a fraction."""
    numerator_bits, denominator_bits = split_bits_half(bits)
    numerator = bits_to_integer(numerator_bits, signed=True)
    denominator = bits_to_integer(denominator_bits, signed=False)
    return Fraction(numerator, denominator)


def rational_to_bits(value: Fraction, num_bits: int) -> BitArray:
    """Convert a fraction to a bitstring."""
    value = normalize_rational(value)
    assert num_bits % 2 == 0, "num_bits must be even to encode both numerator and denominator"
    term_num_bits = num_bits // 2
    numerator_bits = integer_to_bits(value.numerator, term_num_bits, signed=True)
    denominator_bits = integer_to_bits(value.denominator, term_num_bits, signed=False)
    return numerator_bits + denominator_bits


# API


def bytes_to_numeric_primitive(data: bytes, value_type: NumericPrimitiveType, little_endian: bool = True):
    """Convert a bytestring to a numeric primitive value."""
    return {
        NumericPrimitiveType.INT: lambda b: bytes_to_integer(b, signed=True, little_endian=little_endian),
        NumericPrimitiveType.UINT: lambda b: bytes_to_integer(b, signed=False, little_endian=little_endian),
        NumericPrimitiveType.DOUBLE: lambda b: bytes_to_double(b, little_endian=little_endian),
        NumericPrimitiveType.RATIONAL: lambda b: bytes_to_rational(b, little_endian=little_endian),
    }[value_type](data)


def numeric_primitive_to_bytes(
    value: NumericPrimitive, value_type: NumericPrimitiveType, num_bytes: int, little_endian: bool = True
) -> bytes:
    """Convert a numeric primitive value to a bytestring."""
    return {
        NumericPrimitiveType.INT: lambda v: integer_to_bytes(v, num_bytes, signed=True, little_endian=little_endian),
        NumericPrimitiveType.UINT: lambda v: integer_to_bytes(v, num_bytes, signed=False, little_endian=little_endian),
        NumericPrimitiveType.DOUBLE: lambda v: double_to_bytes(v, little_endian=little_endian),
        NumericPrimitiveType.RATIONAL: lambda v: rational_to_bytes(v, num_bytes, little_endian=little_endian),
    }[value_type](value)


def bits_to_numeric_primitive(bits: BitArray, value_type: NumericPrimitiveType) -> NumericPrimitive:
    """Convert a bitstring to a numeric primitive value."""
    return {
        NumericPrimitiveType.INT: lambda b: bits_to_integer(b, signed=True),
        NumericPrimitiveType.UINT: lambda b: bits_to_integer(b, signed=False),
        NumericPrimitiveType.DOUBLE: bits_to_double,
        NumericPrimitiveType.RATIONAL: bits_to_rational,
    }[value_type](bits)


def numeric_primitive_to_bits(value: NumericPrimitive, value_type: NumericPrimitiveType, num_bits: int) -> BitArray:
    """Convert a numeric primitive value to a bitstring."""
    return {
        NumericPrimitiveType.INT: lambda v: integer_to_bits(v, num_bits, signed=True),
        NumericPrimitiveType.UINT: lambda v: integer_to_bits(v, num_bits, signed=False),
        NumericPrimitiveType.DOUBLE: double_to_bits,
        NumericPrimitiveType.RATIONAL: lambda v: rational_to_bits(v, num_bits),
    }[value_type](value)
