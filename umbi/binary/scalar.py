"""(De)serialization for scalar types."""

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

from bitstring import BitArray

from .primitive import (
    bytes_to_primitive,
    primitive_to_bytes,
    bits_to_primitive,
    primitive_to_bits,
)
from .numeric_primitive import (
    bytes_to_numeric_primitive,
    numeric_primitive_to_bytes,
    bits_to_numeric_primitive,
    numeric_primitive_to_bits,
)
from .utils import split_bytes_half


# Intervals


def bytes_to_interval(data: bytes, value_type: IntervalType, little_endian: bool = True) -> Interval:
    """Convert a bytestring to an interval."""
    lower, upper = split_bytes_half(data)
    base_type = value_type.base_type
    lower = bytes_to_numeric_primitive(lower, base_type, little_endian)
    upper = bytes_to_numeric_primitive(upper, base_type, little_endian)
    return Interval(lower, upper)


def interval_to_bytes(
    interval: Interval, value_type: IntervalType, num_bytes: int, little_endian: bool = True
) -> bytes:
    """Convert an interval to a bytestring."""
    assert num_bytes % 2 == 0, "expected an even-sized num_bytes for interval"
    term_num_bytes = num_bytes // 2
    base_type = value_type.base_type
    lower = numeric_primitive_to_bytes(interval.left, base_type, term_num_bytes, little_endian)
    upper = numeric_primitive_to_bytes(interval.right, base_type, term_num_bytes, little_endian)
    return lower + upper


def bits_to_interval(bits: BitArray, value_type: IntervalType) -> Interval:
    """Convert a bitstring to an interval."""
    raise NotImplementedError("unpacking intervals from bitstrings is not supported in umbi")


def interval_to_bits(interval: Interval, value_type: IntervalType, num_bits: int) -> BitArray:
    """Convert an interval to a bitstring."""
    raise NotImplementedError("packing intervals into bitstrings is not supported in umbi")


# API


def bytes_to_scalar(data: bytes, value_type: ScalarType, little_endian: bool = True) -> Scalar:
    """Convert a binary string to a single value of the given common type."""
    if isinstance(value_type, PrimitiveType):
        return bytes_to_primitive(data, value_type)
    else:  # umbi.datatypes.is_numeric_type(value_type):
        if isinstance(value_type, NumericPrimitiveType):
            return bytes_to_numeric_primitive(data, value_type, little_endian=little_endian)
        else:  # umbi.datatypes.is_interval_type(value_type):
            assert isinstance(value_type, IntervalType), "expected an interval type"
            return bytes_to_interval(data, value_type, little_endian=little_endian)


def scalar_to_bytes(
    value: Scalar, value_type: ScalarType, num_bytes: int | None = None, little_endian: bool = True
) -> bytes:
    """
    Convert a scalar to a bytestring.
    :note: this method intentionally uses SizedType instead of ScalarType for ease of use outside this subpackage
    """
    # expected_type = {
    #     PrimitiveType: Primitive,
    #     NumericPrimitiveType: NumericPrimitive,
    #     IntervalType: Interval,
    # }[value_type.__class__]
    # assert isinstance(value, expected_type), f"expected a value of type {expected_type} for type {value_type}, got {type(value)}"
    if isinstance(value_type, PrimitiveType):
        # assert num_bytes is None, "num_bytes should not be provided for primitive types"
        assert isinstance(value, Primitive), "expected a primitive value"
        return primitive_to_bytes(value, value_type)
    else:  # umbi.datatypes.is_numeric_type(value_type):
        assert num_bytes is not None, "num_bytes must be provided for numeric types"
        if isinstance(value_type, NumericPrimitiveType):
            assert isinstance(value, NumericPrimitive), "expected a numeric value"
            return numeric_primitive_to_bytes(value, value_type, num_bytes, little_endian=little_endian)
        else:  # umbi.datatypes.is_interval_type(value_type):
            assert isinstance(value_type, IntervalType), "expected an interval type"
            assert isinstance(value, Interval), "expected an interval value"
            return interval_to_bytes(value, value_type, num_bytes, little_endian=little_endian)


def bits_to_scalar(bits: BitArray, value_type: ScalarType) -> Scalar:
    """Convert a BitArray to a single value of the given common type."""
    if isinstance(value_type, PrimitiveType):
        return bits_to_primitive(bits, value_type)
    else:  # umbi.datatypes.is_numeric_type(value_type):
        if isinstance(value_type, NumericPrimitiveType):
            return bits_to_numeric_primitive(bits, value_type)
        else:  # umbi.datatypes.is_interval_type(value_type):
            return bits_to_interval(bits, value_type)


def scalar_to_bits(value: Scalar, value_type: ScalarType, num_bits: int) -> BitArray:
    """Convert a scalar to a bitstring."""
    if isinstance(value_type, PrimitiveType):
        assert isinstance(value, Primitive), "expected a primitive value"
        return primitive_to_bits(value, value_type, num_bits)
    else:  # umbi.datatypes.is_numeric_type(value_type):
        if isinstance(value_type, NumericPrimitiveType):
            assert isinstance(value, NumericPrimitive), "expected a numeric value"
            return numeric_primitive_to_bits(value, value_type, num_bits)
        else:  # umbi.datatypes.is_interval_type(value_type):
            assert isinstance(value, Interval), "expected an interval value"
            # assert isinstance(value_type, IntervalType), "expected an interval type"
            return interval_to_bits(value, value_type, num_bits)


__all__ = [
    "bytes_to_scalar",
    "scalar_to_bytes",
    "bits_to_scalar",
    "scalar_to_bits",
]
