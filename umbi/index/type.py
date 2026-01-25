"""
Type schema and result classes for UMBI types.
"""

from marshmallow import fields, post_load, validate
from .json_schema import JsonSchema
import umbi.datatypes


class FieldType(fields.String):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            validate=validate.OneOf(
                [t.value for t in umbi.datatypes.AtomicType]
                + [t.value for t in umbi.datatypes.NumericPrimitiveType]
                + [t.value for t in umbi.datatypes.IntervalType],
                error="Must be one of: {choices}. Got: {input}",
            ),
            **kwargs,
        )

    def _deserialize(self, value, attr, data, **kwargs) -> umbi.datatypes.DataType:
        # First deserialize as string (validates against OneOf)
        string_value = super()._deserialize(value, attr, data, **kwargs)
        # Convert string to DataType enum
        for enum_class in [umbi.datatypes.AtomicType, umbi.datatypes.NumericPrimitiveType, umbi.datatypes.IntervalType]:
            try:
                return enum_class(string_value)
            except ValueError:
                pass
        raise ValueError(f"Unknown type: {string_value}")

    def _serialize(self, value, attr, obj, **kwargs) -> str:
        # Convert DataType enum to string
        if hasattr(value, "value"):
            return value.value
        return str(value)


class SizedTypeSchema(JsonSchema):
    type = FieldType(data_key="type", required=True)
    size = fields.Integer(data_key="size", required=False)

    @post_load
    def make_object(self, data: dict, **kwargs) -> umbi.datatypes.SizedType:
        obj = super().make_object(data, **kwargs)
        assert isinstance(obj.type, umbi.datatypes.DataType), f"expected DataType, got {type(obj.type)}"
        return umbi.datatypes.SizedType(type=obj.type, size_bits=obj.size)

    def dump(self, obj, *args, **kwargs):
        assert isinstance(obj, umbi.datatypes.SizedType)
        obj_dict = {
            "type": FieldType()._serialize(obj.type, "type", obj),
            "size": obj.size_bits,
        }
        return obj_dict
