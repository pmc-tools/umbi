import logging
from collections.abc import Iterable, KeysView, Sequence
from dataclasses import dataclass, field
from typing import TypeAlias

from umbi.datatypes import Scalar, ScalarType, scalar_promotion_type_of

from .domain import Domain
from .entity_space import EntityClass

logger = logging.getLogger(__name__)

from .entity_space import EntityMapping, EntitySpace, MappingManager
from .entity_space_mixins import HasCommonEntitySpaces


@dataclass
class Variable:
    """Variable data class."""

    # the name of the variable
    _name: str
    # sorted list of possible values
    _domain: Domain | None = None

    def __init__(self, name: str) -> None:
        self._name = name

    def __hash__(self) -> int:
        return hash(self._name)

    @property
    def name(self) -> str:
        return self._name

    @property
    def has_domain(self) -> bool:
        return self._domain is not None

    def _assert_domain_set(self) -> None:
        if self._domain is None:
            raise ValueError(f"Variable '{self.name}' has no domain defined.")

    def invalidate_domain(self) -> None:
        self._domain = None

    def set_domain(self, domain: Domain) -> None:
        self._domain = domain
        self._domain.sort()

    def set_values(self, values: Iterable[Scalar]) -> None:
        self.set_domain(Domain(values))

    @property
    def domain(self) -> Domain:
        self._assert_domain_set()
        assert self._domain is not None
        return self._domain

    @property
    def promotion_type(self) -> ScalarType:
        self._assert_domain_set()
        assert self._domain is not None
        return scalar_promotion_type_of(self._domain)

    @property
    def lower(self) -> Scalar:
        self._assert_domain_set()
        assert self._domain is not None
        return self._domain.lower

    @property
    def upper(self) -> Scalar:
        self._assert_domain_set()
        assert self._domain is not None
        return self._domain.upper

    def __str__(self) -> str:
        if not self.has_domain:
            return f"Variable(name={self.name}, type=?, domain=?)"
        # if self.type == NumericPrimitiveType.INT and len(self.domain) == (self.upper - self.lower + 1):  # type: ignore
        #     domain_str = f"[{self.lower}..{self.upper}]"
        # else:
        domain_str = str(self.domain)
        return f"Variable(name={self.name}, type={self.promotion_type}, domain={domain_str})"

    def __repr__(self) -> str:
        return self.__str__()

    def validate(self) -> None:
        pass


@dataclass
class EntityVariableValuations:
    """Mapping from entity to a given variable valuations."""

    #: variable
    variable: Variable
    #: entity class to which the variable valuations belong
    entity_space: EntitySpace
    # for each entity, the valuation of the variable
    _entity_to_value_manager: MappingManager[Scalar | None] = field(init=False)

    def __post_init__(self):
        self._entity_to_value_manager = MappingManager[Scalar | None](
            name=f"{self.entity_space.entity_name}_valuations[{self.variable.name}]",
            domain=self.entity_space,
        )
        self.entity_space._subscribe(self, lambda *args: self._entity_to_value_manager.auto_manage())

    @property
    def values(self) -> EntityMapping[Scalar | None]:
        return self._entity_to_value_manager.mapping

    @values.setter
    def values(self, values: Sequence[Scalar | None] | None) -> None:
        self._entity_to_value_manager.mapping = values

    def __str__(self) -> str:
        return f"EntityVariableValuations(variable={self.variable}, values={self.values})"

    def __repr__(self) -> str:
        return self.__str__()

    def sync_domain(self) -> None:
        """Sets the variable domain from the valuations."""
        self.values.validate()
        self.variable.set_values(self.values)  # type: ignore[assignment] validate() above ensures that no values are None

    def validate(self) -> None:
        self.sync_domain()
        self.variable.validate()


#: Valuation of all variables for a single entity.
EntityValuation: TypeAlias = dict[Variable, Scalar | None]


