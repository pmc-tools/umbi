"""Scalar encompasses primitive and numeric types."""

from .primitive import Primitive, PrimitiveType, primitive_type_of
from .numeric import NumericType, Numeric, numeric_type_of, numeric_promotion_type, promote_numeric_to
from typing import TypeAlias
from collections.abc import Iterable, Collection, Sequence


#: Scalar type: either primitive or numeric.
ScalarType: TypeAlias = PrimitiveType | NumericType

#: Scalar value: either primitive or numeric.
Scalar: TypeAlias = Primitive | Numeric


# Determining scalar type.


def scalar_type_of(value: Scalar) -> ScalarType:
    """Determine the scalar type of a scalar."""
    if isinstance(value, Primitive):
        return primitive_type_of(value)
    else:  # isinstance(value, Numeric):
        return numeric_type_of(value)


def scalar_types_of(scalars: Iterable[Scalar]) -> set[ScalarType]:
    """Determine the set of scalar types of elements in the collection."""
    return {scalar_type_of(s) for s in scalars}


# Determining promotion type.


def scalar_promotion_type(types: Collection[ScalarType]) -> ScalarType:
    """
    Determine the scalar type to which all types in the set can be promoted.
    Rules: bool -> Numeric -> string
    :raises ValueError: if the set of types is empty
    """
    if len(types) == 0:
        raise ValueError("cannot determine common type of empty set")
    if PrimitiveType.STRING in types:
        return PrimitiveType.STRING
    if PrimitiveType.BOOL in types:
        if len(types) == 1:
            return PrimitiveType.BOOL
        types = {t for t in types if t != PrimitiveType.BOOL}
    # assert all(isinstance(t, NumericType) for t in types), f"non-numeric types found in set: {types}"
    return numeric_promotion_type(types)  # type: ignore


def scalar_promotion_type_of(collection: Iterable[Scalar]) -> ScalarType:
    """Determine the scalar type to which all scalars in the collection can be promoted."""
    return scalar_promotion_type(scalar_types_of(collection))


# Promotion operations.


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


def promote_scalars_to(scalars: Sequence[Scalar], target_type: ScalarType) -> list[Scalar]:
    """Promote a sequence of scalars to the target type."""
    return [promote_scalar_to(s, target_type) for s in scalars]


def promote_scalars(scalars: Sequence[Scalar]) -> tuple[ScalarType, list[Scalar]]:
    """Promote a sequence of scalars to the common promotion type determined automatically."""
    target_type = scalar_promotion_type_of(scalars)
    vector = promote_scalars_to(scalars, target_type)
    return target_type, vector
