import logging
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Iterable, Sequence, TypeVar

import inflect

logger = logging.getLogger(__name__)
_inflect_engine = inflect.engine()


class EntityClass(str, Enum):
    """Entity type of a transition system the values are usually associated with."""

    STATES = "states"
    CHOICES = "choices"
    BRANCHES = "branches"
    OBSERVATIONS = "observations"
    PLAYERS = "players"


@dataclass
class Observable:
    """Simple observable class that allows observers to subscribe to changes."""

    _observer_callback: list[Callable[[Any], None]] = field(default_factory=list)

    def _subscribe(self, observer: object, callback: Callable[[Any], None]):
        self._observer_callback.append(callback)

    def _notify_changed(self, *args, **kwargs):
        """Notify all observers of the given event."""
        for callback in self._observer_callback:
            callback(*args, **kwargs)

    def __eq__(self, other: object) -> bool:
        """Observable ignores _observer_callback (infrastructure).
        Subclasses should override for meaningful equality."""
        if not isinstance(other, Observable):
            return False
        # Infrastructure callbacks don't affect equality
        return True


@dataclass
class EntitySpace(Observable):
    """Base class for managing a finite collection of entities (e.g. states, choices, etc.) in an ATS."""

    #: Number of entities in the space.
    _num_entities: int = 0
    #: List of entity mappings whose domain corresponds to this entity space.
    _subscribers_domain: list["EntityMapping"] = field(default_factory=list)
    #: List of entity mappings whose codomain corresponds to this entity space.
    _subscribers_codomain: list["EntityMapping"] = field(default_factory=list)

    @property
    def entity_name(self) -> str:
        """Name of the entity type.
        Used for logging. Subclasses should override this to (e.g. to "state", "choice", etc.) to yield a more informative name."""
        return "entity"

    @property
    def entities_name(self) -> str:
        return _inflect_engine.plural(self.entity_name)  # type: ignore

    def _subscribe_domain(self, mapping: "EntityMapping"):
        """Subscribe the given entity mapping as a domain."""
        self._subscribers_domain.append(mapping)

    def _unsubscribe_domain(self, mapping: "EntityMapping"):
        """Unsubscribe the given entity mapping as a domain."""
        self._subscribers_domain.remove(mapping)

    def _subscribe_codomain(self, mapping: "EntityMapping"):
        """Subscribe the given entity mapping as a codomain."""
        self._subscribers_codomain.append(mapping)

    def _unsubscribe_codomain(self, mapping: "EntityMapping"):
        """Unsubscribe the given entity mapping as a codomain."""
        self._subscribers_codomain.remove(mapping)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(num_{self.entities_name}={self.num_entities})"

    def __eq__(self, other: object) -> bool:
        """Compare entity spaces by their number of entities.
        Ignores _subscribers_domain (infrastructure)."""
        if not isinstance(other, EntitySpace):
            return False
        # _subscribers_domain is infrastructure, doesn't affect equality
        return self._num_entities == other._num_entities

    @property
    def num_entities(self) -> int:
        return self._num_entities

    @num_entities.setter
    def num_entities(self, num_entities: int):
        if num_entities < 0:
            raise ValueError(f"num_{self.entities_name} must be >= 0")
        if self._num_entities > num_entities:
            # remove extra entities from the end
            self.remove_entities(list(range(num_entities, self._num_entities)))
        elif self._num_entities < num_entities:
            # add new entities to the end
            self.new_entities(num_entities - self._num_entities)

    @property
    def has_entities(self) -> bool:
        return self.num_entities > 0

    @property
    def entities(self) -> Iterable[int]:
        return range(self.num_entities)

    def __contains__(self, entity: int) -> bool:
        """Check if the given entity index is valid."""
        return 0 <= entity < self.num_entities

    def check_entity(self, entity: int, raise_exception: bool = True) -> bool:
        """Check if the given entity index is valid."""
        if entity not in self:
            if raise_exception:
                raise ValueError(f"Invalid {self.entity_name} index {entity}, must be in [0, {self.num_entities - 1}].")
            return False
        return True

    def new_entity(self) -> int:
        """Create a new entity and return its index."""
        new_entity = self.num_entities
        self._num_entities += 1
        for mapping in self._subscribers_domain:
            mapping._on_new_domain_entity(new_entity)
        self._notify_changed(self._num_entities)
        return new_entity

    def new_entities(self, num_new_entities: int) -> list[int]:
        """Create the given number of new entities.
        :param num_new_entities: number of entities to create
        :return: list of indices of the new entities
        """
        new_entities = list(range(self.num_entities, self.num_entities + num_new_entities))
        self._num_entities += num_new_entities
        for mapping in self._subscribers_domain:
            mapping._on_new_domain_entities(num_new_entities)
        self._notify_changed(self._num_entities)
        return new_entities

    def _new_to_old_to_old_to_new(self, new_to_old: Sequence[int]) -> list[int | None]:
        """Given a new_to_old mapping, compute the corresponding old_to_new mapping."""
        old_to_new: list[int | None] = [None] * self.num_entities
        for new_entity, old_entity in enumerate(new_to_old):
            old_to_new[old_entity] = new_entity
        return old_to_new

    def remove_entity(self, entity: int) -> list[int]:
        """Remove the given entity from the space.
        :param entity: index of the entity to remove
        :return: new_to_old mapping of the remaining entities after the removal
        """
        logger.debug(f"removing {self.entity_name} {entity}")
        self.check_entity(entity)
        new_to_old = [i if i < entity else i + 1 for i in range(self._num_entities - 1)]
        old_to_new = self._new_to_old_to_old_to_new(new_to_old)
        self._num_entities -= 1
        for mapping in self._subscribers_domain:
            mapping._on_remove_domain_entity(entity)
        for mapping in self._subscribers_codomain:
            mapping._on_remove_codomain_entities(old_to_new)
        self._notify_changed(self._num_entities)
        return new_to_old

    def remove_entities(self, entities: Sequence[int]) -> list[int]:
        """Remove the given entities from the space.
        :param entities: indices of the entities to remove
        :return: new_to_old mapping of the remaining entities after the removal
        """
        for entity in entities:
            self.check_entity(entity)
        logger.debug(f"removing {self.entities_name} {entities}")
        entities = sorted(entities)
        new_to_old = []
        removed_count = 0
        for i in range(self._num_entities):
            if removed_count < len(entities) and i == entities[removed_count]:
                removed_count += 1
            else:
                new_to_old.append(i)
        old_to_new = self._new_to_old_to_old_to_new(new_to_old)
        self._num_entities -= len(entities)
        for mapping in self._subscribers_domain:
            mapping._on_remove_domain_entities(entities)
        for mapping in self._subscribers_codomain:
            mapping._on_remove_codomain_entities(old_to_new)
        self._notify_changed(self._num_entities)
        return new_to_old

    def check_permutation(self, new_to_old: Sequence[int]) -> bool:
        """Check if the given new_to_old mapping is a valid permutation of the entities.
        :param new_to_old: new_to_old mapping to check
        :raises ValueError: if the mapping is not a valid permutation
        :return: whether the permutation is non-trivial (i.e. will change the order of the entities)"""
        new_to_old_sorted = sorted(new_to_old)
        if new_to_old_sorted != list(self.entities):
            raise ValueError(
                f"Invalid permutation {new_to_old}, must be a rearrangement of [0, {self._num_entities - 1}]."
            )
        return new_to_old != new_to_old_sorted

    def permute_entities(self, new_to_old: Sequence[int]) -> None:
        if not self.check_permutation(new_to_old):
            return
        logger.debug(f"permuting {self.entities_name} with new_to_old={new_to_old}")
        for mapping in self._subscribers_domain:
            mapping._on_permute_domain(new_to_old)
        old_to_new = self._new_to_old_to_old_to_new(new_to_old)
        for mapping in self._subscribers_codomain:
            mapping._on_permute_codomain(old_to_new)  # type: ignore[assignment] old_to_new cannot have None values
        self._notify_changed(self._num_entities)


