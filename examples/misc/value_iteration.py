"""
umbi demo: Perform reachability via VI on a fitting UMBI model
"""

import math
import pathlib

import click

import umbi
import umbi.ats


def reachability_vi(
    model: umbi.ats.SimpleAts,
    goal_states: set[int],
    maximizing_players: set[int],
    stopping_criterion=1e-6,
):
    if model.time != umbi.ats.TimeType.DISCRETE:
        raise NotImplementedError("Reachability query only supported for discrete time models.")
    if any(p not in range(model.num_players) for p in maximizing_players):
        raise ValueError(f"Model only has {model.num_players} players, invalid maximizing players specified.")
    if any(s not in range(model.num_states) for s in goal_states):
        raise ValueError(f"Model only has {model.num_states} states, invalid goal states specified.")
    if not goal_states:
        return {s: 0.0 for s in model.initial_states}

    value_vector = [1.0 if s in goal_states else 0.0 for s in range(model.num_states)]
    active_states = set(range(model.num_states)) - goal_states
    if model.num_players <= 1:
        maximizing_states = active_states if 0 in maximizing_players else set()
    else:
        assert model.state_to_player is not None, "Model must have player information for reachability VI."
        maximizing_states = set(s for s in active_states if model.state_to_player[s] in maximizing_players)

    assert all(isinstance(p, umbi.datatypes.NumericPrimitive) for p in model.branch_to_probability), (
        "Branch probabilities must be numeric."
    )
    while True:
        max_diff = 0.0
        solved_states = set()
        for s in active_states:
            values: list[umbi.datatypes.NumericPrimitive] = sum(
                model.branch_to_probability[b] * value_vector[model.branch_to_target[b]]  # type: ignore[union-attr]
                for choice in model.get_state_choices(s)
                for b in model.get_choice_branches(choice)
            )
            new_value = max(values) if s in maximizing_states else min(values)
            assert new_value > value_vector[s] or math.isclose(new_value, value_vector[s])
            max_diff = max(max_diff, value_vector[s] - new_value)
            value_vector[s] = new_value
            if new_value > 1.0 - 1e-14:
                solved_states.add(s)
        if max_diff < stopping_criterion:
            break
        active_states -= solved_states
        solved_states.clear()

    return {s: value_vector[s] for s in model.initial_states}


@click.command()
@click.option("--input", type=click.Path(exists=True, path_type=pathlib.Path))
@click.option("--goal-states", multiple=True, required=True, type=int, help="goal state indices")
@click.option("--maximizing-players", multiple=True, default=[0], type=int, help="maximizing player indices")
@click.option("--precision", type=float, default=1e-6, show_default=True, help="stopping criterion for VI")
def main(input: pathlib.Path, goal_states: tuple[int, ...], maximizing_players: tuple[int, ...], precision: float):
    ats = umbi.ats.read(input)
    values = reachability_vi(ats, set(goal_states), set(maximizing_players), precision)
    for s, v in values.items():
        state_str = f"{s}"
        if ats.has_variable_valuations and ats.variable_valuations.has_state_valuations:
            sv = ats.variable_valuations.state_valuations
            state_str = f"({' '.join(f'{k.name}:{v}' for k, v in sv.get_entity_valuation(s).items())})"
        print(f"{state_str}: {v}")


if __name__ == "__main__":
    main()
