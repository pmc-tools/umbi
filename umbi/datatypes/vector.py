"""
Auxiliary vector operations.
"""

from dataclasses import dataclass

from .scalar import ScalarType, Scalar, common_scalar_type, scalar_type_of, promote_scalar_to
from .sized_type import SizedType, BOOL1, UINT64

from collections.abc import Iterable

# TODO CSR vector as a dedicated class
# TODO add vector of ranges (for CSR?)


@dataclass
class VectorType:
    type: SizedType


"""Alias for a vector of booleans."""
BIT_VECTOR = VectorType(BOOL1)

"""Alias for a CSR vector type."""
CSR_VECTOR = VectorType(UINT64)


def assert_is_list(vector: object):
    if not isinstance(vector, list):
        raise TypeError(f"expected a list/vector, got {type(vector)}")


def is_vector_ranges(ranges: list[tuple[int, int]]) -> bool:
    """Check if a vector is a list of ranges."""
    if len(ranges) == 0:
        return False

    def is_interval(x: tuple[int, int]) -> bool:
        return isinstance(x, tuple) and len(x) == 2 and all(isinstance(y, int) for y in x) and x[0] <= x[1]

    if not all(is_interval(interval) for interval in ranges):
        return False
    for i in range(len(ranges) - 1):
        if ranges[i][1] != ranges[i + 1][0]:
            return False
    return True


def is_vector_csr(vector: list[int]) -> bool:
    """Check if a vector is a CSR row start index vector."""
    if len(vector) < 2:
        return False
    if not all(isinstance(x, int) for x in vector):
        return False
    if vector[0] != 0:
        return False
    if not all(vector[i] <= vector[i + 1] for i in range(len(vector) - 1)):
        return False
    return True


def csr_to_ranges(csr: list[int]) -> list[tuple[int, int]]:
    """Convert row start indices to ranges."""
    assert is_vector_csr(csr), "input is not a valid CSR vector"
    ranges = [(csr[i], csr[i + 1]) for i in range(len(csr) - 1)]
    return ranges


def ranges_to_csr(ranges: list[tuple[int, int]]) -> list[int]:
    """Convert ranges to CSR row start indices."""
    assert is_vector_ranges(ranges), "input is not a valid ranges vector"
    csr = [interval[0] for interval in ranges]
    csr.append(ranges[-1][-1])
    return csr


def collection_element_types(collection: Iterable[Scalar]) -> set[ScalarType]:
    """Determine the set of common types of elements in the collection."""
    return set([scalar_type_of(x) for x in collection])


def collection_element_type(collection: Iterable[Scalar]) -> ScalarType:
    """Determine the common type of elements in the collection. Raises an error if multiple types are found."""
    types = collection_element_types(collection)
    if len(types) != 1:
        raise ValueError(f"collection has multiple element types: {types}")
    return types.pop()


def common_collection_element_type(collection: Iterable[Scalar]) -> ScalarType:
    """Determine the common type to which all elements in the collection can be promoted."""
    return common_scalar_type(collection_element_types(collection))


def promote_vector_to(vector: list[Scalar], target_type: ScalarType) -> list[Scalar]:
    """Promote a vector of values to the target type."""
    return [promote_scalar_to(v, target_type) for v in vector]
