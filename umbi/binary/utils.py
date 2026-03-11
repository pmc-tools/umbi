"""Utility functions for byte-level operations."""

from bitstring import BitArray


def split_bytes(bytestring: bytes, length: int) -> tuple[bytes, bytes]:
    """Split a bytestring into chunks of the given size."""
    assert length > 0, "chunk size must be positive"
    assert len(bytestring) >= length, "data is shorter than the specified length"
    return bytestring[:length], bytestring[length:]


def split_bytes_half(bytestring: bytes) -> tuple[bytes, bytes]:
    """Split a bytestring into two equal halves."""
    assert len(bytestring) % 2 == 0, "bytestring length must be even to split in half"
    mid = len(bytestring) // 2
    return bytestring[:mid], bytestring[mid:]


def split_bits(bits: BitArray, length: int) -> tuple[BitArray, BitArray]:
    """Split a bitstring into chunks of the given size."""
    assert length > 0, "chunk size must be positive"
    assert len(bits) >= length, "data is shorter than the specified length"
    return bits[:length], bits[length:]


def split_bits_half(bits: BitArray) -> tuple[BitArray, BitArray]:
    """Split a bitstring into two equal halves."""
    assert len(bits) % 2 == 0, "bitstring length must be even to split in half"
    mid = len(bits) // 2
    return bits[:mid], bits[mid:]
