#!/usr/bin/env python3
"""Demonstration of tarfile manipulation via TarCoder."""

import click

import umbi


@click.command()
@click.option("--input", type=click.Path(exists=True), required=False, help="Input tarfile path")
@click.option("--output", type=click.Path(), default="output.tar.gz", show_default=True, help="Output tarfile path")
def main(input: str, output: str):
    """Read a tarfile, print its contents, modify it, and write it out."""
    umbi.setup_logging()

    print(f"Reading tarfile: {input}")
    tarfile = umbi.io.TarCoder(input)

    print("Filenames in tarfile:")
    print(tarfile.filenames)
    print("Original tarfile contents:")
    print(tarfile)

    print("Accessing individual files:")
    for filename in tarfile.filenames:
        size = len(tarfile[filename])
        print(f"  {filename} ({size} bytes)")

    print("Adding vectors of uint32 to the tarfile...")
    vector = list(range(10))
    sized_type = umbi.binary.SizedType(type=umbi.datatypes.NumericPrimitiveType.UINT, size_bits=32)
    # can also use alias:
    # sized_type = umbi.binary.UINT32
    filename = "x-vector.bin"
    if filename not in tarfile:
        print(f"Adding vector {vector} to {filename} in the tarfile...")
        tarfile.add_vector(filename, sized_type, vector)
    assert tarfile.has_file(filename), f"new file {filename} not found in the tarfile"
    vector_out = tarfile.read_vector(filename, sized_type)
    print(f"Read vector from {filename}: {vector_out}")
    assert vector_out == vector, f"read vector {vector_out} does not match original vector {vector}"

    print("Writing modified tarfile...")
    tarfile.write(tarpath=output, compression="gz")
    print("Done!")


if __name__ == "__main__":
    main()
