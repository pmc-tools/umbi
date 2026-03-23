"""Tests for umbi.tar.tar_coder module."""

import pytest

from umbi.binary import SizedType
from umbi.datatypes import NumericPrimitiveType
from umbi.tar import TarCoder


class TestTarCoderJSON:
    """Test JSON reading and writing."""

    def test_add_and_read_json(self):
        """Test adding and reading JSON data."""
        tc = TarCoder()
        json_obj = {"name": "test", "value": 42}

        tc.add_json("data.json", json_obj)

        loaded = tc.read_json("data.json")
        assert loaded is not None
        assert loaded == json_obj

    def test_read_json_optional_missing(self):
        """Test reading missing optional JSON file returns None."""
        tc = TarCoder()
        result = tc.read_json("missing.json", optional=True)
        assert result is None

    def test_read_json_required_missing(self):
        """Test reading missing required JSON file raises error."""
        tc = TarCoder()
        with pytest.raises(KeyError):
            tc.read_json("missing.json")

    def test_add_json_required_none(self):
        """Test that adding None for required JSON raises error."""
        tc = TarCoder()
        with pytest.raises(ValueError):
            tc.add_json("data.json", None)

    def test_add_json_optional_none(self):
        """Test that adding None for optional JSON does nothing."""
        tc = TarCoder()
        tc.add_json("data.json", None, optional=True)
        assert not tc.has_file("data.json")

    def test_complex_json(self):
        """Test complex nested JSON structures."""
        tc = TarCoder()
        json_obj = {"list": [1, 2, 3], "nested": {"key": "value"}, "float": 3.14, "bool": True, "null": None}

        tc.add_json("complex.json", json_obj)
        loaded = tc.read_json("complex.json")
        assert loaded is not None
        assert loaded == json_obj


class TestTarCoderVectors:
    """Test vector reading and writing."""

    def test_add_and_read_vector(self):
        """Test adding and reading a vector."""
        tc = TarCoder()
        values = [1, 2, 3, 4, 5]
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)

        tc.add_vector("values.bin", sized_type, values)

        loaded = tc.read_vector("values.bin", sized_type)
        assert loaded is not None
        assert loaded == values

    def test_read_vector_optional_missing(self):
        """Test reading missing optional vector returns None."""
        tc = TarCoder()
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)

        result = tc.read_vector("missing.bin", sized_type, optional=True)
        assert result is None

    def test_read_vector_required_missing(self):
        """Test reading missing required vector raises error."""
        tc = TarCoder()
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)

        with pytest.raises(KeyError):
            tc.read_vector("missing.bin", sized_type)

    def test_add_vector_required_none(self):
        """Test that adding None for required vector raises error."""
        tc = TarCoder()
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)

        with pytest.raises(ValueError):
            tc.add_vector("values.bin", sized_type, None)

    def test_vector_roundtrip(self):
        """Test vector round-trip conversion."""
        original = [100, 200, 300, 400]
        sized_type = SizedType(NumericPrimitiveType.UINT, 64)

        tc1 = TarCoder()
        tc1.add_vector("data.bin", sized_type, original)

        loaded = tc1.read_vector("data.bin", sized_type)
        assert loaded is not None
        assert loaded == original


