import logging
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field

from umbi.datatypes import Numeric, is_numeric_a_probability

from .entity_space import EntityMapping
from .entity_space_mixins import HasBranchSpace, HasChoiceSpace, HasStateSpace

logger = logging.getLogger(__name__)


@dataclass
class StateToChoicesMixin(HasStateSpace, HasChoiceSpace):
    #: For every state, a list of choice indices.
    _state_to_choices: EntityMapping[list[int]] = field(init=False)
    #: For every choice, its source state.
    _choice_to_state: EntityMapping[int] = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self._state_to_choices = EntityMapping(
            name="state_to_choices",
            domain=self._state_space,
            codomain=self._choice_space,
            maps_to_powerset=True,
            default_factory=list,
        )
        self._choice_to_state = EntityMapping(
            name="choice_to_state", domain=self._choice_space, codomain=self._state_space
        )

    @property
    def state_to_choices(self) -> EntityMapping[list[int]]:
        """Get the state-to-choices mapping."""
        return self._state_to_choices

    @property
    def choice_to_state(self) -> EntityMapping[int]:
        """Get the choice-to-state mapping."""
        return self._choice_to_state

    def get_state_choices(self, state: int) -> Sequence[int]:
        """Get the list of choices of the given state."""
        # self._state_space._check_entity(state)
        return self._state_to_choices[state]

    def num_state_choices(self, state: int) -> int:
        """Get the number of choices of the given state."""
        return len(self.get_state_choices(state))


@dataclass
class ChoiceToBranchesMixin(HasChoiceSpace, HasBranchSpace):
    #: For every choice, a list of branch indices.
    _choice_to_branches: EntityMapping[list[int]] = field(init=False)
    #: For every branch, its source choice.
    _branch_to_choice: EntityMapping[int] = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self._choice_to_branches = EntityMapping(
            name="choice_to_branches",
            domain=self._choice_space,
            codomain=self._branch_space,
            maps_to_powerset=True,
            default_factory=list,
        )
        self._branch_to_choice = EntityMapping(
            name="branch_to_choice", domain=self._branch_space, codomain=self._choice_space
        )

    @property
    def choice_to_branches(self) -> Sequence[list[int]]:
        """Get the choice-to-branches mapping."""
        return self._choice_to_branches

    def get_choice_branches(self, choice: int) -> Sequence[int]:
        """Get the list of branches of the given choice."""
        # self._choice_space._check_entity(choice)
        return self._choice_to_branches[choice]

    def num_choice_branches(self, choice: int) -> int:
        """Get the number of branches of the given choice."""
        return len(self.get_choice_branches(choice))

    def validate(self) -> None:
        self._choice_to_branches.validate()
        self._branch_to_choice.validate()
        super().validate()


@dataclass
class BranchToTargetMixin(HasStateSpace, HasBranchSpace):
    #: For every branch, its target state.
    _branch_to_target: EntityMapping[int] = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self._branch_to_target = EntityMapping(
            name="branch_to_target", domain=self._branch_space, codomain=self._state_space
        )

    @property
    def branch_to_target(self) -> EntityMapping[int]:
        return self._branch_to_target

    def validate(self) -> None:
        self._branch_to_target.validate()
        super().validate()


@dataclass
class BranchToProbabilityMixin(HasBranchSpace):
    #: For every branch, its probability.
    _branch_to_probability: EntityMapping[Numeric] = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self._branch_to_probability = EntityMapping(name="branch_to_probability", domain=self._branch_space)

    @property
    def branch_to_probability(self) -> EntityMapping[Numeric]:
        return self._branch_to_probability

    def validate(self) -> None:
        self._branch_to_probability.validate(allow_undefined_values=True)
        for branch, prob in enumerate(self._branch_to_probability):
            if prob is not None and not is_numeric_a_probability(prob):
                raise ValueError(f"Branch {branch} has invalid probability {prob}.")
        super().validate()


