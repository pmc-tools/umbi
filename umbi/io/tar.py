"""
Utilities for reading/wrting Tar archives.
"""

import io as std_io
import logging
import pathlib
import tarfile

logger = logging.getLogger(__name__)


class TarReader:
    """
    An auxiliary class to simplify tar reading.
    #TODO lazy loading
    """

    @staticmethod
    def load_tar(tarpath: str | pathlib.Path) -> dict[str, bytes]:
        """
        Load all files from a tarball into memory.
        :return: a dictionary filename -> binary string
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

    def __init__(self, tarpath: str | pathlib.Path):
        self.tarpath = tarpath
        self.filename_bytes = TarReader.load_tar(tarpath)

    @property
    def filenames(self) -> list[str]:
        """List of filenames in the tarball."""
        return list(self.filename_bytes.keys())

    def read(self, filename: str, required: bool = False) -> bytes | None:
        """
        Read raw bytes from a specific file in the tarball.
        :param filename: name of the file to read
        :param required: if True, raise an error if the file is not found
        :return: binary data, or None if the optional file is not found
        """
        if filename not in self.filenames:
            if not required:
                return None
            else:
                raise KeyError(f"tar archive {self.tarpath} has no file {filename}")
        logger.debug(f"loading {filename}")
        return self.filename_bytes[filename]


class TarWriter:
    """An auxiliary class to simplify tar writing."""

    @classmethod
    def tar_write(cls, tarpath: str | pathlib.Path, filename_data: dict[str, bytes], compression: str = "gz"):
        """
        Create a tarball file with the given contents.

        :param tarpath: path to a tarball file
        :param filename_data: a dictionary filename -> binary string
        :param compression: compression algorithm one of ("gz", "bz2", "xz") or "" for no compression
        """
        logger.debug(f"writing tarfile {tarpath} with compression '{compression}' ...")
        assert compression in ("", "gz", "bz2", "xz"), "unsupported compression algorithm"
        mode = "w"
        if compression != "":
            mode = f"w:{compression}"
        with tarfile.open(tarpath, mode=mode) as tar:  # type: ignore
            for filename, data in filename_data.items():
                tar_info = tarfile.TarInfo(name=filename)
                tar_info.size = len(data)
                tar.addfile(tar_info, std_io.BytesIO(data))
        logger.debug("successfully wrote the tarfile")

    def __init__(self):
        self.filename_bytes = {}

    def add(self, filename: str, data: bytes):
        """Add a (binary) file to the tarball."""
        logger.debug(f"writing {filename} ...")
        if filename in self.filename_bytes:
            logger.warning(f"file {filename} already exists in the tarball, overwriting")
        self.filename_bytes[filename] = data

    def write(self, tarpath: str | pathlib.Path):
        """Write all added files to a tarball."""
        TarWriter.tar_write(tarpath, self.filename_bytes)
