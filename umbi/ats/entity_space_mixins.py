from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from .base_mixin import BaseMixin
from .entity_space import (
    BranchActionSpace,
    BranchSpace,
    ChoiceActionSpace,
    ChoiceSpace,
    EntityClass,
    EntitySpace,
    ObservationSpace,
    PlayerSpace,
    StateSpace,
)

### Protocols for ATS mixins that have particular entity spaces.


class HasPlayerSpace(BaseMixin, ABC):
    @property
    @abstractmethod
    def _player_space(self) -> PlayerSpace: ...
    # public API
    @property
    def has_players(self) -> bool:
        return self._player_space.has_entities

    @property
    def num_players(self) -> int:
        return self._player_space.num_entities

    @num_players.setter
    def num_players(self, num_players: int):
        self._player_space.num_entities = num_players

    @property
    def players(self) -> Iterable[int]:
        return self._player_space.entities

    # protected API
    def _new_player(self) -> int:
        return self._player_space.new_entity()

    def _new_players(self, num_players: int) -> list[int]:
        return self._player_space.new_entities(num_players)

    def _remove_player(self, player: int) -> list[int]:
        return self._player_space.remove_entity(player)

    def _remove_players(self, players: Sequence[int]) -> list[int]:
        return self._player_space.remove_entities(players)

    def _permute_players(self, new_to_old: Sequence[int]) -> None:
        return self._player_space.permute_entities(new_to_old)


class HasStateSpace(BaseMixin, ABC):
    @property
    @abstractmethod
    def _state_space(self) -> StateSpace: ...
    # public API
    @property
    def has_states(self) -> bool:
        return self._state_space.has_entities

    @property
    def num_states(self) -> int:
        return self._state_space.num_entities

    @num_states.setter
    def num_states(self, num_states: int):
        self._state_space.num_entities = num_states

    @property
    def states(self) -> Iterable[int]:
        return self._state_space.entities

    # protected API
    def _new_state(self) -> int:
        return self._state_space.new_entity()

    def _new_states(self, num_states: int) -> list[int]:
        return self._state_space.new_entities(num_states)

    def _remove_state(self, state: int) -> list[int]:
        return self._state_space.remove_entity(state)

    def _remove_states(self, states: Sequence[int]) -> list[int]:
        return self._state_space.remove_entities(states)

    def _permute_states(self, new_to_old: Sequence[int]) -> None:
        self._state_space.permute_entities(new_to_old)


class HasObservationSpace(BaseMixin, ABC):
    @property
    @abstractmethod
    def _observation_space(self) -> ObservationSpace: ...
    # public API
    @property
    def has_observations(self) -> bool:
        return self._observation_space.has_entities

    @property
    def num_observations(self) -> int:
        return self._observation_space.num_entities

    @num_observations.setter
    def num_observations(self, num_observations: int):
        self._observation_space.num_entities = num_observations

    @property
    def observations(self) -> Iterable[int]:
        return self._observation_space.entities

    # protected API
    def _new_observation(self) -> int:
        return self._observation_space.new_entity()

    def _new_observations(self, num_observations: int) -> list[int]:
        return self._observation_space.new_entities(num_observations)

    def _remove_observation(self, observation: int) -> list[int]:
        return self._observation_space.remove_entity(observation)

    def _remove_observations(self, observations: Sequence[int]) -> list[int]:
        return self._observation_space.remove_entities(observations)

    def _permute_observations(self, new_to_old: list[int]) -> None:
        return self._observation_space.permute_entities(new_to_old)


class HasChoiceSpace(BaseMixin, ABC):
    @property
    @abstractmethod
    def _choice_space(self) -> ChoiceSpace: ...
    # public API
    @property
    def has_choices(self) -> bool:
        return self._choice_space.has_entities

    @property
    def num_choices(self) -> int:
        return self._choice_space.num_entities

    @property
    def choices(self) -> Iterable[int]:
        return self._choice_space.entities

    # protected API
    def _new_choice(self) -> int:
        return self._choice_space.new_entity()

    def _new_choices(self, num_choices: int) -> list[int]:
        return self._choice_space.new_entities(num_choices)

    def _remove_choice(self, choice: int) -> list[int]:
        return self._choice_space.remove_entity(choice)

    def _remove_choices(self, choices: Sequence[int]) -> list[int]:
        return self._choice_space.remove_entities(choices)

    def _permute_choices(self, new_to_old: Sequence[int]) -> None:
        self._choice_space.permute_entities(new_to_old)


