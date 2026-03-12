"""Tests for umbi.datatypes.json module."""

import pytest

from umbi.datatypes import (
    JsonDict,
    JsonLike,
    JsonList,
    JsonPrimitive,
    json_remove_none_dict_values,
    json_to_string,
    string_to_json,
)


class TestJsonTypes:
    """Test JSON type aliases."""

    def test_json_primitive_examples(self):
        """Test JsonPrimitive type examples."""
        values: list[JsonPrimitive] = [None, True, False, 42, 3.14, "hello"]
        for val in values:
            assert isinstance(val, (type(None), bool, int, float, str))

    def test_json_list_example(self):
        """Test JsonList type example."""
        val: JsonList = [1, "hello", None]
        assert isinstance(val, list)

    def test_json_dict_example(self):
        """Test JsonDict type example."""
        val: JsonDict = {"key": "value", "num": 42}
        assert isinstance(val, dict)

    def test_json_like_examples(self):
        """Test JsonLike type examples."""
        examples: list[JsonLike] = [
            None,
            True,
            42,
            "string",
            [1, 2, 3],
            {"key": "value"},
            {"nested": {"deep": [1, True, None]}},
        ]
        for ex in examples:
            assert isinstance(ex, (type(None), bool, int, float, str, list, dict))


class TestJsonRemoveNoneDictValues:
    """Test json_remove_none_dict_values function."""

    def test_simple_dict_remove_none(self):
        """Test removing None values from simple dict."""
        input_obj: JsonLike = {"a": 1, "b": None, "c": "hello"}
        result = json_remove_none_dict_values(input_obj)
        assert result == {"a": 1, "c": "hello"}

    def test_nested_dict_remove_none(self):
        """Test removing None values from nested dict."""
        input_obj: JsonLike = {
            "level1": {"level2": {"key": None, "value": 42}},
        }
        result = json_remove_none_dict_values(input_obj)
        assert result == {"level1": {"level2": {"value": 42}}}

    def test_list_with_none_preserved(self):
        """Test that None in lists is preserved."""
        input_obj: JsonLike = {"arr": [1, None, 3], "b": None}
        result = json_remove_none_dict_values(input_obj)
        assert result == {"arr": [1, None, 3]}

    def test_complex_structure(self):
        """Test removing None from complex structure."""
        input_obj: JsonLike = {
            "a": 1,
            "b": None,
            "nested": {"x": None, "y": 2},
            "arr": [1, None, {"z": None, "w": 3}],
        }
        result = json_remove_none_dict_values(input_obj)
        expected = {
            "a": 1,
            "nested": {"y": 2},
            "arr": [1, None, {"w": 3}],
        }
        assert result == expected

    def test_all_none_values_removed(self):
        """Test dict with all None values."""
        input_obj: JsonLike = {"a": None, "b": None}
        result = json_remove_none_dict_values(input_obj)
        assert result == {}

    def test_primitive_value_unchanged(self):
        """Test that primitive values are returned unchanged."""
        assert json_remove_none_dict_values(42) == 42
        assert json_remove_none_dict_values("hello") == "hello"
        assert json_remove_none_dict_values(None) is None

    def test_list_unchanged(self):
        """Test that lists are returned with nested cleanup."""
        input_obj: JsonLike = [{"a": None}, {"b": 2}]
        result = json_remove_none_dict_values(input_obj)
        assert result == [{}, {"b": 2}]


class TestJsonToString:
    """Test json_to_string function."""

    def test_simple_dict_to_string(self):
        """Test converting simple dict to JSON string."""
        obj: JsonLike = {"a": 1, "b": "hello"}
        result = json_to_string(obj, indent=None)
        assert isinstance(result, str)
        assert "a" in result
        assert "hello" in result

    def test_list_to_string(self):
        """Test converting list to JSON string."""
        obj: JsonLike = [1, "two", None]
        result = json_to_string(obj, indent=None)
        assert isinstance(result, str)
        assert "two" in result

    def test_string_with_indent(self):
        """Test JSON string with indentation."""
        obj: JsonLike = {"key": "value"}
        result = json_to_string(obj, indent=2)
        assert "\n" in result

    def test_nested_structure_to_string(self):
        """Test converting nested structure."""
        obj: JsonLike = {"nested": {"deep": [1, 2, 3]}}
        result = json_to_string(obj, indent=None)
        assert isinstance(result, str)
        # Should be valid JSON
        assert "nested" in result


class TestStringToJson:
    """Test string_to_json function."""

    def test_simple_dict_from_string(self):
        """Test parsing simple dict from JSON string."""
        json_str = '{"a": 1, "b": "hello"}'
        result = string_to_json(json_str)
        assert result == {"a": 1, "b": "hello"}

    def test_list_from_string(self):
        """Test parsing list from JSON string."""
        json_str = '[1, "two", null]'
        result = string_to_json(json_str)
        assert result == [1, "two", None]

    def test_nested_structure_from_string(self):
        """Test parsing nested structure."""
        json_str = '{"nested": {"deep": [1, 2, 3]}}'
        result = string_to_json(json_str)
        assert result == {"nested": {"deep": [1, 2, 3]}}

    def test_invalid_json_raises(self):
        """Test that invalid JSON raises error."""
        with pytest.raises(Exception):  # JSONDecodeError
            string_to_json("not valid json")

    def test_roundtrip_conversion(self):
        """Test converting to string and back."""
        original: JsonLike = {"a": [1, 2, None], "b": "test"}
        json_str = json_to_string(original, indent=None)
        recovered = string_to_json(json_str)
        assert recovered == original
