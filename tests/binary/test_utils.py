"""Tests for umbi.binary.utils module."""

import pytest
from bitstring import BitArray

from umbi.binary.utils import (
    split_bytes,
    split_bytes_half,
    split_bits,
    split_bits_half,
)


class TestSplitBytes:
    """Test byte splitting functions."""

    def test_split_bytes_basic(self):
        """Test splitting bytes at a specific position."""
        data = b"hello"
        left, right = split_bytes(data, 2)
        assert left == b"he"
        assert right == b"llo"

    def test_split_bytes_zero_position(self):
        """Test splitting at position 0."""
        data = b"hello"
        with pytest.raises(AssertionError):
            split_bytes(data, 0)

    def test_split_bytes_at_end(self):
        """Test splitting at the end."""
        data = b"hello"
        left, right = split_bytes(data, len(data))
        assert left == data
        assert right == b""

    def test_split_bytes_insufficient_data(self):
        """Test that assertion fails when data is shorter than split position."""
        data = b"hi"
        with pytest.raises(AssertionError):
            split_bytes(data, 5)

    def test_split_bytes_full_data(self):
        """Test splitting consumes all data."""
        data = b"abc"
        left, right = split_bytes(data, 1)
        assert left + right == data

    def test_split_bytes_multiple_splits(self):
        """Test multiple sequential splits."""
        data = b"abcdef"
        first, remaining = split_bytes(data, 2)
        second, final = split_bytes(remaining, 2)
        assert first == b"ab"
        assert second == b"cd"
        assert final == b"ef"


class TestSplitBytesHalf:
    """Test half-splitting functions for bytes."""

    def test_split_bytes_half_even(self):
        """Test splitting even-length bytestring in half."""
        data = b"abcd"
        left, right = split_bytes_half(data)
        assert left == b"ab"
        assert right == b"cd"

    def test_split_bytes_half_single_pair(self):
        """Test splitting 2-byte bytestring."""
        data = b"xy"
        left, right = split_bytes_half(data)
        assert left == b"x"
        assert right == b"y"

    def test_split_bytes_half_odd_length(self):
        """Test that odd-length bytestring raises assertion."""
        data = b"abc"
        with pytest.raises(AssertionError):
            split_bytes_half(data)

    def test_split_bytes_half_empty(self):
        """Test that empty bytestring raises assertion."""
        data = b""
        with pytest.raises(AssertionError):
            split_bytes_half(data)

    def test_split_bytes_half_large(self):
        """Test splitting large even-length bytestring."""
        data = b"\x00" * 1000
        left, right = split_bytes_half(data)
        assert len(left) == 500
        assert len(right) == 500
        assert left + right == data


class TestSplitBits:
    """Test bit splitting functions."""

    def test_split_bits_basic(self):
        """Test splitting bits at a specific position."""
        bits = BitArray(bin="11010101")
        left, right = split_bits(bits, 4)
        assert len(left) == 4
        assert len(right) == 4

    def test_split_bits_zero_position(self):
        """Test that zero position raises assertion."""
        bits = BitArray(bin="11010101")
        with pytest.raises(AssertionError):
            split_bits(bits, 0)

    def test_split_bits_at_end(self):
        """Test splitting at the end."""
        bits = BitArray(bin="11010101")
        left, right = split_bits(bits, len(bits))
        assert left == bits
        assert len(right) == 0

    def test_split_bits_insufficient_data(self):
        """Test that assertion fails when data is shorter."""
        bits = BitArray(bin="11")
        with pytest.raises(AssertionError):
            split_bits(bits, 5)

    def test_split_bits_full_data(self):
        """Test splitting preserves all data."""
        bits = BitArray(bin="101010")
        left, right = split_bits(bits, 2)
        assert (left + right).bin == bits.bin

    def test_split_bits_one_bit(self):
        """Test splitting off a single bit."""
        bits = BitArray(bin="1010")
        left, right = split_bits(bits, 1)
        assert len(left) == 1
        assert len(right) == 3


class TestSplitBitsHalf:
    """Test half-splitting functions for bits."""

    def test_split_bits_half_even(self):
        """Test splitting even-length bitstring in half."""
        bits = BitArray(bin="11001100")
        left, right = split_bits_half(bits)
        assert len(left) == 4
        assert len(right) == 4

    def test_split_bits_half_single_pair(self):
        """Test splitting 2-bit bitstring."""
        bits = BitArray(bin="10")
        left, right = split_bits_half(bits)
        assert len(left) == 1
        assert len(right) == 1

    def test_split_bits_half_odd_length(self):
        """Test that odd-length bitstring raises assertion."""
        bits = BitArray(bin="101")
        with pytest.raises(AssertionError):
            split_bits_half(bits)

    def test_split_bits_half_empty(self):
        """Test that empty bitstring raises assertion."""
        bits = BitArray()
        with pytest.raises(AssertionError):
            split_bits_half(bits)

    def test_split_bits_half_large(self):
        """Test splitting large even-length bitstring."""
        bits = BitArray(uint=0, length=1000)
        left, right = split_bits_half(bits)
        assert len(left) == 500
        assert len(right) == 500
        assert (left + right).len == 1000

    def test_split_bits_half_preserves_values(self):
        """Test that values are preserved after splitting."""
        bits = BitArray(bin="10110011")
        left, right = split_bits_half(bits)
        assert (left + right).bin == bits.bin


class TestSplittingConsistency:
    """Test consistency between bytes and bits splitting."""

    def test_split_bytes_then_to_bits_equals_split_bits(self):
        """Test that splitting bytes then converting equals converting then splitting bits."""
        data = b"\xf0\x0f"
        left_bytes, right_bytes = split_bytes_half(data)

        bits = BitArray(bytes=data)
        left_bits, right_bits = split_bits_half(bits)

        assert left_bytes == left_bits.bytes
        assert right_bytes == right_bits.bytes

    def test_multiple_byte_splits_consistency(self):
        """Test consistency across multiple splits."""
        data = b"abcdefgh"

        # Split 1
        chunk1, remaining1 = split_bytes(data, 2)
        # Split 2
        chunk2, remaining2 = split_bytes(remaining1, 2)
        # Split 3
        chunk3, remaining3 = split_bytes(remaining2, 2)
        # Split 4
        chunk4, remaining4 = split_bytes(remaining3, 2)

        # Reconstruct
        reconstructed = chunk1 + chunk2 + chunk3 + chunk4 + remaining4
        assert reconstructed == data
