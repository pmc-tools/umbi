"""Scalar encompasses primitive and numeric types."""

from .primitive import Primitive, PrimitiveType, primitive_type_of
from .numeric import NumericType, Numeric, numeric_type_of, numeric_promotion_type, promote_numeric_to
from .numeric_primitive import NumericPrimitive, NumericPrimitiveType
from .interval import Interval, IntervalType
from typing import TypeAlias, TypeVar
from collections.abc import Callable, Collection, Iterable, Sequence


#: Scalar type: either primitive or numeric.
ScalarType: TypeAlias = PrimitiveType | NumericType

#: Scalar value: either primitive or numeric.
Scalar: TypeAlias = Primitive | Numeric


# Dispatcher for scalar type-specific operations. Handlers are expected to be functions that take the specific type as an argument (e.g. on_primitive is expected to be a function that takes a PrimitiveType as an argument).

# Return type for dispatcher handlers
T = TypeVar("T")


def scalar_type_dispatch(
    value_type: ScalarType,
    *,
    on_primitive: Callable[[PrimitiveType], T],
    on_numeric: Callable[[NumericPrimitiveType], T],
    on_interval: Callable[[IntervalType], T],
) -> T:
    """Route to appropriate handler based on value_type.

    :param value_type: the scalar type to dispatch on
    :param on_primitive: handler for PrimitiveType
    :param on_numeric: handler for NumericPrimitiveType
    :param on_interval: handler for IntervalType
    :return: result from the appropriate handler
    """
    if isinstance(value_type, PrimitiveType):
        return on_primitive(value_type)
    elif isinstance(value_type, NumericPrimitiveType):
        return on_numeric(value_type)
    else:  # IntervalType
        # assert isinstance(value_type, IntervalType), f"unexpected type: {value_type}"
        return on_interval(value_type)


# Determining scalar type


def scalar_type_of(value: Scalar) -> ScalarType:
    """Determine the scalar type of a scalar."""
    if isinstance(value, Primitive):
        return primitive_type_of(value)
    else:  # isinstance(value, Numeric):
        return numeric_type_of(value)


def scalar_types_of(scalars: Iterable[Scalar]) -> set[ScalarType]:
    """Determine the set of scalar types of elements in the collection."""
    return {scalar_type_of(s) for s in scalars}


# Checking scalar value type


def validate_scalar_value_type(value: Scalar, value_type: ScalarType) -> None:
    """Validate that scalar value matches the scalar type."""

    def validate_primitive_instance(value_type: PrimitiveType) -> None:
        assert isinstance(value, Primitive), f"expected Primitive for type {value_type}, got {type(value)}"

    def validate_numeric_primitive_instance(value_type: NumericPrimitiveType) -> None:
        assert isinstance(value, NumericPrimitive), (
            f"expected NumericPrimitive for type {value_type}, got {type(value)}"
        )

    def validate_interval_instance(value_type: IntervalType) -> None:
        assert isinstance(value, Interval), f"expected Interval for type {value_type}, got {type(value)}"

    scalar_type_dispatch(
        value_type,
        on_primitive=validate_primitive_instance,
        on_numeric=validate_numeric_primitive_instance,
        on_interval=validate_interval_instance,
    )


# Determining promotion type


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


# Promotion operations


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
