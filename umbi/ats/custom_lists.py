import logging
from typing import Iterable
from umbi.datatypes import (
    Scalar,
    ScalarType,
    collection_element_types,
    common_scalar_type,
)

logger = logging.getLogger(__name__)


class TypedIterable(Iterable[Scalar]):
    """An iterable that can infer additional type information about its elements."""

    @property
    def types(self) -> set[ScalarType]:
        """Collect the data types of the values in the mapping."""
        return collection_element_types(self)

    @property
    def type(self) -> ScalarType:
        """
        Infer the common data type of the values.
        :raise ValueError: if the iterable is empty
        :note: promotion rules: PrimitiveType.BOOL -> NumericType -> PrimitiveType.STRING
        """
        if len(self.types) == 0:
            raise ValueError("Cannot determine common type of an empty collection.")
        return common_scalar_type(self.types)


class Domain(set[Scalar], TypedIterable):
    """
    A set of values with additional information about the range. The collection can be freely modified, calling sort()
    caches the sorted domain.
    """

    # a sorted list of possible values
    _sorted_domain: list[Scalar] | None = None

    def invalidate(self):
        """Invalidate the cached domain information."""
        self._sorted_domain = None

    @property
    def sorted(self) -> bool:
        return self._sorted_domain is not None

    @property
    def sorted_domain(self) -> list[Scalar]:
        if self._sorted_domain is None:
            raise ValueError("the domain is not sorted")
        return self._sorted_domain

    @property
    def can_be_sorted(self) -> bool:
        try:
            sorted(self)  # type: ignore
            return True
        except TypeError:
            return False

    def sort(self):
        """Sorts the domain."""
        self._sorted_domain = None
        try:
            self._sorted_domain = sorted(self)  # type: ignore
        except TypeError:
            logger.warning("domain values cannot be sorted")

    @property
    def lower(self) -> Scalar:
        if self._sorted_domain is None:
            raise ValueError("the domain is not sorted")
        return self._sorted_domain[0]

    @property
    def upper(self) -> Scalar:
        if self._sorted_domain is None:
            raise ValueError("the domain is not sorted")
        return self._sorted_domain[-1]
