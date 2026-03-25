"""umbi demo: A random walk ATS."""

import logging
from fractions import Fraction

from ..explicit_ats import ExplicitAts, TimeType

logger = logging.getLogger(__name__)


def random_walk_ats(num_states: int) -> ExplicitAts:
    # create ATS
    ats = ExplicitAts()

    # basic parameters
    ats.time = TimeType.DISCRETE
    ats.num_players = 0
    ats.num_initial_states = 1
    ats.set_initial_states([num_states // 2])  # start in the middle state

    # two actions: left (0) and right (1), each with 0.9 success prob
    ats.num_choice_actions = 2
    ats.choice_action_to_name = ["left", "right"]

    # build structure
    for state in range(num_states):
        ats.add_state()

        # left action
        choice = ats.add_state_choice(state=state)
        left = max(0, state - 1)
        choice.add_branch(target=left, prob=Fraction(9, 10))
        choice.add_branch(target=state, prob=Fraction(1, 10))

        # right action
        choice = ats.add_state_choice(state=state)
        right = min(num_states - 1, state + 1)
        choice.add_branch(target=right, prob=Fraction(9, 10))
        choice.add_branch(target=state, prob=Fraction(1, 10))

    ats.state_is_markovian = [True] * ats.num_states
    ats.state_to_exit_rate = [1] * ats.num_states  # type: ignore[assignment]

    # example: APs
    annotation = ats.add_ap_annotation(
        name="is_terminal", alias="Terminal State", description="Indicates whether the state is terminal."
    )
    annotation.set_state_values([s == 0 or s == ats.num_states - 1 for s in ats.states])

    # example: rewards
    annotation = ats.add_reward_annotation(name="steps", alias="step cost", description="Cost incurred at each step.")
    annotation.set_state_values([-1] * ats.num_states)

    # wall hit penalty
    choice_penalty = [0] * ats.num_choices
    for choice in ats.get_state_choices(0):
        assert choice.action is not None
        if ats.choice_action_to_name[choice.action] == "left":  # left action in first state
            choice_penalty[choice.index] = -10
    for choice in ats.get_state_choices(ats.num_states - 1):
        assert choice.action is not None
        if ats.choice_action_to_name[choice.action] == "right":  # right action in last state
            choice_penalty[choice.index] = -10
    annotation = ats.add_reward_annotation(
        name="wall_hit_penalty",
        alias="wall hit penalty",
        description="Penalty incurred when hitting a wall.",
    )
    annotation.set_choice_values(choice_penalty)

    # observations: 3 observations, based on state mod 3
    annotation = ats.add_observation_annotation(num_observations=3)
    annotation.set_state_values([s % 3 for s in ats.states])

    ats.validate()
    return ats
