"""Type definitions for sized scalar types."""

from umbi.datatypes import (
    Primitive,
    PrimitiveType,
    NumericPrimitive,
    NumericPrimitiveType,
    Interval,
    IntervalType,
    Scalar,
    ScalarType,
)

from collections.abc import Sequence
from fractions import Fraction
from dataclasses import dataclass

# Sized type definitions


@dataclass
class SizedType:
    """
    Represents a scalar type with an associated size in bits.
    """

    type: ScalarType
    size_bits: int  # size in bits

    def __init__(self, type: ScalarType, size_bits: int | None = None) -> None:
        self.type = type
        if size_bits is None:
            size_bits = scalar_type_default_bitsize(type)
        self.size_bits = size_bits

    def __post_init__(self):
        self.validate()

    def validate(self):
        assert self.size_bits > 0, "size must be positive"
        validate_scalar_type_size(self.type, self.size_bits)

    @property
    def is_byte_aligned(self) -> bool:
        return self.size_bits % 8 == 0

    @property
    def size_bytes(self) -> int:
        return (self.size_bits + 7) // 8  # ceiling division


# Common sized types used in umbi

BOOL1 = SizedType(PrimitiveType.BOOL, 1)
UINT32 = SizedType(NumericPrimitiveType.UINT, 32)
UINT64 = SizedType(NumericPrimitiveType.UINT, 64)


# Default bitsizes for types


def primitive_type_default_bitsize(type: PrimitiveType) -> int:
    """Get the default size in bits for a primitive type."""
    return {
        PrimitiveType.BOOL: 1,
        PrimitiveType.STRING: 64,
    }[type]


def numeric_primitive_type_default_bitsize(type: NumericPrimitiveType) -> int:
    """Get the default size in bits for a numeric primitive type."""
    return {
        NumericPrimitiveType.INT: 64,
        NumericPrimitiveType.UINT: 64,
        NumericPrimitiveType.DOUBLE: 64,
        NumericPrimitiveType.RATIONAL: 128,
    }[type]


def interval_type_default_bitsize(type: IntervalType) -> int:
    """Get the default size in bits for an interval type."""
    return 2 * numeric_primitive_type_default_bitsize(type.base_type)


def scalar_type_default_bitsize(type: ScalarType) -> int:
    """Get the default size in bits for a scalar type."""
    if isinstance(type, PrimitiveType):
        return primitive_type_default_bitsize(type)
    elif isinstance(type, NumericPrimitiveType):
        return numeric_primitive_type_default_bitsize(type)
    else:  # isinstance(type, IntervalType)
        return interval_type_default_bitsize(type)


def primitive_smallest_bitsize(type: PrimitiveType) -> int:
    """Get the default size in bits for a given primitive type."""
    return primitive_type_default_bitsize(type)


# Scalar type size validation


def validate_primitive_type_size(type: PrimitiveType, size: int) -> None:
    """Validate that a size is valid for a primitive type."""
    if type == PrimitiveType.STRING:
        if size != 64:
            raise ValueError(f"{type.value} size must be 64")


def validate_numeric_primitive_type_size(type: NumericPrimitiveType, size: int) -> None:
    """Validate that a size is valid for a numeric primitive type."""
    if type == NumericPrimitiveType.DOUBLE:
        if size != 64:
            raise ValueError(f"{type.value} size must be 64")
    if type == NumericPrimitiveType.RATIONAL:
        if size % 2 != 0:
            raise ValueError(f"{type.value} size must be a multiple of 2")


def validate_interval_type_size(type: IntervalType, size: int) -> None:
    """Validate that a size is valid for an interval type."""
    if size % 2 != 0:
        raise ValueError(f"{str(type)} size must be a multiple of 2")
    if type.base_type == NumericPrimitiveType.RATIONAL and size % 4 != 0:
        raise ValueError(f"{str(type)} size must be a multiple of 4")


def validate_scalar_type_size(type: ScalarType, size: int) -> None:
    """Validate that a size is valid for a scalar type."""
    if isinstance(type, PrimitiveType):
        validate_primitive_type_size(type, size)
    elif isinstance(type, NumericPrimitiveType):
        validate_numeric_primitive_type_size(type, size)
    else:  # isinstance(type, IntervalType)
        validate_interval_type_size(type, size)


# Size computation for values


