#!/usr/bin/env python3
"""
umbi demo: Create an ATS from a grid string.
"""

import argparse
import pathlib
import sys
from fractions import Fraction

import umbi
import umbi.ats
import logging

logger = logging.getLogger(__name__)


def grid_ats_from_string(grid: str) -> umbi.ats.ExplicitAts:
    """
    Create a simple ATS from a rectangular grid string.

    :param grid: A rectangular grid string where:
        - 'i' represents the initial state
        - 'g' represents a goal state
        - 'x' represents an obstacle
        - any other character represents an empty cell
    :return: An ExplicitAts object.
    """
    # parse the grid into a 2D array
    parsed_grid = [
        list(row.strip()) for row in reversed(grid.strip().split("\n"))
    ]  # reverse to have (0,0) at bottom left
    rows, cols = len(parsed_grid), len(parsed_grid[0])
    if any(len(row) != cols for row in parsed_grid):
        raise ValueError("The grid must be rectangular (all rows must have the same length).")

    # Create ATS
    ats = umbi.ats.ExplicitAts()
    ats.time = umbi.ats.TimeType.DISCRETE
    ats.num_players = 1

    cell_to_state = {}
    initial_states = set()
    goal_states = set()

    state_to_cell = []

    for y in range(rows):
        for x in range(cols):
            c = parsed_grid[y][x]
            if c == "x":
                continue
            state = len(cell_to_state)
            state_to_cell.append((x, y))
            cell_to_state[(x, y)] = state
            if c == "i":
                initial_states.add(state)
            elif c == "g":
                goal_states.add(state)

    ats.num_states = len(cell_to_state)
    ats.set_initial_states(list(initial_states))

    if ats.variable_valuations is None:
        ats.variable_valuations = umbi.ats.EntityClassValuations()
    if not ats.variable_valuations.has_state_valuations:
        ats.variable_valuations.set_state_valuations(umbi.ats.EntityValuations())
    state_valuations = ats.variable_valuations.state_valuations
    vx = state_valuations.add_variable("x")
    vy = state_valuations.add_variable("y")
    for state in range(ats.num_states):
        x, y = state_to_cell[state]
        state_valuations.set_entity_valuation(state, {vx: x, vy: y})

    direction_dxdy = {
        "up": (0, 1),
        "down": (0, -1),
        "left": (-1, 0),
        "right": (1, 0),
    }

    ats.state_to_choice = []
    ats.choice_to_branch = []
    ats.branch_to_target = []
    ats.branch_probabilities = []
    ats.choice_to_choice_action = []
    ats.choice_action_to_name = list(direction_dxdy.keys())
    ats.num_choice_actions = len(ats.choice_action_to_name)

    for (x, y), state in cell_to_state.items():
        ats.state_to_choice.append(len(ats.choice_to_choice_action))

        for direction, (dx, dy) in direction_dxdy.items():
            target = (x + dx, y + dy)
            ats.choice_to_choice_action.append(ats.choice_action_to_name.index(direction))
            ats.choice_to_branch.append(len(ats.branch_to_target))

            if target in cell_to_state:
                target_state = cell_to_state[target]
                ats.branch_to_target.extend([target_state, state])
                ats.branch_probabilities.extend([Fraction(9, 10), Fraction(1, 10)])
            else:
                ats.branch_to_target.append(state)
                ats.branch_probabilities.append(1)

    ats.state_to_choice.append(len(ats.choice_to_choice_action))
    ats.choice_to_branch.append(len(ats.branch_to_target))
    ats.num_choices = len(ats.choice_to_choice_action)
    ats.num_branches = len(ats.branch_to_target)

    goal_ap = umbi.ats.AtomicPropositionAnnotation(name="goal")
    goal_ap.set_state_values([s in goal_states for s in range(ats.num_states)])
    ats.add_ap_annotation(goal_ap)

    step_cost_reward = umbi.ats.RewardAnnotation(name="step_cost")
    step_cost_reward.set_choice_values([1 for _ in range(ats.num_choices)])
    ats.add_reward_annotation(step_cost_reward)

    return ats


def main(args):
    if args.input == "-":
        text = sys.stdin.read()
    else:
        with pathlib.Path(args.input).open("rt") as f:
            text = f.read()
    ats = grid_ats_from_string(text)
    ats.validate()
    # umbi.io.write_ats(ats, args.output)
    # logger.info(f"Written to {args.output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an umbfile from a gridworld text file.")
    parser.add_argument(
        "input", help="filename of the gridworld text file (or '-' to read from stdin)", type=str, default="-"
    )
    parser.add_argument(
        "--output",
        help="Destination to write to",
        type=pathlib.Path,
        required=False,
        default=pathlib.Path("out.umb"),
    )
    main(parser.parse_args())
