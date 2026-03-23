#!/usr/bin/env python3
"""Demonstration of umbfile manipulation via ExplicitUmb."""

import click

import umbi


@click.command()
@click.option("--input", type=click.Path(exists=True), required=True, help="Input umbfile path")
@click.option("--output", type=click.Path(), default="out.umb", show_default=True, help="Output umbfile path")
def main(input: str, output: str):
    """Read a umbfile, print its contents, modify it, and write it out."""
    umbi.setup_logging()

    umb = umbi.umb.read(input)
    print("UMB file contents:")
    print(umb)

    num_states = umb.index.transition_system.num_states
    print("Number of states:", num_states)
    print("Existing annotations:")
    print(umb.annotations)

    print("Adding custom rewards...")
    annotation_category = "reward"
    annotation_name = "state_index"
    # add reward annotation description to the index file
    if umb.index.annotations is None:
        umb.index.annotations = {}
    if annotation_category not in umb.index.annotations:
        umb.index.annotations[annotation_category] = {}
    umb.index.annotations[annotation_category][annotation_name] = umbi.umb.index.AnnotationDescription(
        alias="state_index",
        description="Reward annotation for states, equal to the state index",
        type=umbi.binary.UINT32,
        applies_to=["states"],
    )
    # add reward annotation values to the umb file
    if umb.annotations is None:
        umb.annotations = {}
    if annotation_category not in umb.annotations:
        umb.annotations[annotation_category] = {}
    if annotation_name not in umb.annotations[annotation_category]:
        umb.annotations[annotation_category][annotation_name] = {}
    umb.annotations[annotation_category][annotation_name]["states"] = list(range(num_states))

    print("Writing modified UMB file...")
    umbi.umb.write(umb, output)

    print("Reading back to validate...")
    umb = umbi.umb.read(output)
    assert umb.index.annotations is not None
    assert annotation_category in umb.index.annotations
    assert annotation_name in umb.index.annotations[annotation_category]
    print("Annotation description:")
    print(umb.index.annotations[annotation_category][annotation_name])
    print("Annotation values:")
    print(umb.annotations[annotation_category][annotation_name])
    print("Done!")


if __name__ == "__main__":
    main()
