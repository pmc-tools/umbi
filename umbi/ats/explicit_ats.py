import logging
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field, fields
from enum import Enum

from umbi.datatypes import Interval, Numeric, NumericPrimitive

from .annotations import (
    Annotation,
    AtomicPropositionAnnotation,
    ObservationAnnotation,
    RewardAnnotation,
)
from .entity_class import EntityClass
from .model_info import ModelInfo
from .variable_valuations import EntityClassValuations

logger = logging.getLogger(__name__)


class TimeType(str, Enum):
    """Time types for transition systems."""

    DISCRETE = "discrete"
    STOCHASTIC = "stochastic"
    URGENT_STOCHASTIC = "urgent-stochastic"


@dataclass
class Branch:
    """Branch of a choice."""

    #: Target state of the branch.
    target: int
    #: Branch probability. If set, must be a stochastic numeric value.
    prob: Numeric | None = None
    #: Branch action.
    action: int | None = None

    def __post_init__(self):
        self.validate()

    def validate(self, num_states: int | None = None, num_branch_actions: int | None = None):
        if self.target < 0:
            raise ValueError(f"Invalid branch target {self.target}, must be >= 0.")
        if num_states is not None and self.target >= num_states:
            raise ValueError(f"Invalid branch target {self.target}, must be < num_states ({num_states}).")
        if self.prob is not None:
            if isinstance(self.prob, NumericPrimitive):
                if self.prob < 0 or self.prob > 1:
                    raise ValueError(f"Invalid branch probability {self.prob}, must be in [0, 1].")
            else:  # isinstance(self.prob, Interval):
                assert isinstance(self.prob, Interval)
                if self.prob.left < 0 or self.prob.right > 1:
                    raise ValueError(f"Invalid branch probability interval {self.prob}, must be in [0, 1].")
        if self.action is not None:
            if self.action < 0:
                raise ValueError(f"Invalid branch action {self.action}, must be >= 0.")
            if num_branch_actions is not None and self.action >= num_branch_actions:
                raise ValueError(
                    f"Invalid branch action {self.action}, must be < num_branch_actions ({num_branch_actions})."
                )


@dataclass
class Choice:
    """Choice of a state."""

    #: Global choice index.
    _index: int
    #: Source state of the choice.
    state: int
    #: List of branches of the choice. Probabilities must sum to 1.
    branches: list[Branch] = field(default_factory=list)
    #: Choice action.
    action: int | None = None

    @property
    def index(self) -> int:
        """Get the global choice index."""
        return self._index

    @property
    def num_branches(self) -> int:
        """Get the number of branches."""
        return len(self.branches)

    def add_branch(self, target: int, prob: Numeric | None = None, action: int | None = None) -> Branch:
        """Add a branch to the choice with the given target, probability, and action, and return it."""
        branch = Branch(target=target, prob=prob, action=action)
        self.branches.append(branch)
        return branch

    def validate(
        self,
        num_states: int | None = None,
        num_choice_actions: int | None = None,
        num_branch_actions: int | None = None,
    ):
        if len(self.branches) == 0:
            raise ValueError("A choice must have at least one branch.")
        for branch in self.branches:
            branch.validate(num_states=num_states, num_branch_actions=num_branch_actions)
            # TODO validate branch probabilities sum to 1
        if self.action is not None:
            if self.action < 0:
                raise ValueError(f"Invalid choice action {self.action}, must be >= 0.")
            if num_choice_actions is not None and self.action >= num_choice_actions:
                raise ValueError(
                    f"Invalid choice action {self.action}, must be < num_choice_actions ({num_choice_actions})."
                )


