import itertools
import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import cast

from umbi.datatypes import (
    NumericPrimitiveType,
    NumericType,
    PrimitiveType,
    Scalar,
    ScalarType,
    scalar_promotion_type_of,
)

from .entity_class import EntityClass

logger = logging.getLogger(__name__)


@dataclass
class Annotation:
    """General annotation."""

    name: str
    alias: str | None = None
    description: str | None = None
    _entity_class_to_values: dict[EntityClass, list[Scalar]] = field(default_factory=dict[EntityClass, list[Scalar]])

    @classmethod
    def entity_class_enabled(cls, entity_class: EntityClass) -> bool:
        """Check if the given entity class is enabled for this annotation type. Can be overridden by subclasses to restrict which entity classes the annotation subclass can be applied to."""
        return True

    def __str__(self) -> str:
        s = f"Annotation(name={self.name!r}, alias={self.alias!r}, description={self.description!r}, values={{\n"
        indent_str = "  "
        for entity_class, values in self._entity_class_to_values.items():
            s += f"{indent_str}{entity_class}: {values}\n"
        s += "})"
        return s

    @property
    def mappings(self) -> dict[EntityClass, list[Scalar]]:
        """Alias for entity_class_to_values."""
        return self._entity_class_to_values

    @property
    def has_values(self) -> bool:
        """Check if the annotation has any values set."""
        return len(self._entity_class_to_values) > 0

    @property
    def entity_classes(self) -> set[EntityClass]:
        """Get the set of entity classes for which this annotation has values."""
        return set(self._entity_class_to_values.keys())

    def has_values_for(self, entity_class: EntityClass) -> bool:
        """Check if the annotation has values for the given entity class."""
        return self._entity_class_to_values.get(entity_class) is not None

    def get_values_for(self, entity_class: EntityClass) -> list[Scalar]:
        """
        Get the values for the given entity class.
        :raises KeyError: if no values are set for the given entity class
        """
        if not self.has_values_for(entity_class):
            raise KeyError(f"Annotation has no values for entity class {entity_class}")
        return self._entity_class_to_values[entity_class]

    def set_values_for(self, entity_class: EntityClass, values: Sequence[Scalar]) -> None:
        """Set the values for the given entity class."""
        if not self.entity_class_enabled(entity_class):
            raise ValueError(f"Entity class {entity_class} is not enabled for this annotation type")
        self._entity_class_to_values[entity_class] = list(values)

    def unset_values_for(self, entity_class: EntityClass) -> None:
        """Unset the values for the given entity class."""
        if not self.has_values_for(entity_class):
            raise KeyError(f"Annotation has no values for entity class {entity_class}")
        del self._entity_class_to_values[entity_class]

    ### Convenience properties and methods for each entity class ###
    @property
    def has_state_values(self) -> bool:
        return self.has_values_for(EntityClass.STATES)

    @property
    def has_choice_values(self) -> bool:
        return self.has_values_for(EntityClass.CHOICES)

    @property
    def has_branch_values(self) -> bool:
        return self.has_values_for(EntityClass.BRANCHES)

    @property
    def has_observation_values(self) -> bool:
        return self.has_values_for(EntityClass.OBSERVATIONS)

    @property
    def has_player_values(self) -> bool:
        return self.has_values_for(EntityClass.PLAYERS)

    @property
    def state_values(self) -> list[Scalar]:
        return self.get_values_for(EntityClass.STATES)

    @property
    def choice_values(self) -> list[Scalar]:
        return self.get_values_for(EntityClass.CHOICES)

    @property
    def branch_values(self) -> list[Scalar]:
        return self.get_values_for(EntityClass.BRANCHES)

    @property
    def observation_values(self) -> list[Scalar]:
        return self.get_values_for(EntityClass.OBSERVATIONS)

    @property
    def player_values(self) -> list[Scalar]:
        return self.get_values_for(EntityClass.PLAYERS)

    def set_state_values(self, values: Sequence[Scalar]):
        self.set_values_for(EntityClass.STATES, values)

    def set_choice_values(self, values: Sequence[Scalar]):
        self.set_values_for(EntityClass.CHOICES, values)

    def set_branch_values(self, values: Sequence[Scalar]):
        self.set_values_for(EntityClass.BRANCHES, values)

    def set_observation_values(self, values: Sequence[Scalar]):
        self.set_values_for(EntityClass.OBSERVATIONS, values)

    def set_player_values(self, values: Sequence[Scalar]):
        self.set_values_for(EntityClass.PLAYERS, values)

    def unset_state_values(self):
        self.unset_values_for(EntityClass.STATES)

    def unset_choice_values(self):
        self.unset_values_for(EntityClass.CHOICES)

    def unset_branch_values(self):
        self.unset_values_for(EntityClass.BRANCHES)

    def unset_observation_values(self):
        self.unset_values_for(EntityClass.OBSERVATIONS)

    def unset_player_values(self):
        self.unset_values_for(EntityClass.PLAYERS)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Annotation):
            return False
        return (
            self.name == other.name
            and self.alias == other.alias
            and self.description == other.description
            and self._entity_class_to_values == other._entity_class_to_values
        )

    def get_common_type(self) -> ScalarType:
        """
        Infer the common data type of annotation values.
        :raises ValueError: if the annotation has no values
        """
        return scalar_promotion_type_of(itertools.chain.from_iterable(self._entity_class_to_values.values()))

    def validate(self):
        """Validate the annotation data."""
        return

    def _reorder_entities(self, entity_class: EntityClass, new_order: list[int]) -> None:
        """Reorder the values for the given entity class according to the new order.

        :param entity_class: the entity class for which to reorder values
        :param new_order: a list of indices representing the new order of values. Must be a permutation of the full list of entity indices.
        """
        if not self.has_values_for(entity_class):
            return
        values = self._entity_class_to_values[entity_class]
        # we don't check the order
        self._entity_class_to_values[entity_class] = [values[i] for i in new_order]


