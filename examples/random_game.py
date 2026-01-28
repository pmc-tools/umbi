#!/usr/bin/env python3
"""
umbi demo: A random stochastic game generator based on Azeem et al. "Optimistic and Topological Value Iteration for
Simple Stochastic Games".
"""

import argparse
import logging
import pathlib
import random
import time

import umbi
import umbi.ats

log = logging.getLogger(__name__)


def fill_action(s: int, action: int, num_states: int, delta: dict) -> list[tuple[int, float]]:
    """
    Create a valid probability distribution for an action from state s.

    :param s: source state.
    :param action: action identifier.
    :param num_states: total number of states.
    :param delta: transition function delta[s][a] = [(target, prob), ...].
    :return: list of (target_state, probability) tuples.
    """
    # initialize state entry if needed
    if s not in delta:
        delta[s] = {}
    if action not in delta[s]:
        delta[s][action] = []

    branches = delta[s][action]
    existing_targets = {target for target, _ in branches}

    # maintain a list of available targets and update it incrementally
    available_targets = [sp for sp in range(num_states) if sp not in existing_targets]

    while available_targets:
        # pick a random state s' from available targets
        idx = random.randrange(len(available_targets))
        sp = available_targets[idx]

        # increase delta[s][a] with sp by a random number in (0, 1]
        prob = random.uniform(0.01, 1.0)
        branches.append((sp, prob))

        # remove the chosen target from available list
        available_targets[idx] = available_targets[-1]
        available_targets.pop()

        # calculate total probability
        total_prob = sum(p for _, p in branches)

        # check termination conditions
        if total_prob > 1:
            # decrease the most recently modified probability so sum = 1
            branches[-1] = (sp, prob - (total_prob - 1))
            break
        elif total_prob == 1 or not available_targets:
            # either sum is 1 or all states have been assigned
            if total_prob < 1:
                # increase the most recently modified probability so sum = 1
                branches[-1] = (sp, prob + (1 - total_prob))
            break

    return branches


def generate_random_transition_function(
    num_states: int, seed: int | None = None, max_actions_per_state: int = 3
) -> tuple[dict, dict[int, list[int]], list[str]]:
    """
    Generate a random transition function for a stochastic game.

    :param num_states: number of states (n).
    :param seed: random seed for reproducibility.
    :param max_actions_per_state: maximum number of actions per state.
        - delta: transition function delta[s][a] = [(target, prob), ...]
        - actions_at_state: mapping from state to list of available actions
        - all_actions: list of action names
    """
    if seed is not None:
        random.seed(seed)

    # enumerate states in a random order
    state_order = list(range(num_states))
    random.shuffle(state_order)

    # track transitions: delta[s][a] = [(target, prob), ...]
    delta = {}
    # track actions available at each state: Av(s)
    actions_at_state = {s: [] for s in range(num_states)}
    # track which states have incoming transitions for fast lookup
    states_with_incoming = [False] * num_states
    # global action list
    all_actions = []
    action_counter = 0

    # forward procedure: ensure connectivity from initial state
    log.info("Starting forward procedure")
    forward_start = time.time()
    for i in range(1, num_states):
        s = state_order[i]

        # if s has an incoming transition then skip
        if states_with_incoming[s]:
            continue

        # pick any state s' with index smaller than s
        sp = random.choice(state_order[:i])

        # create an action a that starts at s'
        action = action_counter
        action_counter += 1
        all_actions.append(f"fwd_a{action}")

        # assign to (s', a) a positive probability of reaching s and create valid distribution
        branches = fill_action(sp, action, num_states, delta)

        # ensure s is reachable with positive probability
        if not any(target == s for target, _ in branches):
            # force s to be reachable
            if len(branches) == 0:
                branches.append((s, 1.0))
            else:
                # redistribute to make room for s
                scale = 0.5
                branches = [(t, p * scale) for t, p in branches]
                branches.append((s, 1.0 - scale))
            delta[sp][action] = branches

        # mark all target states as having incoming transitions
        for target, _ in branches:
            states_with_incoming[target] = True

        # add action to Av(s')
        actions_at_state[sp].append(action)

    forward_time = time.time() - forward_start
    log.info(f"Forward procedure completed in {forward_time:.3f}s")

    # backward procedure: add as many actions as possible
    log.info("Starting backward procedure")
    backward_start = time.time()
    for i in range(num_states - 1, -1, -1):
        s = state_order[i]

        # pick a random number m to determine how many actions to add
        m = random.randint(1, max_actions_per_state)

        # every state must have at least one action
        if len(actions_at_state[s]) == 0:
            m = max(m, 1)

        # add m actions
        for _ in range(m):
            action = action_counter
            action_counter += 1
            all_actions.append(f"bwd_a{action}")

            # fill the action with valid probability distribution
            branches = fill_action(s, action, num_states, delta)

            # mark all target states as having incoming transitions
            for target, _ in branches:
                states_with_incoming[target] = True

            # add action to Av(s)
            actions_at_state[s].append(action)

    backward_time = time.time() - backward_start
    log.info(f"Backward procedure completed in {backward_time:.3f}s")

    return delta, actions_at_state, all_actions