@dataclass
class ChoicesMixin(
    StateToChoicesMixin,
    ChoiceToBranchesMixin,
    BranchToTargetMixin,
    BranchToProbabilityMixin,
):
    def __post_init__(self):
        super().__post_init__()

    def validate(self) -> None:
        for choice in self.choices:
            num_branches = self.num_choice_branches(choice)
            if num_branches == 0:
                raise ValueError(f"Choice {choice} has no branches.")
            if num_branches == 1 and self._branch_to_probability[self._choice_to_branches[choice][0]] is None:
                self._branch_to_probability[self._choice_to_branches[choice][0]] = 1
            branch_probs = [self._branch_to_probability[branch] for branch in self._choice_to_branches[choice]]
            if any(prob is None for prob in branch_probs):
                raise ValueError(f"Choice {choice} has multiple branches but some have undefined probabilities.")
            # TODO check that probabilities sum to 1
        super().validate()

    def new_state_choice(
        self,
        state: int,
        targets: Iterable[int] | None = None,
        target_prob: Callable[[int], Numeric | None] | None = None,
    ) -> int:
        """Add a choice to the given state.
        :param state: source state for the new choice
        :param targets: optional iterable of target states for the branches of the new choice
        :param target_prob: optional function mapping target states to branch probabilities
        :return: the new choice index
        """
        # self.state_space._check_entity(state)
        choice = self._new_choice()
        self.state_to_choices[state].append(choice)
        self._choice_to_state[choice] = state
        if targets is not None and target_prob is not None:
            self.new_choice_branches(choice, targets=targets, target_prob=target_prob)
        return choice

    def remove_choice(self, choice: int) -> list[int]:
        """
        Remove a choice and all its branches.
        :param choice: choice to remove
        :return: new-to-old choice mapping after removal
        """
        self._choice_space.check_entity(choice)
        # remove choice from state-to-choices
        state = self._choice_to_state[choice]
        self.state_to_choices[state].remove(choice)
        self._remove_branches(self._choice_to_branches[choice])
        return self._remove_choice(choice)

    def remove_choices(self, choices: Sequence[int]) -> None:
        # copy and sort in reverse to avoid messing up indices when removing
        choices = sorted(choices, reverse=True)
        for choice in choices:
            self.remove_choice(choice)

    def new_choice_branch(self, choice: int, target: int | None = None, prob: Numeric | None = None) -> int:
        """Add a branch to the given choice and return it."""
        self._choice_space.check_entity(choice)
        if target is not None:
            self._state_space.check_entity(target)
        new_branch = self._new_branch()
        self._choice_to_branches[choice].append(new_branch)
        self._branch_to_choice[new_branch] = choice
        if target is not None:
            self._branch_to_target[new_branch] = target
        if prob is not None:
            self._branch_to_probability[new_branch] = prob
        return new_branch

    def new_choice_branches(
        self, choice: int, targets: Iterable[int], target_prob: Callable[[int], Numeric | None]
    ) -> list[int]:
        """Add branches to the given choice for multiple targets.
        :param choice: choice to add branches to
        :param targets: target states for the new branches
        :param target_prob: function mapping target states to branch probabilities
        :return: list of new branches added
        """
        new_branches = []
        for target in targets:
            prob = target_prob(target)
            branch = self.new_choice_branch(choice, target=target, prob=prob)
            new_branches.append(branch)
        return new_branches

    def remove_branch(self, branch: int) -> None:
        self._branch_space.check_entity(branch)
        choice = self._branch_to_choice[branch]
        self._choice_to_branches[choice].remove(branch)
        self._remove_branch(branch)

    def remove_branches(self, branches: Sequence[int]) -> None:
        for branch in branches:
            self.remove_branch(branch)

    def sort_choices(self) -> list[int]:
        """Reorder choices by sorting by their source states.
        :return: new-to-old choice mapping after sorting
        """
        new_to_old = sorted(self.choices, key=lambda c: self._choice_to_state[c])
        self._permute_choices(new_to_old)
        for state in self._state_space.entities:
            self.state_to_choices[state] = sorted(self.state_to_choices[state])
        return new_to_old

    def sort_branches(self) -> list[int]:
        """Reorder branches by sorting by their source choices and targets.
        :return: new-to-old branch mapping after sorting
        """
        new_to_old = sorted(self.branches, key=lambda b: (self._branch_to_choice[b], self._branch_to_target[b]))
        self._permute_branches(new_to_old)
        for choice in self._choice_space.entities:
            self._choice_to_branches[choice] = sorted(self._choice_to_branches[choice])
        return new_to_old

    def sort_transitions(self) -> None:
        """Reorder choices and branches by sorting by their source states and choices."""
        self.sort_choices()
        self.sort_branches()
