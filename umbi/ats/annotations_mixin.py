import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

from .annotations import (
    Annotation,
    AtomicPropositionAnnotation,
    ObservationAnnotation,
    RewardAnnotation,
)
from .entity_space_mixins import HasCommonEntitySpaces


@dataclass
class AnnotationsMixin(HasCommonEntitySpaces):
    #: Annotation category -> (annotation name -> annotation) mapping. Categories 'rewards' and 'aps' can be used, but
    #: must be of the type RewardAnnotation and AtomicPropositionAnnotation, respectively.
    _annotations: dict[str, dict[str, Annotation]] = field(default_factory=lambda: {})

    @property
    def annotations(self) -> dict[str, dict[str, Annotation]]:
        """Get the annotations of the ATS."""
        return self._annotations

    @property
    def annotation_categories(self) -> list[str]:
        """Get the annotation categories of the ATS."""
        return list(self.annotations.keys())

    def new_annotation(self, category: str, name: str, **kwargs) -> Annotation:
        """Add an annotation to the ATS."""
        if category not in self.annotations:
            self.annotations[category] = {}
        if name in self.annotations[category]:
            raise ValueError(f"annotation with name {name} already exists in category {category}")
        annotation = Annotation(name=name, entity_spaces=self._common_entity_spaces, **kwargs)
        self.annotations[category][name] = annotation
        return annotation

    @property
    def reward_annotations(self) -> dict[str, RewardAnnotation]:
        """Get the reward annotations."""
        if "rewards" not in self.annotations:
            self.annotations["rewards"] = {}
        return self.annotations["rewards"]  # type: ignore

    @property
    def has_reward_annotations(self) -> bool:
        """Check if there are any reward annotations."""
        return len(self.reward_annotations) > 0

    @property
    def reward_annotation_names(self) -> list[str]:
        """Get the names of all reward annotations."""
        return list(self.reward_annotations.keys())

    def has_reward_annotation(self, name: str) -> bool:
        """Check if a reward annotation with the given name exists."""
        return name in self.reward_annotations

    def new_reward_annotation(self, name: str, **kwargs) -> RewardAnnotation:
        """Add a reward annotation."""
        if self.has_reward_annotation(name):
            raise ValueError(f"reward annotation with name {name} already exists")
        annotation = RewardAnnotation(name=name, entity_spaces=self._common_entity_spaces, **kwargs)
        self.reward_annotations[name] = annotation
        return annotation

    def get_reward_annotation(self, name: str) -> RewardAnnotation:
        """Get the reward annotation with the given name."""
        if not self.has_reward_annotation(name):
            raise ValueError(f"reward annotation with name {name} does not exist")
        return self.reward_annotations[name]

    ### Atomic propositions. ###

    @property
    def has_ap_annotations(self) -> bool:
        """Check if there are any atomic proposition annotations."""
        return len(self.ap_annotations) > 0

    @property
    def ap_annotations(self) -> dict[str, AtomicPropositionAnnotation]:
        """Get the atomic proposition annotations."""
        if "aps" not in self.annotations:
            self.annotations["aps"] = {}
        return self.annotations["aps"]  # type: ignore

    @property
    def ap_annotation_names(self) -> list[str]:
        """Get the names of all atomic proposition annotations."""
        return list(self.ap_annotations.keys())

    def has_ap_annotation(self, name: str) -> bool:
        """Check if an atomic proposition annotation with the given name exists."""
        return name in self.ap_annotations

    def new_ap_annotation(self, name: str, **kwargs) -> AtomicPropositionAnnotation:
        """Add an atomic proposition annotation."""
        if self.has_ap_annotation(name):
            raise ValueError(f"atomic proposition annotation with name {name} already exists")
        annotation = AtomicPropositionAnnotation(name=name, entity_spaces=self._common_entity_spaces, **kwargs)
        self.ap_annotations[name] = annotation
        return annotation

    def get_ap_annotation(self, name: str) -> AtomicPropositionAnnotation:
        """Get the atomic proposition annotation with the given name."""
        if not self.has_ap_annotation(name):
            raise ValueError(f"atomic proposition annotation with name {name} does not exist")
        return self.ap_annotations[name]

    def validate(self):
        """Validate annotations of the ATS."""
        for _, annotations in self.annotations.items():
            for _, annotation in annotations.items():
                annotation.validate()
        super().validate()


class ObservationAnnotationMixin(HasCommonEntitySpaces):
    #: Observation annotation.
    _observation_annotation: ObservationAnnotation | None = None

    def __post_init__(self):
        self._observation_space._subscribe(
            self,
            lambda num_observations: ObservationAnnotationMixin._on_num_observations_changed(self, num_observations),
        )
        super().__post_init__()

    def _on_num_observations_changed(self, num_observations: int) -> None:
        if self.has_observation_annotation and num_observations == 0:
            logger.debug("num_observations changed to 0, removing observation annotation")
            self._remove_observation_annotation()
        if not self.has_observation_annotation and num_observations > 0:
            logger.debug("num_observations changed to >0, adding observation annotation")
            self._add_observation_annotation()

    @property
    def has_observation_annotation(self) -> bool:
        """Check if the ATS has an observation annotation."""
        return self._observation_annotation is not None

    @property
    def observation_annotation(self) -> ObservationAnnotation:
        """Get the observation annotation of the ATS."""
        if self._observation_annotation is None:
            raise ValueError("observation_annotation is not set")
        return self._observation_annotation

    def _add_observation_annotation(self):
        """Add an observation annotation to the ATS."""
        if self.has_observation_annotation:
            return
        self._observation_annotation = ObservationAnnotation(entity_spaces=self._common_entity_spaces)

    def _remove_observation_annotation(self):
        """Remove the observation annotation from the ATS."""
        if not self.has_observation_annotation:
            return
        self._observation_annotation = None

    def validate(self) -> None:
        if self.has_observation_annotation:
            self.observation_annotation.validate()
        super().validate()


class ObservationsMixin(ObservationAnnotationMixin):
    def __post_init__(self):
        super().__post_init__()
