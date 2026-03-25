"""
Main UMB index class and schema.
"""

from dataclasses import dataclass, field

from marshmallow import fields

from .annotations import AnnotationCategoryToAnnotationMap, AnnotationDescription
from .file_data import FileData, FileDataSchema
from .json_schema import (
    FieldUint32,
    JsonSchema,
    JsonSchemaResult,
)
from .model_data import ModelData, ModelDataSchema
from .transition_system import TransitionSystem, TransitionSystemSchema
from .valuations import ValuationDescription, ValuationsSchema


class UmbIndexSchema(JsonSchema):
    """UMB index file schema."""

    format_version = FieldUint32(data_key="format-version", required=True)
    format_revision = FieldUint32(data_key="format-revision", required=True)
    file_data = fields.Nested(FileDataSchema, data_key="file-data", required=False)
    model_data = fields.Nested(ModelDataSchema, data_key="model-data", required=False)
    transition_system = fields.Nested(TransitionSystemSchema, data_key="transition-system", required=True)
    annotations = AnnotationCategoryToAnnotationMap(data_key="annotations", required=False)
    valuations = ValuationsSchema(data_key="valuations", required=False)

    @classmethod
    def schema_class(cls) -> type:
        return UmbIndex


@dataclass
class UmbIndex(JsonSchemaResult):
    #: major version of format, change breaks compatibility
    format_version: int = 0
    #: minor version of format, nothing that breaks compatibility (additions and such)
    format_revision: int = 0
    file_data: FileData | None = field(default=None, compare=False)  # exclude from equality checks
    model_data: ModelData | None = None
    transition_system: TransitionSystem = field(default_factory=TransitionSystem)
    # TODO validate that reward annotations have continuous numeric type, applied to ?
    # TODO validate that ap annotations have boolean type, applied to states
    annotations: dict[str, dict[str, AnnotationDescription]] | None = None
    valuations: dict[str, ValuationDescription] | None = None

    @classmethod
    def class_schema(cls) -> type:
        return UmbIndexSchema

    def validate(self):
        """Validate the index data."""
        # validate syntacitally by converting to json and back
        self.from_json(self.to_json())
        # validate semantically
        if self.file_data is not None:
            self.file_data.validate()
        if self.model_data is not None:
            self.model_data.validate()
        self.transition_system.validate()
        if self.annotations is not None:
            for name_to_desc in self.annotations.values():
                for desc in name_to_desc.values():
                    desc.validate()
        if self.valuations is not None:
            for desc in self.valuations.values():
                desc.validate()