class TestTarCoderBitvector:
    """Test bitvector reading and writing."""

    def test_add_and_read_bitvector(self):
        """Test adding and reading a bitvector."""
        tc = TarCoder()
        bitvector = [True, False, True, False, True]

        tc.add_bitvector("bits.bin", bitvector)

        loaded = tc.read_bitvector("bits.bin", num_entries=5)
        assert loaded is not None
        # May be padded, so check the first 5 elements
        assert loaded[:5] == bitvector

    def test_bitvector_padding(self):
        """Test bitvector padding to 8-byte boundary."""
        tc = TarCoder()
        # 5 bits, should be padded to 64 bits (8 bytes)
        bitvector = [True, False, True, False, True]

        tc.add_bitvector("bits.bin", bitvector, pad_to_8_bytes=True)

        loaded = tc.read_bitvector("bits.bin", num_entries=5)
        assert loaded is not None
        assert loaded[:5] == bitvector
        # Remaining should be False (padding)
        assert all(not bit for bit in loaded[5:])

    def test_bitvector_no_padding(self):
        """Test bitvector without padding."""
        tc = TarCoder()
        bitvector = [True, False, True, False, True, False, True, False]  # 8 bits

        tc.add_bitvector("bits.bin", bitvector, pad_to_8_bytes=False)

        loaded = tc.read_bitvector("bits.bin", num_entries=8)
        assert loaded is not None
        assert loaded == bitvector

    def test_bitvector_truncation(self):
        """Test bitvector truncation to num_entries."""
        tc = TarCoder()
        # Create a bitvector with 16 bits
        bitvector = [i % 2 == 0 for i in range(16)]

        tc.add_bitvector("bits.bin", bitvector, pad_to_8_bytes=False)

        # Read only 8 entries
        loaded = tc.read_bitvector("bits.bin", num_entries=8)
        assert loaded is not None
        assert len(loaded) == 8
        assert loaded == bitvector[:8]


class TestTarCoderVectorWithRanges:
    """Test vector with CSR ranges reading and writing."""

    def test_add_and_read_vector_with_ranges(self):
        """Test adding and reading a vector with CSR ranges."""
        tc = TarCoder()
        vector = [1, 2, 3, 4, 5, 6, 7, 8]
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)

        tc.add_vector_with_ranges("data.bin", sized_type, vector, "ranges.bin")

        loaded = tc.read_vector_with_ranges("data.bin", NumericPrimitiveType.UINT, filename_csr="ranges.bin")
        assert loaded is not None
        assert loaded == vector

    def test_read_vector_with_ranges_optional_missing(self):
        """Test reading missing optional vector with ranges returns None."""
        tc = TarCoder()
        result = tc.read_vector_with_ranges(
            "missing.bin", NumericPrimitiveType.UINT, optional=True, filename_csr="ranges.bin"
        )
        assert result is None

    def test_read_vector_with_ranges_required_missing(self):
        """Test reading missing required vector with ranges raises error."""
        tc = TarCoder()
        with pytest.raises(KeyError):
            tc.read_vector_with_ranges("missing.bin", NumericPrimitiveType.UINT, filename_csr="ranges.bin")

    def test_read_vector_with_ranges_missing_csr(self):
        """Test that missing CSR file raises error even if main file exists."""
        tc = TarCoder()
        vector = [1, 2, 3, 4, 5]
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)

        tc.add_vector_with_ranges("data.bin", sized_type, vector, "ranges.bin")
        # Remove the CSR file using dict interface
        tc.pop("ranges.bin", None)

        with pytest.raises(KeyError):
            tc.read_vector_with_ranges("data.bin", NumericPrimitiveType.UINT, filename_csr="ranges.bin")

    def test_add_vector_with_ranges_required_none(self):
        """Test that adding None for required vector with ranges raises error."""
        tc = TarCoder()
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)

        with pytest.raises(ValueError):
            tc.add_vector_with_ranges("data.bin", sized_type, None, "ranges.bin")

    def test_add_vector_with_ranges_optional_none(self):
        """Test that adding None for optional vector with ranges does nothing."""
        tc = TarCoder()
        sized_type = SizedType(NumericPrimitiveType.UINT, 32)

        tc.add_vector_with_ranges("data.bin", sized_type, None, "ranges.bin", optional=True)
        assert not tc.has_file("data.bin")
        assert not tc.has_file("ranges.bin")

    def test_vector_with_ranges_roundtrip(self):
        """Test vector with ranges round-trip conversion."""
        original = [100, 200, 300, 400, 500, 600]
        sized_type = SizedType(NumericPrimitiveType.UINT, 64)

        tc1 = TarCoder()
        tc1.add_vector_with_ranges("data.bin", sized_type, original, "ranges.bin")

        loaded = tc1.read_vector_with_ranges("data.bin", NumericPrimitiveType.UINT, filename_csr="ranges.bin")
        assert loaded is not None
        assert loaded == original


