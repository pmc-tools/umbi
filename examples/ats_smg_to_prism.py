#!/usr/bin/env python3
"""
Convert an ATS SMG to PRISM format.
"""

import argparse
import logging
import pathlib

import umbi
import umbi.ats
import umbi.examples.ats

log = logging.getLogger(__name__)


def ats_smg_to_prism(ats: umbi.ats.ExplicitAts, output_path: pathlib.Path) -> None:
    """
    Convert an ATS SMG to flat PRISM format.

    :param ats: the ATS SMG to convert.
    :param output_path: path to write the PRISM file.
    """
    assert ats.choice_to_choice_action is not None, "ATS must have choice to choice action mapping"
    assert ats.branch_probabilities is not None, "ATS must have branch probabilities"
    assert ats.branch_to_target is not None, "ATS must have branch to target mapping"
    assert ats.choice_action_to_name is not None, "ATS must have choice action to name mapping"

    with open(output_path, "w") as f:
        # header
        f.write("smg\n\n")

        # global state variable
        f.write(f"global state: [0..{ats.num_states - 1}];\n\n")

        # player declarations
        if ats.num_players > 0:
            # group states by player
            player_to_states = {}
            for state in range(ats.num_states):
                player = ats.state_to_player[state] if ats.state_to_player else 0
                if player not in player_to_states:
                    player_to_states[player] = []
                player_to_states[player].append(state)

            # collect actions for each player
            player_to_actions = {p: set() for p in player_to_states}
            for state in range(ats.num_states):
                player = ats.state_to_player[state] if ats.state_to_player else 0
                for choice in ats.state_choice_range(state):
                    action_id = ats.choice_to_choice_action[choice]
                    action_name = ats.choice_action_to_name[action_id]
                    player_to_actions[player].add(action_name)

            # write player declarations
            for player in sorted(player_to_states.keys()):
                actions = sorted(player_to_actions[player])
                action_list = ", ".join(f"[{a}]" for a in actions)
                f.write(f"player P{player} player{player}, {action_list} endplayer\n")
            f.write("\n")

        # group states by player for module generation
        if ats.num_players > 0:
            for player in sorted(player_to_states.keys()):
                f.write(f"module player{player}\n")

                # write transitions for all states controlled by this player
                for state in range(ats.num_states):
                    if ats.state_to_player and ats.state_to_player[state] != player:
                        continue

                    for choice in ats.state_choice_range(state):
                        action_id = ats.choice_to_choice_action[choice]
                        action_name = ats.choice_action_to_name[action_id]

                        # collect branches for this choice
                        branches = []
                        for branch in ats.choice_branch_range(choice):
                            target = ats.branch_to_target[branch]
                            prob = ats.branch_probabilities[branch]
                            branches.append((target, prob))

                        # write transition
                        f.write(f"\t[{action_name}] state={state} -> ")

                        # format branches
                        branch_strs = []
                        for target, prob in branches:
                            prob_str = str(prob)
                            branch_strs.append(f"{prob_str} : (state'={target})")

                        f.write(" + ".join(branch_strs))
                        f.write(";\n")

                f.write("endmodule\n\n")
        else:
            # single module for all states if no players
            f.write("module main\n")

            for state in range(ats.num_states):
                for choice in ats.state_choice_range(state):
                    action_id = ats.choice_to_choice_action[choice]
                    action_name = ats.choice_action_to_name[action_id]

                    # collect branches for this choice
                    branches = []
                    for branch in ats.choice_branch_range(choice):
                        target = ats.branch_to_target[branch]
                        prob = ats.branch_probabilities[branch]
                        branches.append((target, prob))

                    # write transition
                    f.write(f"\t[{action_name}] state={state} -> ")

                    # format branches
                    branch_strs = []
                    for target, prob in branches:
                        prob_str = str(prob)
                        branch_strs.append(f"{prob_str} : (state'={target})")

                    f.write(" + ".join(branch_strs))
                    f.write(";\n")

            f.write("endmodule\n\n")

        # write labels for atomic propositions
        if ats.ap_annotations:
            f.write("// Labels\n")
            for ap_name, ap_annotation in ats.ap_annotations.items():
                # collect states where this AP is true
                true_states = []
                for state in range(ats.num_states):
                    if ap_annotation.state_values[state]:
                        true_states.append(state)

                if true_states:
                    # write as disjunction
                    state_conditions = " | ".join(f"state={s}" for s in true_states)
                    f.write(f'label "{ap_name}" = {state_conditions};\n')
            f.write("\n")

        # write initial state constraint if needed
        if ats.num_initial_states > 0:
            initial_states = ats.initial_states
            if len(initial_states) == 1:
                f.write("// Initial state\n")
                f.write(f"init state={initial_states[0]} endinit\n")
            else:
                f.write("// Initial states\n")
                init_condition = " | ".join(f"state={s}" for s in initial_states)
                f.write(f"init {init_condition} endinit\n")

    log.info(f"Written PRISM file to {output_path}")


def main(args):
    logging.basicConfig(level=logging.INFO)
    log.info(f"Reading ATS from {args.input}")
    ats = umbi.io.read_ats(args.input)
    ats.validate()
    log.info(f"ATS has {ats.num_states} states, {ats.num_choices} choices, {ats.num_branches} branches")
    ats_smg_to_prism(ats, args.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert ATS SMG to flat PRISM format")
    parser.add_argument("input", help="Input ATS file", type=pathlib.Path)
    parser.add_argument(
        "--output",
        help="Output PRISM file",
        type=pathlib.Path,
        required=True,
    )
    main(parser.parse_args())
