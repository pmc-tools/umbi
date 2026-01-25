"""
(De)serialization of common types.
"""

from umbi.datatypes import (
    ValueType,
    DataType,
    NumericPrimitive,
    SizedType,
    AtomicType,
    NumericPrimitiveType,
    Interval,
    IntervalType,
)

from .numeric_primitives import (
    bytes_to_numeric_primitive,
    numeric_primitive_to_bytes,
    bits_to_numeric_primitive,
    numeric_primitive_to_bits,
)
from .bitvectors import bits_to_bool, bool_to_bits
from .intervals import bytes_to_interval, interval_to_bytes
from .strings import bytes_to_string, string_to_bytes
from bitstring import BitArray


def bytes_to_value(data: bytes, value_type: DataType, little_endian: bool = True) -> ValueType:
    """Convert a binary string to a single value of the given common type."""
    if isinstance(value_type, AtomicType):
        if value_type == AtomicType.BOOL:
            return any(b != 0 for b in data)
        else:  # value_type == AtomicType.STRING:
            return bytes_to_string(data)
    else:  # umbi.datatypes.is_numeric_type(value_type):
        if isinstance(value_type, NumericPrimitiveType):
            return bytes_to_numeric_primitive(data, value_type, little_endian=little_endian)
        else:  # umbi.datatypes.is_interval_type(value_type):
            assert isinstance(value_type, IntervalType), "expected an interval type"
            return bytes_to_interval(data, value_type, little_endian=little_endian)


def value_to_bytes(value: ValueType, sized_type: SizedType, little_endian: bool = True) -> bytes:
    """Convert a value of a given type to a bytestring."""
    type = sized_type.type
    if isinstance(type, AtomicType):
        if type == AtomicType.BOOL:
            assert isinstance(value, bool), "expected a boolean value"
            return bytes([1 if value else 0])
        else:  # type == AtomicType.STRING:
            assert isinstance(value, str), "expected a string value"
            return string_to_bytes(value)
    else:  # umbi.datatypes.is_numeric_type(type):
        if isinstance(type, NumericPrimitiveType):
            assert isinstance(value, NumericPrimitive), "expected a numeric value"
            return numeric_primitive_to_bytes(value, sized_type, little_endian=little_endian)
        else:  # umbi.datatypes.is_interval_type(type):
            assert isinstance(type, IntervalType), "expected an interval type"
            assert isinstance(value, Interval), "expected an interval value"
            return interval_to_bytes(value, sized_type, little_endian=little_endian)


def bits_to_value(bits: BitArray, value_type: DataType) -> ValueType:
    """Convert a BitArray to a single value of the given common type."""
    if isinstance(value_type, AtomicType):
        if value_type == AtomicType.BOOL:
            return bits_to_bool(bits)
        else:  # value_type == AtomicType.STRING:
            raise ValueError("cannot unpack string from bits")
    else:  # umbi.datatypes.is_numeric_type(value_type):
        if isinstance(value_type, NumericPrimitiveType):
            return bits_to_numeric_primitive(bits, value_type)
        else:  # umbi.datatypes.is_interval_type(value_type):
            raise ValueError("cannot unpack interval from bits")


def value_to_bits(value: ValueType, sized_type: SizedType) -> BitArray:
    """Convert a value of a given type to a fixed-length bit representation."""
    type = sized_type.type
    if isinstance(type, AtomicType):
        if type == AtomicType.BOOL:
            assert isinstance(value, bool), "expected a boolean value"
            return bool_to_bits(value, sized_type.size_bits)
        else:  # type == AtomicType.STRING:
            raise ValueError("cannot pack string to bits")
    else:  # umbi.datatypes.is_numeric_type(type):
        if isinstance(type, NumericPrimitiveType):
            assert isinstance(value, NumericPrimitive), "expected a numeric value"
            return numeric_primitive_to_bits(value, sized_type)
        else:  # umbi.datatypes.is_interval_type(type):
            raise ValueError("cannot pack interval to bits")
