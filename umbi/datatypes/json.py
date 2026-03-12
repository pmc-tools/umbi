"""JSON datatype."""

import json as std_json
from typing import TypeAlias

#: JSON scalar values (`null`, boolean, number, string).
JsonPrimitive: TypeAlias = None | bool | int | float | str
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


def json_to_string(json_obj: JsonLike, indent: int | str | None = 2, **kwargs) -> str:
    """
    :raises: TypeError if the object is not JSON-serializable
    """
    return std_json.dumps(json_obj, indent=indent, **kwargs)


def string_to_json(json_str: str) -> JsonLike:
    """
    :raises: JSONDecodeError if the string is not valid JSON
    """
    return std_json.loads(json_str)
