"""Utilities for (de)serializing intervals."""

from umbi.datatypes import SizedType, Interval, IntervalType, interval_base_type
from .utils import split_bytes_half

from .numeric_primitives import bytes_to_numeric_primitive, numeric_primitive_to_bytes


def bytes_to_interval(data: bytes, value_type: IntervalType, little_endian: bool = True) -> Interval:
    lower, upper = split_bytes_half(data)
    base_type = interval_base_type(value_type)
    lower = bytes_to_numeric_primitive(lower, base_type, little_endian)
    upper = bytes_to_numeric_primitive(upper, base_type, little_endian)
    return Interval(lower, upper)


def interval_to_bytes(interval: Interval, sized_type: SizedType, little_endian: bool = True) -> bytes:
    assert isinstance(sized_type.type, IntervalType), "expected an IntervalType"
    base_type = interval_base_type(sized_type.type)
    # TODO ensure both rationals use the same size for numerator and denominator
    assert sized_type.size_bits % 2 == 0, "expected an even-sized SizedType for interval"
    sized_base_type = SizedType(type=base_type, size_bits=sized_type.size_bits // 2)
    lower = numeric_primitive_to_bytes(interval.left, sized_base_type, little_endian)
    upper = numeric_primitive_to_bytes(interval.right, sized_base_type, little_endian)
    return lower + upper
