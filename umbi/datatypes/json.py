"""JSON datatype."""

import json as std_json
from typing import TypeAlias
from collections.abc import Iterable

#: JSON scalar values (`null`, boolean, number, string).
JsonPrimitive: TypeAlias = None | bool | int | float | str
#: JSON primitive types at runtime (for isinstance checks).
JsonPrimitiveRuntime = (type(None), bool, int, float, str)
#: JSON arrays.
JsonList: TypeAlias = list["JsonLike"]
#: JSON objects with string keys.
JsonDict: TypeAlias = dict[str, "JsonLike"]
#: Any valid JSON value.
JsonLike: TypeAlias = JsonPrimitive | JsonList | JsonDict


def json_remove_none_dict_values(json_obj: JsonLike) -> JsonLike:
    """Recursively remove all None (null) dictionary values from a JSON (sub-)object."""
    if isinstance(json_obj, dict):
        return {k: json_remove_none_dict_values(v) for k, v in json_obj.items() if v is not None}
    elif isinstance(json_obj, list):
        return [json_remove_none_dict_values(v) for v in json_obj]
    return json_obj


def json_to_string(json_obj: JsonLike, indent: int | str | None = 2, compact_formatting: bool = True) -> str:
    """
    Format JSON to string. Lists of length 1 with primitive elements are formatted on one line.

    :param indent: indentation level for pretty printing (passed to json.dumps)
    :param compact_formatting: whether to use compact formatting for short lists and dicts
    """

    def _collection_is_primitive(collection: Iterable[object]):
        """Check if a list contains only primitive values."""
        return all(isinstance(item, JsonPrimitiveRuntime) for item in collection)

    def _should_be_compact_list(obj: list, key_name=None):
        """Check if a list should be formatted on one line."""
        # short list of primitives
        if len(obj) <= 1 and _collection_is_primitive(obj):
            return True
        # "applies-to" list of primitives
        if key_name == "applies-to" and _collection_is_primitive(obj):
            return True
        return False

    def _should_be_compact_dict(obj: dict) -> bool:
        """Check if a dict should be formatted on one line (single entry with primitive value, or empty)."""
        if len(obj) <= 1 and _collection_is_primitive(obj.values()):
            return True
        if len(obj) == 2 and set(obj.keys()) == {"type", "size"} and _collection_is_primitive(obj.values()):
            return True
        return False

    def _format_multiline(items: list[str], open_bracket: str, close_bracket: str, depth: int) -> str:
        """Format items as a multiline indented structure."""
        indent_str = indent if isinstance(indent, str) else (" " * indent if indent else "")
        next_indent = indent_str * (depth + 1)
        current_indent = indent_str * depth

        return (
            open_bracket + "\n" + next_indent + f",\n{next_indent}".join(items) + "\n" + current_indent + close_bracket
        )

    def _format_singleline(items: list[str], open_bracket: str, close_bracket: str) -> str:
        return f"{open_bracket}" + ", ".join(items) + f"{close_bracket}"

    def _format(obj, indent: int | str | None = 2, depth=0, key_name=None):
        if isinstance(obj, list):
            if _should_be_compact_list(obj, key_name=key_name):
                items = [std_json.dumps(item) for item in obj]
                return _format_singleline(items, "[", "]")
            else:
                items = [_format(item, indent=indent, depth=depth + 1) for item in obj]
                if indent:
                    return _format_multiline(items, "[", "]", depth)
                else:
                    return _format_singleline(items, "[", "]")
        elif isinstance(obj, dict):
            if _should_be_compact_dict(obj):
                items = [f'"{key}": {std_json.dumps(value)}' for key, value in obj.items()]
                return _format_singleline(items, "{", "}")
            else:
                items = [f'"{k}": {_format(v, indent=indent, depth=depth + 1, key_name=k)}' for k, v in obj.items()]
                if indent:
                    return _format_multiline(items, "{", "}", depth)
                else:
                    return _format_singleline(items, "{", "}")
        else:
            return std_json.dumps(obj)

    if not compact_formatting:
        return std_json.dumps(json_obj, indent=indent)
    return _format(json_obj, indent=indent)


def string_to_json(json_str: str) -> JsonLike:
    """
    :raises: JSONDecodeError if the string is not valid JSON
    """
    return std_json.loads(json_str)
