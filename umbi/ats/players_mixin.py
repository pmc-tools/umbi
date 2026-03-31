import logging
from collections.abc import Sequence
from dataclasses import dataclass, field

from .entity_space import EntityMapping, OptionalMappingManager
from .entity_space_mixins import HasPlayerSpace, HasStateSpace

logger = logging.getLogger(__name__)


@dataclass
class PlayerToNameMixin(HasPlayerSpace):
    #: Player-to-name mapping. Can be set only if num_players >= 1.
    _player_to_name_manager: OptionalMappingManager[str] = field(init=False)

    def __post_init__(self):
        self._player_to_name_manager = OptionalMappingManager(
            name="player_to_name",
            domain=self._player_space,
            can_have_mapping=lambda: self._can_have_player_to_name(),
            must_have_mapping=lambda: self._must_have_player_to_name(),
        )
        self._player_space._subscribe(self, lambda *args: self._player_to_name_manager.auto_manage())
        super().__post_init__()

    def _can_have_player_to_name(self, *args) -> bool:
        return self._player_space.has_entities

    def _must_have_player_to_name(self, *args) -> bool:
        return False  # player_to_name is always optional

    def add_player_to_name(self):
        self._player_to_name_manager.create_mapping()

    def remove_player_to_name(self):
        self._player_to_name_manager.remove_mapping()

    @property
    def has_player_to_name(self) -> bool:
        return self._player_to_name_manager.has_mapping

    @property
    def player_to_name(self) -> EntityMapping[str]:
        return self._player_to_name_manager.mapping

    @player_to_name.setter
    def player_to_name(self, values: Sequence[str] | None) -> None:
        self._player_to_name_manager.mapping = values

    def validate(self):
        self._player_to_name_manager.validate()
        super().validate()


@dataclass
class StateToPlayerMixin(HasPlayerSpace, HasStateSpace):
    #: State-to-player mapping. Set iff num_players >= 1.
    _state_to_player_manager: OptionalMappingManager[int] = field(init=False)

    def __post_init__(self):
        self._state_to_player_manager = OptionalMappingManager[int](
            name="state_to_player",
            domain=self._state_space,
            codomain=self._player_space,
            default_factory=lambda: 0,
            can_have_mapping=self._can_have_state_to_player,
            must_have_mapping=self._must_have_state_to_player,
        )
        self._player_space._subscribe(self, lambda *args: self._state_to_player_manager.auto_manage())
        super().__post_init__()

    def _can_have_state_to_player(self) -> bool:
        return self._player_space.has_entities

    def _must_have_state_to_player(self) -> bool:
        return self._can_have_state_to_player()

    @property
    def has_state_to_player(self) -> bool:
        return self._state_to_player_manager.has_mapping

    @property
    def state_to_player(self) -> EntityMapping[int]:
        return self._state_to_player_manager.mapping

    @state_to_player.setter
    def state_to_player(self, values: Sequence[int]) -> None:
        self._state_to_player_manager.mapping = values

    def validate(self) -> None:
        self._state_to_player_manager.validate()
        super().validate()


@dataclass
class PlayersMixin(
    PlayerToNameMixin,
    StateToPlayerMixin,
):
    def __post_init__(self):
        super().__post_init__()
