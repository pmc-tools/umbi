#!/usr/bin/env python3
"""Demonstration of umbfile manipulation via ExplicitAts."""

import click
import umbi


@click.command()
@click.option("--input", type=click.Path(exists=True), required=True, help="Input umbfile path")
@click.option("--output", type=click.Path(), default="out.umb", show_default=True, help="Output umbfile path")
def main(input: str, output: str):
    """Read a umbfile, print its contents, modify it, and write it out."""
    umbi.setup_logging()

    ats = umbi.ats.read(input)
    print("ATS contents:")
    print(ats)

    print("Number of states:", ats.num_states)
    print("Existing annotations:")
    print(ats.reward_annotations)

    print("Adding custom rewards...")
    annotation_name = "state_index"
    reward_annotation = umbi.ats.RewardAnnotation(
        name=annotation_name,
        description="Reward annotation for states, equal to the state index",
    )
    reward_annotation.set_state_values(list(range(ats.num_states)))
    ats.add_reward_annotation(reward_annotation)

    print("Writing modified ATS ...")
    umbi.ats.write(ats, output)

    print("Reading back to validate...")
    ats = umbi.ats.read(output)
    print("Annotation description and values:")
    print(ats.get_reward_annotation(annotation_name))
    print("Done!")


if __name__ == "__main__":
    main()
