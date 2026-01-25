"""
Annotation schemas and classes.
"""

from dataclasses import dataclass
from typing import Literal, Type

from marshmallow import fields, validate

from umbi.datatypes import SizedType

from .type import SizedTypeSchema

from .json_schema import (
    JsonSchema,
    JsonSchemaResult,
)


class AnnotationSchema(JsonSchema):
    """Schema for one annotation."""

    alias = fields.String(data_key="alias", required=False)
    description = fields.String(data_key="description", required=False)
    applies_to = fields.List(
        fields.String(validate=validate.OneOf(["states", "choices", "branches"])),
        data_key="applies-to",
        required=False,
        validate=validate.Length(min=1),
    )
    type = fields.Nested(SizedTypeSchema, data_key="type", required=True)
    lower = fields.Integer(data_key="lower", required=False, validate=validate.Range(-(2**63), 2**63 - 1))
    upper = fields.Integer(data_key="upper", required=False, validate=validate.Range(-(2**63), 2**63 - 1))
    num_strings = fields.Integer(data_key="#strings", required=False, validate=validate.Range(1, 2**31 - 1))
    probability_type = fields.Nested(SizedTypeSchema, data_key="probability-type", required=False)

    @classmethod
    def schema_class(cls) -> Type:
        return Annotation


@dataclass
class Annotation(JsonSchemaResult):
    """Annotation data class."""

    alias: str | None = None
    description: str | None = None
    applies_to: list[Literal["states", "choices", "branches"]] | None = None
    type: SizedType | None = None
    lower: float | None = None
    upper: float | None = None
    num_strings: int | None = None
    probability_type: SizedType | None = None

    @classmethod
    def class_schema(cls) -> Type:
        return AnnotationSchema


class AnnotationMap(fields.Dict):
    """Marshmallow field for a map from keys to AnnotationMap values."""

    def __init__(self, *args, **kwargs):
        super().__init__(keys=fields.String(), values=fields.Nested(AnnotationSchema), *args, **kwargs)


class AnnotationTypeToAnnotationMap(fields.Dict):
    """Marshmallow field for a map from annotation category to a key-to-annotation map."""

    def __init__(self, *args, **kwargs):
        super().__init__(keys=fields.String(), values=AnnotationMap(), *args, **kwargs)
