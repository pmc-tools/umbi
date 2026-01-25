"""Utility functions for byte-level operations."""


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
