"""umbi demo: Create an SimpleAts from a grid string."""

import logging
import random
from fractions import Fraction

from ..simple_ats import SimpleAts
from ..time_type import TimeType

logger = logging.getLogger(__name__)


def random_grid_string(width: int, height: int, seed: int | None = None) -> str:
    """
    Generate a random grid string of size width x height.

    :param width: the width of the grid
    :param height: the height of the grid
    :param seed: optional seed for reproducible randomness
    :return: A grid string with:
        - exactly 1 'i' (initial state)
        - random number of 'g' (goal states)
        - random number of 'x' (obstacles)
        - rest are '.' (empty cells)
    """
    if seed is not None:
        random.seed(seed)

    total_cells = width * height
    cells = ["."] * total_cells

    # Place exactly one 'i'
    i_idx = random.randint(0, total_cells - 1)
    cells[i_idx] = "i"

    # Random number of 'g's (at least 1, up to ~5% of remaining cells)
    num_goals = random.randint(1, max(1, total_cells // 20))
    goal_positions = random.sample([i for i in range(total_cells) if i != i_idx], min(num_goals, total_cells - 1))
    for pos in goal_positions:
        cells[pos] = "g"

    # Random number of 'x's from remaining cells (20 to ~50% of remaining cells)
    remaining_positions = [i for i in range(total_cells) if cells[i] == "."]
    num_obstacles = random.randint(max(1, len(remaining_positions) // 5), max(1, len(remaining_positions) // 2))
    obstacle_positions = random.sample(remaining_positions, min(num_obstacles, len(remaining_positions)))
    for pos in obstacle_positions:
        cells[pos] = "x"

    # Convert to grid string (width x height, with newlines)
    grid_rows = ["".join(cells[i * width : (i + 1) * width]) for i in range(height)]
    return "\n".join(reversed(grid_rows))  # reverse for top-to-bottom display


def grid(grid: str) -> SimpleAts:
    """
    Create a simple ATS from a rectangular grid string.

    :param grid: A rectangular grid string where:
        - 'i' represents the initial state
        - 'g' represents a goal state
        - 'x' represents an obstacle
        - any other character represents an empty cell
    :return: An SimpleAts object.
    """
    # parse the grid into a 2D array
    parsed_grid = [
        list(row.strip()) for row in reversed(grid.strip().split("\n"))
    ]  # reverse to have (0,0) at bottom left
    rows, cols = len(parsed_grid), len(parsed_grid[0])
    if any(len(row) != cols for row in parsed_grid):
        raise ValueError("The grid must be rectangular (all rows must have the same length).")

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

    # Create ATS
    ats = SimpleAts()
    ats.time = TimeType.DISCRETE
    ats.num_players = 1
    ats.num_states = len(cell_to_state)
    ats.initial_states = list(initial_states)

    variable_valuations = ats.add_variable_valuations()
    state_valuations = variable_valuations.add_state_valuations()
    vx = state_valuations.new_variable("x")
    vy = state_valuations.new_variable("y")
    for state in ats.states:
        x, y = state_to_cell[state]
        state_valuations.set_entity_valuation(state, {vx: x, vy: y})

    direction_dxdy = {
        "up": (0, 1),
        "down": (0, -1),
        "left": (-1, 0),
        "right": (1, 0),
    }

    ats.num_choice_actions = len(direction_dxdy)
    ats.choice_action_to_name = list(direction_dxdy.keys())

    for (x, y), state in cell_to_state.items():
        for direction, (dx, dy) in direction_dxdy.items():
            target = (x + dx, y + dy)
            choice = ats.new_state_choice(state=state)
            ats.choice_to_choice_action[choice] = ats.choice_action_to_name.index(direction)

            if target in cell_to_state:
                target_state = cell_to_state[target]
                ats.new_choice_branch(choice=choice, target=target_state, prob=Fraction(9, 10))
                ats.new_choice_branch(choice=choice, target=state, prob=Fraction(1, 10))
            else:
                ats.new_choice_branch(choice=choice, target=state)

    annotation = ats.new_ap_annotation(name="goal")
    annotation.state_values = [s in goal_states for s in ats.states]

    annotation = ats.new_reward_annotation(name="step_cost")
    annotation.choice_values = [1 for _ in ats.choices]

    ats.validate()
    return ats
