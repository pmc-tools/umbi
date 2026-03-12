"""Tests for umbi.binary.sequence module."""

import pytest

from umbi.binary import (
    bytes_to_vector,
    vector_to_bytes,
    bytes_with_ranges_to_vector,
    vector_to_bytes_with_ranges,
    SizedType,
    BOOL1,
    UINT32,
)
from umbi.datatypes import PrimitiveType, NumericPrimitiveType
from umbi.io.utils import csr_to_ranges


class TestBytesToBitvector:
    """Test bitvector conversion."""

    def test_bytes_to_bitvector(self):
        """Test converting bytes to bitvector."""
        # 0b00000001, 0b10000000 -> [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        data = b"\x01\x80"
        result = bytes_to_vector(data, BOOL1)
        assert len(result) == 16
        assert result[0]
        assert not result[1]

    def test_bitvector_to_bytes(self):
        """Test converting bitvector to bytes."""
        bitvector = [True, False, False, False, False, False, False, False]
        result = vector_to_bytes(bitvector, BOOL1)
        assert result == b"\x01"

    def test_bitvector_roundtrip(self):
        """Test bitvector round-trip conversion."""
        original = [True, False, True, False, True, False, True, False] * 2
        bytes_data = vector_to_bytes(original, BOOL1)
        result = bytes_to_vector(bytes_data, BOOL1)
        assert result == original


class TestVectorConversion:
    """Test vector conversion for various types."""

    def test_bytes_to_empty_vector(self):
        """Test converting empty bytes to vector."""
        result = bytes_to_vector(b"", UINT32)
        assert result == []

    def test_uint_vector_to_bytes(self):
        """Test converting vector of integers to bytes."""
        # Create a vector of 4-byte integers
        values = [1, 2, 3]
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)

        bytes_data = vector_to_bytes(values, sized_type, little_endian=True)
        assert len(bytes_data) == 12  # 3 * 4 bytes

    def test_uint_bytes_to_vector(self):
        """Test converting bytes to vector of integers."""
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)
        # Create bytes representing [1, 2, 3]
        bytes_data = b"\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00"

        result = bytes_to_vector(bytes_data, sized_type, little_endian=True)
        assert len(result) == 3
        assert result[0] == 1
        assert result[1] == 2
        assert result[2] == 3

    def test_vector_roundtrip(self):
        """Test vector round-trip conversion."""
        original = [10, 20, 30, 40, 50]
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)

        bytes_data = vector_to_bytes(original, sized_type, little_endian=True)
        result = bytes_to_vector(bytes_data, sized_type, little_endian=True)

        assert result == original


class TestByteAlignmentRequirement:
    """Test that vectors require byte-aligned types."""

    def test_non_byte_aligned_raises_error(self):
        """Test that non-byte-aligned types raise an error."""
        non_aligned = SizedType(PrimitiveType.BOOL, 5)
        with pytest.raises(AssertionError):
            bytes_to_vector(b"\x00", non_aligned)

    def test_byte_aligned_accepted(self):
        """Test that byte-aligned types are accepted."""
        aligned = SizedType(NumericPrimitiveType.UINT, 32)
        # Should not raise
        result = bytes_to_vector(b"\x2a\x00\x00\x00", aligned)
        assert result == [42]


class TestEndianness:
    """Test little-endian and big-endian vector conversion."""

    def test_little_endian_vector(self):
        """Test little-endian vector conversion."""
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)
        # 256 in little-endian: [0x00, 0x01, 0x00, 0x00]
        bytes_data = b"\x00\x01\x00\x00"

        result = bytes_to_vector(bytes_data, sized_type, little_endian=True)
        assert result[0] == 256

    def test_big_endian_vector(self):
        """Test big-endian vector conversion."""
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)
        # 256 in big-endian: [0x00, 0x00, 0x01, 0x00]
        bytes_data = b"\x00\x00\x01\x00"

        result = bytes_to_vector(bytes_data, sized_type, little_endian=False)
        assert result[0] == 256


class TestBytesWithRanges:
    """Test vector conversion with byte ranges."""

    def test_bytes_with_ranges_to_vector(self):
        """Test converting bytes with ranges to vector."""
        # Two 4-byte values
        bytes_data = b"\x01\x00\x00\x00\x02\x00\x00\x00"
        ranges = [(0, 4), (4, 8)]
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)

        result = bytes_with_ranges_to_vector(bytes_data, sized_type.type, ranges, little_endian=True)
        assert len(result) == 2

    def test_vector_to_bytes_with_ranges(self):
        """Test converting vector to bytes with ranges."""
        values = [1, 2, 3]
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)

        bytes_data, chunk_csr = vector_to_bytes_with_ranges(values, sized_type, little_endian=True)
        assert chunk_csr is not None
        assert len(bytes_data) == 12  # 3 * 4 bytes
        chunk_ranges = csr_to_ranges(chunk_csr)
        assert len(chunk_ranges) == 3  # 3 values

    def test_ranges_roundtrip(self):
        """Test round-trip with ranges."""
        original = [100, 200, 300]
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)

        bytes_data, chunk_csr = vector_to_bytes_with_ranges(original, sized_type, little_endian=True)
        assert chunk_csr is not None
        chunk_ranges = csr_to_ranges(chunk_csr)
        result = bytes_with_ranges_to_vector(bytes_data, sized_type.type, chunk_ranges, little_endian=True)

        assert result == original


class TestInvalidVectorInputs:
    """Test validation of vector inputs."""

    def test_unaligned_byte_count(self):
        """Test that unaligned byte counts raise errors."""
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)
        # 5 bytes is not divisible by 4
        with pytest.raises(AssertionError):
            bytes_to_vector(b"12345", sized_type)

    def test_empty_vector(self):
        """Test handling of empty vectors."""
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)
        result = bytes_to_vector(b"", sized_type)
        assert result == []

        result = vector_to_bytes([], sized_type)
        assert result == b""
