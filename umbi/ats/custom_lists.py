import logging
from typing import Iterable
from umbi.datatypes import (
    ValueType,
    DataType,
    collection_element_types,
    common_datatype,
)

logger = logging.getLogger(__name__)


class TypedIterable(Iterable[ValueType]):
    """A list that can infer additional type information about its elements."""

    @property
    def types(self) -> set[DataType]:
        """Collect the data types of the values in the mapping."""
        return collection_element_types(self)

    @property
    def type(self) -> DataType:
        """
        Infer the common data type of the values.
        :raise ValueError: if the list is empty
        :note: promotion rules: AtomicType.BOOL -> NumericType -> AtomicType.STRING
        """
        if len(self.types) == 0:
            raise ValueError("Cannot determine common type of an empty collection.")
        return common_datatype(self.types)


class Domain(set[ValueType], TypedIterable):
    """
    A set of values with additional information about the range. The collection can be freely modified, calling sync()
    caches the sorted domain.
    """

    # a sorted list of possible values
    _sorted_domain: list[ValueType] | None = None

    def invalidate(self):
        """Invalidate the cached domain information."""
        self._sorted_domain = None

    @property
    def sorted(self) -> bool:
        return self._sorted_domain is not None

    @property
    def sorted_domain(self) -> list[ValueType]:
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
            logger.warning("Domain values cannot be sorted.")

    @property
    def lower(self) -> ValueType:
        if self._sorted_domain is None:
            raise ValueError("the domain is not sorted")
        return self._sorted_domain[0]

    @property
    def upper(self) -> ValueType:
        if self._sorted_domain is None:
            raise ValueError("the domain is not sorted")
        return self._sorted_domain[-1]