### Entity space mapping.


T = TypeVar("T")


@dataclass
class EntityMapping(list[T]):
    """A mapping from an entity space to some values."""

    #: Name of the mapping, used for logging and error messages.
    name: str
    #: Entity space this mapping maps from.
    domain: EntitySpace
    #: Default value factory for new entities. Can be None to represent undefined values.
    default_factory: Callable[[], T] | None = None
    #: Entity space this mapping maps to.
    codomain: EntitySpace | None = None
    #: Whether this maps to the powerset of the codomain.
    maps_to_powerset: bool = False

    def __post_init__(self):
        self.domain._subscribe_domain(self)
        if self.codomain is not None:
            self.codomain._subscribe_codomain(self)
        self.reset()

    def __str__(self):
        return list.__str__(self)

    def __repr__(self):
        return list.__repr__(self)

    def __eq__(self, other: object) -> bool:
        """Compare entity mappings by their list contents."""
        if not isinstance(other, EntityMapping):
            return False
        return list.__eq__(self, other)

    def _unsubscribe(self):
        """Unsubscribe this mapping from its domain and codomain. Called when the mapping is removed."""
        self.domain._unsubscribe_domain(self)
        if self.codomain is not None:
            self.codomain._unsubscribe_codomain(self)

    def _default_value(self) -> T | None:
        """Create a default item using the default factory."""
        return self.default_factory() if self.default_factory is not None else None

    def reset(self):
        """Reset the mapping to the default value for all entities."""
        self.clear()
        self._on_new_domain_entities(self.domain.num_entities)

    def _check_input_value(self, value: T | None, accept_none: bool = True):
        """Check if the given value is valid for the codomain, if applicable."""
        if value is None and not accept_none:
            raise ValueError("None value is not accepted for this mapping.")
        if self.codomain is None:
            return
        if not isinstance(value, int):
            raise ValueError(
                f"Modifying {self.name} failed: invalid value {value} for mapping with codomain {self.codomain.entity_name}, expected an integer value."
            )
        self.codomain.check_entity(value)

    def _check_input_sequence(self, input_list: Sequence[T]):
        """Check if the given sequence is valid for setting the mapping values."""
        if len(input_list) != self.domain.num_entities:
            raise ValueError(
                f"Modifying {self.name} failed: input list length {len(input_list)} does not match the number of {self.domain.entities_name} {self.domain.num_entities}."
            )
        [self._check_input_value(value) for value in input_list]

    def _set_values(self, values: Sequence[T]):
        """Set the values of the mapping to the given sequence. The length of the sequence must match the number of entities in the associated entity space."""
        self._check_input_sequence(values)
        for i, value in enumerate(values):
            self[i] = value

    def _on_new_domain_entity(self, entity: int):
        assert entity == len(self), f"Invalid entity index {entity} for addition, expected {len(self)}."
        logger.debug(f"{self.name}: adding new entity {entity} with default value {self._default_value()}")
        self.append(self._default_value())  # type: ignore[assignment]

    def _on_new_domain_entities(self, num_new_entities: int):
        assert len(self) + num_new_entities == self.domain.num_entities
        logger.debug(f"{self.name}: adding {num_new_entities} new entities with default value {self._default_value()}")
        self.extend(self._default_value() for _ in range(num_new_entities))  # type: ignore[assignment]

    def _on_remove_domain_entity(self, entity: int):
        logger.debug(f"{self.name}: removing domain entity {entity}")
        del self[entity]

    def _on_remove_domain_entities(self, entities: Sequence[int]):
        """Remove the given entities from the mapping. The entities must be given in a sequence sorted in a ascending order."""
        assert len(self) - len(entities) == self.domain.num_entities
        assert all(entities[i] < entities[i + 1] for i in range(len(entities) - 1)), (
            "Entities to remove must be given in a sequence sorted in a ascending order."
        )
        logger.debug(f"{self.name}: removing domain entities {entities}")
        for entity in reversed(entities):
            del self[entity]

    def _on_remove_codomain_entities(self, old_to_new: Sequence[int | None]):
        logger.debug(f"{self.name}: removing codomain entities with old_to_new {old_to_new}")
        # assert all(isinstance(value, int) for value in self), f"Invalid mapping values {self} for codomain permutation, expected all values to be integers corresponding to indices of the codomain."
        if not self.maps_to_powerset:
            for i, value in enumerate(self):
                if value is not None:
                    assert isinstance(value, int), (
                        f"Invalid mapping value {value} at index {i} for codomain permutation, expected an integer corresponding to an index of the codomain."
                    )
                    new_value = old_to_new[value]
                    if new_value is None:
                        logger.debug(
                            f"{self.name}: value {value} at index {i} is invalidated due to codomain entity removal"
                        )
                    self[i] = new_value  # type: ignore[assignment]
        else:
            for i, values in enumerate(self):
                assert all(isinstance(value, int) for value in values)  # type: ignore check
                self[i] = [old_to_new[v] for v in values]  # type: ignore[assignment]

    def _on_permute_domain(self, new_to_old: Sequence[int]):
        assert len(self) == self.domain.num_entities
        logger.debug(f"{self.name}: permuting domain with new_to_old={new_to_old}")
        new_self = [self[old_entity] for old_entity in new_to_old]
        self.clear()
        self.extend(new_self)

    def _on_permute_codomain(self, old_to_new: Sequence[int]):
        logger.debug(f"{self.name}: permuting codomain with old_to_new={old_to_new}")
        assert self.codomain is not None
        if not self.maps_to_powerset:
            assert all(isinstance(value, int) for value in self), (
                f"Invalid mapping values {self} for permutation, expected all values to be integers corresponding to indices of the codomain."
            )
            new_self = [old_to_new[value] for value in self]  # type: ignore
            self.clear()
            self.extend(new_self)
        else:
            new_self = []
            for values in self:
                assert all(isinstance(value, int) for value in values)  # type: ignore check
                new_values = [old_to_new[v] for v in values]  # type: ignore
                new_self.append(new_values)
            self.clear()
            self.extend(new_self)

    def has_undefined_values(self) -> bool:
        """Check if the mapping contains any undefined values."""
        return any(value is None for value in self)

    def validate(self, allow_undefined_values: bool = False) -> None:
        """Validate that the entity mapping contains no undefined values."""
        assert len(self) == self.domain.num_entities
        for entity_index, entity in enumerate(self):
            if entity is None and not allow_undefined_values:
                raise ValueError(f"{self.name} contains undefined value at index {entity_index}")


