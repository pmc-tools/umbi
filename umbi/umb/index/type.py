"""
Type schema and result classes for UMBI types.
"""

from typing import Any
from marshmallow import fields, post_load
from .json_schema import JsonSchema
import umbi.datatypes
from umbi.binary.sized_type import SizedType


class FieldType(fields.String):
    def _deserialize(self, value: Any, attr: Any, data: Any, **kwargs: Any) -> Any:
        # Validate the input value directly without using parent's validator
        # which expects a String return type
        if not isinstance(value, str):
            raise ValueError(f"Expected string value, got {type(value)}")

        string_value = value

        # Validate against allowed types
        allowed_types = (
            [t.value for t in umbi.datatypes.PrimitiveType]
            + [t.value for t in umbi.datatypes.NumericPrimitiveType]
            + [f"{t.value}-interval" for t in umbi.datatypes.NumericPrimitiveType]
        )
        if string_value not in allowed_types:
            raise ValueError(f"Must be one of: {', '.join(allowed_types)}. Got: {string_value}")

        # Convert string to ScalarType enum or IntervalType
        for enum_class in [
            umbi.datatypes.PrimitiveType,
            umbi.datatypes.NumericPrimitiveType,
        ]:
            try:
                return enum_class(string_value)
            except ValueError:
                pass
        try:
            return umbi.datatypes.IntervalType.from_string(string_value)
        except ValueError:
            raise ValueError(f"Unknown type: {string_value}")

    def _serialize(self, value: Any, attr: Any, obj: Any, **kwargs: Any) -> str:
        assert isinstance(value, umbi.datatypes.ScalarType), "expected a ScalarType value"
        if isinstance(value, (umbi.datatypes.PrimitiveType, umbi.datatypes.NumericPrimitiveType)):
            return value.value
        else:  # isinstance(value, umbi.datatypes.IntervalType)
            return str(value)


class SizedTypeSchema(JsonSchema):
    type = FieldType(data_key="type", required=True)
    size = fields.Integer(data_key="size", required=False)

    @post_load
    def make_object(self, data: dict, **kwargs: Any) -> SizedType:
        obj = super().make_object(data, **kwargs)
        assert isinstance(obj.type, umbi.datatypes.ScalarType), f"expected ScalarType, got {type(obj.type)}"
        return SizedType(type=obj.type, size_bits=obj.size)

    def dump(self, obj: Any, *args: Any, **kwargs: Any) -> Any:
        assert isinstance(obj, SizedType)
        obj_dict = {
            "type": FieldType()._serialize(obj.type, "type", obj),
            "size": obj.size_bits,
        }
        return obj_dict