class RewardAnnotation(Annotation):
    """Reward annotation is a numeric annotation that can be associated with states, choices, or branches."""

    @classmethod
    def entity_class_enabled(cls, entity_class: EntityClass) -> bool:
        return entity_class in {
            EntityClass.STATES,
            EntityClass.CHOICES,
            EntityClass.BRANCHES,
        }

    def validate(self):
        super().validate()
        type = self.get_common_type()
        if not isinstance(type, NumericType):
            raise ValueError(f"Reward annotation type must be NumericType, got {type}")


class AtomicPropositionAnnotation(Annotation):
    """Atomic proposition annotation is a boolean annotation that can only be associated with states."""

    @classmethod
    def entity_class_enabled(cls, entity_class: EntityClass) -> bool:
        return entity_class == EntityClass.STATES

    def validate(self):
        super().validate()
        type = self.get_common_type()
        if type != PrimitiveType.BOOL:
            raise ValueError(f"AP annotation type must be PrimitiveType.BOOL, got {type}")


@dataclass
class ObservationAnnotation(Annotation):
    """Observation annotation is an integer annotation that can only be associated with either states or branches."""

    def __init__(self, num_observations: int) -> None:
        super().__init__(name="observation")
        self.num_observations = num_observations

    @classmethod
    def entity_class_enabled(cls, entity_class: EntityClass) -> bool:
        return entity_class in {EntityClass.STATES, EntityClass.BRANCHES}

    @property
    def entity_class(self) -> EntityClass:
        """Get the entity class for which this observation annotation has values."""
        if not self.has_values:
            raise ValueError("Observation annotation does not have any values set")
        return next(iter(self.entity_classes))

    @property
    def values(self) -> list[int]:
        """Get the values for the entity class of this observation annotation."""
        return cast(list[int], self.get_values_for(self.entity_class))

    def set_values_for(self, entity_class: EntityClass, values: Sequence[Scalar]) -> None:
        if self.has_values and entity_class != self.entity_class:
            raise ValueError("Observation annotation can only have values for one entity class")
        return super().set_values_for(entity_class, values)

    def validate(self) -> None:
        super().validate()
        if not (0 < self.num_observations):
            raise ValueError(f"num_observations must be a positive integer, got {self.num_observations}")
        if self.get_common_type() != NumericPrimitiveType.INT:
            raise ValueError(f"Observation annotation type must be INT, got {self.get_common_type()}")
        for item, obs in enumerate(self.values):
            if not 0 <= obs < self.num_observations:  # type: ignore
                raise ValueError(f"observation mapping[{item}] = {obs} is out of range [0, {self.num_observations})")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ObservationAnnotation):
            return False
        return super().__eq__(other) and self.num_observations == other.num_observations
