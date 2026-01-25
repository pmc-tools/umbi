"""
Utilities for packing and unpacking composite datatypes (structs).
"""

from bitstring import BitArray

from umbi.datatypes import StructType, StructAttribute, StructPadding, AtomicType, ValueType, UINT64
from .common import bits_to_value, value_to_bits
from .utils import split_bytes


class StructUnpacker:
    """Utility class for unpacking composite datatypes from a bytestring."""

    def __init__(self, bytestring: bytes):
        self.bytestring = bytestring  # input bytestring, little-endian order
        self.buffer = BitArray()  # bit buffer, MSB at [0]

    def assert_buffer_empty(self):
        if len(self.buffer) > 0:
            raise RuntimeError("expected the buffer to be empty")

    def align_buffer(self, num_bits: int):
        """Ensure the buffer has the required number ofbits."""
        if len(self.buffer) >= num_bits:
            return
        num_bytes_needed = (num_bits - len(self.buffer) + 7) // 8
        assert len(self.bytestring) >= num_bytes_needed, "not enough data to fill the buffer"
        for _ in range(num_bytes_needed):  # read one byte at a time since the bytestring is little-endian
            next_bytes, self.bytestring = split_bytes(self.bytestring, 1)
            self.buffer = BitArray(bytes=next_bytes) + self.buffer  # prepend to the buffer to keep MSB at [0]

    def extract_from_buffer(self, num_bits: int):
        """Extract the given number of bits from the buffer."""
        assert num_bits >= 0
        self.align_buffer(num_bits)
        bits = self.buffer[-num_bits:]  # remove from the end (LSB side)
        self.buffer = self.buffer[:-num_bits]
        return bits

    def skip_padding(self, field: StructPadding):
        self.extract_from_buffer(field.padding)

    def unpack_attribute(self, field: StructAttribute) -> ValueType | None:
        """
        Unpack a single field from the buffer.
        :return: the unpacked value, or None if the field is optional and not present
        """
        sized_type = field.sized_type
        if field.sized_type.type == AtomicType.STRING:
            # a string is stored as an index to the list of strings
            sized_type = UINT64
        bits = self.extract_from_buffer(sized_type.size_bits)
        if field.is_optional:
            is_present_bit = bits[-1]  # remove from the end (LSB side)
            bits = bits[:-1]
            if not is_present_bit:
                return None
        return bits_to_value(bits, sized_type.type)

    def unpack_struct(self, value_type: StructType) -> dict[str, ValueType | None]:
        name_value = dict()
        for field in value_type:
            if isinstance(field, StructPadding):
                self.skip_padding(field)
                continue
            name_value[field.name] = self.unpack_attribute(field)
        self.assert_buffer_empty()
        return name_value


class StructPacker:
    """Utility class for packing structs into a bytestring."""

    def __init__(self):
        self.buffer = BitArray()  # bit buffer, MSB at [0]
        self.bytestring = bytes()  # output bytestring, little-endian order

    def assert_buffer_empty(self):
        if len(self.buffer) > 0:
            raise RuntimeError("expected the buffer to be empty")

    def flush_buffer(self):
        """Flush full bytes from the buffer to the bytestring."""
        while len(self.buffer) >= 8:  # append one byte at a time so that the bytestring is little-endian
            self.buffer, bits = (
                self.buffer[:-8],
                self.buffer[-8:],
            )  # get new bits from the end (LSB side)
            new_bytes = bits.tobytes()
            self.bytestring += new_bytes

    def append_to_buffer(self, bits: BitArray):
        """Append bits to the buffer flush full bytes to the bytestring."""
        self.buffer = bits + self.buffer  # prepend to the start (MSB side)
        self.flush_buffer()

    def add_padding(self, field: StructPadding):
        """Add padding bits to the buffer."""
        self.append_to_buffer(BitArray(uint=0, length=field.padding))

    def pack_attribute(self, field: StructAttribute, value: ValueType | None):
        """Pack a single attribute into the buffer or the bytestring."""
        sized_type = field.sized_type
        if field.sized_type.type == AtomicType.STRING:
            # a string is stored as an index to the list of strings
            sized_type = UINT64
        bits = None
        if value is None:
            assert field.is_optional, "only optional fields can have None value"
            # add an arbitrary value with the presence bit set to 0
            bits = value_to_bits(0, sized_type)
            bits = bits + BitArray(uint=0, length=1)  # set presence bit to 0
        else:
            bits = value_to_bits(value, sized_type)
            if field.is_optional:
                presence_flag = BitArray(uint=1, length=1)  # set presence bit to 1
                bits = bits + presence_flag
        if field.is_optional:
            is_present_bit = bits[-1]  # remove from the end (LSB side)
            bits = bits[:-1]
            if not is_present_bit:
                return None
        self.append_to_buffer(bits)

    def pack_struct(self, value_sized_type: StructType, values: dict[str, ValueType | None]) -> bytes:
        for field in value_sized_type:
            if isinstance(field, StructPadding):
                self.add_padding(field)
            else:
                assert isinstance(field, StructAttribute)
                self.pack_attribute(field, values[field.name])
        self.assert_buffer_empty()
        return self.bytestring


def struct_unpack(bytestring: bytes, value_type: StructType) -> dict[str, ValueType | None]:
    """Unpack a BitArray to a composite datatype."""
    return StructUnpacker(bytestring).unpack_struct(value_type)


def struct_pack(values: dict[str, ValueType | None], value_type: StructType) -> bytes:
    """Convert a composite datatype to a BitArray."""
    return StructPacker().pack_struct(value_type, values)
