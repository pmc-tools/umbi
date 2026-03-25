"""umbi demo: Create an ExplicitAts from a grid string."""

import logging
from fractions import Fraction

from ..explicit_ats import ExplicitAts, TimeType
from ..variable_valuations import EntityClassValuations, EntityValuations

logger = logging.getLogger(__name__)


def grid_ats(grid: str) -> ExplicitAts:
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
    ats = ExplicitAts()
    ats.time = TimeType.DISCRETE
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

    ats.set_initial_states(list(initial_states))

    if ats.variable_valuations is None:
        ats.variable_valuations = EntityClassValuations()
    if not ats.variable_valuations.has_state_valuations:
        ats.variable_valuations.set_state_valuations(EntityValuations())
    state_valuations = ats.variable_valuations.state_valuations
    vx = state_valuations.add_variable("x")
    vy = state_valuations.add_variable("y")
    for state in ats.states:
        x, y = state_to_cell[state]
        state_valuations.set_entity_valuation(state, {vx: x, vy: y})

    direction_dxdy = {
        "up": (0, 1),
        "down": (0, -1),
        "left": (-1, 0),
        "right": (1, 0),
    }

    ats.choice_action_to_name = list(direction_dxdy.keys())
    ats.num_choice_actions = len(ats.choice_action_to_name)

    for (x, y), state in cell_to_state.items():
        ats.add_state()
        for direction, (dx, dy) in direction_dxdy.items():
            target = (x + dx, y + dy)
            choice = ats.add_state_choice(state=state)
            choice.action = ats.choice_action_to_name.index(direction)

            if target in cell_to_state:
                target_state = cell_to_state[target]
                choice.add_branch(target=target_state, prob=Fraction(9, 10))
                choice.add_branch(target=state, prob=Fraction(1, 10))
            else:
                choice.add_branch(target=state)

    annotation = ats.add_ap_annotation(name="goal")
    annotation.set_state_values([s in goal_states for s in range(ats.num_states)])

    annotation = ats.add_reward_annotation(name="step_cost")
    annotation.set_choice_values([1 for _ in range(ats.num_choices)])

    ats.validate()
    return ats
