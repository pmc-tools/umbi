from dataclasses import dataclass
from .atomic import AtomicType
from .numeric_primitive import NumericPrimitiveType
from .interval import IntervalType
from .datatype import DataType


def atomic_type_default_size(type: AtomicType) -> int:
    return {
        AtomicType.BOOL: 1,
        AtomicType.STRING: 64,
    }[type]


def numeric_primitive_type_default_size(type: NumericPrimitiveType) -> int:
    return {
        NumericPrimitiveType.INT: 64,
        NumericPrimitiveType.UINT: 64,
        NumericPrimitiveType.DOUBLE: 64,
        NumericPrimitiveType.RATIONAL: 128,
    }[type]


def interval_type_default_size(type: IntervalType) -> int:
    return {
        IntervalType.INT: 128,
        IntervalType.UINT: 128,
        IntervalType.DOUBLE: 128,
        IntervalType.RATIONAL: 256,
    }[type]


def type_default_size(type: DataType) -> int:
    if isinstance(type, AtomicType):
        return atomic_type_default_size(type)
    elif isinstance(type, NumericPrimitiveType):
        return numeric_primitive_type_default_size(type)
    else:  # isinstance(type, IntervalType)
        return interval_type_default_size(type)


def validate_atomic_type_size(type: AtomicType, size: int) -> None:
    if type == AtomicType.STRING:
        if size != 64:
            raise ValueError(f"{type.value} size must be 64")


def validate_numeric_primitive_type_size(type: NumericPrimitiveType, size: int) -> None:
    if type == NumericPrimitiveType.DOUBLE:
        if size != 64:
            raise ValueError(f"{type.value} size must be 64")
    if type == NumericPrimitiveType.RATIONAL:
        if size % 2 != 0:
            raise ValueError(f"{type.value} size must be a multiple of 2")


def validate_interval_type_size(type: IntervalType, size: int) -> None:
    if type in {IntervalType.INT, IntervalType.UINT, IntervalType.DOUBLE, IntervalType.RATIONAL}:
        if size % 2 != 0:
            raise ValueError(f"{type.value} size must be a multiple of 2")
        if type == IntervalType.RATIONAL and size % 4 != 0:
            raise ValueError(f"{type.value} size must be a multiple of 4")


def validate_type_size(type: DataType, size: int) -> None:
    if isinstance(type, AtomicType):
        validate_atomic_type_size(type, size)
    elif isinstance(type, NumericPrimitiveType):
        validate_numeric_primitive_type_size(type, size)
    else:  # isinstance(type, IntervalType)
        validate_interval_type_size(type, size)


@dataclass
class SizedType:
    """
    Represents a type definition for common types.
    """

    type: DataType
    size_bits: int  # size in bits

    def __init__(self, type: DataType, size_bits: int | None = None):
        self.type = type
        if size_bits is None:
            size_bits = type_default_size(type)
        self.size_bits = size_bits

    def __post_init__(self):
        self.validate()

    def validate(self):
        assert self.size_bits > 0, "size must be positive"
        validate_type_size(self.type, self.size_bits)

    @property
    def is_byte_aligned(self) -> bool:
        return self.size_bits % 8 == 0

    @property
    def size_bytes(self) -> int:
        return (self.size_bits + 7) // 8  # ceiling division


# Common sized types used in umbi
BOOL1 = SizedType(AtomicType.BOOL, 1)
UINT16 = SizedType(NumericPrimitiveType.UINT, 16)
UINT32 = SizedType(NumericPrimitiveType.UINT, 32)
UINT64 = SizedType(NumericPrimitiveType.UINT, 64)
