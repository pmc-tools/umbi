"""
Composite datatype definitions.

This module contains the core classes for defining composite datatypes (structs).
The serialization operations for composites remain in umbi.binary.composites.
"""

from dataclasses import dataclass, field

from .interval import IntervalType
from .sized_type import SizedType
from .atomic import AtomicType


@dataclass
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

    def validate(self):
        self.sized_type.validate()
        if isinstance(self.sized_type.type, IntervalType):
            raise ValueError(f"Struct attribute cannot be of interval type: {self.sized_type.type}")
        if self.offset is not None and self.offset != 0:
            raise NotImplementedError("non-zero offset validation not implemented")
        # TODO validate bounds for numeric types

    @property
    def size_bits(self) -> int:
        size_bits = self.sized_type.size_bits
        if self.is_optional:
            size_bits += 1  # presence flag
        return size_bits


""" Alias for either struct field type """
StructField = StructPadding | StructAttribute


@dataclass
class StructType:
    """A composite datatype consisting of attributes and paddings."""

    fields: list[StructField] = field(default_factory=list)

    def validate(self):
        for item in self.fields:
            item.validate()

    @property
    def size_bits(self) -> int:
        return sum(f.size_bits for f in self.fields)

    @property
    def is_byte_aligned(self) -> bool:
        return self.size_bits % 8 == 0

    @property
    def size_bytes(self) -> int:
        num_bytes = self.size_bits // 8
        if self.size_bits % 8 != 0:
            num_bytes += 1
        return num_bytes

    @property
    def contains_strings(self) -> bool:
        return any(isinstance(f, StructAttribute) and f.sized_type.type == AtomicType.STRING for f in self.fields)

    def __str__(self) -> str:
        lines = ["struct:"]
        for f in self.fields:
            lines.append(f"  {f}")
        return "\n".join(lines)

    def __iter__(self):
        return iter(self.fields)

    def bits_to_pad(self) -> int:
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
        self.add_padding(self.bits_to_pad())

    def add_attribute(self, name: str, sized_type: SizedType) -> None:
        """Add an attribute field to the struct."""
        self.fields.append(StructAttribute(name=name, sized_type=sized_type))
