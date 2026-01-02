import argparse
import pathlib

import umbi


def main(args):
    ats_loaded = umbi.io.read_ats(args.input)
    print(f"Loaded ATS has {ats_loaded.num_states} states and {ats_loaded.num_choices} choices")
    if args.output is not None:
        umbi.io.write_ats(ats_loaded, args.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Read an UMBI model, print out basic statistics, and (optionally) write it out"
    )
    parser.add_argument("input", help="The UMBI model to load", type=pathlib.Path)
    parser.add_argument("--output", help="Destination to write to", type=pathlib.Path, required=False)
    main(parser.parse_args())
