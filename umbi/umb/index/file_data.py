"""
File data schemas and classes.
"""

import time
from dataclasses import dataclass

from marshmallow import fields

import umbi.datatypes
import umbi.version

from .json_schema import (
    FieldUint64,
    JsonSchema,
    JsonSchemaResult,
)


class FileDataSchema(JsonSchema):
    """File data schema."""

    tool = fields.String(data_key="tool", required=False)
    tool_version = fields.String(data_key="tool-version", required=False)
    creation_date = FieldUint64(data_key="creation-date", required=False)
    parameters = fields.Raw(data_key="parameters", required=False)

    @classmethod
    def schema_class(cls) -> type:
        return FileData


@dataclass
class FileData(JsonSchemaResult):
    """File data class."""

    tool: str | None = None
    tool_version: str | None = None
    creation_date: int | None = None
    parameters: umbi.datatypes.JsonLike | None = None

    @classmethod
    def class_schema(cls) -> type:
        return FileDataSchema


def umbi_file_data() -> FileData:
    """Generate file data for use in umbfiles created by umbi."""
    return FileData(
        tool=umbi.version.__toolname__,
        tool_version=umbi.version.__version__,
        creation_date=int(time.time()),
        # parameters=parameters,
    )
