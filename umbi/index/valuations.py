"""
Variable valuation schemas and classes.
"""

from dataclasses import dataclass, field
from marshmallow import fields, post_load, validate
from marshmallow_oneofschema.one_of_schema import OneOfSchema

import umbi.datatypes
from .type import SizedTypeSchema

from .json_schema import (
    JsonSchema,
    JsonSchemaResult,
    FieldUint,
)


class ValuationPaddingSchema(JsonSchema):
    """Schema for padding fields."""

    padding = FieldUint(data_key="padding", required=True, validate=validate.Range(min=1))

    @post_load
    def make_object(self, data: dict, **kwargs) -> umbi.datatypes.StructPadding:
        """Create a Padding object from the deserialized data."""
        obj = super().make_object(data, **kwargs)
        return umbi.datatypes.StructPadding(padding=obj.padding)

    def dump(self, obj, *args, **kwargs):
        assert isinstance(obj, umbi.datatypes.StructPadding)
        obj_dict = {
            "padding": obj.padding,
        }
        return obj_dict


class ValuationAttributeSchema(JsonSchema):
    """Schema for variable fields."""

    name = fields.String(data_key="name", required=True)
    type = fields.Nested(SizedTypeSchema, data_key="type", required=True)
    is_optional = fields.Boolean(data_key="is-optional", required=False, load_default=False)
    lower = fields.Integer(data_key="lower", required=False)
    upper = fields.Integer(data_key="upper", required=False)
    offset = fields.Integer(data_key="offset", required=False)

    @post_load
    def make_object(self, data: dict, **kwargs) -> umbi.datatypes.StructAttribute:
        """Validate and create a Variable object from the deserialized data."""
        obj = super().make_object(data, **kwargs)
        return umbi.datatypes.StructAttribute(
            name=obj.name,
            sized_type=obj.type,
            is_optional=obj.is_optional,
            lower=getattr(obj, "lower", None),
            upper=getattr(obj, "upper", None),
            offset=getattr(obj, "offset", None),
        )

    def dump(self, obj, *args, **kwargs):
        obj_dict = {
            "name": obj.name,
            "type": SizedTypeSchema().dump(obj.sized_type),
            "is-optional": obj.is_optional,
            "lower": obj.lower,
            "upper": obj.upper,
            "offset": obj.offset,
        }
        return obj_dict


class ValuationFieldSchema(OneOfSchema):
    """Schema for valuation fields (padding or variable)."""

    type_schemas = {
        "padding": ValuationPaddingSchema,
        "attribute": ValuationAttributeSchema,
    }

    # custom discriminator field since the default 'type' field is used in ValuationAttributeSchema
    type_field = "_discriminator"

    def get_obj_type(self, obj):
        """Determine which schema to use based on the object's attributes."""
        if hasattr(obj, "padding"):
            return "padding"
        elif hasattr(obj, "name") and hasattr(obj, "type"):
            return "attribute"
        else:
            raise ValueError("Object must be either a padding or attribute namespace")

    def load(self, json_data, *args, **kwargs):
        """Add discriminator field before loading."""
        assert isinstance(json_data, dict)
        json_data = dict(
            json_data,
            _discriminator="padding" if "padding" in json_data else "attribute",
        )
        return super().load(json_data, *args, **kwargs)

    def dump(self, obj, *args, **kwargs):
        """Remove discriminator field after dumping."""
        result = super().dump(obj, *args, **kwargs)
        assert isinstance(result, dict)
        result.pop("_discriminator", None)
        return result


class ValuationClassSchema(JsonSchema):
    """Schema for variable valuations."""

    variables = fields.List(fields.Nested(ValuationFieldSchema), data_key="variables", required=True)

    @post_load
    def make_object(self, data: dict, **kwargs) -> umbi.datatypes.StructType:
        obj = super().make_object(data, **kwargs)
        return umbi.datatypes.StructType(
            fields=obj.variables,
        )

    def dump(self, obj, *args, **kwargs):
        assert isinstance(obj, umbi.datatypes.StructType)
        variables = []
        for f in obj.fields:
            if isinstance(f, umbi.datatypes.StructPadding):
                variables.append(ValuationPaddingSchema().dump(f))
            else:
                assert isinstance(f, umbi.datatypes.StructAttribute)
                variables.append(ValuationAttributeSchema().dump(f))
        obj_dict = {
            "variables": variables,
        }
        return obj_dict


class ValuationDescriptionSchema(JsonSchema):
    unique = fields.Boolean(data_key="unique", required=True)
    num_strings = FieldUint(data_key="#strings", required=False, validate=validate.Range(min=1))
    classes = fields.List(
        fields.Nested(ValuationClassSchema), data_key="classes", required=True, validate=validate.Length(min=1)
    )

    @classmethod
    def schema_class(cls) -> type:
        return ValuationDescription


@dataclass
class ValuationDescription(JsonSchemaResult):
    unique: bool = False
    num_strings: int | None = None
    classes: list[umbi.datatypes.StructType] = field(default_factory=list)

    @classmethod
    def class_schema(cls) -> type:
        return ValuationDescriptionSchema


class ValuationsSchema(fields.Dict):
    """Schema for variable valuations as a dictionary."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            keys=fields.String(validate=validate.OneOf(["states", "choices", "branches", "observations", "players"])),
            values=fields.Nested(ValuationDescriptionSchema),
            *args,
            **kwargs,
        )
