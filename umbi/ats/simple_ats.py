import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass, fields

from umbi.datatypes import Numeric

from .actions_mixin import ActionsMixin
from .annotations_mixin import AnnotationsMixin, ObservationsMixin
from .choices_mixin import ChoicesMixin
from .entity_space_mixins import EntitySpaceMixin
from .model_info import ModelInfoMixin
from .players_mixin import PlayersMixin
from .states_mixin import StatesMixin
from .time_type import TimeTypeMixin
from .variable_valuations import VariableValuationsMixin

logger = logging.getLogger(__name__)


@dataclass
class SimpleAts(
    ModelInfoMixin,
    EntitySpaceMixin,
    TimeTypeMixin,
    PlayersMixin,
    StatesMixin,
    ChoicesMixin,
    ActionsMixin,
    AnnotationsMixin,
    ObservationsMixin,
    VariableValuationsMixin,
):
    """
    Annotated transition system (ATS) with a simple and exhaustive interface.
    """

    def __post_init__(self):
        super().__post_init__()

    ### Extra methods. ###

    def __str__(self) -> str:
        # TODO pretty print
        lines = [f"{self.__class__.__name__}("]
        for dataclass_field in fields(self):
            lines.append(f"  {dataclass_field.name}={str(getattr(self, dataclass_field.name))}")
        lines.append(")")
        return "\n".join(lines)

    def equals(self, other: object, debug: bool = False) -> bool:
        """Check equality with another SimpleAts by comparing all mixin fields."""
        if not isinstance(other, SimpleAts):
            if debug:
                logger.debug("SimpleAts.equals: other is not a SimpleAts")
            return False
        # chain through all parent mixins to compare their fields
        return super().equals(other, debug)

    def __eq__(self, other: object) -> bool:
        return self.equals(other)

    def new_state_choice(
        self,
        state: int,
        targets: Sequence[int] | None = None,
        probs: Sequence[Numeric] | None = None,
        target_prob: Callable[[int], Numeric] | None = None,
        action: int | None = None,
        action_name: str | None = None,
    ) -> int:
        """Add a choice to the given state.
        :param state: source state for the new choice
        :param targets: optional iterable of target states for the branches of the new choice
        :param probs: optional probabilities for the new branches
        :param target_prob: optional function mapping target states to branch probabilities
        :param action: optional choice action; will ensure the existence of the choice action if provided
        :param action_name: optional choice action name; will ensure the existence of the choice action name if provided
        :return: the new choice index
        """
        choice = super().new_state_choice(state, targets=targets, probs=probs, target_prob=target_prob)
        if action is not None:
            self._ensure_choice_action_exists(action)
        elif action_name is not None:
            # look up the choice action by name, or create a new one if it doesn't exist
            if not self.has_choice_to_choice_action:
                action = self._new_choice_action()
            if not self.has_choice_action_to_name:
                self.add_choice_action_to_name()
            if action is None:
                try:
                    action = self.choice_action_to_name.index(action_name)
                except ValueError:
                    action = self._new_choice_action()
            self.choice_action_to_name[action] = action_name
        if action is not None:
            self.choice_to_choice_action[choice] = action
        return choice

    ### Removing states leading to removing choices. ###

    def remove_state(self, state: int) -> list[int]:
        """Remove a state and all its associated choices.
        :param state: state to remove
        :return: new-to-old state mapping after removal
        """
        self._state_space.check_entity(state)
        self.remove_choices(self.state_to_choices[state])
        return self._remove_state(state)

    def remove_states(self, states: Sequence[int]) -> list[int]:
        """Remove multiple states and all their associated choices.
        :param states: states to remove
        :return: new-to-old state mapping after removal
        """
        for state in states:
            self._state_space.check_entity(state)
            self.remove_choices(self.state_to_choices[state])
        return self._remove_states(states)

    ### Reordering. ###

    def state_order_by_valuations(self) -> list[int]:
        """Get a new state order based on sorting by variable valuations.
        :return: new state order as a list of state indices
        :raises ValueError: if the ATS does not have state valuations
        """
        if self.variable_valuations is None or not self.variable_valuations.has_state_valuations:
            raise ValueError("ATS does not have state valuations")
        valuations = self.variable_valuations.state_valuations
        variables = sorted(valuations.variables, key=lambda v: v.name)
        state_valuation_tuples = [
            valuations.get_entity_valuation_tuple(s, variable_order=variables) for s in self.states
        ]
        new_to_old = sorted(self.states, key=lambda s: state_valuation_tuples[s])
        return new_to_old

    def sort_states_by_valuations(self) -> list[int]:
        """Reorder states based on sorting by variable valuations.
        :return new state order as a list of state indices
        :raises ValueError: if the ATS does not have state valuations
        """
        new_to_old = self.state_order_by_valuations()
        self.permute_states(new_to_old)

        # check that the new order is correct
        check_order = self.state_order_by_valuations()
        if check_order != list(range(self.num_states)):
            raise ValueError("State order after sorting by valuations is not correct")
        return new_to_old