class HasBranchSpace(BaseMixin, ABC):
    @property
    @abstractmethod
    def _branch_space(self) -> BranchSpace: ...
    # public API
    @property
    def has_branches(self) -> bool:
        return self._branch_space.has_entities

    @property
    def num_branches(self) -> int:
        return self._branch_space.num_entities

    @property
    def branches(self) -> Iterable[int]:
        return self._branch_space.entities

    # protected API
    def _new_branch(self) -> int:
        return self._branch_space.new_entity()

    def _new_branches(self, num_branches: int) -> list[int]:
        return self._branch_space.new_entities(num_branches)

    def _remove_branch(self, branch: int) -> list[int]:
        return self._branch_space.remove_entity(branch)

    def _remove_branches(self, branches: Sequence[int]) -> list[int]:
        return self._branch_space.remove_entities(branches)

    def _permute_branches(self, new_to_old: Sequence[int]) -> None:
        self._branch_space.permute_entities(new_to_old)


class HasChoiceActionSpace(BaseMixin, ABC):
    @property
    @abstractmethod
    def _choice_action_space(self) -> ChoiceActionSpace: ...
    # public API
    @property
    def has_choice_actions(self) -> bool:
        return self._choice_action_space.has_entities

    @property
    def num_choice_actions(self) -> int:
        return self._choice_action_space.num_entities

    @num_choice_actions.setter
    def num_choice_actions(self, num_choice_actions: int):
        self._choice_action_space.num_entities = num_choice_actions

    # protected API
    def _new_choice_action(self) -> int:
        return self._choice_action_space.new_entity()

    def _new_choice_actions(self, num_choice_actions: int) -> list[int]:
        return self._choice_action_space.new_entities(num_choice_actions)

    def _remove_choice_action(self, choice_action: int) -> list[int]:
        return self._choice_action_space.remove_entity(choice_action)

    def _remove_choice_actions(self, choice_actions: Sequence[int]) -> list[int]:
        return self._choice_action_space.remove_entities(choice_actions)

    def _permute_choice_actions(self, new_to_old: Sequence[int]) -> None:
        return self._choice_action_space.permute_entities(new_to_old)


class HasBranchActionSpace(BaseMixin, ABC):
    @property
    @abstractmethod
    def _branch_action_space(self) -> BranchActionSpace: ...
    # public API
    @property
    def has_branch_actions(self) -> bool:
        return self._branch_action_space.has_entities

    @property
    def num_branch_actions(self) -> int:
        return self._branch_action_space.num_entities

    @num_branch_actions.setter
    def num_branch_actions(self, num_branch_actions: int):
        self._branch_action_space.num_entities = num_branch_actions

    # protected API
    def _new_branch_action(self) -> int:
        return self._branch_action_space.new_entity()

    def _new_branch_actions(self, num_branch_actions: int) -> list[int]:
        return self._branch_action_space.new_entities(num_branch_actions)

    def _remove_branch_action(self, branch_action: int) -> list[int]:
        return self._branch_action_space.remove_entity(branch_action)

    def _remove_branch_actions(self, branch_actions: Sequence[int]) -> list[int]:
        return self._branch_action_space.remove_entities(branch_actions)

    def _permute_branch_actions(self, new_to_old: Sequence[int]) -> None:
        return self._branch_action_space.permute_entities(new_to_old)


class HasCommonEntitySpaces(
    HasPlayerSpace,
    HasStateSpace,
    HasObservationSpace,
    HasChoiceSpace,
    HasBranchSpace,
):
    @property
    def _common_entity_spaces(self) -> dict[EntityClass, EntitySpace]:
        """Get a dict of all entity spaces of the ATS."""
        return {
            EntityClass.STATES: self._state_space,
            EntityClass.PLAYERS: self._player_space,
            EntityClass.CHOICES: self._choice_space,
            EntityClass.BRANCHES: self._branch_space,
            EntityClass.OBSERVATIONS: self._observation_space,
        }


### Mixins for ATSs with particular entity spaces.


@dataclass
class PlayerSpaceMixin(HasPlayerSpace):
    #: Underlying player space.
    _player_space_mixin: PlayerSpace = field(default_factory=PlayerSpace)

    @property
    def _player_space(self) -> PlayerSpace:
        return self._player_space_mixin

    # public API
    def new_player(self) -> int:
        return self._new_player()

    def new_players(self, num_players: int) -> list[int]:
        return self._new_players(num_players)

    def remove_player(self, player: int) -> list[int]:
        return self._remove_player(player)

    def remove_players(self, players: Sequence[int]) -> list[int]:
        return self._remove_players(players)

    def permute_players(self, new_to_old: Sequence[int]) -> None:
        return self._player_space.permute_entities(new_to_old)


