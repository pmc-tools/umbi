from dataclasses import dataclass, field


from umbi.datatypes import (
    DataType,
    ValueType,
)

from collections.abc import Iterable

from .entity_class import EntityClass

from .custom_lists import Domain


@dataclass
class Variable:
    """Variable data class."""

    # the name of the variable
    _name: str
    # sorted list of possible values
    _domain: Domain | None = None

    def __init__(self, name: str):
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

    def set_values(self, values: Iterable[ValueType]) -> None:
        self.set_domain(Domain(values))

    @property
    def domain(self) -> Domain:
        self._assert_domain_set()
        assert self._domain is not None
        return self._domain

    @property
    def type(self) -> DataType:
        self._assert_domain_set()
        assert self._domain is not None
        return self._domain.type

    @property
    def lower(self) -> ValueType:
        self._assert_domain_set()
        assert self._domain is not None
        return self._domain.lower

    @property
    def upper(self) -> ValueType:
        self._assert_domain_set()
        assert self._domain is not None
        return self._domain.upper

    def __str__(self) -> str:
        if not self.has_domain:
            return f"Variable(name={self.name}, type=?, domain=?)"
        if self.type == DataType.INT and len(self.domain) == (self.upper - self.lower + 1):  # type: ignore
            domain_str = f"[{self.lower}..{self.upper}]"
        else:
            domain_str = str(self.domain)
        return f"Variable(name={self.name}, type={self.type}, domain={domain_str})"

    def __repr__(self) -> str:
        return self.__str__()

    def validate(self) -> None:
        pass


@dataclass
class VariableValuations:
    """Mapping from entity to variable valuations."""

    # the variable
    _variable: Variable
    # for each entity, the valuation of the variable
    _values: list[ValueType | None] = field(default_factory=list)

    @property
    def variable(self) -> Variable:
        return self._variable

    @property
    def values(self) -> list[ValueType | None]:
        return self._values

    @property
    def num_values(self) -> int:
        return len(self._values)

    def __str__(self) -> str:
        return f"VariableValuations(variable={self.variable}, values={self.values})"

    def __repr__(self) -> str:
        return self.__str__()

    def ensure_capacity(self, num_entities: int) -> None:
        """Ensures that the valuations list has at least num_entities entries."""
        while len(self._values) < num_entities:
            self._values.append(None)

    def get_entity_value(self, entity: int) -> ValueType | None:
        """Gets the valuation for a given entity index."""
        if entity < 0 or entity >= self.num_values:
            raise IndexError(f"entity index {entity} out of range [0, {self.num_values})")
        return self._values[entity]

    def set_entity_value(self, entity: int, value: ValueType | None) -> None:
        """Sets the valuation for a given entity index. Increases capacity if needed."""
        self.ensure_capacity(entity + 1)
        self._values[entity] = value

    @property
    def has_undefined_values(self) -> bool:
        """Checks if there are any undefined (None) values."""
        return any(v is None for v in self._values)

    def sync_domain(self) -> None:
        """Sets the variable domain from the valuations."""
        if self.has_undefined_values:
            raise ValueError(f"The domain cannot be synced: entity {self._values.index(None)} has undefined value.")
        self._variable.set_values(self._values)  # type: ignore
        assert self._variable.type is not None

    def validate(self) -> None:
        self.sync_domain()
        self._variable.validate()


