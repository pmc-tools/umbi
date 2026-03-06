"""
Scalar encompasses primitive and numeric types.
"""

from .primitive import Primitive, PrimitiveType, primitive_type_of
from .numeric import NumericType, Numeric, numeric_type_of, common_numeric_type, promote_numeric_to

""" Alias for names of scalar types. """
ScalarType = PrimitiveType | NumericType

""" Alias for objects of scalar type. """
Scalar = Primitive | Numeric


def scalar_type_of(value: Scalar) -> ScalarType:
    """Determine the common or interval type of a given value."""
    if isinstance(value, Primitive):
        return primitive_type_of(value)
    else:  # isinstance(value, Numeric):
        return numeric_type_of(value)


def common_scalar_type(types: set[ScalarType]) -> ScalarType:
    """
    Determine the common type from a set of types. Used for type promotion.
    Rules: bool -> Numeric -> string
    """
    assert len(types) > 0, "cannot determine common type of empty set"
    assert all(isinstance(t, ScalarType) for t in types), f"non-common types found in set: {types}"
    if PrimitiveType.STRING in types:
        return PrimitiveType.STRING
    if PrimitiveType.BOOL in types:
        if len(types) == 1:
            return PrimitiveType.BOOL
        types.remove(PrimitiveType.BOOL)
    return common_numeric_type(types)  # type: ignore


def promote_scalar_to(value: Scalar, target_type: ScalarType) -> Scalar:
    """Promote a value to the target type."""
    if target_type == PrimitiveType.STRING:
        return str(value)
    elif target_type == PrimitiveType.BOOL:
        assert isinstance(value, bool), f"cannot promote {value} to bool"
        return value
    else:  # isinstance(target_type, NumericType):
        if isinstance(value, bool):
            value = int(value)
        assert isinstance(value, Numeric), f"cannot promote {value} to numeric type {target_type}"
        return promote_numeric_to(value, target_type)