@dataclass
class ExplicitAts:
    """
    Explicit container for an annotated transition system (ATS). Public attributes are managed by the user and must be
    set appropriately; calling validate() checks for consistency.
    """

    #: Number of states.
    _num_states: int = 0
    #: For every state, a list of choices.
    _state_choices: list[list[Choice]] = field(default_factory=list)
    #: Number of choices.
    _num_choices: int = 0

    #: Information about the model.
    model_info: ModelInfo | None = None
    #: Type of time.
    time: TimeType = TimeType.DISCRETE

    #: Number of players.
    num_players: int = 0
    #: State-to-player mapping. Must be set if num_players >= 1.
    state_to_player: list[int] | None = None
    #: Player-to-name mapping. Can be set only if num_players >= 1.
    player_to_name: list[str] | None = None

    #: Number of initial states. Must be consistent with state_is_initial.
    num_initial_states: int = 0
    #: For each state, whether it is an initial one.
    state_is_initial: list[bool] = field(default_factory=list)

    #: State-to-whether-markovian mapping. Must be set if time is TimeType.URGENT_STOCHASTIC.
    state_is_markovian: list[bool] | None = None
    #: State-to-exit-rate mapping. Must be set if time is TimeType.STOCHASTIC or TimeType.URGENT_STOCHASTIC. Can contain arbitrary Numeric values.
    state_to_exit_rate: list[Numeric] | None = None

    #: Number of actions associated with choices.
    num_choice_actions: int = 0
    #: Choice-action-to-string mapping. Can only be set if num_choice_actions > 0.
    choice_action_to_name: list[str] | None = None

    #: Number of actions associated with branches.
    num_branch_actions: int = 0
    #: Branch-action-to-string mapping. Can only be set if num_branch_actions > 0.
    branch_action_to_name: list[str] | None = None

    #: Annotation category -> (annotation name -> annotation) mapping. Categories 'rewards' and 'aps' can be used, but
    #: must be of the type RewardAnnotation and AtomicPropositionAnnotation, respectively.
    annotations: dict[str, dict[str, Annotation]] = field(default_factory=lambda: {})

    #: Observation annotation.
    observation_annotation: ObservationAnnotation | None = None

    #: EntityClassValuations associated with the ATS.
    variable_valuations: EntityClassValuations | None = None

    def __str__(self) -> str:
        # TODO pretty print
        lines = [f"{self.__class__.__name__}("]
        for dataclass_field in fields(self):
            lines.append(f"  {dataclass_field.name}={getattr(self, dataclass_field.name)!r}")
        lines.append(")")
        return "\n".join(lines)

    # helper properties and methods

    @property
    def num_states(self) -> int:
        """Get the number of states."""
        return self._num_states

    @property
    def states(self) -> Iterable[int]:
        """Get the list of all states."""
        return range(self._num_states)

    def _check_state(self, state: int):
        if state < 0 or state >= self._num_states:
            raise ValueError(f"Invalid state {state}, must be >= 0 and < {self._num_states}.")

    def add_state(self) -> int:
        """Add a new state and return its index."""
        new_state = self._num_states
        self._num_states += 1
        self._state_choices.append([])
        return new_state

    def remove_state(self, state: int):
        """Remove the given state."""
        self._check_state(state)
        del self._state_choices[state]
        self._num_states -= 1
        # TODO check whether any branches point to the removed state

    @property
    def initial_states(self) -> list[int]:
        """Get the list of the initial states."""
        return [i for i, is_initial in enumerate(self.state_is_initial) if is_initial]

    def set_initial_states(self, initial_states: Iterable[int]):
        """Set the initial states."""
        self.state_is_initial = [False] * self.num_states
        for s in initial_states:
            self._check_state(s)
            self.state_is_initial[s] = True
        self.num_initial_states = len([is_initial for is_initial in self.state_is_initial if is_initial])

    def get_player_of_state(self, state: int) -> int:
        """Get the player controlling the given state."""
        self._check_state(state)
        if self.state_to_player is None:
            raise ValueError("state_to_player is not set")
        return self.state_to_player[state]

    @property
    def markovian_states(self) -> list[int]:
        """Get the list of the markovian states."""
        if self.state_is_markovian is None:
            raise ValueError("state_is_markovian is not set")
        return [i for i, is_markovian in enumerate(self.state_is_markovian) if is_markovian]

    def set_markovian_states(self, markovian_states: Iterable[int]):
        """Set the markovian states."""
        self.state_is_markovian = [False] * self.num_states
        for s in markovian_states:
            self._check_state(s)
            self.state_is_markovian[s] = True

    ### Choices and branches. ###

    def _check_choice_index(self, choice_index: int):
        if choice_index < 0 or choice_index >= self._num_choices:
            raise ValueError(f"Invalid choice index {choice_index}, must be >= 0 and < {self._num_choices}.")

    def add_state_choice(self, state: int) -> Choice:
        """Add a choice to the given state with the given action and return it."""
        self._check_state(state)
        choice_index = self._num_choices
        choice = Choice(_index=choice_index, state=state)
        self._state_choices[state].append(choice)
        self._num_choices += 1
        return choice

    def get_state_choices(self, state: int) -> Sequence[Choice]:
        """Get the list of choices of the given state."""
        self._check_state(state)
        return self._state_choices[state]

    def num_state_choices(self, state: int) -> int:
        """Get the number of choices of the given state."""
        self._check_state(state)
        return len(self._state_choices[state])

    def get_choice_by_index(self, choice_index: int) -> Choice:
        """Get the choice with the given global index."""
        self._check_choice_index(choice_index)
        # TODO optimize
        for choices in self._state_choices:
            for choice in choices:
                if choice.index == choice_index:
                    return choice
        raise ValueError(f"Choice with index {choice_index} not found.")

    def remove_choice(self, choice: Choice):
        """Remove the given choice."""
        self._check_state(choice.state)
        if choice not in self._state_choices[choice.state]:
            raise ValueError("Choice not found in state_choices.")
        self._state_choices[choice.state].remove(choice)
        self._num_choices -= 1

    @property
    def choices(self) -> Iterable[Choice]:
        """Get the list of all choices."""
        for choices in self._state_choices:
            yield from choices

    @property
    def num_choices(self) -> int:
        """Get the number of choices."""
        return self._num_choices

    @property
    def num_branches(self) -> int:
        """Get the number of branches."""
        return sum(choice.num_branches for choice in self.choices)

    @property
    def branches(self) -> Iterable[Branch]:
        """Get the list of all branches."""
        for choice in self.choices:
            yield from choice.branches

    ### Rewards. ###

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

    def add_reward_annotation(self, name: str, **kwargs) -> RewardAnnotation:
        """Add a reward annotation."""
        if self.has_reward_annotation(name):
            raise ValueError(f"reward annotation with name {name} already exists")
        annotation = RewardAnnotation(name=name, **kwargs)
        self.reward_annotations[name] = annotation
        return annotation

    def get_reward_annotation(self, name: str) -> RewardAnnotation:
        """Get the reward annotation with the given name."""
        if not self.has_reward_annotation(name):
            raise ValueError(f"reward annotation with name {name} does not exist")
        return self.reward_annotations[name]

    ### Atomic propositions. ###

    @property
    def ap_annotations(self) -> dict[str, AtomicPropositionAnnotation]:
        """Get the atomic proposition annotations."""
        if "aps" not in self.annotations:
            self.annotations["aps"] = {}
        return self.annotations["aps"]  # type: ignore

    @property
    def has_ap_annotations(self) -> bool:
        """Check if there are any atomic proposition annotations."""
        return len(self.ap_annotations) > 0

    @property
    def ap_annotation_names(self) -> list[str]:
        """Get the names of all atomic proposition annotations."""
        return list(self.ap_annotations.keys())

    def has_ap_annotation(self, name: str) -> bool:
        """Check if an atomic proposition annotation with the given name exists."""
        return name in self.ap_annotations

    def add_ap_annotation(self, name: str, **kwargs) -> AtomicPropositionAnnotation:
        """Add an atomic proposition annotation."""
        if self.has_ap_annotation(name):
            raise ValueError(f"atomic proposition annotation with name {name} already exists")
        annotation = AtomicPropositionAnnotation(name=name, **kwargs)
        self.ap_annotations[name] = annotation
        return annotation

    def get_ap_annotation(self, name: str) -> AtomicPropositionAnnotation:
        """Get the atomic proposition annotation with the given name."""
        if not self.has_ap_annotation(name):
            raise ValueError(f"atomic proposition annotation with name {name} does not exist")
        return self.ap_annotations[name]

    ### Observations. ###

    @property
    def num_observations(self) -> int:
        if self.observation_annotation is None:
            return 0
        return self.observation_annotation.num_observations

    @property
    def has_observations(self) -> bool:
        return self.num_observations > 0

    def add_observation_annotation(self, num_observations: int) -> ObservationAnnotation:
        if self.observation_annotation is not None:
            raise ValueError("observation annotation already exists")
        self.observation_annotation = ObservationAnnotation(num_observations=num_observations)
        return self.observation_annotation

    def get_observation_annotation(self) -> ObservationAnnotation:
        if self.observation_annotation is None:
            raise ValueError("observation annotation does not exist")
        return self.observation_annotation

    ### Variable valuations. ###

    @property
    def has_variable_valuations(self) -> bool:
        return self.variable_valuations is not None

    ### Extra methods. ###

    def validate(self):
        # TODO more checks

        if not self.num_states > 0:
            raise ValueError("expected num_states > 0")

        if self.num_players > 1:
            if self.state_to_player is None:
                raise ValueError("num_players > 1 but state_to_player is None")
            if len(self.state_to_player) != self.num_states:
                raise ValueError("expected len(state_to_player) == num_states")

        if len(self.state_is_initial) != self.num_states:
            raise ValueError("expected len(state_is_initial) == num_states")
        if self.num_initial_states != len(self.initial_states):
            raise ValueError("expected num_initial_states == len(initial_states)")

        if self.choices is not None:
            for choice in self.choices:
                choice.validate(
                    num_states=self.num_states,
                    num_choice_actions=self.num_choice_actions,
                    num_branch_actions=self.num_branch_actions,
                )

        for reward_annotation in self.reward_annotations.values():
            reward_annotation.validate()
        for ap_annotation in self.ap_annotations.values():
            ap_annotation.validate()
        if self.observation_annotation is not None:
            self.observation_annotation.validate()
        if self.has_variable_valuations:
            assert self.variable_valuations is not None
            for entity_class in self.variable_valuations.entity_classes:
                valuations = self.variable_valuations.get_valuations_for(entity_class)
                num_entities = {
                    EntityClass.STATES: self.num_states,
                    EntityClass.CHOICES: self.num_choices,
                    EntityClass.BRANCHES: self.num_branches,
                    EntityClass.OBSERVATIONS: self.num_observations,
                    EntityClass.PLAYERS: self.num_players,
                }[entity_class]
                if not valuations.num_entities == num_entities:
                    raise ValueError(
                        f"{entity_class} valuations has {valuations.num_entities} entities, expected {num_entities}"
                    )
                valuations.validate()

    def equal(self, other: object, debug: bool = False) -> bool:
        if not isinstance(other, ExplicitAts):
            if debug:
                logger.debug("ExplicitAts.__eq__: other is not an ExplicitAts")
            return False
        equal = True
        for field_name in self.__dataclass_fields__:
            if getattr(self, field_name) != getattr(other, field_name):
                equal = False
                if not debug:
                    break
                logger.debug(f"ExplicitAts.__eq__: field {field_name} differs")
                logger.debug(f"  self: {getattr(self, field_name)}")
                logger.debug(f"  other: {getattr(other, field_name)}")
        return equal

    def __eq__(self, other: object) -> bool:
        return self.equal(other)

    def _check_order(self, new_order: list[int], num_entities: int):
        if sorted(new_order) != list(range(num_entities)):
            raise ValueError("new_order must be a permutation of the entity indices")

    @property
    def _annotations(self) -> Iterable[Annotation]:
        if self.annotations is not None:
            for _, name_annotation in self.annotations.items():
                for _, annotation in name_annotation.items():
                    yield annotation
        if self.observation_annotation is not None:
            yield self.observation_annotation

    def _reorder_annotations(self, entity_class: EntityClass, new_order: list[int]):
        for annotation in self._annotations:
            annotation._reorder_entities(entity_class=entity_class, new_order=new_order)
        if self.variable_valuations is not None:
            self.variable_valuations._reorder_entities(entity_class=entity_class, new_order=new_order)

    def _reorder_choices(self, new_order: list[int]):
        """Reorder choices according to the given new order."""
        self._check_order(new_order, self.num_choices)

        # compute new branch order based on new choice order
        choice_to_branch_indices = []
        num_branches = 0
        for choice in self.choices:
            branch_indices = list(range(num_branches, num_branches + choice.num_branches))
            choice_to_branch_indices.append(branch_indices)
            num_branches += choice.num_branches
        branch_new_order = []
        for choice_index in new_order:
            branch_new_order.extend(choice_to_branch_indices[choice_index])
        self._reorder_annotations(entity_class=EntityClass.BRANCHES, new_order=branch_new_order)

        # reorder choice-related attributes
        for choice in self.choices:
            choice._index = new_order[choice._index]
        self._reorder_annotations(entity_class=EntityClass.CHOICES, new_order=new_order)

    def reorder_states(self, new_order: list[int]):
        """Reorder states according to the given new order."""
        self._check_order(new_order, self.num_states)

        # compute new choice order based on new state order
        state_to_choice_indices = []
        num_choices = 0
        for state in self.states:
            choice_indices = list(range(num_choices, num_choices + self.num_state_choices(state)))
            state_to_choice_indices.append(choice_indices)
            num_choices += self.num_state_choices(state)
        choice_new_order = []
        for state_index in new_order:
            choice_new_order.extend(state_to_choice_indices[state_index])
        self._reorder_choices(choice_new_order)

        # reorder state-related attributes
        self._state_choices = [self._state_choices[i] for i in new_order]
        for choice in self.choices:
            choice.state = new_order[choice.state]
            for branch in choice.branches:
                branch.target = new_order[branch.target]
        self.state_is_initial = [self.state_is_initial[i] for i in new_order]
        if self.state_to_player is not None:
            self.state_to_player = [self.state_to_player[i] for i in new_order]
        if self.state_is_markovian is not None:
            self.state_is_markovian = [self.state_is_markovian[i] for i in new_order]
        if self.state_to_exit_rate is not None:
            self.state_to_exit_rate = [self.state_to_exit_rate[i] for i in new_order]

        # reorder annotations with state values
        self._reorder_annotations(entity_class=EntityClass.STATES, new_order=new_order)

    def state_order_by_valuations(self) -> list[int]:
        """Get a new state order based on sorting by variable valuations."""
        if self.variable_valuations is None:
            raise ValueError("variable_valuations is not set")
        if not self.variable_valuations.has_state_valuations:
            raise ValueError("variable_valuations does not have state valuations")
        valuations = self.variable_valuations.state_valuations
        new_order = sorted(range(self.num_states), key=lambda s: valuations.get_entity_valuation_tuple(s))
        return new_order

    def reorder_states_by_valuations(self):
        """Reorder states based on sorting by variable valuations."""
        new_order = self.state_order_by_valuations()
        logger.debug(f"Reordering states by valuations with new order {new_order}")
        self.reorder_states(new_order)
