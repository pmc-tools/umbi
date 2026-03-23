"""Definitions and utilities for scalar types associated with fixed size."""

from collections.abc import Collection
from dataclasses import dataclass
from fractions import Fraction

from umbi.datatypes import (
    Interval,
    IntervalType,
    NumericPrimitive,
    NumericPrimitiveType,
    Primitive,
    PrimitiveType,
    Scalar,
    ScalarType,
    scalar_type_dispatch,
    validate_scalar_value_type,
)

# Sized type definitions


@dataclass(frozen=True)
class SizedType:
    """Represents a scalar type with an associated size in bits."""

    #: the scalar type
    type: ScalarType
    #: the size in bits for this type (must be positive and valid for the type)
    size_bits: int

    @classmethod
    def for_type(cls, type: ScalarType) -> "SizedType":
        """Create a SizedType for a given scalar type, using the default size if not provided."""
        return cls(type, scalar_type_default_bitsize(type))

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


# Default bitsizes for types


def primitive_type_default_bitsize(type: PrimitiveType) -> int:
    """Get the default size in bits for a primitive type."""
    return {
        PrimitiveType.BOOL: 1,
        PrimitiveType.STRING: 64,  # strings are represented as UINT64 index to the list of string values
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
    return scalar_type_dispatch(
        type,
        on_primitive=lambda t: primitive_type_default_bitsize(t),
        on_numeric=lambda t: numeric_primitive_type_default_bitsize(t),
        on_interval=lambda t: interval_type_default_bitsize(t),
    )


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
    return scalar_type_dispatch(
        type,
        on_primitive=lambda t: validate_primitive_type_size(t, size),
        on_numeric=lambda t: validate_numeric_primitive_type_size(t, size),
        on_interval=lambda t: validate_interval_type_size(t, size),
    )


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
    # should not be needed in umbi
    raise NotImplementedError("num_bits_for_interval is not implemented yet")
    # left_bits = num_bits_for_numeric_primitive(value.left, value_type.base_type)
    # right_bits = num_bits_for_numeric_primitive(value.right, value_type.base_type)
    # return max(left_bits, right_bits) * 2


def num_bits_for_scalar(value: Scalar, value_type: ScalarType) -> int:
    """Calculate the number of bits needed to represent a scalar value."""
    validate_scalar_value_type(value, value_type)
    return scalar_type_dispatch(
        value_type,
        on_primitive=lambda vt: num_bits_for_primitive(value, vt),  # type: ignore[argument]
        on_numeric=lambda vt: num_bits_for_numeric_primitive(value, vt),  # type: ignore[argument]
        on_interval=lambda vt: num_bits_for_interval(value, vt),  # type: ignore[argument]
    )


# Size computation for sequences


def max_num_bits_for_collection_element(values: Collection[Scalar], value_type: ScalarType) -> int:
    """Calculate the number of bits needed to represent an element of a sequence."""
    assert len(values) > 0, "cannot compute max bitsize for an empty sequence"
    return max(num_bits_for_scalar(v, value_type) for v in values)


# Aliases for common sized types used in umbi

#: a single bit
BOOL1 = SizedType(PrimitiveType.BOOL, 1)
#: uint32
UINT32 = SizedType(NumericPrimitiveType.UINT, 32)
#: uint64
UINT64 = SizedType(NumericPrimitiveType.UINT, 64)