@dataclass
class EntityValuations:
    """Maintains a collection of VariableValuations."""

    #: entity space to which the variable valuations belong
    entity_space: EntitySpace
    # for each variable name, the corresponding Variable
    _variable_name_to_variable: dict[str, Variable] = field(default_factory=dict)
    # for each variable, the corresponding EntityVariableValuations
    _variable_to_valuations: dict[Variable, EntityVariableValuations] = field(default_factory=dict)

    @property
    def variables(self) -> list[Variable]:
        """Returns a list of all variables defined."""
        return list(self._variable_to_valuations.keys())

    def __str__(self) -> str:
        lines = [f"{self.__class__.__name__}:"]
        for variable in self.variables:
            variable_valuation = self.get_variable_valuations(variable)
            lines.append(f"  {variable_valuation}")
        return "\n".join(lines)

    @property
    def num_variables(self) -> int:
        """Returns the number of variables defined."""
        return len(self.variables)

    def has_variable(self, variable_name: str) -> bool:
        """Checks if a VariableValuation exists for the given variable name."""
        return variable_name in self._variable_name_to_variable

    def new_variable(self, variable_name: str) -> Variable:
        """Adds a new VariableValuation for a given variable."""
        if self.has_variable(variable_name):
            raise ValueError(f"Variable '{variable_name}' already exists.")
        variable = Variable(name=variable_name)
        self._variable_name_to_variable[variable_name] = variable
        self._variable_to_valuations[variable] = EntityVariableValuations(variable, entity_space=self.entity_space)
        return variable

    def get_variable(self, variable_name: str) -> Variable:
        """Retrieves the Variable for a given variable name."""
        if not self.has_variable(variable_name):
            raise KeyError(f"Variable '{variable_name}' not found.")
        return self._variable_name_to_variable[variable_name]

    def get_or_create_variable(self, variable_name: str) -> Variable:
        """Retrieves the Variable for a given variable name, adding it if it does not exist."""
        if not self.has_variable(variable_name):
            return self.new_variable(variable_name)
        return self.get_variable(variable_name)

    def remove_variable(self, variable: Variable) -> None:
        """Removes the EntityVariableValuations for a given variable."""
        if not self.has_variable(variable.name):
            raise KeyError(f"Variable '{variable.name}' not found.")
        variable = self._variable_name_to_variable[variable.name]
        del self._variable_name_to_variable[variable.name]
        del self._variable_to_valuations[variable]

    def get_variable_valuations(self, variable: Variable) -> EntityVariableValuations:
        """Retrieves the EntityVariableValuations for a given variable."""
        if not self.has_variable(variable.name):
            raise KeyError(f"Variable '{variable.name}' not found.")
        variable = self._variable_name_to_variable[variable.name]
        return self._variable_to_valuations[variable]

    def get_entity_valuation(self, entity: int) -> EntityValuation:
        """Gets the variable valuations for a given entity index."""
        return {
            variable: variable_valuation.values[entity]
            for variable, variable_valuation in self._variable_to_valuations.items()
        }

    def get_entity_valuation_tuple(
        self, entity: int, variable_order: list[Variable] | None = None
    ) -> tuple[Scalar | None, ...]:
        """Gets the variable valuations for a given entity index as a tuple in the specified variable order."""
        if variable_order is None:
            variable_order = list(self._variable_to_valuations.keys())
        return tuple(self.get_entity_valuation(entity)[variable] for variable in variable_order)

    def set_entity_valuation(self, entity: int, valuation: EntityValuation) -> None:
        """Adds a new entity with the given variable valuations."""
        for variable, value in valuation.items():
            variable_valuation = self.get_variable_valuations(variable)
            variable_valuation.values[entity] = value

    def remove_entity(self, entity: int) -> None:
        """Removes the valuations for a given entity index."""
        raise NotImplementedError

    @property
    def has_distinct_valuations(self) -> bool:
        """Determines whether the variable valuations are distinct across all entities."""
        valuations = [self.get_entity_valuation_tuple(entity) for entity in range(self.entity_space.num_entities)]
        return len(valuations) == len(set(valuations))

    def sync_domains(self) -> None:
        """Synchronizes the domains of all variables based on their valuations."""
        for variable_valuation in self._variable_to_valuations.values():
            variable_valuation.sync_domain()

    def validate(self) -> None:
        self.sync_domains()
        for variable_valuation in self._variable_to_valuations.values():
            variable_valuation.validate()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EntityValuations):
            return False
        # TODO more thorough comparison
        return True


