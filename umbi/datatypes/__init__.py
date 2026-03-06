"""
umbi.datatypes: Core datatype definitions and utilities.

This package contains the fundamental datatype classes and definitions used throughout umbi,
including intervals, composite types, vector utilities, and JSON operations.

Scalar types: the following describe enums for names of scalar types and their python equivalents:
- PrimitiveType and Primitive: primitive scalar types (e.g., BOOL, STRING)
- NumericPrimitiveType and NumericPrimitive: numeric primitive types (e.g., INT, FLOAT, RATIONAL)
- IntervalType and Interval: interval types (e.g., INT_INTERVAL)
- NumericType and Numeric: numeric primitive and interval types
- ScalarType and Scalar: all scalar types (primitive, numeric primitive, and interval)

Composite types: these do not need an enum for type names, as they are defined by their python class:
- SizedType: a single scalar type with an associated size (e.g., BOOL-4, UINT-64)
- StructType: a composite type with named attributes of type SizedType
- VectorType: a vector of values of a certain SizedType

Extra aliases:
- BIT_VECTOR: a vector of 1-bit booleans
- CSR_VECTOR: a vector of UINT64 used for CSR row start indices
- JsonLike: a union of JSON primitive, list, and dict types
"""

# primitive.py
from .primitive import PrimitiveType, Primitive, primitive_type_of

# numeric_primitive.py
from .numeric_primitive import (
    NumericPrimitiveType,
    NumericPrimitive,
    numeric_primitive_type_of,
    common_numeric_primitive_type,
    promote_numeric_primitive_to,
    is_integer_type,
    integer_type_signed,
)

# interval.py
from .interval import IntervalType, Interval, interval_base_type, base_to_interval_type

# numeric.py
from .numeric import (
    NumericType,
    Numeric,
    is_numeric_primitive_type,
    is_interval_type,
    numeric_type_of,
    common_numeric_type,
    promote_numeric_to,
)

# scalar.py
from .scalar import ScalarType, Scalar, scalar_type_of, common_scalar_type, promote_scalar_to

# sized_type.py
from .sized_type import (
    SizedType,
    atomic_type_default_size,
    numeric_primitive_type_default_size,
    interval_type_default_size,
    type_default_size,
    validate_atomic_type_size,
    validate_numeric_primitive_type_size,
    validate_interval_type_size,
    validate_type_size,
    BOOL1,
    UINT16,
    UINT32,
    UINT64,
)

# struct.py
from .struct import StructPadding, StructAttribute, StructType

# vector.py
from .vector import (
    VectorType,
    assert_is_list,
    is_vector_ranges,
    is_vector_csr,
    csr_to_ranges,
    ranges_to_csr,
    collection_element_types,
    collection_element_type,
    common_collection_element_type,
    promote_vector_to,
)

# json.py
from .json import (
    JsonPrimitive,
    JsonList,
    JsonDict,
    JsonLike,
    is_json_instance,
    json_remove_none_dict_values,
    json_to_string,
    string_to_json,
)


__all__ = [
    # primitive.py
    "PrimitiveType",
    "Primitive",
    "primitive_type_of",
    # numeric_primitive.py
    "NumericPrimitiveType",
    "NumericPrimitive",
    "numeric_primitive_type_of",
    "common_numeric_primitive_type",
    "promote_numeric_primitive_to",
    "is_integer_type",
    "integer_type_signed",
    # interval.py
    "IntervalType",
    "Interval",
    "interval_base_type",
    "base_to_interval_type",
    # numeric.py
    "NumericType",
    "Numeric",
    "is_numeric_primitive_type",
    "is_interval_type",
    "numeric_type_of",
    "common_numeric_type",
    "promote_numeric_to",
    # scalar.py
    "ScalarType",
    "Scalar",
    "scalar_type_of",
    "common_scalar_type",
    "promote_scalar_to",
    # sized_type.py
    "SizedType",
    "atomic_type_default_size",
    "numeric_primitive_type_default_size",
    "interval_type_default_size",
    "type_default_size",
    "validate_atomic_type_size",
    "validate_numeric_primitive_type_size",
    "validate_interval_type_size",
    "validate_type_size",
    "BOOL1",
    "UINT16",
    "UINT32",
    "UINT64",
    # struct.py
    "StructPadding",
    "StructAttribute",
    "StructType",
    # vector.py
    "VectorType",
    "assert_is_list",
    "is_vector_ranges",
    "is_vector_csr",
    "csr_to_ranges",
    "ranges_to_csr",
    "collection_element_types",
    "collection_element_type",
    "common_collection_element_type",
    "promote_vector_to",
    # json.py
    "JsonPrimitive",
    "JsonList",
    "JsonDict",
    "JsonLike",
    "is_json_instance",
    "json_remove_none_dict_values",
    "json_to_string",
    "string_to_json",
]
