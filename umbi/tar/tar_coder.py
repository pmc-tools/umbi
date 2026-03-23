import logging
import typing
from collections.abc import Sequence

import umbi.binary
import umbi.datatypes
from umbi.binary import BOOL1, UINT64, SizedType
from umbi.datatypes import JsonLike, PrimitiveType, Scalar

from .tar_file import TarFile

logger = logging.getLogger(__name__)


class TarCoder(TarFile):
    """Auxiliary class to simplify reading files of specific types from a tarfile."""

    def _skip_missing_optional_data(self, filename: str, data: typing.Any | None, optional: bool) -> bool:
        """Check that the data are provided (is not None) for a mandatory file (optional=False).

        :return: True if no data were provided for an optional file (further processing should be skipped); False otherwise
        :raises ValueError: if optional=False and data is None
        """
        if data is None:
            if not optional:
                raise ValueError(f"missing mandatory data for {filename}")
            return True
        return False

    def read_json(self, filename: str, optional: bool = False) -> JsonLike | None:
        """Read a file as a json object.

        :param filename: name of the file to read
        :param optional: if False, the file is mandatory and must exist
        :return: parsed JSON object, or None if optional=True and file not found
        :raises KeyError: if optional=False and the file is not found
        """
        if (data := self.read_file(filename, optional)) is None:
            return None
        json_str = umbi.binary.bytes_to_scalar(data, PrimitiveType.STRING)
        assert isinstance(json_str, str)
        json_obj = umbi.datatypes.string_to_json(json_str)
        return json_obj

    def add_json(self, filename: str, json_obj: JsonLike | None, optional: bool = False):
        """Store json object to a json file.

        :param filename: name of the file to add
        :param json_obj: json data to add, or None if file should be skipped
        :param optional: if False, the file is mandatory and json_obj must not be None
        :raises ValueError: if optional=False and json_obj is None
        """
        if self._skip_missing_optional_data(filename, json_obj, optional):
            return
        assert json_obj is not None
        json_str = umbi.datatypes.json_to_string(json_obj)
        json_bytes = umbi.binary.scalar_to_bytes(json_str, PrimitiveType.STRING)
        self.add_file(filename, json_bytes)

    def read_vector(self, filename: str, sized_type: SizedType, optional: bool = False) -> list | None:
        """Read a file as a vector of values.

        :param filename: name of the file to read
        :param sized_type: type of the values in the file
        :param optional: if False, the file is mandatory and must exist
        :return: list of values, or None if optional=True and file not found
        :raises KeyError: if optional=False and the file is not found
        """
        if (data := self.read_file(filename, optional)) is None:
            return None
        return umbi.binary.bytes_to_vector(data, sized_type)

    def add_vector(self, filename: str, sized_type: SizedType, vector: Sequence[Scalar] | None, optional: bool = False):
        """Add a file containing a vector of values.

        :param filename: name of the file to add
        :param sized_type: type of the values
        :param vector: vector to add
        :param optional: if False, the file is mandatory and vector must not be None
        :raises ValueError: if optional=False and vector is None
        """
        if self._skip_missing_optional_data(filename, vector, optional):
            return
        assert vector is not None
        data_out = umbi.binary.vector_to_bytes(vector, sized_type)
        self.add_file(filename, data_out)

    @staticmethod
    def truncate_bitvector(vector: list[bool], num_entries: int) -> list[bool]:
        """Truncate a bitvector if its length exceeds num_entries."""
        if len(vector) > num_entries:
            if any(vector[num_entries:]):
                logger.warning(
                    f"bitvector {len(vector)} exceeds expected length of {num_entries}, truncating and discarding non-False entries"
                )
            vector = vector[:num_entries]
        return vector

    def read_bitvector(self, filename: str, num_entries: int | None, optional: bool = False) -> list[bool] | None:
        """
        Read a file as a bitvector and truncate it to num_entries if necessary.

        :param filename: name of the file to read
        :param num_entries: expected number of entries in the bitvector
        :param optional: if False, the file is mandatory and must exist
        :return: list of bools representing the bitvector, or None if the optional file is not found
        """
        if (vector := self.read_vector(filename, BOOL1, optional=optional)) is None:
            return None
        # assert isinstance(vector, list)
        if num_entries is not None:
            vector = self.truncate_bitvector(vector, num_entries)
        return vector

    @staticmethod
    def pad_bitvector(vector: Sequence[bool], num_bytes: int) -> list[bool]:
        """Pad a bitvector with False entries to make its length a multiple of num_bytes*8."""
        num_bits = num_bytes * 8
        items_to_add = (num_bits - (len(vector) % num_bits)) % num_bits
        vector = list(vector)
        if items_to_add > 0:
            # logger.debug(
            #     f"padding bitvector with {items_to_add} False entries to align to a {num_bytes}-byte boundary"
            # )
            vector = vector + [False] * items_to_add
        return vector

    def add_bitvector(self, filename: str, vector: Sequence[bool], optional: bool = False, pad_to_8_bytes: bool = True):
        """Add a bitvector file.

        :param filename: name of the file to add
        :param vector: bitvector data to write
        :param optional: if False, the file is mandatory and vector must not be None
        :param pad_to_8_bytes: if True, pad the bitvector to a multiple of 8 bytes
        """
        if vector is not None and pad_to_8_bytes:
            vector = self.pad_bitvector(vector, 8)
        self.add_vector(filename, BOOL1, vector, optional)

    def read_vector_with_ranges(
        self, filename: str, value_type: umbi.datatypes.ScalarType, optional: bool = False, filename_csr: str = ""
    ) -> list | None:
        """Read a file containing a vector using an accompanying CSR.

        :param filename: name of the main file to read
        :param value_type: vector element type
        :param optional: if False, the main file is mandatory and must exist
        :param filename_csr: name of the accompanying CSR file
        :return: list of values, or None if optional=True and file not found
        :raises KeyError: if optional=False and the file is not found, or if CSR file is not found
        """
        if (data := self.read_file(filename, optional)) is None:
            return None
        chunk_csr = self.read_vector(filename_csr, UINT64)
        assert chunk_csr is not None
        # here, we add some sanity checks to make sure we don't read out-of-bounts data
        # however, we don't check whether chunk_csr is well-formed
        assert len(chunk_csr) > 0, f"CSR file {filename_csr} must have at least one entry"
        assert all(0 <= idx <= len(data) for idx in chunk_csr), (
            f"CSR indices in {filename_csr} must be within data length"
        )
        chunk_ranges = list(zip(chunk_csr[:-1], chunk_csr[1:]))
        return umbi.binary.bytes_with_ranges_to_vector(data, value_type, chunk_ranges=chunk_ranges)

    def add_vector_with_ranges(
        self,
        filename: str,
        sized_type: SizedType,
        vector: Sequence[Scalar] | None,
        filename_csr: str,
        optional: bool = False,
    ):
        """Add a file containing a vector, with an accompanying CSR file if needed.

        :param filename: name of the main file to add
        :param sized_type: vector element type
        :param vector: vector data to write
        :param filename_csr: name of the accompanying CSR file
        :param optional: if False, the file is mandatory and vector must not be None
        :raises ValueError: if optional=False and vector is None
        """
        if self._skip_missing_optional_data(filename, vector, optional):
            return
        assert vector is not None
        data_out, chunk_csr = umbi.binary.vector_to_bytes_with_ranges(vector, sized_type)
        self.add_file(filename, data_out)
        if chunk_csr is not None:
            self.add_vector(filename_csr, UINT64, chunk_csr, optional=False)

    def read_strings(self, filename: str, optional: bool = False, filename_csr: str = "") -> list[str] | None:
        """Read a file containing a vector of strings, using an accompanying CSR file.

        :param filename: name of the main file to read
        :param optional: if False, the main file is mandatory and must exist
        :param filename_csr: name of the accompanying CSR file
        :return: list of strings, or None if optional=True and file not found
        :raises KeyError: if optional=False and the file is not found, or if CSR file is not found
        """
        return self.read_vector_with_ranges(filename, PrimitiveType.STRING, optional, filename_csr)

    def add_strings(self, filename: str, vector: Sequence[str] | None, filename_csr: str, optional: bool = False):
        """Add a file containing a vector of strings, using an accompanying CSR file.

        :param filename: name of the main file to add
        :param vector: list of strings to add
        :param filename_csr: name of the accompanying CSR file
        :param optional: if False, the file is mandatory and vector must not be None
        :raises ValueError: if optional=False and vector is None
        """
        self.add_vector_with_ranges(
            filename, SizedType.for_type(umbi.datatypes.PrimitiveType.STRING), vector, filename_csr, optional
        )

    def _file_to_string(self, filename: str) -> str:
        if filename.endswith(".json"):
            try:
                json_obj = self.read_json(filename, optional=False)
                json_str = umbi.datatypes.json_to_string(json_obj, compact_formatting=False)
                return f"{json_str}"
            except Exception as e:
                return f"invalid .json file, {type(e).__name__} error: {e}"
        return super()._file_to_string(filename)
