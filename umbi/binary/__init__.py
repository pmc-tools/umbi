"""
umbi.binary: Utilities for (de)serializing basic types.

Introduces some composite types.
- SizedType: a scalar type with an associated size (e.g., BOOL-4, UINT-64)
- StructType: a composite type with named attributes of type SizedType
- Struct: a mapping from field names to scalar values, representing an instance of a StructType
"""

from .scalar import bytes_to_scalar, scalar_to_bytes
from .sequence import (
    bytes_to_vector,
    bytes_with_ranges_to_vector,
    vector_to_bytes,
    vector_to_bytes_with_ranges,
)
from .sized_type import (
    SizedType,
    BOOL1,
    UINT32,
    UINT64,
)
from .struct_type import (
    StructType,
    StructPadding,
    StructAttribute,
    Struct,
)

__all__ = [
    # scalar.py
    "scalar_to_bytes",
    "bytes_to_scalar",
    # sequence.py
    "bytes_to_vector",
    "bytes_with_ranges_to_vector",
    "vector_to_bytes",
    "vector_to_bytes_with_ranges",
    # sized_type.py
    "SizedType",
    "BOOL1",
    "UINT32",
    "UINT64",
    # struct_type.py
    "StructType",
    "StructPadding",
    "StructAttribute",
    "Struct",
]