def num_bits_for_primitive(value: Primitive, type: PrimitiveType) -> int:
    """Calculate the number of bits needed to represent a primitive value."""
    return primitive_type_default_bitsize(type)


def num_bits_for_integer(value: int, signed: bool = True, round_to_8: bool = True) -> int:
    """
    Return the number of bits needed to represent an integer value.
    :param signed: if True, the integer is signed
    :param round_to_8: if True, the number of bits is rounded up to the nearest multiple of 8
    """
    if not signed:
        num_bits = value.bit_length()
    else:
        if value >= 0:
            num_bits = value.bit_length()
        else:
            num_bits = (-value - 1).bit_length()
        num_bits += 1  # add sign bit
    if round_to_8 and num_bits % 8 != 0:
        num_bits += 8 - (num_bits % 8)
    return num_bits


def num_bits_for_numeric_primitive(value: NumericPrimitive, value_type: NumericPrimitiveType) -> int:
    """Calculate the number of bits needed to represent a numeric primitive value."""
    if value_type == NumericPrimitiveType.INT or value_type == NumericPrimitiveType.UINT:
        assert isinstance(value, int), f"expected an int value, got {type(value)}"
        return num_bits_for_integer(value, signed=(value_type == NumericPrimitiveType.INT), round_to_8=False)
    elif value_type == NumericPrimitiveType.DOUBLE:
        return numeric_primitive_type_default_bitsize(value_type)
    else:  # value_type == NumericPrimitiveType.RATIONAL
        assert isinstance(value, Fraction), f"expected a Fraction, got {type(value)}"
        numerator_bits = num_bits_for_integer(value.numerator, signed=True, round_to_8=True)
        denominator_bits = num_bits_for_integer(value.denominator, signed=False, round_to_8=True)
        return max(numerator_bits, denominator_bits) * 2


def num_bits_for_interval(value: Interval, value_type: IntervalType) -> int:
    """Calculate the number of bits needed to represent an interval value."""
    left_bits = num_bits_for_numeric_primitive(value.left, value_type.base_type)
    right_bits = num_bits_for_numeric_primitive(value.right, value_type.base_type)
    return max(left_bits, right_bits) * 2


def num_bits_for_scalar(value: Scalar, value_type: ScalarType) -> int:
    """Calculate the number of bits needed to represent a scalar value."""
    if isinstance(value_type, PrimitiveType):
        assert isinstance(value, Primitive), f"expected a primitive value for type {value_type}, got {type(value)}"
        return num_bits_for_primitive(value, value_type)
    elif isinstance(value_type, NumericPrimitiveType):
        assert isinstance(value, NumericPrimitive), (
            f"expected a numeric primitive value for type {value_type}, got {type(value)}"
        )
        return num_bits_for_numeric_primitive(value, value_type)
    else:  # isinstance(value_type, IntervalType):
        assert isinstance(value, Interval), f"expected an interval value for type {value_type}, got {type(value)}"
        return num_bits_for_interval(value, value_type)


# Size computation for sequences


def max_num_bits_for_sequence_element(values: Sequence[Scalar], value_type: ScalarType) -> int:
    """Calculate the number of bits needed to represent an element of a sequence."""
    assert len(values) > 0, "cannot compute max bitsize for an empty sequence"
    return max(num_bits_for_scalar(v, value_type) for v in values)


# def num_bytes_for_integer(value: int, signed: bool = True, round_to_8: bool = True) -> int:
#     """
#     Return the number of bytes needed to represent an integer value.
#     :param round_to_8: if True, the number of bytes is rounded up to the nearest multiple of 8
#     """
#     num_bytes = num_bits_for_integer(value, signed=signed, round_to_8=round_to_8) // 8  # round up to full bytes
#     if round_to_8 and num_bytes % 8 != 0:
#         num_bytes += 8 - (num_bytes % 8)
#     return num_bytes


# def num_bytes_for_rational(value: Fraction) -> int:
#     """Calculate the number of bytes needed to represent a rational number."""
#     # rounding up to a number of bytes of multiple of 8
#     numerator_size = num_bytes_for_integer(value.numerator, signed=True, round_to_8=True)
#     denominator_size = num_bytes_for_integer(value.denominator, signed=False, round_to_8=True)
#     return max(numerator_size, denominator_size) * 2
