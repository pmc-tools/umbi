"""Tests for umbi.binary.primitive module."""

import pytest
from bitstring import BitArray

from umbi.binary.primitive import (
    bits_to_bool,
    bits_to_string,
    bool_to_bits,
    bool_to_bytes,
    bytes_to_bool,
    bytes_to_string,
    string_to_bits,
    string_to_bytes,
)


class TestBooleanConversion:
    """Test boolean conversion functions."""

    def test_bool_true_to_bits(self):
        """Test converting True to bits."""
        bits = bool_to_bits(True)
        assert bits.uint == 1
        assert len(bits) == 1

    def test_bool_false_to_bits(self):
        """Test converting False to bits."""
        bits = bool_to_bits(False)
        assert bits.uint == 0
        assert len(bits) == 1

    def test_bool_to_bits_custom_length(self):
        """Test converting boolean to bits with custom length."""
        bits = bool_to_bits(True, num_bits=8)
        assert bits.uint == 1
        assert len(bits) == 8

    def test_bits_to_bool_true(self):
        """Test converting bits to True."""
        bits = BitArray(uint=1, length=1)
        assert bits_to_bool(bits) is True

    def test_bits_to_bool_false(self):
        """Test converting bits to False."""
        bits = BitArray(uint=0, length=1)
        assert bits_to_bool(bits) is False

    def test_bits_to_bool_nonzero_multiple_bits(self):
        """Test converting non-zero bits (multiple bits) to True."""
        bits = BitArray(uint=255, length=8)
        assert bits_to_bool(bits) is True

    def test_bool_roundtrip(self):
        """Test roundtrip conversion for boolean values."""
        for value in [True, False]:
            bits = bool_to_bits(value)
            result = bits_to_bool(bits)
            assert result == value

    def test_bool_to_bytes_not_implemented(self):
        """Test that bool_to_bytes raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            bool_to_bytes(True)

    def test_bytes_to_bool_not_implemented(self):
        """Test that bytes_to_bool raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            bytes_to_bool(b"\x01")


class TestStringConversion:
    """Test string conversion functions."""

    def test_string_to_bytes_simple(self):
        """Test converting a simple string to bytes."""
        result = string_to_bytes("hello")
        assert result == b"hello"

    def test_string_to_bytes_empty(self):
        """Test converting an empty string to bytes."""
        result = string_to_bytes("")
        assert result == b""

    def test_string_to_bytes_unicode(self):
        """Test converting a unicode string to bytes."""
        result = string_to_bytes("héllo")
        assert result == "héllo".encode("utf-8")

    def test_bytes_to_string_simple(self):
        """Test converting bytes to a simple string."""
        result = bytes_to_string(b"hello")
        assert result == "hello"

    def test_bytes_to_string_empty(self):
        """Test converting empty bytes to a string."""
        result = bytes_to_string(b"")
        assert result == ""

    def test_bytes_to_string_unicode(self):
        """Test converting unicode bytes to a string."""
        original = "héllo"
        encoded = original.encode("utf-8")
        result = bytes_to_string(encoded)
        assert result == original

    def test_string_roundtrip(self):
        """Test roundtrip conversion for string values."""
        test_strings = ["hello", "", "unicode: 日本語", "special chars: !@#$%^&*()"]
        for value in test_strings:
            result = bytes_to_string(string_to_bytes(value))
            assert result == value

    def test_string_to_bits_not_implemented(self):
        """Test that string_to_bits raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            string_to_bits("hello")

    def test_bits_to_string_not_implemented(self):
        """Test that bits_to_string raises NotImplementedError."""
        bits = BitArray(bin="01001000")
        with pytest.raises(NotImplementedError):
            bits_to_string(bits)
