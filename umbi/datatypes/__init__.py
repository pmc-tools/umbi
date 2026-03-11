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

TODO: consider moving json-related utilities outside of datatypes
"""

from .primitive import PrimitiveType, Primitive
from .numeric_primitive import NumericPrimitiveType, NumericPrimitive
from .interval import IntervalType, Interval
from .numeric import NumericType, Numeric
from .scalar import ScalarType, Scalar, scalar_promotion_type
from .collection import collection_promotion_type, promote_vector_to, promote_vector

# json.py
from .json import (
    JsonLike,
    json_remove_none_dict_values,
    json_to_string,
    string_to_json,
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
    # scalar.py
    "ScalarType",
    "Scalar",
    "scalar_promotion_type",
    # vector.py
    "collection_promotion_type",
    "promote_vector_to",
    "promote_vector",
    # json.py
    "JsonLike",
    "json_remove_none_dict_values",
    "json_to_string",
    "string_to_json",
]
