"""Composite datatype definitions."""

from umbi.datatypes import IntervalType, PrimitiveType, Scalar

from .sized_type import SizedType, UINT64
from .scalar import bits_to_scalar, scalar_to_bits
from .utils import split_bytes

from bitstring import BitArray
from dataclasses import dataclass, field as dataclass_field


# Struct type definitions

# alias for instances of StructType, as a mapping from attribute names to (optional) values
Struct = dict[str, Scalar | None]


@dataclass(frozen=True)
class StructPadding:
    """Padding bits in a composite datatype."""

    padding: int

    def validate(self):
        if self.padding <= 0:
            raise ValueError(f"Padding must be positive ({self.padding})")

    @property
    def size_bits(self) -> int:
        return self.padding


@dataclass
class StructAttribute:
    """A variable field in a composite datatype."""

    name: str
    sized_type: SizedType
    is_optional: bool = (
        False  # if True, then the value is preceded with a presence flag, 1 = present, 0 = present but must be ignored
    )
    lower: int | None = None  # lower bound (for numeric types)
    upper: int | None = None  # upper bound (for numeric types)
    offset: int | None = None  # lower value offset (for numeric types)

    @property
    def size_bits(self) -> int:
        size_bits = self.sized_type.size_bits
        if self.is_optional:
            size_bits += 1  # presence flag
        return size_bits

    def validate(self):
        self.sized_type.validate()
        if isinstance(self.sized_type.type, IntervalType):
            raise ValueError(f"Struct attribute cannot be of interval type: {self.sized_type.type}")
        if self.offset is not None and self.offset != 0:
            raise NotImplementedError("non-zero offset validation not implemented")
        # TODO validate bounds for numeric types


""" Alias for either struct field type """
StructField = StructPadding | StructAttribute


@dataclass
class StructType:
    """A composite datatype consisting of attributes and paddings."""

    fields: list[StructField] = dataclass_field(default_factory=list)

    def validate(self):
        for item in self.fields:
            item.validate()

    @property
    def attributes(self):
        """Iterate over attributes only, skipping padding fields."""
        return [f for f in self.fields if isinstance(f, StructAttribute)]

    @property
    def size_bits(self) -> int:
        return sum(f.size_bits for f in self.fields)

    @property
    def is_byte_aligned(self) -> bool:
        return self.size_bits % 8 == 0

    @property
    def size_bytes(self) -> int:
        return (self.size_bits + 7) // 8  # ceiling division

    @property
    def contains_strings(self) -> bool:
        return any(isinstance(f, StructAttribute) and f.sized_type.type == PrimitiveType.STRING for f in self.fields)

    def __str__(self) -> str:
        lines = ["struct:"]
        for f in self.fields:
            lines.append(f"  {f}")
        return "\n".join(lines)

    def __iter__(self):
        return iter(self.fields)

    @property
    def num_bits_to_pad(self) -> int:
        """Calculate the number of padding bits needed to align current struct to a full byte."""
        return (8 - self.size_bits % 8) % 8

    def add_padding(self, num_bits: int) -> None:
        """Add padding bits to the struct."""
        assert num_bits > 0
        self.fields.append(StructPadding(padding=num_bits))

    def pad_to_byte(self) -> None:
        """Add padding bits to align struct to a full byte."""
        if self.is_byte_aligned:
            return
        self.add_padding(self.num_bits_to_pad)

    def add_attribute(self, name: str, sized_type: SizedType) -> None:
        """Add an attribute field to the struct."""
        self.fields.append(StructAttribute(name=name, sized_type=sized_type))


# Struct (de)serialization


class StructUnpacker:
    """Utility class for unpacking composite datatypes from a bytestring."""

    def __init__(self, bytestring: bytes) -> None:
        self.bytestring = bytestring  # input bytestring, little-endian order
        self.buffer = BitArray()  # bit buffer, MSB at [0]

    def assert_buffer_empty(self):
        if len(self.buffer) > 0:
            raise RuntimeError("expected the buffer to be empty")

    def align_buffer(self, num_bits: int):
        """Ensure the buffer has the required number of bits."""
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

    def unpack_attribute(self, field: StructAttribute) -> Scalar | None:
        """
        Unpack a single field from the buffer.
        :return: the unpacked value, or None if the field is optional and not present
        """
        sized_type = field.sized_type
        if field.sized_type.type == PrimitiveType.STRING:
            # a string is stored as an index to the list of strings
            sized_type = UINT64
        bits = self.extract_from_buffer(sized_type.size_bits)
        if field.is_optional:
            is_present_bit = bits[-1]  # remove from the end (LSB side)
            bits = bits[:-1]
            if not is_present_bit:
                return None
        return bits_to_scalar(bits, sized_type.type)

    def unpack_struct(self, value_type: StructType) -> Struct:
        name_value: Struct = {}
        for field in value_type:
            if isinstance(field, StructPadding):
                self.skip_padding(field)
                continue
            name_value[field.name] = self.unpack_attribute(field)
        self.assert_buffer_empty()
        return name_value


class StructPacker:
    """Utility class for packing structs into a bytestring."""

    def __init__(self) -> None:
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

    def pack_attribute(self, field: StructAttribute, value: Scalar | None):
        """Pack a single attribute into the buffer or the bytestring."""
        sized_type = field.sized_type
        if field.sized_type.type == PrimitiveType.STRING:
            # a string is stored as an index to the list of strings
            sized_type = UINT64
        value_present = value is not None
        if not value_present:
            assert field.is_optional, "only optional fields can have None value"
            value = 0  # use an arbitrary value
        bits = scalar_to_bits(value, sized_type.type, sized_type.size_bits)
        if field.is_optional:
            presence_value = 1 if value_present else 0
            presence_bit = BitArray(uint=presence_value, length=1)  # set presence bit
            bits = bits + presence_bit  # append presence bit to the end (LSB side)
        self.append_to_buffer(bits)

    def pack_struct(self, value_sized_type: StructType, struct: Struct) -> bytes:
        assert value_sized_type.is_byte_aligned, "cannot pack a struct that is not byte-aligned"
        for field in value_sized_type:
            if isinstance(field, StructPadding):
                self.add_padding(field)
            else:
                assert isinstance(field, StructAttribute)
                self.pack_attribute(field, struct[field.name])
        self.assert_buffer_empty()
        return self.bytestring


# API


def bytes_to_struct(bytestring: bytes, value_type: StructType) -> Struct:
    """Unpack a BitArray to a composite datatype."""
    return StructUnpacker(bytestring).unpack_struct(value_type)


def struct_to_bytes(struct: Struct, value_type: StructType) -> bytes:
    """Convert a composite datatype to a BitArray."""
    return StructPacker().pack_struct(value_type, struct)
