"""(De)serialization of sequences of common types or structs."""

import logging
from collections.abc import Sequence

from umbi.datatypes import Scalar, ScalarType
from .sized_type import SizedType, BOOL1
from .struct_type import Struct, StructType, bytes_to_struct, struct_to_bytes
from .scalar import (
    bytes_to_scalar,
    scalar_to_bytes,
)

logger = logging.getLogger(__name__)


# Bitvectors


def bytes_to_bitvector(bytestring: bytes) -> list[bool]:
    """Convert a bytestring representing a bitvector into a list of booleans."""
    return [(byte >> bit) & 1 == 1 for byte in bytestring for bit in range(8)]


def bitvector_to_bytes(bitvector: Sequence[bool]) -> bytes:
    """Convert a list of booleans representing a bitvector into a bytestring."""
    byte_array = bytearray()
    for i in range(0, len(bitvector), 8):
        byte = sum((1 << j) for j in range(8) if i + j < len(bitvector) and bitvector[i + j])
        byte_array.append(byte)
    return bytes(byte_array)


# Utils for later


def bytes_with_ranges_into_chunks(data: bytes, chunk_ranges: list[tuple[int, int]]) -> list[bytes]:
    """Split bytestring into chunks according to chunk ranges."""
    assert len(data) == chunk_ranges[-1][1], "data length does not match the end of the last chunk range"
    return [data[start:end] for start, end in chunk_ranges]


def chunks_to_csr(chunks: list[bytes]) -> list[int]:
    """Build csr for a list of chunks."""
    current_pos = 0
    csr = [current_pos]
    for chunk in chunks:
        current_pos += len(chunk)
        csr.append(current_pos)
    return csr


def bytes_into_chunks(data: bytes, chunk_size: int) -> list[bytes]:
    """Split bytestring into evenly sized chunks."""
    assert chunk_size > 0, f"expected {chunk_size} to be a positive number"
    assert len(data) % chunk_size == 0, f"expected {len(data)} to be divisible by {chunk_size}"
    return [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]


# Vector (de)serialization


def bytes_to_vector(
    data: bytes, value_sized_type: SizedType | StructType, little_endian: bool = True
) -> list[Scalar] | list[Struct]:
    """
    Decode a binary string as a list of elements of the given type.
    :param value_sized_type: vector element (sized) type
    :param little_endian: if True, the binary string is interpreted as little-endian
    """

    if len(data) == 0:
        return []

    if value_sized_type == BOOL1:
        assert little_endian, "big-endianness for bitvectors is not implemented"
        return bytes_to_bitvector(data)  # type: ignore[return-value] (promoting list[bool] to list[Scalar])

    assert value_sized_type.is_byte_aligned, "expected a byte-aligned type as chunk sizes"
    chunk_size = value_sized_type.size_bytes
    chunks = bytes_into_chunks(data, chunk_size)

    if isinstance(value_sized_type, StructType):
        return [bytes_to_struct(chunk, value_sized_type) for chunk in chunks]
    else:
        return [bytes_to_scalar(chunk, value_sized_type.type, little_endian) for chunk in chunks]


def bytes_with_ranges_to_vector(
    data: bytes,
    value_type: ScalarType,
    chunk_ranges: list[tuple[int, int]],
    little_endian: bool = True,
) -> list[Scalar]:
    """
    Decode a binary string as a list of numbers.
    :param value_type: vector element type
    :param chunk_ranges: (optional) chunk ranges to split the data into
    :param little_endian: if True, the binary string is interpreted as little-endian
    """
    if len(data) == 0:
        return []
    chunks = bytes_with_ranges_into_chunks(data, chunk_ranges)
    return [bytes_to_scalar(chunk, value_type, little_endian) for chunk in chunks]


def vector_to_bytes(
    vector: Sequence[Scalar] | Sequence[Struct], value_sized_type: SizedType | StructType, little_endian: bool = True
) -> bytes:
    """Encode a list of values as a binary string.
    :param value_sized_type: vector element type
    :return: encoded binary string
    """

    if len(vector) == 0:
        logger.warning("converting empty vector to bytes")
        return b""

    if value_sized_type == BOOL1:
        assert little_endian, "big-endianness for bitvectors is not implemented"
        assert all(isinstance(v, bool) for v in vector), "expected a list of booleans for BOOL1 type"
        return bitvector_to_bytes(vector)  # type: ignore[arg-type]

    if isinstance(value_sized_type, StructType):
        assert all(isinstance(v, dict) for v in vector), f"expected a list of structs, got {vector}"
        chunks = [struct_to_bytes(item, value_sized_type) for item in vector]  # type: ignore[list-item]
    else:
        assert all(isinstance(v, Scalar) for v in vector), f"expected a list of scalars, got {vector}"
        chunks = [
            scalar_to_bytes(item, value_sized_type.type, value_sized_type.size_bytes, little_endian)  # type: ignore
            for item in vector
        ]
    bytestring = b"".join(chunks)
    expected_size = len(vector) * (value_sized_type.size_bytes)
    assert len(bytestring) == expected_size, f"expected {expected_size} bytes, but got {len(bytestring)} bytes"
    return bytestring


def vector_to_bytes_with_ranges(
    vector: Sequence[Scalar], value_sized_type: SizedType, little_endian: bool = True
) -> tuple[bytes, list[int] | None]:
    """Encode a list of values as a binary string.
    :param value_sized_type: vector element type
    :return: encoded binary string
    :return: (optional) chunk csr if non-trivial splitting is needed to split the resulting bytestring into chunks, e.g. for strings or non-standard rationals
    """

    if len(vector) == 0:
        logger.warning("converting empty vector to bytes")
        return (b"", None)

    chunks = [
        scalar_to_bytes(item, value_sized_type.type, value_sized_type.size_bytes, little_endian) for item in vector
    ]
    chunks_csr = chunks_to_csr(chunks)
    bytestring = b"".join(chunks)

    return bytestring, chunks_csr
