"""Tests for umbi.binary.struct_type module."""

import pytest

from umbi.binary import (
    SizedType,
    StructType,
    Struct,
    StructAttribute,
    StructPadding,
    BOOL1,
    UINT32,
)
from umbi.binary.struct_type import bytes_to_struct, struct_to_bytes
from umbi.datatypes import NumericPrimitiveType, PrimitiveType


class TestStructPadding:
    """Test StructPadding functionality."""

    def test_create_padding(self):
        """Test creating padding."""
        padding = StructPadding(padding=8)
        assert padding.padding == 8
        assert padding.size_bits == 8

    def test_padding_must_be_positive(self):
        """Test that padding must be positive."""
        with pytest.raises(ValueError):
            StructPadding(padding=0).validate()

        with pytest.raises(ValueError):
            StructPadding(padding=-1).validate()


class TestStructAttribute:
    """Test StructAttribute functionality."""

    def test_create_attribute(self):
        """Test creating a struct attribute."""
        attr = StructAttribute(name="count", sized_type=UINT32)
        assert attr.name == "count"
        assert attr.sized_type == UINT32
        assert attr.is_optional is False

    def test_attribute_size(self):
        """Test size calculation for attributes."""
        attr = StructAttribute(name="flag", sized_type=BOOL1)
        assert attr.size_bits == 1

    def test_optional_attribute_size(self):
        """Test that optional attributes add presence bit."""
        attr = StructAttribute(name="opt_field", sized_type=UINT32, is_optional=True)
        # UINT32 (32 bits) + presence flag (1 bit)
        assert attr.size_bits == 33

    def test_validate_no_interval_types(self):
        """Test that interval types are not allowed in structs."""
        from umbi.datatypes import IntervalType

        interval_type = SizedType(IntervalType(NumericPrimitiveType.RATIONAL), 128)
        attr = StructAttribute(name="interval_field", sized_type=interval_type)

        with pytest.raises(ValueError):
            attr.validate()

    def test_validate_bounds_require_numeric(self):
        """Test that bounds only work with numeric types."""
        attr = StructAttribute(
            name="string_field",
            sized_type=SizedType(PrimitiveType.STRING, 64),
            lower=0,
            upper=100,
        )

        with pytest.raises(ValueError):
            attr.validate()

    def test_validate_lower_greater_than_upper(self):
        """Test that lower bound cannot be greater than upper."""
        attr = StructAttribute(
            name="bounded_field",
            sized_type=UINT32,
            lower=100,
            upper=50,
        )

        with pytest.raises(ValueError):
            attr.validate()

    def test_non_zero_offset_not_implemented(self):
        """Test that non-zero offsets raise NotImplementedError."""
        attr = StructAttribute(
            name="offset_field",
            sized_type=UINT32,
            offset=10,  # non-zero offset
        )

        with pytest.raises(NotImplementedError):
            attr.validate()


class TestStructTypeBasic:
    """Test basic StructType functionality."""

    def test_create_empty_struct_type(self):
        """Test creating an empty struct type."""
        struct_type = StructType()
        assert len(struct_type.fields) == 0
        assert struct_type.size_bits == 0

    def test_add_attribute(self):
        """Test adding an attribute to struct."""
        struct_type = StructType()
        struct_type.add_attribute("count", UINT32)

        assert len(struct_type.fields) == 1
        assert isinstance(struct_type.fields[0], StructAttribute)
        assert struct_type.fields[0].name == "count"

    def test_add_padding(self):
        """Test adding padding to struct."""
        struct_type = StructType()
        struct_type.add_padding(4)

        assert len(struct_type.fields) == 1
        assert isinstance(struct_type.fields[0], StructPadding)
        assert struct_type.fields[0].padding == 4

    def test_struct_size_calculation(self):
        """Test struct size calculation."""
        struct_type = StructType()
        struct_type.add_attribute("field1", BOOL1)  # 1 bit
        struct_type.add_padding(7)  # 7 bits
        struct_type.add_attribute("field2", UINT32)  # 32 bits

        assert struct_type.size_bits == 1 + 7 + 32


class TestStructTypeAlignment:
    """Test byte alignment functionality."""

    def test_is_byte_aligned(self):
        """Test byte alignment detection."""
        struct_type = StructType()
        struct_type.add_attribute("field", UINT32)
        assert struct_type.is_byte_aligned

    def test_not_byte_aligned(self):
        """Test non-aligned struct detection."""
        struct_type = StructType()
        struct_type.add_attribute("field", BOOL1)  # 1 bit
        assert not struct_type.is_byte_aligned

    def test_padding_to_byte(self):
        """Test automatic padding to byte boundary."""
        struct_type = StructType()
        struct_type.add_attribute("field", BOOL1)  # 1 bit
        struct_type.pad_to_byte()

        assert struct_type.is_byte_aligned
        assert struct_type.size_bits == 8

    def test_num_bits_to_pad(self):
        """Test calculation of padding bits needed."""
        struct_type = StructType()
        struct_type.add_attribute("field", BOOL1)  # 1 bit
        assert struct_type.num_bits_to_pad == 7

    def test_size_bytes_calculation(self):
        """Test size_bytes property."""
        struct_type = StructType()
        struct_type.add_attribute("field1", UINT32)  # 32 bits
        struct_type.add_attribute("field2", UINT32)  # 32 bits

        assert struct_type.size_bytes == 8