def random_game_ats(num_states: int, seed: int | None = None) -> umbi.ats.ExplicitAts:
    """
    Generate a random stochastic game connected from initial state.

    :param num_states: Number of states (n).
    :param seed: Random seed for reproducibility.
    :return: ExplicitAts representing the random stochastic game.
    """
    delta, actions_at_state, all_actions = generate_random_transition_function(num_states, seed)

    # create ATS
    ats = umbi.ats.ExplicitAts(
        time=umbi.ats.TimeType.STOCHASTIC,
        num_states=num_states,
        num_players=2,
    )

    # partition S uniformly at random into player states and probabilistic states
    # player states are controlled by player 0, probabilistic states by player 1
    is_player0_state = [random.choice([True, False]) for _ in range(num_states)]

    # set player information
    ats.state_to_player = [0 if is_player0 else 1 for is_player0 in is_player0_state]

    # set initial state to the state with index 0
    ats.set_initial_states([0])

    # build the ATS structure from delta and actions_at_state
    ats.num_choice_actions = len(all_actions)
    ats.choice_action_to_name = all_actions

    # count choices and branches
    ats.num_choices = sum(len(actions) for actions in actions_at_state.values())
    ats.num_branches = sum(
        len(delta.get(s, {}).get(action, [])) for s in range(num_states) for action in actions_at_state[s]
    )

    # build CSR structures
    log.info("Building CSR structures")
    build_start = time.time()
    ats.state_to_choice = []
    ats.choice_to_choice_action = []
    ats.choice_to_branch = []
    ats.branch_to_target = []
    ats.branch_probabilities = []

    for s in range(num_states):
        ats.state_to_choice.append(len(ats.choice_to_choice_action))

        for action in sorted(actions_at_state[s]):
            ats.choice_to_choice_action.append(action)
            ats.choice_to_branch.append(len(ats.branch_to_target))

            # get all branches for this (s, action) pair
            branches = delta[s][action]
            branches.sort()  # sort by target state

            for target, prob in branches:
                ats.branch_to_target.append(target)
                ats.branch_probabilities.append(prob)

    ats.state_to_choice.append(len(ats.choice_to_choice_action))
    ats.choice_to_branch.append(len(ats.branch_to_target))

    build_time = time.time() - build_start
    log.info(f"CSR building completed in {build_time:.3f}s")
    log.info(f"Generated random game: {num_states} states, {ats.num_choices} choices, {ats.num_branches} branches")
    log.info(f"Player0 states: {sum(is_player0_state)}, Player1 states: {num_states - sum(is_player0_state)}")

    return ats


def main(args):
    logging.basicConfig(level=logging.INFO)
    ats = random_game_ats(args.states, args.seed)
    ats.validate()
    # umbi.io.write_ats(ats, args.output)
    # log.info(f"Written to {args.output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a random stochastic game UMBI model")
    parser.add_argument("states", help="Number of states", type=int)
    parser.add_argument(
        "--output",
        help="Destination to write to",
        type=pathlib.Path,
        required=True,
    )
    parser.add_argument(
        "--seed",
        help="Random seed for reproducibility",
        type=int,
        default=None,
    )
    main(parser.parse_args())
