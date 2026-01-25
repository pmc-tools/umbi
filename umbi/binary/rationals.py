"""
Utilities for (de)serializing fractions.
"""

from fractions import Fraction

from .integers import (
    num_bytes_for_integer,
    integer_to_bytes,
    bytes_to_integer,
)
from .utils import split_bytes_half
from bitstring import BitArray

# Convention: a normalized rational has a non-negative denominator.
# Rationals are represented as two integers of equal lengths: a signed numerator and an unsigned denominator.


def normalize_rational(value: Fraction) -> Fraction:
    """Ensure that the denominator of a fraction is non-negative."""
    if value.denominator < 0:
        value = Fraction(-value.numerator, -value.denominator)
    return value


# def num_bits_for_rational(value: Fraction) -> int:
#     """Calculate the number of bits needed to represent a rational number."""
#     numerator_size = num_bits_for_integer(value.numerator, signed=True, round_to_8=False)
#     denominator_size = num_bits_for_integer(value.denominator, signed=False, round_to_8=False)
#     total_size = max(numerator_size, denominator_size) * 2
#     return total_size


def num_bytes_for_rational(value: Fraction) -> int:
    """Calculate the number of bytes needed to represent a rational number."""
    # rounding up to a number of bytes of multiple of 8
    numerator_size = num_bytes_for_integer(value.numerator, signed=True, round_to_8=True)
    denominator_size = num_bytes_for_integer(value.denominator, signed=False, round_to_8=True)
    return max(numerator_size, denominator_size) * 2


def bytes_to_rational(data: bytes, little_endian: bool = True) -> Fraction:
    """Convert a bytestring to a fraction. The bytestring must have even length, with the first half representing the numerator as a signed integer and the second half representing the denominator as an unsigned integer."""
    numerator_bytes, denominator_bytes = split_bytes_half(data)
    numerator = bytes_to_integer(numerator_bytes, signed=True, little_endian=little_endian)
    denominator = bytes_to_integer(denominator_bytes, signed=False, little_endian=little_endian)
    return Fraction(numerator, denominator)


def rational_to_bytes(value: Fraction, term_size_bytes: int, little_endian: bool = True) -> bytes:
    """
    Convert a fraction to a bytestring. Both numberator and denominator are encoded as signed and unsigned integers, respectively, and have the same size.
    :param term_size: maximum size in bytes for numerator/denominator
    """
    value = normalize_rational(value)
    minimal_term_size = num_bytes_for_rational(value) // 2
    if term_size_bytes < minimal_term_size:
        raise ValueError(
            f"term_size {term_size_bytes} is too small to represent the rational {value}, which requires at least {minimal_term_size} bytes per term"
        )
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
    assert len(bits) % 8 == 0, "rational bit length must be a multiple of 8"
    # rational are always byte-alignd
    bytestring = bits.tobytes()
    return bytes_to_rational(bytestring)


def rational_to_bits(value: Fraction, term_size_bytes: int) -> BitArray:
    bytestring = rational_to_bytes(value, term_size_bytes=term_size_bytes)
    return BitArray(bytestring)
