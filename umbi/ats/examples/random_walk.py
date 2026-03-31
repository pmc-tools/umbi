"""umbi demo: A random walk ATS."""

import logging
from fractions import Fraction

from ..simple_ats import SimpleAts
from ..time_type import TimeType

logger = logging.getLogger(__name__)


def random_walk(num_states: int) -> SimpleAts:
    # create ATS
    ats = SimpleAts()

    # basic parameters
    ats.time = TimeType.STOCHASTIC
    ats.num_players = 0

    # two actions: left (0) and right (1), each with 0.9 success prob
    ats.num_choice_actions = 2
    ats.choice_action_to_name = ["left", "right"]

    ats.num_states = num_states
    ats.initial_states = [num_states // 2]  # start in the middle state
    ats.state_to_exit_rate = [1] * ats.num_states

    # build structure
    for state in ats.states:
        # left action
        choice = ats.new_state_choice(state=state)
        ats.choice_to_choice_action[choice] = 0
        left = max(0, state - 1)
        ats.new_choice_branch(choice=choice, target=left, prob=Fraction(9, 10))
        ats.new_choice_branch(choice=choice, target=state, prob=Fraction(1, 10))

        # right action
        choice = ats.new_state_choice(state=state)
        ats.choice_to_choice_action[choice] = 1
        right = min(num_states - 1, state + 1)
        ats.new_choice_branch(choice=choice, target=right, prob=Fraction(9, 10))
        ats.new_choice_branch(choice=choice, target=state, prob=Fraction(1, 10))

    # example: APs
    annotation = ats.new_ap_annotation(
        name="is_terminal", alias="Terminal State", description="Indicates whether the state is terminal."
    )
    annotation.state_values = [s == 0 or s == ats.num_states - 1 for s in ats.states]

    # example: rewards
    annotation = ats.new_reward_annotation(name="steps", alias="step cost", description="Cost incurred at each step.")
    annotation.state_values = [-1] * ats.num_states

    # wall hit penalty
    choice_penalty = [0] * ats.num_choices
    for choice in ats.get_state_choices(0):
        if ats.choice_action_to_name[ats.choice_to_choice_action[choice]] == "left":  # left action in first state
            choice_penalty[choice] = -10
    for choice in ats.get_state_choices(ats.num_states - 1):
        if ats.choice_action_to_name[ats.choice_to_choice_action[choice]] == "right":  # right action in last state
            choice_penalty[choice] = -10
    annotation = ats.new_reward_annotation(
        name="wall_hit_penalty",
        alias="wall hit penalty",
        description="Penalty incurred when hitting a wall.",
    )
    annotation.choice_values = choice_penalty

    # observations: 3 observations, based on state mod 3
    ats.num_observations = 3
    ats.observation_annotation.state_values = [s % 3 for s in ats.states]

    ats.validate()
    return ats
