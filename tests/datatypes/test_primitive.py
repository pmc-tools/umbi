"""Tests for umbi.datatypes.primitive module."""

from umbi.datatypes import Primitive, PrimitiveType
from umbi.datatypes.primitive import primitive_type_of


class TestPrimitiveType:
    """Test PrimitiveType enum."""

    def test_primitive_type_values(self):
        """Test PrimitiveType enum values."""
        assert PrimitiveType.BOOL.value == "bool"
        assert PrimitiveType.STRING.value == "string"

    def test_primitive_type_members(self):
        """Test all PrimitiveType members exist."""
        assert hasattr(PrimitiveType, "BOOL")
        assert hasattr(PrimitiveType, "STRING")
        assert len(PrimitiveType) == 2


class TestPrimitiveTypeOf:
    """Test primitive_type_of function."""

    def test_bool_type(self):
        """Test boolean type identification."""
        assert primitive_type_of(True) == PrimitiveType.BOOL
        assert primitive_type_of(False) == PrimitiveType.BOOL

    def test_string_type(self):
        """Test string type identification."""
        assert primitive_type_of("hello") == PrimitiveType.STRING
        assert primitive_type_of("") == PrimitiveType.STRING
        assert primitive_type_of("123") == PrimitiveType.STRING

    def test_alias_matches_actual_types(self):
        """Test that Primitive alias matches the underlying types."""
        bool_val: Primitive = True
        str_val: Primitive = "test"
        assert isinstance(bool_val, (bool, str))
        assert isinstance(str_val, (bool, str))
