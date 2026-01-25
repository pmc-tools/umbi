import logging

import umbi.binary
import umbi.datatypes
from umbi.datatypes import (
    DataType,
    AtomicType,
    SizedType,
    BOOL1,
    UINT64,
)

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
        data = self.read(filename, required)
        if data is None:
            return None
        return umbi.binary.bytes_to_vector(data, sized_type)

    @staticmethod
    def truncate_bitvector(vector: list, num_entries: int) -> list:
        """Truncate a bitvector if its length exceeds this num_entries."""
        if len(vector) > num_entries:
            if any(vector[num_entries:]):
                logger.warning(
                    f"bitvector {len(vector)} exceeds expected length of {num_entries}, truncating and discarding non-False entries"
                )
            vector = vector[:num_entries]
        return vector

    def read_bitvector(self, filename: str, num_entries: int) -> list[bool]:
        """Read a bitvector and truncate it to num_entries if necessary."""
        vector = self.read_vector(filename, BOOL1, required=True)
        assert isinstance(vector, list)
        return self.truncate_bitvector(vector, num_entries)

    def read_vector_with_csr(
        self, filename: str, value_type: DataType, required: bool, filename_csr: str
    ) -> list | None:
        """
        Read a file containing a vector of values. Use an accompanying CSR file if needed.
        :param filename: name of the main file to read
        :param value_type: value type
        :param required: if True, raise an error if the main file is not found
        :param filename_csr: name of the accompanying CSR file
        :param required_csr: if True, raise an error if the CSR file is not found
        """
        data = self.read(filename, required)
        if data is None:
            return None
        chunk_ranges = self.read_vector(filename_csr, UINT64, required=True)
        assert chunk_ranges is not None, "chunk_ranges must be prprovided"
        assert isinstance(chunk_ranges, list)
        chunk_ranges = umbi.datatypes.csr_to_ranges(chunk_ranges)
        return umbi.binary.bytes_with_csr_to_vector(data, value_type, chunk_ranges=chunk_ranges)

    def read_strings(self, filename: str, required: bool, filename_csr: str) -> list[str] | None:
        """
        Read a file containing a vector of strings, using an accompanying CSR file.
        :param filename: name of the main file to read
        :param required: if True, raise an error if the main file is not found
        :param filename_csr: name of the accompanying CSR file
        """
        return self.read_vector_with_csr(filename, umbi.datatypes.AtomicType.STRING, required, filename_csr)


class TarEncoder(TarWriter):
    def add_vector(self, filename: str, sized_type: SizedType, data: list | None, required: bool = False):
        """
        Write a file containing a vector of values.
        :param filename: name of the file to write
        :param sized_type: type of the values
        :param data: vector data to write
        :param required: if True, raise an error if data is None
        """
        if data is None:
            if required:
                raise ValueError(f"missing required data for {filename}")
            return
        data_out = umbi.binary.vector_to_bytes(data, sized_type)
        self.add(filename, data_out)

    def add_bitvector(self, filename: str, data: list[bool], required: bool = False, pad_to_8_bytes: bool = False):
        """Write a bitvector."""
        if pad_to_8_bytes:
            items_to_add = (64 - (len(data) % 64)) % 64
            if items_to_add > 0:
                # logger.debug(f"padding bitvector {filename} with {items_to_add} False entries to align to 64-bit boundary")
                data = data + [False] * items_to_add
        self.add_vector(filename, BOOL1, data, required)

    def add_vector_with_csr(
        self, filename: str, sized_type: SizedType, data: list | None, filename_csr: str, required: bool = False
    ):
        """
        Write a file containing a vector of values, with an accompanying CSR file if needed.
        :param filename: name of the main file to write
        :param sized_type: value type
        :param data: vector data to write
        :param filename_csr: name of the accompanying CSR file
        :param required: if True, raise an error if data is None
        """
        if data is None:
            if required:
                raise ValueError(f"missing required data for {filename}")
            return
        data_out, chunk_csr = umbi.binary.vector_to_bytes_with_csr(data, sized_type)
        self.add(filename, data_out)
        if chunk_csr is not None:
            self.add_vector(filename_csr, UINT64, chunk_csr, required=True)

    def add_strings(self, filename: str, data: list[str] | None, filename_csr: str, required: bool = False):
        """
        Write a file containing a vector of strings, using an accompanying CSR file.
        :param filename: name of the main file to write
        :param data: list of strings to write
        :param filename_csr: name of the accompanying CSR file
        :param required: if True, raise an error if data is None
        """
        self.add_vector_with_csr(filename, SizedType(AtomicType.STRING), data, filename_csr, required)