T = TypeVar("T")


@dataclass
class OptionalMappingManager[T]:
    #: Name of the mapping, used for logging.
    name: str
    #: Domain of the mapping, used for validation when adding the mapping.
    domain: EntitySpace
    #: Codomain of the mapping, used for validation when adding the mapping (if applicable).
    codomain: EntitySpace | None = None
    #: Default factory for the mapping values, used when adding the mapping.
    default_factory: Callable[[], T] | None = None
    #: Whether the mapping can be created.
    can_have_mapping: Callable[[], bool] = field(default_factory=lambda: lambda: True)
    #: Whether the mapping must be created (if can_have_mapping is True).
    must_have_mapping: Callable[[], bool] = field(default_factory=lambda: lambda: False)
    #: Optional mapping, managed by this class.
    _mapping: EntityMapping[T] | None = None

    @property
    def has_mapping(self) -> bool:
        return self._mapping is not None

    @property
    def mapping(self) -> EntityMapping[T]:
        if self._mapping is None:
            raise ValueError(f"ATS has no {self.name}")
        return self._mapping

    @mapping.setter
    def mapping(self, values: Sequence[T] | None) -> None:
        if values is None:
            self.remove_mapping()
            return
        if not self.has_mapping:
            self.create_mapping()
        self.mapping._set_values(values)

    def auto_manage(self) -> None:
        if self.has_mapping and not self.can_have_mapping():
            logger.debug(f"{self.name} is no longer valid, removing")
            self.remove_mapping()
        elif not self.has_mapping and self.must_have_mapping():
            logger.debug(f"{self.name} is now required, adding")
            self.create_mapping()

    def create_mapping(self):
        if self.has_mapping:
            return
        if not self.can_have_mapping():
            raise ValueError(f"{self.name} cannot be created in the current ATS state.")
        self._mapping = EntityMapping[T](
            domain=self.domain, codomain=self.codomain, default_factory=self.default_factory, name=self.name
        )

    def remove_mapping(self):
        if self._mapping is None:
            return
        self._mapping._unsubscribe()
        self._mapping = None

    def validate(self) -> None:
        if self._mapping is not None:
            self._mapping.validate()

    def __str__(self) -> str:
        return f"{self.name}: " + (f"{self._mapping}" if self.has_mapping else "None")

    def __repr__(self) -> str:
        return self.__str__()

    def equals(self, other: object, debug: bool = False) -> bool:
        if not isinstance(other, OptionalMappingManager):
            if debug:
                logger.debug(f"other is not an OptionalMappingManager")
            return False
        return self._mapping == other._mapping

    def __eq__(self, other: object) -> bool:
        return self.equals(other, debug=True)

    ## Extra methods for mappings to boolean values, treating them as sets of indices.

    @property
    def indices(self) -> Sequence[int]:
        return [i for i, value in enumerate(self.mapping) if value]

    @indices.setter
    def indices(self, indices: Iterable[int]) -> None:
        values = [False] * self.domain.num_entities
        for i in indices:
            values[i] = True
        self.mapping = values  # type: ignore

    @property
    def num_indices(self) -> int:
        return len(self.indices)


