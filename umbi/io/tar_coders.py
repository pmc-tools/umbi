import logging

import umbi.binary
import umbi.datatypes
from umbi.binary.sized_type import SizedType, BOOL1, UINT64
from .utils import csr_to_ranges

from .tar import TarReader, TarWriter

logger = logging.getLogger(__name__)


class TarDecoder(TarReader):
    """An auxiliary class to simplify reading files of specific types from a tarball."""

    def read_vector(self, filename: str, sized_type: SizedType, required: bool = False) -> list | None:
        """
        Read a file as a vector of values.
        :param filename: name of the file to read
        :param sized_type: type of the values in the file
        :param required: if True, raise an error if the file is not found
        """
        data = self.read_file(filename, required)
        if data is None:
            return None
        return umbi.binary.bytes_to_vector(data, sized_type)

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

    def read_bitvector(self, filename: str, num_entries: int | None) -> list[bool]:
        """Read a bitvector and truncate it to num_entries if necessary."""
        vector = self.read_vector(filename, BOOL1, required=True)
        assert isinstance(vector, list)
        if num_entries is not None:
            vector = self.truncate_bitvector(vector, num_entries)
        return vector

    def read_vector_with_csr(
        self, filename: str, value_type: umbi.datatypes.ScalarType, required: bool, filename_csr: str
    ) -> list | None:
        """
        Read a file containing a vector of values while using an accompanying CSR.
        :param filename: name of the main file to read
        :param value_type: value type
        :param required: if True, raise an error if the main file is not found
        :param filename_csr: name of the accompanying CSR file
        """
        data = self.read_file(filename, required)
        if data is None:
            return None
        chunk_csr = self.read_vector(filename_csr, UINT64, required=True)
        assert chunk_csr is not None
        chunk_ranges = csr_to_ranges(chunk_csr)
        return umbi.binary.bytes_with_ranges_to_vector(data, value_type, chunk_ranges=chunk_ranges)

    def read_strings(self, filename: str, required: bool, filename_csr: str) -> list[str] | None:
        """
        Read a file containing a vector of strings, using an accompanying CSR file.
        :param filename: name of the main file to read
        :param required: if True, raise an error if the main file is not found
        :param filename_csr: name of the accompanying CSR file
        """
        return self.read_vector_with_csr(filename, umbi.datatypes.PrimitiveType.STRING, required, filename_csr)


class TarEncoder(TarWriter):
    def add_vector(self, filename: str, sized_type: SizedType, vector: list | None, required: bool = False):
        """
        Add a file containing a vector of values.
        :param filename: name of the file to add
        :param sized_type: type of the values
        :param vector: vector to add
        :param required: whether the file is required
        :raise ValueError: if required is True and vector is None
        """
        if vector is None:
            if required:
                raise ValueError(f"missing required data for {filename}")
            return
        data_out = umbi.binary.vector_to_bytes(vector, sized_type)
        self.add_file(filename, data_out)

    @staticmethod
    def pad_bitvector(vector: list[bool], num_bytes: int) -> list[bool]:
        """Pad a bitvector with False entries to make its length a multiple of num_bytes*8."""
        num_bits = num_bytes * 8
        items_to_add = (num_bits - (len(vector) % num_bits)) % num_bits
        if items_to_add > 0:
            # logger.debug(
            #     f"padding bitvector with {items_to_add} False entries to align to a {num_bytes}-byte boundary"
            # )
            vector = vector + [False] * items_to_add
        return vector

    def add_bitvector(self, filename: str, vector: list[bool], required: bool = False, pad_to_8_bytes: bool = True):
        """
        Add a bitvector file.
        :param filename: name of the file to add
        :param vector: bitvector data to write
        :param required: if True, raise an error if vector is None
        :param pad_to_8_bytes: if True, pad the bitvector to a multiple of 8 bytes
        """
        if vector is not None and pad_to_8_bytes:
            vector = self.pad_bitvector(vector, 8)
        self.add_vector(filename, BOOL1, vector, required)

    def add_vector_with_csr(
        self,
        filename: str,
        sized_type: SizedType,
        vector: list | None,
        filename_csr: str,
        required: bool = False,
    ):
        """
        Add a file containing a vector of values, with an accompanying CSR file if needed.
        :param filename: name of the main file to add
        :param sized_type: value type
        :param vector: vector data to write
        :param filename_csr: name of the accompanying CSR file
        :param required: if True, raise an error if vector is None
        """
        if vector is None:
            if required:
                raise ValueError(f"missing required data for {filename}")
            return
        data_out, chunk_csr = umbi.binary.vector_to_bytes_with_ranges(vector, sized_type)
        self.add_file(filename, data_out)
        if chunk_csr is not None:
            self.add_vector(filename_csr, UINT64, chunk_csr, required=True)

    def add_strings(self, filename: str, vector: list[str] | None, filename_csr: str, required: bool = False):
        """
        Add a file containing a vector of strings, using an accompanying CSR file.
        :param filename: name of the main file to add
        :param vector: list of strings to add
        :param filename_csr: name of the accompanying CSR file
        :param required: if True, raise an error if vector is None
        """
        self.add_vector_with_csr(
            filename, SizedType.for_type(umbi.datatypes.PrimitiveType.STRING), vector, filename_csr, required
        )
