import logging
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from umbi.datatypes import Numeric

from .entity_space import EntityMapping, MappingManager, OptionalMappingManager
from .entity_space_mixins import HasStateSpace
from .time_type import ObservesTimeType, TimeType

logger = logging.getLogger(__name__)


@dataclass
class StateIsInitialMixin(HasStateSpace):
    #: state-to-whether-initial mapping
    _state_is_initial_manager: MappingManager[bool] = field(init=False)

    def __post_init__(self):
        self._state_is_initial_manager = MappingManager[bool](
            name="state_is_initial",
            domain=self._state_space,
            # default_factory=lambda: False
        )
        super().__post_init__()

    @property
    def state_is_initial(self) -> EntityMapping[bool]:
        return self._state_is_initial_manager.mapping

    @state_is_initial.setter
    def state_is_initial(self, state_is_initial: Sequence[bool]):
        self._state_is_initial_manager.mapping._set_values(state_is_initial)

    @property
    def initial_states(self) -> Sequence[int]:
        return self._state_is_initial_manager.indices

    @initial_states.setter
    def initial_states(self, initial_states: Iterable[int]):
        self._state_is_initial_manager.indices = initial_states

    @property
    def num_initial_states(self) -> int:
        return self._state_is_initial_manager.num_indices

    def validate(self) -> None:
        self._state_is_initial_manager.validate()
        super().validate()


@dataclass
class StateToExitRateMixin(HasStateSpace, ObservesTimeType):
    #: manager for state-to-exit-rate mapping
    _state_to_exit_rate_manager: OptionalMappingManager[Numeric] = field(init=False)

    def __post_init__(self):
        self._state_to_exit_rate_manager = OptionalMappingManager(
            name="state_to_exit_rate",
            domain=self._state_space,
            can_have_mapping=self._can_have_state_to_exit_rate,
            must_have_mapping=self._must_have_state_to_exit_rate,
        )
        self._observable_time._subscribe(self, callback=lambda *args: self._state_to_exit_rate_manager.auto_manage())
        super().__post_init__()

    def _can_have_state_to_exit_rate(self) -> bool:
        return self._observable_time.time != TimeType.DISCRETE

    def _must_have_state_to_exit_rate(self) -> bool:
        return self._can_have_state_to_exit_rate()

    @property
    def has_state_to_exit_rate(self) -> bool:
        return self._state_to_exit_rate_manager.has_mapping

    @property
    def state_to_exit_rate(self) -> EntityMapping[Numeric]:
        return self._state_to_exit_rate_manager.mapping

    @state_to_exit_rate.setter
    def state_to_exit_rate(self, values: Sequence[Numeric]) -> None:
        self._state_to_exit_rate_manager.mapping = values

    def validate(self) -> None:
        self._state_to_exit_rate_manager.validate()
        super().validate()
        # TODO validate non-negative exit rates
        # if exit_rate < 0:
        #     raise ValueError(f"Invalid exit rate {exit_rate} for state {s}, must be >= 0.")


@dataclass
class StateIsMarkovianMixin(HasStateSpace, ObservesTimeType):
    #: manager for state-to-whether-markovian mapping
    _state_is_markovian_manager: OptionalMappingManager[bool] = field(init=False)

    def __post_init__(self):
        self._state_is_markovian_manager = OptionalMappingManager[bool](
            name="state_is_markovian",
            domain=self._state_space,
            can_have_mapping=self._can_have_state_is_markovian,
            must_have_mapping=self._must_have_state_is_markovian,
        )
        self._observable_time._subscribe(self, lambda *args: self._state_is_markovian_manager.auto_manage())
        super().__post_init__()

    def _can_have_state_is_markovian(self) -> bool:
        return self._observable_time.time == TimeType.URGENT_STOCHASTIC

    def _must_have_state_is_markovian(self) -> bool:
        return self._can_have_state_is_markovian()

    @property
    def has_state_is_markovian(self) -> bool:
        return self._state_is_markovian_manager.has_mapping

    @property
    def state_is_markovian(self) -> EntityMapping[bool]:
        return self._state_is_markovian_manager.mapping

    @state_is_markovian.setter
    def state_is_markovian(self, values: Sequence[bool]) -> None:
        self._state_is_markovian_manager.mapping = values

    @property
    def markovian_states(self) -> Sequence[int]:
        return self._state_is_markovian_manager.indices

    @markovian_states.setter
    def markovian_states(self, markovian_states: Iterable[int]):
        self._state_is_markovian_manager.indices = markovian_states

    @property
    def num_markovian_states(self) -> int:
        return self._state_is_markovian_manager.num_indices

    def validate(self) -> None:
        self._state_is_markovian_manager.validate()
        super().validate()


@dataclass
class StatesMixin(
    StateIsInitialMixin,
    StateToExitRateMixin,
    StateIsMarkovianMixin,
):
    def __post_init__(self):
        super().__post_init__()