@dataclass
class MappingManager[T](OptionalMappingManager[T]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_have_mapping = lambda *args: True
        self.create_mapping()

    def remove_mapping(self):
        raise ValueError(f"{self.name} is required and cannot be removed.")

    def equals(self, other: object, debug: bool = False) -> bool:
        if not isinstance(other, MappingManager):
            if debug:
                logger.debug(f"other is not a MappingManager")
            return False
        return self._mapping == other._mapping

    def __eq__(self, other: object) -> bool:
        return self.equals(other, debug=True)


### A collection of common entity spaces in an ATS.


class PlayerSpace(EntitySpace):
    @property
    def entity_name(self) -> str:
        return "player"


class StateSpace(EntitySpace):
    @property
    def entity_name(self) -> str:
        return "state"


class ChoiceSpace(EntitySpace):
    @property
    def entity_name(self) -> str:
        return "choice"


class BranchSpace(EntitySpace):
    @property
    def entity_name(self) -> str:
        return "branch"


class ObservationSpace(EntitySpace):
    @property
    def entity_name(self) -> str:
        return "observation"


class ChoiceActionSpace(EntitySpace):
    @property
    def entity_name(self) -> str:
        return "choice action"


class BranchActionSpace(EntitySpace):
    @property
    def entity_name(self) -> str:
        return "branch action"
