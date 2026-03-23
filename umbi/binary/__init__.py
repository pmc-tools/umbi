"""
umbi.binary: Utilities for (de)serializing scalar and composite types.

Introduces some composite types.
- SizedType: a scalar type with an associated size (e.g., BOOL-4, UINT-64)
- StructType: a composite type with paddings and named attributes of type SizedType
- Struct: an instance of a StructType -- a mapping from attribute names to scalar values
"""

from .scalar import bytes_to_scalar, scalar_to_bytes
from .sequence import (
    bytes_to_vector,
    bytes_with_ranges_to_vector,
    vector_to_bytes,
    vector_to_bytes_with_ranges,
)
from .sized_type import (
    BOOL1,
    UINT32,
    UINT64,
    SizedType,
    max_num_bits_for_collection_element,
)
from .struct_type import (
    Struct,
    StructAttribute,
    StructPadding,
    StructType,
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
    "max_num_bits_for_collection_element",
    # struct_type.py
    "StructType",
    "StructPadding",
    "StructAttribute",
    "Struct",
]
