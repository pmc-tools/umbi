"""
Common datatype for all primitive and interval types.
"""

from .atomic import Atomic, AtomicType, atomic_type_of
from .numeric import NumericType, Numeric, numeric_type_of, common_numeric_type, promote_numeric_to

""" Alias for all common types. """
DataType = AtomicType | NumericType

""" Alias for all common objects. """
ValueType = Atomic | Numeric


def datatype_of(value: ValueType) -> DataType:
    """Determine the common or interval type of a given value."""
    if isinstance(value, Atomic):
        return atomic_type_of(value)
    else:  # isinstance(value, Numeric):
        return numeric_type_of(value)


# def is_instance_of_type(value: object, type: DataType) -> bool:
#     """Check if a value is an instance of the given common or interval type."""
#     return get_instance_type(value) == type


def common_datatype(types: set[DataType]) -> DataType:
    """
    Determine the common type from a set of types. Used for type promotion.
    Rules: bool -> Numeric -> string
    """
    assert len(types) > 0, "cannot determine common type of empty set"
    assert all(isinstance(t, DataType) for t in types), f"non-common types found in set: {types}"
    if AtomicType.STRING in types:
        return AtomicType.STRING
    if AtomicType.BOOL in types:
        if len(types) == 1:
            return AtomicType.BOOL
        types.remove(AtomicType.BOOL)
    return common_numeric_type(types)  # type: ignore


def promote_value_to(value: ValueType, target_type: DataType) -> ValueType:
    """Promote a value to the target type."""
    if target_type == AtomicType.STRING:
        return str(value)
    elif target_type == AtomicType.BOOL:
        assert isinstance(value, bool), f"cannot promote {value} to bool"
        return value
    else:  # is_numeric_type(target_type):
        if isinstance(value, bool):
            value = int(value)
        assert isinstance(value, Numeric), f"cannot promote {value} to numeric type {target_type}"
        return promote_numeric_to(value, target_type)
