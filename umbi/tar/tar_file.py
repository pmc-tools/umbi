import collections.abc
import io as std_io
import logging
import pathlib
import tarfile as std_tarfile
import typing

logger = logging.getLogger(__name__)


class TarFile(dict[str, bytes]):
    """A simple in-memory representation of a tarfile: a mapping from filenames to bytestrings.
    TODO: consider adding lazy loading of file contents for large tarfiles
    """

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

    def read_file(self, filename: str, optional: bool = False) -> bytes | None:
        """Read bytestring associated with a specific file in the tarfile.

        :param filename: name of the file to read
        :param optional: if False, the file is mandatory and must exist
        :return: file contents as bytes, or None if optional=True and file not found
        :raises KeyError: if optional=False and the file is not found
        """
        if not self.has_file(filename):
            if not optional:
                raise KeyError(f"tarfile does not have a mandatory file {filename}")
            else:
                logger.debug(f"optional file {filename} not found, skipping")
                return None
        logger.debug(f"loading {filename} ...")
        return self[filename]

    def add_file(self, filename: str, data: bytes, overwrite: bool = False) -> None:
        """Add a file to the tarfile.

        :param filename: name of the file to add
        :param data: bytestring to associate with the file
        :param overwrite: if False, raise an error if the file already exists; if True, overwrite existing file
        :raises KeyError: if the file already exists and overwrite is False
        """
        if self.has_file(filename):
            if not overwrite:
                raise KeyError(f"file {filename} already exists in the tarfile")
            else:
                logger.warning(f"file {filename} already exists in the tarfile, overwriting")
        self[filename] = data

    def read(self, tarpath: str | pathlib.Path) -> None:
        """Replace tarfile contents with the ones from a tarball.

        :param tarpath: path to a tarball
        :raises FileNotFoundError: if the tarball is not found
        :raises tarfile.TarError: if the file cannot be read as a tarball
        """
        new_tarfile = read(tarpath)
        self.clear()
        self.update(new_tarfile)

    def write(self, tarpath: str | pathlib.Path, compression: typing.Literal["gz", "bz2", "xz"] | None = "gz") -> None:
        """Write tarfile contents to a tarball.

        :param tarpath: path to a tarball
        :param compression: compression algorithm or None for no compression
        :raises IOError: if the tarball cannot be written
        """
        write(tarpath, self, compression)

    def _file_to_string(self, filename: str) -> str:
        """Format the contents of a specific file in the tarfile as a string for debugging."""
        # assert self.has_file(filename), f"file {filename} not found in tarfile"
        data = self[filename]
        return f"{data!r}"

    def __str__(self) -> str:
        num_files = len(self)
        s = f"{self.__class__.__name__} ({num_files} files):\n"
        for i, filename in enumerate(self.filenames, start=1):
            s += f"file {i}/{num_files}: {filename} ({len(self[filename])} bytes)\n"
            s += f"{self._file_to_string(filename)}\n"
        return s


def read(tarpath: str | pathlib.Path) -> TarFile:
    """Load TarFile from a tarball.

    :param tarpath: path to a tarball
    :return: a TarFile object containing filename -> bytestring mappings
    :raises FileNotFoundError: if the tarball is not found
    :raises tarfile.TarError: if the file cannot be read as a tarball
    """
    logger.debug(f"loading tarfile from {tarpath} ...")
    filename_data = TarFile()
    with std_tarfile.open(tarpath, mode="r:*") as tar:
        for member in tar.getmembers():
            if member.isfile():
                fileobj = tar.extractfile(member)
                if fileobj is None:
                    raise std_tarfile.TarError(f"failed to extract file {member.name} from tarball")
                filename_data[member.name] = fileobj.read()
    logger.debug("tarfile successfully loaded")
    return filename_data


def write(
    tarpath: str | pathlib.Path,
    tarfile: TarFile,
    compression: typing.Literal["gz", "bz2", "xz"] | None = "gz",
):
    """Write TarFile to a tarball.

    :param tarpath: path to a tarball
    :param tarfile: a TarFile object containing filename -> bytestring mappings
    :param compression: compression algorithm or None for no compression
    :raises IOError: if the tarball cannot be written
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
