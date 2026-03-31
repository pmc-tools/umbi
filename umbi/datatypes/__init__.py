"""
umbi.datatypes: Core datatype definitions and utilities.

This package contains the fundamental datatype classes and definitions used throughout umbi,
including utilities for datatype conversions and promotions.

Scalar types: the following describe enums for names of scalar types and aliases for their python equivalents:
- PrimitiveType and Primitive: primitive scalar types (e.g., BOOL, STRING)
- NumericPrimitiveType and NumericPrimitive: numeric primitive types (e.g., INT, FLOAT, RATIONAL)
- IntervalType and Interval: interval types (e.g., INT_INTERVAL)
- NumericType and Numeric: numeric primitive and interval types
- ScalarType and Scalar: all scalar types (primitive, numeric primitive, and interval)

TODO: consider moving json-related definitions outside of datatypes
"""

from .interval import Interval, IntervalType
from .json import (
    JsonDict,
    JsonLike,
    JsonList,
    JsonPrimitive,
    json_remove_none_dict_values,
    json_to_string,
    string_to_json,
)
from .numeric import Numeric, NumericType, is_numeric_a_probability
from .numeric_primitive import NumericPrimitive, NumericPrimitiveType
from .primitive import Primitive, PrimitiveType
from .scalar import (
    Scalar,
    ScalarType,
    promote_scalars,
    promote_scalars_to,
    scalar_promotion_type_of,
    scalar_type_dispatch,
    validate_scalar_value_type,
)

__all__ = [
    # primitive.py
    "PrimitiveType",
    "Primitive",
    # numeric_primitive.py
    "NumericPrimitiveType",
    "NumericPrimitive",
    # interval.py
    "IntervalType",
    "Interval",
    # numeric.py
    "NumericType",
    "Numeric",
    "is_numeric_a_probability",
    # scalar.py
    "ScalarType",
    "Scalar",
    "scalar_promotion_type_of",
    "promote_scalars_to",
    "promote_scalars",
    "scalar_type_dispatch",
    "validate_scalar_value_type",
    # json.py
    "JsonPrimitive",
    "JsonList",
    "JsonDict",
    "JsonLike",
    "json_remove_none_dict_values",
    "json_to_string",
    "string_to_json",
]
