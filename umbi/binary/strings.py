"""
Utilities for (de)serializing strings.
"""


def bytes_to_string(bytestring: bytes) -> str:
    """Convert a binary string to a utf-8 string."""
    return bytestring.decode("utf-8")


def string_to_bytes(string: str) -> bytes:
    """Convert a utf-8 string to a binary string."""
    return string.encode("utf-8")
