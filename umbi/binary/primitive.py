"""(De)serializers for primitive types."""

from bitstring import BitArray

from umbi.datatypes import Primitive, PrimitiveType

# Booleans


def bytes_to_bool(data: bytes) -> bool:
    # should not be needed in umbi
    raise NotImplementedError("conversion from bytes to boolean not supported")


def bool_to_bytes(value: bool) -> bytes:
    # should not be needed in umbi
    raise NotImplementedError("conversion from boolean to bytes not supported")


def bits_to_bool(bits: BitArray) -> bool:
    """Convert a bitstring to a boolean."""
    return bits.uint != 0


def bool_to_bits(value: bool, num_bits: int = 1) -> BitArray:
    """Convert a boolean to a bitstring."""
    value_uint = 1 if value else 0
    return BitArray(uint=value_uint, length=num_bits)


# Strings


def bytes_to_string(bytestring: bytes) -> str:
    """Convert a bytestring to a utf-8 string."""
    return bytestring.decode("utf-8")


def string_to_bytes(value: str) -> bytes:
    """Convert a utf-8 string to a bytestring."""
    return value.encode("utf-8")


def string_to_bits(value: str) -> BitArray:
    # should not be needed in umbi
    raise NotImplementedError("conversion from string to bitstring not supported")


def bits_to_string(bits: BitArray) -> str:
    # should not be needed in umbi
    raise NotImplementedError("conversion from bitstring to string not supported")


# API


def bytes_to_primitive(data: bytes, value_type: PrimitiveType) -> Primitive:
    return {
        PrimitiveType.BOOL: bytes_to_bool,
        PrimitiveType.STRING: bytes_to_string,
    }[value_type](data)


def primitive_to_bytes(value: Primitive, value_type: PrimitiveType) -> bytes:
    return {
        PrimitiveType.BOOL: bool_to_bytes,
        PrimitiveType.STRING: string_to_bytes,
    }[value_type](value)


def bits_to_primitive(bits: BitArray, value_type: PrimitiveType) -> Primitive:
    return {
        PrimitiveType.BOOL: bits_to_bool,
        PrimitiveType.STRING: bits_to_string,
    }[value_type](bits)


def primitive_to_bits(value: Primitive, value_type: PrimitiveType, num_bits: int) -> BitArray:
    return {
        PrimitiveType.BOOL: lambda v: bool_to_bits(v, num_bits),
        PrimitiveType.STRING: string_to_bits,
    }[value_type](value)
