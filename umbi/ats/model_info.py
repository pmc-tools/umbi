from dataclasses import dataclass


@dataclass
class ModelInfo:
    """Container to store information about the model."""

    name: str | None = None
    version: str | None = None
    authors: list[str] | None = None
    description: str | None = None
    comment: str | None = None
    doi: str | None = None
    url: str | None = None


class ModelInfoMixin:
    #: Information about the model.
    _model_info: ModelInfo | None = None

    @property
    def has_model_info(self) -> bool:
        return self._model_info is not None

    # getter and setter below are technically not needed since we can make _model_info public
    # but we keep them for consistency across mixins

    @property
    def model_info(self) -> ModelInfo | None:
        return self._model_info

    @model_info.setter
    def model_info(self, model_info: ModelInfo | None) -> None:
        self._model_info = model_info