@dataclass
class EntityClassValuations(dict[EntityClass, EntityValuations]):
    """Mapping from entity class to variable valuations."""

    #: entity space to which the variable valuations belong
    entity_spaces: dict[EntityClass, EntitySpace]

    @property
    def has_values(self) -> bool:
        """Check if the annotation has any values set."""
        return len(self) > 0

    @property
    def entity_classes(self) -> KeysView[EntityClass]:
        """Get the set of entity classes for which this annotation has values."""
        return self.keys()

    def has_values_for(self, entity_class: EntityClass) -> bool:
        """Check if the annotation has values for the given entity class."""
        return self.get(entity_class) is not None

    def add_valuations_for(self, entity_class: EntityClass) -> EntityValuations:
        """Add a new EntityValuations for the given entity class."""
        if self.has_values_for(entity_class):
            raise ValueError(f"Annotation already has values for entity class {entity_class}")
        valuations = EntityValuations(entity_space=self.entity_spaces[entity_class])
        self[entity_class] = valuations
        return valuations

    def get_valuations_for(self, entity_class: EntityClass) -> EntityValuations:
        """
        Get the values for the given entity class.
        :raises KeyError: if no values are set for the given entity class
        """
        if not self.has_values_for(entity_class):
            raise KeyError(f"Annotation has no values for entity class {entity_class}")
        return self[entity_class]

    def set_valuations_for(self, entity_class: EntityClass, values: EntityValuations) -> None:
        """Set the values for the given entity class."""
        self[entity_class] = values

    def unset_valuations_for(self, entity_class: EntityClass) -> None:
        """Unset the values for the given entity class."""
        if not self.has_values_for(entity_class):
            raise KeyError(f"Annotation has no values for entity class {entity_class}")
        del self[entity_class]

    def __str__(self) -> str:
        lines = [f"{self.__class__.__name__}:"]
        for entity_class, valuations in self.items():
            lines.append(f"  {entity_class}: {valuations}")
        return "\n".join(lines)

    ### Convenience properties and methods for each entity class ###

    @property
    def has_state_valuations(self) -> bool:
        return self.has_values_for(EntityClass.STATES)

    @property
    def has_choice_valuations(self) -> bool:
        return self.has_values_for(EntityClass.CHOICES)

    @property
    def has_branch_valuations(self) -> bool:
        return self.has_values_for(EntityClass.BRANCHES)

    @property
    def has_observation_valuations(self) -> bool:
        return self.has_values_for(EntityClass.OBSERVATIONS)

    @property
    def has_player_valuations(self) -> bool:
        return self.has_values_for(EntityClass.PLAYERS)

    @property
    def state_valuations(self) -> EntityValuations:
        return self.get_valuations_for(EntityClass.STATES)

    @property
    def choice_valuations(self) -> EntityValuations:
        return self.get_valuations_for(EntityClass.CHOICES)

    @property
    def branch_valuations(self) -> EntityValuations:
        return self.get_valuations_for(EntityClass.BRANCHES)

    @property
    def observation_valuations(self) -> EntityValuations:
        return self.get_valuations_for(EntityClass.OBSERVATIONS)

    @property
    def player_valuations(self) -> EntityValuations:
        return self.get_valuations_for(EntityClass.PLAYERS)

    def add_state_valuations(self) -> EntityValuations:
        return self.add_valuations_for(EntityClass.STATES)

    def add_choice_valuations(self) -> EntityValuations:
        return self.add_valuations_for(EntityClass.CHOICES)

    def add_branch_valuations(self) -> EntityValuations:
        return self.add_valuations_for(EntityClass.BRANCHES)

    def add_observation_valuations(self) -> EntityValuations:
        return self.add_valuations_for(EntityClass.OBSERVATIONS)

    def add_player_valuations(self) -> EntityValuations:
        return self.add_valuations_for(EntityClass.PLAYERS)

    def set_state_valuations(self, values: EntityValuations):
        self.set_valuations_for(EntityClass.STATES, values)

    def set_choice_valuations(self, values: EntityValuations):
        self.set_valuations_for(EntityClass.CHOICES, values)

    def set_branch_valuations(self, values: EntityValuations):
        self.set_valuations_for(EntityClass.BRANCHES, values)

    def set_observation_valuations(self, values: EntityValuations):
        self.set_valuations_for(EntityClass.OBSERVATIONS, values)

    def set_player_valuations(self, values: EntityValuations):
        self.set_valuations_for(EntityClass.PLAYERS, values)

    def unset_state_valuations(self):
        self.unset_valuations_for(EntityClass.STATES)

    def unset_choice_valuations(self):
        self.unset_valuations_for(EntityClass.CHOICES)

    def unset_branch_valuations(self):
        self.unset_valuations_for(EntityClass.BRANCHES)

    def unset_observation_valuations(self):
        self.unset_valuations_for(EntityClass.OBSERVATIONS)

    def unset_player_valuations(self):
        self.unset_valuations_for(EntityClass.PLAYERS)

    ### Utility methods. ###

    def validate(self) -> None:
        for entity_class in self.entity_classes:
            valuations = self.get_valuations_for(entity_class)
            valuations.validate()


@dataclass
class VariableValuationsMixin(HasCommonEntitySpaces):
    """Valuation of a variable for a specific entity (e.g. state or choice)."""

    #: EntityClassValuations associated with the ATS.
    _variable_valuations: EntityClassValuations | None = None

    @property
    def has_variable_valuations(self) -> bool:
        return self._variable_valuations is not None

    @property
    def variable_valuations(self) -> EntityClassValuations:
        if self._variable_valuations is None:
            raise ValueError("variable valuations do not exist")
        return self._variable_valuations

    def add_variable_valuations(self) -> EntityClassValuations:
        if self._variable_valuations is not None:
            logger.warning("ATS that already has variable valuations, skipping add_variable_valuations")
            return self._variable_valuations
        self._variable_valuations = EntityClassValuations(entity_spaces=self._common_entity_spaces)
        return self._variable_valuations

    def remove_variable_valuations(self):
        self._variable_valuations = None

    def validate(self):
        if self.has_variable_valuations:
            self.variable_valuations.validate()
        super().validate()
