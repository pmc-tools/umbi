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

from .entity_space import EntityClass, EntityMapping, EntitySpace, OptionalMappingManager

logger = logging.getLogger(__name__)


@dataclass
class Annotation:
    """General annotation."""

    name: str
    entity_spaces: dict[EntityClass, EntitySpace]
    alias: str | None = None
    description: str | None = None
    _entity_managers: dict[EntityClass, OptionalMappingManager] = field(default_factory=dict)

    @classmethod
    def entity_class_enabled(cls, entity_class: EntityClass) -> bool:
        """Check if the given entity class is enabled for this annotation type. Can be overridden by subclasses to restrict which entity classes the annotation subclass can be applied to."""
        return True

    def __post_init__(self):
        for entity_class in EntityClass:
            assert entity_class in self.entity_spaces, f"Entity space for {entity_class} must be provided"
            self._entity_managers[entity_class] = OptionalMappingManager[Scalar](
                name=f"{self.name}::{entity_class.value}_to_value",
                domain=self.entity_spaces[entity_class],
                can_have_mapping=lambda entity_class=entity_class: self.entity_class_enabled(entity_class),
            )
            self.entity_spaces[entity_class]._subscribe(
                self, lambda *args: self._entity_managers[entity_class].auto_manage()
            )

    @property
    def _state_values_manager(self) -> OptionalMappingManager[Scalar]:
        return self._entity_managers[EntityClass.STATES]

    @property
    def _choice_values_manager(self) -> OptionalMappingManager[Scalar]:
        return self._entity_managers[EntityClass.CHOICES]

    @property
    def _branch_values_manager(self) -> OptionalMappingManager[Scalar]:
        return self._entity_managers[EntityClass.BRANCHES]

    @property
    def _player_values_manager(self) -> OptionalMappingManager[Scalar]:
        return self._entity_managers[EntityClass.PLAYERS]

    @property
    def _observation_values_manager(self) -> OptionalMappingManager[Scalar]:
        return self._entity_managers[EntityClass.OBSERVATIONS]

    def add_state_values(self):
        self._state_values_manager.create_mapping()

    def remove_state_values(self):
        self._state_values_manager.remove_mapping()

    @property
    def has_state_values(self) -> bool:
        return self._state_values_manager.has_mapping

    @property
    def state_values(self) -> EntityMapping[Scalar]:
        return self._state_values_manager.mapping

    @state_values.setter
    def state_values(self, values: Sequence[Scalar] | None) -> None:
        self._state_values_manager.mapping = values

    def add_choice_values(self):
        self._choice_values_manager.create_mapping()

    def remove_choice_values(self):
        self._choice_values_manager.remove_mapping()

    @property
    def has_choice_values(self) -> bool:
        return self._choice_values_manager.has_mapping

    @property
    def choice_values(self) -> EntityMapping[Scalar]:
        return self._choice_values_manager.mapping

    @choice_values.setter
    def choice_values(self, values: Sequence[Scalar] | None) -> None:
        self._choice_values_manager.mapping = values

    def add_branch_values(self):
        self._branch_values_manager.create_mapping()

    def remove_branch_values(self):
        self._branch_values_manager.remove_mapping()

    @property
    def has_branch_values(self) -> bool:
        return self._branch_values_manager.has_mapping

    @property
    def branch_values(self) -> EntityMapping[Scalar]:
        return self._branch_values_manager.mapping

    @branch_values.setter
    def branch_values(self, values: Sequence[Scalar] | None) -> None:
        self._branch_values_manager.mapping = values

    def add_player_values(self):
        self._player_values_manager.create_mapping()

    def remove_player_values(self):
        self._player_values_manager.remove_mapping()

    @property
    def has_player_values(self) -> bool:
        return self._player_values_manager.has_mapping

    @property
    def player_values(self) -> EntityMapping[Scalar]:
        return self._player_values_manager.mapping

    @player_values.setter
    def player_values(self, values: Sequence[Scalar] | None) -> None:
        self._player_values_manager.mapping = values

    def add_observation_values(self):
        self._observation_values_manager.create_mapping()

    def remove_observation_values(self):
        self._observation_values_manager.remove_mapping()

    @property
    def has_observation_values(self) -> bool:
        return self._observation_values_manager.has_mapping

    @property
    def observation_values(self) -> EntityMapping[Scalar]:
        return self._observation_values_manager.mapping

    @observation_values.setter
    def observation_values(self, values: Sequence[Scalar] | None) -> None:
        self._observation_values_manager.mapping = values

    def validate(self):
        for manager in self._entity_managers.values():
            manager.validate()

    def __str__(self) -> str:
        s = f"Annotation(name={self.name!r}, alias={self.alias!r}, description={self.description!r}, values={{\n"
        indent_str = "  "
        for entity_class, values in self._entity_class_to_values.items():
            s += f"{indent_str}{entity_class}: {values}\n"
        s += "})"
        return s

    ### legacy methods

    @property
    def _entity_class_to_values(self) -> dict[EntityClass, EntityMapping[Scalar]]:
        """Get a mapping from entity class to the corresponding values mapping for this annotation."""
        entity_class_to_values = {}
        for entity_class, manager in self._entity_managers.items():
            if manager.has_mapping:
                entity_class_to_values[entity_class] = manager.mapping
        return entity_class_to_values

    # @property
    # def mappings(self) -> dict[EntityClass, EntityMapping[Scalar]]:
    #     """Alias for entity_class_to_values."""
    #     return self._entity_class_to_values

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

    def get_values_for(self, entity_class: EntityClass) -> EntityMapping[Scalar]:
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
        self._entity_managers[entity_class].mapping = values

    def remove_values_for(self, entity_class: EntityClass) -> None:
        """Remove the values for the given entity class."""
        if not self.has_values_for(entity_class):
            raise KeyError(f"Annotation has no values for entity class {entity_class}")
        del self._entity_class_to_values[entity_class]

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

    def __init__(self, **kwargs) -> None:
        super().__init__(name="observation", **kwargs)
        self._entity_managers[EntityClass.STATES].codomain = self.entity_spaces[EntityClass.OBSERVATIONS]
        self._entity_managers[EntityClass.BRANCHES].codomain = self.entity_spaces[EntityClass.OBSERVATIONS]

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
        datatype = self.get_common_type()
        if datatype != NumericPrimitiveType.INT:
            raise ValueError(f"Observation annotation type must be INT, got {datatype}")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ObservationAnnotation):
            return False
        return super().__eq__(other)
