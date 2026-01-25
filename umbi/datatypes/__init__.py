"""
umbi.datatypes: Core datatype definitions and utilities.

This package contains the fundamental datatype classes and definitions used throughout umbi,
including intervals, composite types, vector utilities, and JSON operations.
"""

# atomic.py
from .atomic import AtomicType, Atomic, atomic_type_of

# datatype.py
from .datatype import DataType, ValueType, datatype_of, common_datatype

# interval.py
from .interval import IntervalType, Interval, interval_base_type, base_to_interval_type

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
    vector_element_types,
    vector_element_type,
    common_vector_element_type,
)

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

__all__ = [
    # atomic.py
    "AtomicType",
    "Atomic",
    "atomic_type_of",
    # datatype.py
    "DataType",
    "ValueType",
    "datatype_of",
    "common_datatype",
    # interval.py
    "IntervalType",
    "Interval",
    "interval_base_type",
    "base_to_interval_type",
    # json.py
    "JsonPrimitive",
    "JsonList",
    "JsonDict",
    "JsonLike",
    "is_json_instance",
    "json_remove_none_dict_values",
    "json_to_string",
    "string_to_json",
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
    "vector_element_types",
    "vector_element_type",
    "common_vector_element_type",
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
    # numeric_primitive.py
    "NumericPrimitiveType",
    "NumericPrimitive",
    "numeric_primitive_type_of",
    "common_numeric_primitive_type",
    "promote_numeric_primitive_to",
    "is_integer_type",
    "integer_type_signed",
    # numeric.py
    "NumericType",
    "Numeric",
    "is_numeric_primitive_type",
    "is_interval_type",
    "numeric_type_of",
    "common_numeric_type",
    "promote_numeric_to",
]
