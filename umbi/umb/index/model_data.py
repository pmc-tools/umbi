"""Model data schemas and classes."""

from dataclasses import dataclass

from marshmallow import fields

from .json_schema import (
    JsonSchema,
    JsonSchemaResult,
)


class ModelDataSchema(JsonSchema):
    """Model data schema."""

    name = fields.String(data_key="name", required=False)
    version = fields.String(data_key="version", required=False)
    authors = fields.List(fields.String(), data_key="authors", required=False)
    description = fields.String(data_key="description", required=False)
    comment = fields.String(data_key="comment", required=False)
    doi = fields.String(data_key="doi", required=False)
    url = fields.String(data_key="url", required=False)

    @classmethod
    def schema_class(cls) -> type:
        return ModelData


@dataclass
class ModelData(JsonSchemaResult):
    """Model data class.

    Information about the model that this file represents.
    """

    #: the (short) name of the model
    name: str | None = None
    #: information about the version of this model (e.g. the date when it was last modified)
    version: str | None = None
    #: information about the creators of the model
    authors: list[str] | None = None
    #: a description of the model
    description: str | None = None
    #: additional comments
    comment: str | None = None
    #: the DOI of the paper where this model was introduced/used/described
    doi: str | None = None
    #: a URL pointing to more information about the model
    url: str | None = None

    @classmethod
    def class_schema(cls) -> type:
        return ModelDataSchema
