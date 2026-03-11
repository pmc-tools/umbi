"""
Auxiliary collection operations.
"""

from .scalar import ScalarType, Scalar, scalar_promotion_type, scalar_type_of, promote_scalar_to

from collections.abc import Sequence, Collection


def collection_types(collection: Collection[Scalar]) -> set[ScalarType]:
    """Determine the set of scalar types of elements in the collection."""
    return {scalar_type_of(x) for x in collection}


def collection_promotion_type(collection: Collection[Scalar]) -> ScalarType:
    """Determine the common type to which all elements in the collection can be promoted."""
    return scalar_promotion_type(collection_types(collection))


def promote_vector_to(vector: Sequence[Scalar], target_type: ScalarType) -> list[Scalar]:
    """Promote a vector of scalars to the target type."""
    return [promote_scalar_to(v, target_type) for v in vector]


def promote_vector(vector: Sequence[Scalar]) -> tuple[ScalarType, list[Scalar]]:
    """
    Promote a vector of scalars to the common promotion type.
    :returns: the promotion type and the promoted vector
    """
    target_type = collection_promotion_type(vector)
    vector = promote_vector_to(vector, target_type)
    return target_type, vector