@dataclass
class StateSpaceMixin(HasStateSpace):
    """ATS mixin for state space management."""

    #: Underlying state space.
    _state_space_mixin: StateSpace = field(default_factory=StateSpace)

    @property
    def _state_space(self) -> StateSpace:
        return self._state_space_mixin

    # public API
    def new_state(self) -> int:
        return self._new_state()

    def new_states(self, num_states: int) -> list[int]:
        return self._new_states(num_states)

    def permute_states(self, new_to_old: Sequence[int]) -> None:
        self._permute_states(new_to_old)

    def validate(self) -> None:
        if not self.has_states:
            raise ValueError("ATS must have at least one state.")
        super().validate()


@dataclass
class ObservationSpaceMixin(HasObservationSpace):
    """ATS mixin for observation space management."""

    #: Underlying observation space.
    _observation_space_mixin: ObservationSpace = field(default_factory=ObservationSpace)

    @property
    def _observation_space(self) -> ObservationSpace:
        return self._observation_space_mixin

    # public API
    def new_observation(self) -> int:
        return self._new_observation()

    def new_observations(self, num_observations: int) -> list[int]:
        return self._new_observations(num_observations)

    def remove_observation(self, observation: int) -> list[int]:
        return self._remove_observation(observation)

    def remove_observations(self, observations: Sequence[int]) -> list[int]:
        return self._remove_observations(observations)

    def permute_observations(self, new_to_old: list[int]) -> None:
        return self._permute_observations(new_to_old)


@dataclass
class ChoiceSpaceMixin(HasChoiceSpace):
    """ATS mixin for choice space management."""

    #: Underlying choice space.
    _choice_space_mixin: ChoiceSpace = field(default_factory=ChoiceSpace)

    @property
    def _choice_space(self) -> ChoiceSpace:
        return self._choice_space_mixin

    # public API
    def permute_choices(self, new_to_old: Sequence[int]) -> None:
        self._permute_choices(new_to_old)


@dataclass
class BranchSpaceMixin(HasBranchSpace):
    """ATS mixin for branch space management."""

    #: Underlying branch space.
    _branch_space_mixin: BranchSpace = field(default_factory=BranchSpace)

    @property
    def _branch_space(self) -> BranchSpace:
        return self._branch_space_mixin


@dataclass
class ChoiceActionSpaceMixin(HasChoiceActionSpace):
    """ATS mixin for choice action space management."""

    #: Underlying choice action space.
    _choice_action_space_mixin: ChoiceActionSpace = field(default_factory=ChoiceActionSpace)

    @property
    def _choice_action_space(self) -> ChoiceActionSpace:
        return self._choice_action_space_mixin

    # public API
    def new_choice_action(self) -> int:
        return self._new_choice_action()

    def new_choice_actions(self, num_choice_actions: int) -> list[int]:
        return self._new_choice_actions(num_choice_actions)

    def remove_choice_action(self, choice_action: int) -> list[int]:
        return self._remove_choice_action(choice_action)

    def remove_choice_actions(self, choice_actions: Sequence[int]) -> list[int]:
        return self._remove_choice_actions(choice_actions)

    def permute_choice_actions(self, new_to_old: Sequence[int]) -> None:
        return self._permute_choice_actions(new_to_old)


@dataclass
class BranchActionSpaceMixin(HasBranchActionSpace):
    """ATS mixin for branch action space management."""

    #: Underlying branch action space.
    _branch_action_space_mixin: BranchActionSpace = field(default_factory=BranchActionSpace)

    @property
    def _branch_action_space(self) -> BranchActionSpace:
        return self._branch_action_space_mixin

    def new_branch_action(self) -> int:
        return self._new_branch_action()

    def new_branch_actions(self, num_branch_actions: int) -> list[int]:
        return self._new_branch_actions(num_branch_actions)

    def remove_branch_action(self, branch_action: int) -> list[int]:
        return self._remove_branch_action(branch_action)

    def remove_branch_actions(self, branch_actions: Sequence[int]) -> list[int]:
        return self._remove_branch_actions(branch_actions)

    def permute_branch_actions(self, new_to_old: Sequence[int]) -> None:
        return self._permute_branch_actions(new_to_old)


class EntitySpaceMixin(
    PlayerSpaceMixin,
    StateSpaceMixin,
    ObservationSpaceMixin,
    ChoiceSpaceMixin,
    ChoiceActionSpaceMixin,
    BranchSpaceMixin,
    BranchActionSpaceMixin,
):
    def __post_init__(self):
        super().__post_init__()
