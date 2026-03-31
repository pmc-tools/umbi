from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

from .base_mixin import BaseMixin
from .entity_space import Observable


class TimeType(str, Enum):
    """Time types for transition systems."""

    DISCRETE = "discrete"
    STOCHASTIC = "stochastic"
    URGENT_STOCHASTIC = "urgent-stochastic"


class TimeTypeObservable(Observable):
    #: Time type of the ATS.
    _time: TimeType = TimeType.DISCRETE

    @property
    def time(self) -> TimeType:
        return self._time

    @time.setter
    def time(self, time: TimeType) -> None:
        if time == self._time:
            return
        self._time = time
        self._notify_changed(time)

    def __eq__(self, other: object) -> bool:
        """Compare time types by their value.
        Ignores _observer_callback (infrastructure)."""
        if not isinstance(other, TimeTypeObservable):
            return False
        # _observer_callback is infrastructure, doesn't affect equality
        return self._time == other._time


class ObservesTimeType(ABC):
    @property
    @abstractmethod
    def _observable_time(self) -> TimeTypeObservable: ...


@dataclass
class TimeTypeMixin(BaseMixin):
    _time_type: TimeTypeObservable = field(default_factory=TimeTypeObservable)

    @property
    def _observable_time(self) -> TimeTypeObservable:
        return self._time_type

    @property
    def time(self) -> TimeType:
        return self._time_type.time

    @time.setter
    def time(self, time: TimeType) -> None:
        self._time_type.time = time
