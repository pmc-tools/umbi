from dataclasses import dataclass, field
from umbi.datatypes import (
    AtomicType,
    DataType,
    NumericType,
    NumericPrimitiveType,
    common_datatype,
)

from .entity_class import EntityClass
from .custom_lists import TypedIterable
import logging

logger = logging.getLogger(__name__)


class EntityToValue(list, TypedIterable):
    """A list of values associated with entities of a certain class."""

    pass


@dataclass
class Annotation:
    """General annotation."""

    name: str
    alias: str | None = None
    description: str | None = None
    entity_class_to_values: dict[EntityClass, EntityToValue] = field(default_factory=dict[EntityClass, EntityToValue])

    @classmethod
    def entity_class_enabled(cls, entity_class: EntityClass) -> bool:
        """Check if the given entity class is enabled for this annotation type. Can be overridden by subclasses."""
        return True

    @property
    def mappings(self) -> dict[EntityClass, EntityToValue]:
        """Alias for entity_class_to_values."""
        return self.entity_class_to_values

    @property
    def has_values(self) -> bool:
        """Check if the annotation has any values set."""
        return len(self.entity_class_to_values) > 0

    @property
    def entity_classes(self) -> set[EntityClass]:
        """Get the set of entity classes for which this annotation has values."""
        return set(self.entity_class_to_values.keys())

    def has_values_for(self, entity_class: EntityClass) -> bool:
        """Check if the annotation has values for the given entity class."""
        return self.entity_class_to_values.get(entity_class) is not None

    def get_values_for(self, entity_class: EntityClass) -> EntityToValue:
        """
        Get the values for the given entity class.
        :raises KeyError: if no values are set for the given entity class
        """
        if not self.has_values_for(entity_class):
            raise KeyError(f"Annotation has no values for entity class {entity_class}")
        return self.entity_class_to_values[entity_class]

    def set_values_for(self, entity_class: EntityClass, values: EntityToValue | list) -> None:
        """Set the values for the given entity class."""
        if not self.entity_class_enabled(entity_class):
            raise ValueError(f"Entity class {entity_class} is not enabled for this annotation type")
        if isinstance(values, list):
            values = EntityToValue(values)
        self.entity_class_to_values[entity_class] = values

    def unset_values_for(self, entity_class: EntityClass) -> None:
        """Unset the values for the given entity class."""
        if not self.has_values_for(entity_class):
            raise KeyError(f"Annotation has no values for entity class {entity_class}")
        del self.entity_class_to_values[entity_class]

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
        return self.has_values_for(EntityClass.OBSERVATION)

    @property
    def has_player_values(self) -> bool:
        return self.has_values_for(EntityClass.PLAYERS)

    @property
    def state_values(self) -> EntityToValue:
        return self.get_values_for(EntityClass.STATES)

    @property
    def choice_values(self) -> EntityToValue:
        return self.get_values_for(EntityClass.CHOICES)

    @property
    def branch_values(self) -> EntityToValue:
        return self.get_values_for(EntityClass.BRANCHES)

    @property
    def observation_values(self) -> EntityToValue:
        return self.get_values_for(EntityClass.OBSERVATION)

    @property
    def player_values(self) -> EntityToValue:
        return self.get_values_for(EntityClass.PLAYERS)

    def set_state_values(self, values: EntityToValue | list):
        self.set_values_for(EntityClass.STATES, values)

    def set_choice_values(self, values: EntityToValue | list):
        self.set_values_for(EntityClass.CHOICES, values)

    def set_branch_values(self, values: EntityToValue | list):
        self.set_values_for(EntityClass.BRANCHES, values)

    def set_observation_values(self, values: EntityToValue | list):
        self.set_values_for(EntityClass.OBSERVATION, values)

    def set_player_values(self, values: EntityToValue | list):
        self.set_values_for(EntityClass.PLAYERS, values)

    def unset_state_values(self):
        self.unset_values_for(EntityClass.STATES)

    def unset_choice_values(self):
        self.unset_values_for(EntityClass.CHOICES)

    def unset_branch_values(self):
        self.unset_values_for(EntityClass.BRANCHES)

    def unset_observation_values(self):
        self.unset_values_for(EntityClass.OBSERVATION)

    def unset_player_values(self):
        self.unset_values_for(EntityClass.PLAYERS)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Annotation):
            return False
        return (
            self.name == other.name
            and self.alias == other.alias
            and self.description == other.description
            and self.entity_class_to_values == other.entity_class_to_values
        )

    @property
    def common_type(self) -> DataType:
        """Infer the data type of the annotation from its values."""
        types: set[DataType] = set()
        for v in self.entity_class_to_values.values():
            types.add(v.type)
        if len(types) == 0:
            raise ValueError("Annotation has no values to infer type from")
        return common_datatype(types)

    def validate(self):
        """Validate the annotation data."""
        if not isinstance(self.name, str):
            raise ValueError("name must be a string")
        if not isinstance(self.alias, (str, type(None))):
            raise ValueError("alias must be a string or None")
        if not isinstance(self.description, (str, type(None))):
            raise ValueError("description must be a string or None")
        return


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
        # Additional validation for reward annotations can be added here
        type = self.common_type
        if not isinstance(type, NumericType):
            raise ValueError(f"Reward annotation type must be NumericType, got {type}")


class AtomicPropositionAnnotation(Annotation):
    """Atomic proposition annotation is a boolean annotation that can only be associated with states."""

    @classmethod
    def entity_class_enabled(cls, entity_class: EntityClass) -> bool:
        return entity_class == EntityClass.STATES

    def validate(self):
        super().validate()
        # Additional validation for AP annotations can be added here
        type = self.common_type
        if type != AtomicType.BOOL:
            raise ValueError(f"AP annotation type must be AtomicType.BOOL, got {type}")


@dataclass
class ObservationAnnotation(Annotation):
    """Observation annotation is an integer annotation that can only be associated with either states or branches."""

    def __init__(self, num_observations: int):
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
    def values(self) -> EntityToValue:
        """Get the values for the entity class of this observation annotation."""
        return self.get_values_for(self.entity_class)

    def set_values_for(self, entity_class: EntityClass, values: EntityToValue | list):
        if self.has_values and entity_class != self.entity_class:
            raise ValueError("Observation annotation can only have values for one entity class")
        return super().set_values_for(entity_class, values)

    def validate(self) -> None:
        super().validate()
        if not (isinstance(self.num_observations, int) and 0 < self.num_observations):
            raise ValueError(f"num_observations must be a positive integer, got {self.num_observations}")
        if self.common_type != NumericPrimitiveType.INT:
            raise ValueError(f"Observation annotation type must be INT, got {self.common_type}")
        for item, obs in enumerate(self.values):
            if not 0 <= obs < self.num_observations:  # type: ignore
                raise ValueError(f"observation mapping[{item}] = {obs} is out of range [0, {self.num_observations})")

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.num_observations == other.num_observations