class TestTarCoderStrings:
    """Test string vector reading and writing with CSR."""

    def test_add_and_read_strings(self):
        """Test adding and reading strings with CSR."""
        tc = TarCoder()
        strings = ["hello", "world", "test", "data"]

        tc.add_strings("strings.bin", strings, "strings_csr.bin")

        loaded = tc.read_strings("strings.bin", filename_csr="strings_csr.bin")
        assert loaded is not None
        assert loaded == strings

    def test_read_strings_optional_missing(self):
        """Test reading missing optional strings returns None."""
        tc = TarCoder()
        result = tc.read_strings("missing.bin", optional=True, filename_csr="strings_csr.bin")
        assert result is None

    def test_read_strings_required_missing(self):
        """Test reading missing required strings raises error."""
        tc = TarCoder()
        with pytest.raises(KeyError):
            tc.read_strings("missing.bin", filename_csr="strings_csr.bin")

    def test_read_strings_missing_csr(self):
        """Test that missing CSR file raises error even if main file exists."""
        tc = TarCoder()
        strings = ["a", "b", "c"]

        tc.add_strings("strings.bin", strings, "strings_csr.bin")
        # Remove the CSR file using dict interface
        tc.pop("strings_csr.bin", None)

        with pytest.raises(KeyError):
            tc.read_strings("strings.bin", filename_csr="strings_csr.bin")

    def test_add_strings_required_none(self):
        """Test that adding None for required strings raises error."""
        tc = TarCoder()

        with pytest.raises(ValueError):
            tc.add_strings("strings.bin", None, "strings_csr.bin")

    def test_add_strings_optional_none(self):
        """Test that adding None for optional strings does nothing."""
        tc = TarCoder()

        tc.add_strings("strings.bin", None, "strings_csr.bin", optional=True)
        assert not tc.has_file("strings.bin")
        assert not tc.has_file("strings_csr.bin")

    def test_strings_roundtrip(self):
        """Test strings round-trip conversion."""
        original = ["foo", "bar", "baz", "qux", "long string with spaces"]

        tc1 = TarCoder()
        tc1.add_strings("strings.bin", original, "strings_csr.bin")

        loaded = tc1.read_strings("strings.bin", filename_csr="strings_csr.bin")
        assert loaded is not None
        assert loaded == original

    def test_strings_single_empty_string(self):
        """Test handling of empty strings in list."""
        tc = TarCoder()
        strings = ["", "non-empty", ""]

        tc.add_strings("strings.bin", strings, "strings_csr.bin")

        loaded = tc.read_strings("strings.bin", filename_csr="strings_csr.bin")
        assert loaded is not None
        assert loaded == strings


class TestTarCoderIntegration:
    """Integration tests for TarCoder."""

    def test_multiple_files(self):
        """Test adding and reading multiple files."""
        tc = TarCoder()

        # Add different types of files
        tc.add_json("metadata.json", {"version": 1})
        tc.add_vector("values.bin", SizedType(NumericPrimitiveType.UINT, 32), [1, 2, 3])
        tc.add_bitvector("flags.bin", [True, False, True, False])

        # Verify all files exist and can be read
        json_data = tc.read_json("metadata.json")
        assert json_data is not None
        assert json_data == {"version": 1}
        vector_data = tc.read_vector("values.bin", SizedType(NumericPrimitiveType.UINT, 32))
        assert vector_data is not None
        assert vector_data == [1, 2, 3]
        bits_data = tc.read_bitvector("flags.bin", num_entries=4)
        assert bits_data is not None
        assert bits_data[:4] == [True, False, True, False]

    def test_tar_coder_inherits_tarfile(self):
        """Test that TarCoder has all TarFile functionality."""
        tc = TarCoder()

        # Test dict interface
        tc["raw.bin"] = b"raw data"
        assert tc.read_file("raw.bin") == b"raw data"

        # Test add_file
        tc.add_file("file.bin", b"content")
        assert tc.has_file("file.bin")
