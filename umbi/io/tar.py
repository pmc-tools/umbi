"""
Utilities for reading/writing tarfiles.
"""

import io as std_io
import logging
import pathlib
import tarfile
from typing_extensions import Literal

logger = logging.getLogger(__name__)


class TarReader:
    """
    An auxiliary class to simplify tar reading.
    #TODO lazy loading
    """

    @staticmethod
    def tar_read(tarpath: str | pathlib.Path) -> dict[str, bytes]:
        """
        Load all files from a tarball into memory.
        :return: a dictionary filename -> bytestring
        """
        logger.debug(f"loading tarfile from {tarpath} ...")
        filename_data = {}
        with tarfile.open(tarpath, mode="r:*") as tar:
            for member in tar.getmembers():
                if member.isfile():
                    fileobj = tar.extractfile(member)
                    if fileobj is None:
                        raise KeyError(f"Could not extract file {member.name} from {tarpath}")
                    filename_data[member.name] = fileobj.read()
        logger.debug("tarfile successfully loaded")
        return filename_data

    def __init__(self, tarpath: str | pathlib.Path) -> None:
        self.tarpath = tarpath
        self.filename_bytes = TarReader.tar_read(tarpath)

    @property
    def filenames(self) -> list[str]:
        """List of filenames in the tarfile."""
        return list(self.filename_bytes.keys())

    def has_file(self, filename: str) -> bool:
        """Check if the tarfile contains a file with the given name."""
        return filename in self.filename_bytes

    def read_file(self, filename: str, required: bool = False) -> bytes | None:
        """
        Read raw bytes from a specific file in the tarfile.
        :param filename: name of the file to read
        :param required: whether the file is required
        :return: bytestring, or None if the optional file is not found
        :raises KeyError: if the required file is not found
        """
        if not self.has_file(filename):
            if not required:
                return None
            else:
                raise KeyError(f"tarfile {self.tarpath} has no file {filename}")
        logger.debug(f"loading {filename} ...")
        return self.filename_bytes[filename]


class TarWriter:
    """An auxiliary class to simplify tar writing."""

    @classmethod
    def tar_write(
        cls,
        tarpath: str | pathlib.Path,
        filename_data: dict[str, bytes],
        compression: Literal["gz", "bz2", "xz"] | None = "gz",
    ):
        """
        Create a tarball file with the given contents.

        :param tarpath: path to a tarball file
        :param filename_data: a dictionary filename -> bytestring
        :param compression: compression algorithm or None for no compression
        """
        logger.debug(f"writing tarfile {tarpath} with compression '{compression}' ...")
        mode = "w"
        if compression is not None:
            mode = f"w:{compression}"
        with tarfile.open(tarpath, mode=mode) as tar:  # type: ignore
            for filename, data in filename_data.items():
                tar_info = tarfile.TarInfo(name=filename)
                tar_info.size = len(data)
                tar.addfile(tar_info, std_io.BytesIO(data))
        logger.debug("successfully wrote the tarfile")

    def __init__(self) -> None:
        self.filename_bytes = {}

    @property
    def filenames(self) -> list[str]:
        """List of filenames added to the tarfile."""
        return list(self.filename_bytes.keys())

    def has_file(self, filename: str) -> bool:
        """Check if a file with the given name has been added to the tarfile."""
        return filename in self.filename_bytes

    def add_file(self, filename: str, data: bytes):
        """Add a binary file to the tarfile."""
        logger.debug(f"adding {filename} ...")
        if self.has_file(filename):
            logger.warning(f"file {filename} already exists in the tarfile, overwriting")
        self.filename_bytes[filename] = data

    def write(self, tarpath: str | pathlib.Path):
        """Write all added files to a tarfile."""
        TarWriter.tar_write(tarpath, self.filename_bytes)