class TestStructTypeAttributes:
    """Test attribute access and iteration."""

    def test_iterate_attributes(self):
        """Test iterating over attributes only."""
        struct_type = StructType()
        struct_type.add_attribute("field1", UINT32)
        struct_type.add_padding(8)
        struct_type.add_attribute("field2", BOOL1)

        attributes = struct_type.attributes
        assert len(attributes) == 2
        assert attributes[0].name == "field1"
        assert attributes[1].name == "field2"

    def test_iterate_all_fields(self):
        """Test iterating over all fields."""
        struct_type = StructType()
        struct_type.add_attribute("field1", UINT32)
        struct_type.add_padding(8)

        fields = list(struct_type)
        assert len(fields) == 2

    def test_contains_strings(self):
        """Test detection of string fields."""
        struct_with_strings = StructType()
        struct_with_strings.add_attribute("name", SizedType(PrimitiveType.STRING, 64))
        assert struct_with_strings.contains_strings

        struct_without_strings = StructType()
        struct_without_strings.add_attribute("count", UINT32)
        assert not struct_without_strings.contains_strings


class TestStructSerialization:
    """Test struct serialization and deserialization."""

    def test_simple_struct_to_bytes(self):
        """Test packing a simple struct to bytes."""
        struct_type = StructType()
        struct_type.add_attribute("flag", BOOL1)
        struct_type.pad_to_byte()

        struct: Struct = {"flag": True}
        result = struct_to_bytes(struct, struct_type)
        assert isinstance(result, bytes)
        assert len(result) == 1

    def test_simple_bytes_to_struct(self):
        """Test unpacking bytes to a simple struct."""
        struct_type = StructType()
        struct_type.add_attribute("flag", BOOL1)
        struct_type.pad_to_byte()

        data = b"\x01"
        result = bytes_to_struct(data, struct_type)
        assert isinstance(result, dict)
        assert result["flag"]

    def test_struct_roundtrip(self):
        """Test struct round-trip conversion."""
        struct_type = StructType()
        struct_type.add_attribute("count", UINT32)

        original: Struct = {"count": 42}
        bytes_data = struct_to_bytes(original, struct_type)
        result = bytes_to_struct(bytes_data, struct_type)

        assert result["count"] == original["count"]

    def test_multi_field_struct(self):
        """Test struct with multiple fields."""
        struct_type = StructType()
        struct_type.add_attribute("flag", BOOL1)
        struct_type.pad_to_byte()
        struct_type.add_attribute("count", UINT32)

        original: Struct = {"flag": True, "count": 100}
        bytes_data = struct_to_bytes(original, struct_type)
        result = bytes_to_struct(bytes_data, struct_type)

        assert result["flag"] == original["flag"]
        assert result["count"] == original["count"]


class TestOptionalFields:
    """Test optional field handling."""

    def test_optional_field_present(self):
        """Test optional field when present."""
        struct_type = StructType()
        struct_type.add_attribute(
            "optional_value",
            UINT32,
            is_optional=True,
        )
        struct_type.pad_to_byte()

        original: Struct = {"optional_value": 42}
        bytes_data = struct_to_bytes(original, struct_type)
        result = bytes_to_struct(bytes_data, struct_type)

        assert result["optional_value"] == 42

    def test_optional_field_absent(self):
        """Test optional field when absent."""
        struct_type = StructType()
        struct_type.add_attribute(
            "optional_value",
            UINT32,
            is_optional=True,
        )
        struct_type.pad_to_byte()

        original: Struct = {"optional_value": None}
        bytes_data = struct_to_bytes(original, struct_type)
        print(len(bytes_data), bytes_data)
        result = bytes_to_struct(bytes_data, struct_type)

        assert result["optional_value"] is None

    def test_required_field_cannot_be_none(self):
        """Test that required fields cannot be None."""
        struct_type = StructType()
        struct_type.add_attribute("required_value", UINT32)

        with pytest.raises(AssertionError):
            struct_to_bytes({"required_value": None}, struct_type)


class TestStructValidation:
    """Test struct type validation."""

    def test_validate_valid_struct_type(self):
        """Test validation of valid struct type."""
        struct_type = StructType()
        struct_type.add_attribute("field", UINT32)
        # Should not raise
        struct_type.validate()

    def test_validate_struct_with_invalid_padding(self):
        """Test validation catches invalid padding."""
        struct_type = StructType()
        # Add invalid padding directly (bypass validation)
        struct_type.fields.append(StructPadding(padding=0))

        with pytest.raises(ValueError):
            struct_type.validate()
