import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from umbi.datatypes import DataType, common_collection_element_type
from .entity_class import EntityClass
from .annotations import (
    Annotation,
    RewardAnnotation,
    AtomicPropositionAnnotation,
    ObservationAnnotation,
)
from .model_info import ModelInfo
from .variable_valuations import EntityClassValuations

logger = logging.getLogger(__name__)


class TimeType(str, Enum):
    """Time types for transition systems."""

    DISCRETE = "discrete"
    STOCHASTIC = "stochastic"
    URGENT_STOCHASTIC = "urgent-stochastic"


@dataclass
class ExplicitAts:
    """
    Explicit container for an annotated transition system (ATS). All the attributes can be freely manipulated.
    Method validate() can be used to check for consistency.
    """

    model_info: ModelInfo | None = None
    """Information about the model."""
    time: TimeType = TimeType.DISCRETE
    """Type of time."""
    num_states: int = 1
    """Number of states. Must be > 0."""

    num_players: int = 0
    """Number of players."""
    state_to_player: list[int] | None = None
    """State-to-player mapping. Must be set if num_players >= 1."""
    player_to_name: list[str] | None = None
    """Player-to-name mapping. Can be set only if num_players >= 1."""

    num_initial_states: int = 0
    """Number of initial states. Must be consistent with state_is_initial."""
    state_is_initial: list[bool] = field(default_factory=list)
    """State-to-whether-initial mapping."""

    num_choices: int = 0
    """Number of choices."""
    state_to_choice: list[int] | None = None
    """CSR list of length num_states + 1. Must be set if num_choices > 0."""

    num_branches: int = 0
    """Number of branches."""
    choice_to_branch: list[int] | None = None
    """CSR list of length num_choices + 1. Must be set if num_branches > 0."""

    branch_to_target: list[int] | None = None
    """Branch-to-target-state mapping. Must be set if num_branches > 0."""
    branch_probabilities: list | None = None
    """Branch-to-probability mapping. Must be set if num_branches > 0. Can contain arbitrary Numeric values."""

    state_is_markovian: list[bool] | None = None
    """State-to-whether-markovian mapping. Must be set if time is TimeType.STOCHASTIC."""
    state_exit_rate: list | None = None
    """State-to-exit-rate mapping. Must be set if time is TimeType.STOCHASTIC. Can contain arbitrary Numeric values."""

    num_choice_actions: int = 0
    """Number of actions associated with choices."""
    choice_to_choice_action: list[int] | None = None
    """Choice-to-choice-action mapping. Must be set if num_choice_actions > 0."""
    choice_action_to_name: list[str] | None = None
    """Choice-action-to-string mapping. Can only be set if num_choice_actions > 0."""

    num_branch_actions: int = 0
    """Number of actions associated with branches."""
    branch_to_branch_action: list[int] | None = None
    """Branch-to-branch-action mapping. Must be set if num_branch_actions > 0."""
    branch_action_to_name: list[str] | None = None
    """Branch-action-to-string mapping. Can only be set if num_branch_actions > 0."""

    annotations: dict[str, dict[str, Annotation]] = field(default_factory=dict)
    """
    Annotation category -> (annotation name -> annotation) mapping. Categories 'rewards' and 'aps' can be used, but
    must be of the type RewardAnnotation and AtomicPropositionAnnotation, respectively.
    """

    observation_annotation: ObservationAnnotation | None = None
    """Observation annotation."""

    variable_valuations: EntityClassValuations | None = None
    """EntityClassValuations associated with the ATS."""

    # helper properties and methods

    @property
    def initial_states(self) -> list[int]:
        """Get the list of the initial states."""
        return [i for i, is_initial in enumerate(self.state_is_initial) if is_initial]

    def set_initial_states(self, initial_states: Iterable[int]):
        """Set the initial states."""
        self.state_is_initial = [False] * self.num_states
        for s in initial_states:
            if s >= self.num_states:
                raise ValueError(f"Invalid state {s}, must be < {self.num_states}.")
            self.state_is_initial[s] = True
        self.num_initial_states = len([is_initial for is_initial in self.state_is_initial if is_initial])

    def get_player_of_state(self, state: int) -> int:
        """Get the player controlling the given state."""
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
            if s >= self.num_states:
                raise ValueError(f"Invalid state {s}, must be < {self.num_states}.")
            self.state_is_markovian[s] = True

    def state_choice_range(self, state: int) -> Iterable[int]:
        """Return the choice range of the given state."""
        if self.state_to_choice is None:
            raise ValueError("state_to_choice is not set")
        assert state <= self.num_states
        return range(self.state_to_choice[state], self.state_to_choice[state + 1])

    def choice_branch_range(self, choice: int) -> Iterable[int]:
        """Return the branch range of the given choice."""
        if self.choice_to_branch is None:
            raise ValueError("choice_to_branch is not set")
        assert choice <= self.num_choices
        return range(self.choice_to_branch[choice], self.choice_to_branch[choice + 1])

    @property
    def branch_probability_type(self) -> DataType | None:
        if self.branch_probabilities is None:
            return None
        return common_collection_element_type(self.branch_probabilities)

    @property
    def exit_rate_type(self) -> DataType | None:
        if self.state_exit_rate is None:
            return None
        return common_collection_element_type(self.state_exit_rate)

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

    def add_reward_annotation(self, annotation: RewardAnnotation):
        """Add a reward annotation."""
        if self.has_reward_annotation(annotation.name):
            raise ValueError(f"reward annotation with name {annotation.name} already exists")
        self.reward_annotations[annotation.name] = annotation

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

    def add_ap_annotation(self, annotation: AtomicPropositionAnnotation):
        """Add an atomic proposition annotation."""
        if self.has_ap_annotation(annotation.name):
            raise ValueError(f"atomic proposition annotation with name {annotation.name} already exists")
        self.ap_annotations[annotation.name] = annotation

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

    ### Variable valuations. ###

    @property
    def has_variable_valuations(self) -> bool:
        return self.variable_valuations is not None

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

        if self.state_to_choice is not None:
            if len(self.state_to_choice) != self.num_states + 1:
                raise ValueError("expected len(state_to_choice) == num_states+1")
        if self.choice_to_branch is not None:
            if len(self.choice_to_branch) != self.num_choices + 1:
                raise ValueError("expected len(choice_to_branch) == num_choices+1")
        if self.branch_to_target is not None:
            if len(self.branch_to_target) != self.num_branches:
                raise ValueError("expected len(branch_to_target) == num_branches")

        for reward_annotation in self.reward_annotations.values():
            if not isinstance(reward_annotation, RewardAnnotation):
                raise ValueError(f"expected RewardAnnotation, got {type(reward_annotation)}")
            reward_annotation.validate()
        for ap_annotation in self.ap_annotations.values():
            if not isinstance(ap_annotation, AtomicPropositionAnnotation):
                raise ValueError(f"expected AtomicPropositionAnnotation, got {type(ap_annotation)}")
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
                    EntityClass.OBSERVATION: self.num_observations,
                    EntityClass.PLAYERS: self.num_players,
                }[entity_class]
                if not valuations.num_entities == num_entities:
                    raise ValueError(
                        f"{entity_class} valuations has {valuations.num_entities} entities, expected {num_entities}"
                    )
                valuations.validate()

    def equal(self, other: object, debug=False) -> bool:
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

    def __eq__(self, other):
        return self.equal(other)
