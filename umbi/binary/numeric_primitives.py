from umbi.datatypes import NumericPrimitive, NumericPrimitiveType, SizedType
from .doubles import bytes_to_double, double_to_bytes, bits_to_double, double_to_bits
from .integers import bytes_to_integer, integer_to_bytes, bits_to_integer, integer_to_bits
from .rationals import bytes_to_rational, rational_to_bytes, bits_to_rational, rational_to_bits
from fractions import Fraction
from bitstring import BitArray


def bytes_to_numeric_primitive(data: bytes, value_type: NumericPrimitiveType, little_endian: bool = True):
    """Convert a binary string to a single value of the given numeric primitive type."""
    if value_type == NumericPrimitiveType.INT:
        return bytes_to_integer(data, signed=True, little_endian=little_endian)
    elif value_type == NumericPrimitiveType.UINT:
        return bytes_to_integer(data, signed=False, little_endian=little_endian)
    elif value_type == NumericPrimitiveType.DOUBLE:
        return bytes_to_double(data, little_endian=little_endian)
    else:  # value_type == NumericPrimitiveType.RATIONAL:
        return bytes_to_rational(data, little_endian=little_endian)


def numeric_primitive_to_bytes(value: NumericPrimitive, sized_type: SizedType, little_endian: bool = True) -> bytes:
    """Convert a numeric primitive value to a bytestring."""
    value_type = sized_type.type
    assert isinstance(value_type, NumericPrimitiveType), "expected a NumericPrimitiveType"
    if value_type == NumericPrimitiveType.INT:
        assert isinstance(value, int), "expected an integer value"
        return integer_to_bytes(value, sized_type.size_bytes, signed=True, little_endian=little_endian)
    if value_type == NumericPrimitiveType.UINT:
        assert isinstance(value, int), "expected an integer value"
        return integer_to_bytes(value, sized_type.size_bytes, signed=False, little_endian=little_endian)
    elif value_type == NumericPrimitiveType.DOUBLE:
        assert isinstance(value, float), "expected a float value"
        return double_to_bytes(value, little_endian=little_endian)
    else:  # value_type == NumericPrimitiveType.RATIONAL:
        assert isinstance(value, Fraction), "expected a rational value"
        return rational_to_bytes(value, sized_type.size_bytes, little_endian=little_endian)


def bits_to_numeric_primitive(bits: BitArray, value_type: NumericPrimitiveType) -> NumericPrimitive:
    """Convert a BitArray to a single value of the given numeric primitive type."""
    if value_type == NumericPrimitiveType.INT:
        return bits_to_integer(bits, signed=True)
    elif value_type == NumericPrimitiveType.UINT:
        return bits_to_integer(bits, signed=False)
    elif value_type == NumericPrimitiveType.DOUBLE:
        return bits_to_double(bits)
    else:  # value_type == NumericPrimitiveType.RATIONAL:
        return bits_to_rational(bits)


def numeric_primitive_to_bits(value: NumericPrimitive, sized_type: SizedType) -> BitArray:
    """Convert a numeric primitive value to a fixed-length bit representation."""
    value_type = sized_type.type
    if value_type == NumericPrimitiveType.INT:
        assert isinstance(value, int), "expected an integer value"
        return integer_to_bits(value, sized_type.size_bits, signed=True)
    elif value_type == NumericPrimitiveType.UINT:
        assert isinstance(value, int), "expected an integer value"
        return integer_to_bits(value, sized_type.size_bits, signed=False)
    elif value_type == NumericPrimitiveType.DOUBLE:
        assert isinstance(value, float), "expected a float value"
        return double_to_bits(value)
    else:  # value_type == NumericPrimitiveType.RATIONAL:
        assert isinstance(value, Fraction), "expected a rational value"
        return rational_to_bits(value, sized_type.size_bits)
