"""(De)serialization for scalar types."""

from bitstring import BitArray

from umbi.datatypes import (
    Interval,
    IntervalType,
    PrimitiveType,
    Scalar,
    ScalarType,
    scalar_type_dispatch,
    validate_scalar_value_type,
)

from .numeric_primitive import (
    bits_to_numeric_primitive,
    bytes_to_numeric_primitive,
    numeric_primitive_to_bits,
    numeric_primitive_to_bytes,
)
from .primitive import (
    bits_to_primitive,
    bytes_to_primitive,
    primitive_to_bits,
    primitive_to_bytes,
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
    # should not be needed in umbi
    raise NotImplementedError("converting bitstrings to intervals is not supported")


def interval_to_bits(interval: Interval, value_type: IntervalType, num_bits: int) -> BitArray:
    """Convert an interval to a bitstring."""
    # should not be needed in umbi
    raise NotImplementedError("converting intervals to bitstrings is not supported")


# Dispatcher for the API


# API


def bytes_to_scalar(data: bytes, value_type: ScalarType, little_endian: bool = True) -> Scalar:
    """Convert a binary string to a single value of the given common type."""
    return scalar_type_dispatch(
        value_type,
        on_primitive=lambda vt: bytes_to_primitive(data, vt),
        on_numeric=lambda vt: bytes_to_numeric_primitive(data, vt, little_endian),
        on_interval=lambda vt: bytes_to_interval(data, vt, little_endian),
    )


def scalar_to_bytes(
    value: Scalar, value_type: ScalarType, num_bytes: int | None = None, little_endian: bool = True
) -> bytes:
    """Convert a scalar to a bytestring."""
    validate_scalar_value_type(value, value_type)
    if num_bytes is None:
        assert isinstance(value_type, PrimitiveType), "num_bytes can be None only for PrimitiveType"
    return scalar_type_dispatch(
        value_type,
        on_primitive=lambda vt: primitive_to_bytes(value, vt),  # type: ignore[argument]
        on_numeric=lambda vt: numeric_primitive_to_bytes(value, vt, num_bytes, little_endian),  # type: ignore[argument]
        on_interval=lambda vt: interval_to_bytes(value, vt, num_bytes, little_endian),  # type: ignore[argument]
    )


def bits_to_scalar(bits: BitArray, value_type: ScalarType) -> Scalar:
    """Convert a BitArray to a single value of the given common type."""
    return scalar_type_dispatch(
        value_type,
        on_primitive=lambda vt: bits_to_primitive(bits, vt),
        on_numeric=lambda vt: bits_to_numeric_primitive(bits, vt),
        on_interval=lambda vt: bits_to_interval(bits, vt),
    )


def scalar_to_bits(value: Scalar, value_type: ScalarType, num_bits: int) -> BitArray:
    """Convert a scalar to a bitstring."""
    validate_scalar_value_type(value, value_type)
    return scalar_type_dispatch(
        value_type,
        on_primitive=lambda vt: primitive_to_bits(value, vt, num_bits),  # type: ignore[argument]
        on_numeric=lambda vt: numeric_primitive_to_bits(value, vt, num_bits),  # type: ignore[argument]
        on_interval=lambda vt: interval_to_bits(value, vt, num_bits),  # type: ignore[argument]
    )
