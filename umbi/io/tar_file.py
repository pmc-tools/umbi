"""Utilities for reading/writing tarfiles."""

import collections.abc
import io as std_io
import logging
import pathlib
import tarfile as std_tarfile
import typing

logger = logging.getLogger(__name__)


class TarFile(dict[str, bytes]):
    """A simple in-memory representation of a tarfile: a mapping from filenames to bytestrings."""

    def __init__(self, tarpath: str | pathlib.Path | None = None, *args, **kwargs):
        """Initialize TarFile, optionally loading from a tarball."""
        super().__init__(*args, **kwargs)
        if tarpath is not None:
            self.read(tarpath)

    @property
    def filenames(self) -> collections.abc.KeysView[str]:
        """View of filenames in the tarfile."""
        return self.keys()

    def has_file(self, filename: str) -> bool:
        """Check if the tarfile contains the given file."""
        return filename in self

    def get_file(self, filename: str, required: bool = False) -> bytes | None:
        """Read bytestring associated with a specific file in the tarfile.

        :param filename: name of the file to read
        :param required: whether the file is required
        :return: bytestring, or None if the optional file is not found
        :raises KeyError: if the required file is not found
        """
        if not self.has_file(filename):
            if required:
                raise KeyError(f"tarfile does not have a required file {filename}")
            else:
                logger.debug(f"optional file {filename} not found, skipping")
                return None
        logger.debug(f"loading {filename} ...")
        return self[filename]

    def add_file(self, filename: str, data: bytes, overwrite: bool = False) -> None:
        """Add a file to the tarfile."""
        if self.has_file(filename):
            if not overwrite:
                raise KeyError(f"file {filename} already exists in the tarfile")
            else:
                logger.warning(f"file {filename} already exists in the tarfile, overwriting")
        self[filename] = data

    def read(self, tarpath: str | pathlib.Path) -> None:
        """Load tarfile contents from a tarball."""
        new_tarfile = tarfile_read(tarpath)
        self.clear()
        self.update(new_tarfile)

    def write(self, tarpath: str | pathlib.Path, compression: typing.Literal["gz", "bz2", "xz"] | None = "gz") -> None:
        """Write tarfile contents to a tarball."""
        tarfile_write(tarpath, self, compression)

    def file_to_string(self, filename: str) -> str:
        """Format the contents of a specific file in the tarfile as a string for debugging."""
        assert self.has_file(filename), f"file {filename} not found in tarfile"
        data = self[filename]
        return f"{data!r}"

    def __str__(self) -> str:
        num_files = len(self)
        s = f"{self.__class__.__name__} ({num_files} files):\n"
        for i, filename in enumerate(self.filenames, start=1):
            s += f"file {i}/{num_files}: {filename} ({len(self[filename])} bytes)\n"
            s += f"{self.file_to_string(filename)}\n"
        return s


def tarfile_read(tarpath: str | pathlib.Path) -> TarFile:
    """Load TarFile from a tarball.

    :param tarpath: path to a tarball file
    :return: a TarFile object containing filename -> bytestring mappings
    :raises FileNotFoundError: if the tarball file is not found
    :raises tarfile.TarError: if the tarball file cannot be read as a tarball
    """
    logger.debug(f"loading tarfile from {tarpath} ...")
    filename_data = TarFile()
    with std_tarfile.open(tarpath, mode="r:*") as tar:
        for member in tar.getmembers():
            if member.isfile():
                fileobj = tar.extractfile(member)
                if fileobj is None:
                    raise KeyError(f"could not extract file {member.name} from {tarpath}")
                filename_data[member.name] = fileobj.read()
    logger.debug("tarfile successfully loaded")
    return filename_data


def tarfile_write(
    tarpath: str | pathlib.Path,
    tarfile: TarFile,
    compression: typing.Literal["gz", "bz2", "xz"] | None = "gz",
):
    """Write TarFile to a tarball.

    :param tarpath: path to a tarball file
    :param tarfile: a TarFile object containing filename -> bytestring mappings
    :param compression: compression algorithm or None for no compression
    """
    logger.debug(f"writing tarfile {tarpath} with compression '{compression}' ...")
    mode = "w"
    if compression is not None:
        mode = f"w:{compression}"
    with std_tarfile.open(tarpath, mode=mode) as tar:  # type: ignore[arg-type]
        for filename, bytestring in tarfile.items():
            tar_info = std_tarfile.TarInfo(name=filename)
            tar_info.size = len(bytestring)
            tar.addfile(tar_info, std_io.BytesIO(bytestring))
    logger.debug("tarfile successfully written")