@dataclass
class EntityValuations:
    """Maintains a collection of VariableValuations."""

    # number of entities (states, actions, etc.) to be associated with variable valuations
    _num_entities: int = 0
    # for each variable name, the corresponding Variable
    _variable_name_to_variable: dict[str, Variable] = field(default_factory=dict)
    # for each variable, the corresponding VariableValuations
    _variable_to_valuations: dict[Variable, VariableValuations] = field(default_factory=dict)

    @property
    def variables(self) -> list[Variable]:
        """Returns a list of all variables defined."""
        return list(self._variable_to_valuations.keys())

    def __str__(self) -> str:
        lines = [f"{self.__class__.__name__}(num_entities={self.num_entities}):"]
        for variable in self.variables:
            variable_valuation = self.get_variable_valuations(variable)
            lines.append(f"  {variable_valuation}")
        return "\n".join(lines)

    @property
    def num_variables(self) -> int:
        """Returns the number of variables defined."""
        return len(self.variables)

    @property
    def num_entities(self) -> int:
        return self._num_entities

    def has_variable(self, variable_name: str) -> bool:
        """Checks if a VariableValuation exists for the given variable name."""
        return variable_name in self._variable_name_to_variable

    def add_variable(self, variable_name: str) -> Variable:
        """Adds a new VariableValuation for a given variable."""
        if self.has_variable(variable_name):
            raise ValueError(f"Variable '{variable_name}' already exists.")
        variable = Variable(name=variable_name)
        self._variable_name_to_variable[variable_name] = variable
        self._variable_to_valuations[variable] = VariableValuations(variable)
        return variable

    def get_variable(self, variable_name: str) -> Variable:
        """Retrieves the Variable for a given variable name."""
        if not self.has_variable(variable_name):
            raise KeyError(f"Variable '{variable_name}' not found.")
        return self._variable_name_to_variable[variable_name]

    def get_or_add_variable(self, variable_name: str) -> Variable:
        """Retrieves the Variable for a given variable name, adding it if it does not exist."""
        if not self.has_variable(variable_name):
            return self.add_variable(variable_name)
        return self.get_variable(variable_name)

    def remove_variable(self, variable: Variable) -> None:
        """Removes the VariableValuations for a given variable."""
        if not self.has_variable(variable.name):
            raise KeyError(f"Variable '{variable.name}' not found.")
        variable = self._variable_name_to_variable[variable.name]
        del self._variable_name_to_variable[variable.name]
        del self._variable_to_valuations[variable]

    def get_variable_valuations(self, variable: Variable) -> VariableValuations:
        """Retrieves the VariableValuations for a given variable."""
        if not self.has_variable(variable.name):
            raise KeyError(f"Variable '{variable.name}' not found.")
        variable = self._variable_name_to_variable[variable.name]
        return self._variable_to_valuations[variable]

    def ensure_capacity(self, num_entities: int) -> None:
        """Ensures that all VariableValuations have at least num_entities entries."""
        for variable_valuation in self._variable_to_valuations.values():
            variable_valuation.ensure_capacity(num_entities)
        if self._num_entities < num_entities:
            self._num_entities = num_entities

    def get_entity_valuation(self, entity: int) -> dict[Variable, ValueType | None]:
        """Gets the variable valuations for a given entity index."""
        if entity < 0 or entity >= self.num_entities:
            raise IndexError(f"entity {entity} out of range [0, {self.num_entities})")
        return {
            variable: variable_valuation.get_entity_value(entity)
            for variable, variable_valuation in self._variable_to_valuations.items()
        }

    def set_entity_valuation(self, entity: int, valuations: dict[Variable, ValueType | None]) -> None:
        """Adds a new entity with the given variable valuations."""
        self.ensure_capacity(entity + 1)
        for variable, value in valuations.items():
            variable_valuation = self.get_variable_valuations(variable)
            variable_valuation.set_entity_value(entity, value)

    def remove_entity(self, entity: int) -> None:
        """Removes the valuations for a given entity index."""
        raise NotImplementedError

    def sync_domains(self) -> None:
        """Synchronizes the domains of all variables based on their valuations."""
        for variable_valuation in self._variable_to_valuations.values():
            variable_valuation.sync_domain()

    def validate(self) -> None:
        self.sync_domains()
        for v in self._variable_to_valuations.keys():
            assert v.type is not None, f"Variable '{v.name}' has no type after syncing domains"
        for v in self.variables:
            assert v.type is not None, f"Variable '{v.name}' has no type after syncing domains"
        assert all(v.type is not None for v in self.variables)
        for variable_valuation in self._variable_to_valuations.values():
            if not variable_valuation.num_values == self.num_entities:
                raise ValueError(
                    f"Variable '{variable_valuation.variable.name}' has {variable_valuation.num_values} "
                    f"entities, expected {self.num_entities}"
                )
            variable_valuation.validate()

    def __eq__(self, other) -> bool:
        if not isinstance(other, EntityValuations):
            return False
        if self.num_entities != other.num_entities:
            return False
        # TODO more thorough comparison
        return True


class EntityClassValuations(dict[EntityClass, EntityValuations]):
    """Mapping from entity class to variable valuations."""

    @property
    def has_values(self) -> bool:
        """Check if the annotation has any values set."""
        return len(self) > 0

    @property
    def entity_classes(self) -> set[EntityClass]:
        """Get the set of entity classes for which this annotation has values."""
        return set(self.keys())

    def has_values_for(self, entity_class: EntityClass) -> bool:
        """Check if the annotation has values for the given entity class."""
        return self.get(entity_class) is not None

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
        return self.has_values_for(EntityClass.OBSERVATION)

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
        return self.get_valuations_for(EntityClass.OBSERVATION)

    @property
    def player_valuations(self) -> EntityValuations:
        return self.get_valuations_for(EntityClass.PLAYERS)

    def set_state_valuations(self, values: EntityValuations):
        self.set_valuations_for(EntityClass.STATES, values)

    def set_choice_valuations(self, values: EntityValuations):
        self.set_valuations_for(EntityClass.CHOICES, values)

    def set_branch_valuations(self, values: EntityValuations):
        self.set_valuations_for(EntityClass.BRANCHES, values)

    def set_observation_valuations(self, values: EntityValuations):
        self.set_valuations_for(EntityClass.OBSERVATION, values)

    def set_player_valuations(self, values: EntityValuations):
        self.set_valuations_for(EntityClass.PLAYERS, values)

    def unset_state_valuations(self):
        self.unset_valuations_for(EntityClass.STATES)

    def unset_choice_valuations(self):
        self.unset_valuations_for(EntityClass.CHOICES)

    def unset_branch_valuations(self):
        self.unset_valuations_for(EntityClass.BRANCHES)

    def unset_observation_valuations(self):
        self.unset_valuations_for(EntityClass.OBSERVATION)

    def unset_player_valuations(self):
        self.unset_valuations_for(EntityClass.PLAYERS)
