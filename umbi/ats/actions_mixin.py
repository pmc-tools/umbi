import logging
from collections.abc import Sequence
from dataclasses import dataclass, field

from .choices_mixin import HasBranchSpace, HasChoiceSpace
from .entity_space import EntityMapping, OptionalMappingManager
from .entity_space_mixins import HasBranchActionSpace, HasChoiceActionSpace

logger = logging.getLogger(__name__)


@dataclass
class ChoiceToChoiceActionMixin(HasChoiceSpace, HasChoiceActionSpace):
    #: Choice-to-choice-action mapping manager.
    _choice_to_choice_action_manager: OptionalMappingManager[int] = field(init=False)

    def __post_init__(self):
        self._choice_to_choice_action_manager = OptionalMappingManager[int](
            name="choice_to_choice_action",
            domain=self._choice_space,
            can_have_mapping=lambda: self._can_have_choice_to_choice_action(),
            must_have_mapping=lambda: self._must_have_choice_to_choice_action(),
        )
        self._choice_action_space._subscribe(self, lambda *args: self._choice_to_choice_action_manager.auto_manage())
        super().__post_init__()

    def _can_have_choice_to_choice_action(self) -> bool:
        return self._choice_action_space.has_entities

    def _must_have_choice_to_choice_action(self) -> bool:
        return self._can_have_choice_to_choice_action()

    @property
    def has_choice_to_choice_action(self) -> bool:
        return self._choice_to_choice_action_manager.has_mapping

    @property
    def choice_to_choice_action(self) -> EntityMapping[int]:
        return self._choice_to_choice_action_manager.mapping

    @choice_to_choice_action.setter
    def choice_to_choice_action(self, values: Sequence[int]) -> None:
        self._choice_to_choice_action_manager.mapping = values

    def validate(self):
        self._choice_to_choice_action_manager.validate()
        super().validate()


@dataclass
class ChoiceActionToNameMixin(HasChoiceActionSpace):
    #: Choice-to-choice-action mapping manager.
    _choice_action_to_name_manager: OptionalMappingManager[str] = field(init=False)

    def __post_init__(self):
        self._choice_action_to_name_manager = OptionalMappingManager[str](
            name="choice_action_to_name",
            domain=self._choice_action_space,
            can_have_mapping=lambda: self._can_have_choice_action_to_name(),
            must_have_mapping=lambda: self._must_have_choice_action_to_name(),
        )
        self._choice_action_space._subscribe(self, lambda *args: self._choice_action_to_name_manager.auto_manage())
        super().__post_init__()

    def _can_have_choice_action_to_name(self) -> bool:
        return self._choice_action_space.has_entities

    def _must_have_choice_action_to_name(self) -> bool:
        return False  # choice_action_to_name is always optional

    def new_choice_action_to_name(self):
        self._choice_action_to_name_manager.create_mapping()

    def remove_choice_action_to_name(self):
        self._choice_action_to_name_manager.remove_mapping()

    @property
    def has_choice_action_to_name(self) -> bool:
        return self._choice_action_to_name_manager.has_mapping

    @property
    def choice_action_to_name(self) -> EntityMapping[str]:
        return self._choice_action_to_name_manager.mapping

    @choice_action_to_name.setter
    def choice_action_to_name(self, values: Sequence[str] | None) -> None:
        self._choice_action_to_name_manager.mapping = values

    def validate(self):
        self._choice_action_to_name_manager.validate()
        super().validate()


@dataclass
class BranchToBranchActionMixin(HasBranchSpace, HasBranchActionSpace):
    #: Branch-to-branch-action mapping manager.
    _branch_to_branch_action_manager: OptionalMappingManager[int] = field(init=False)

    def __post_init__(self):
        self._branch_to_branch_action_manager = OptionalMappingManager[int](
            name="branch_to_branch_action",
            domain=self._branch_space,
            can_have_mapping=lambda *args: self._can_have_branch_to_branch_action(),
            must_have_mapping=lambda *args: self._must_have_branch_to_branch_action(),
        )
        self._branch_action_space._subscribe(self, lambda *args: self._branch_to_branch_action_manager.auto_manage())
        super().__post_init__()

    def _can_have_branch_to_branch_action(self) -> bool:
        return self._branch_action_space.has_entities

    def _must_have_branch_to_branch_action(self) -> bool:
        return self._can_have_branch_to_branch_action()

    @property
    def has_branch_to_branch_action(self) -> bool:
        return self._branch_to_branch_action_manager.has_mapping

    @property
    def branch_to_branch_action(self) -> EntityMapping[int]:
        return self._branch_to_branch_action_manager.mapping

    @branch_to_branch_action.setter
    def branch_to_branch_action(self, values: Sequence[int]) -> None:
        self._branch_to_branch_action_manager.mapping = values

    def validate(self):
        self._branch_to_branch_action_manager.validate()
        super().validate()


@dataclass
class BranchActionToNameMixin(HasBranchActionSpace):
    #: Branch-to-branch-action mapping manager.
    _branch_action_to_name_manager: OptionalMappingManager[str] = field(init=False)

    def __post_init__(self):
        self._branch_action_to_name_manager = OptionalMappingManager[str](
            name="branch_action_to_name",
            domain=self._branch_action_space,
            can_have_mapping=lambda *args: self._can_have_branch_action_to_name(),
            must_have_mapping=lambda *args: self._must_have_branch_action_to_name(),
        )
        self._branch_action_space._subscribe(self, lambda *args: self._branch_action_to_name_manager.auto_manage())
        super().__post_init__()

    def _can_have_branch_action_to_name(self) -> bool:
        return self._branch_action_space.has_entities

    def _must_have_branch_action_to_name(self) -> bool:
        return False  # branch_action_to_name is always optional

    def add_branch_action_to_name(self):
        self._branch_action_to_name_manager.create_mapping()

    def remove_branch_action_to_name(self):
        self._branch_action_to_name_manager.remove_mapping()

    @property
    def has_branch_action_to_name(self) -> bool:
        return self._branch_action_to_name_manager.has_mapping

    @property
    def branch_action_to_name(self) -> EntityMapping[str]:
        return self._branch_action_to_name_manager.mapping

    @branch_action_to_name.setter
    def branch_action_to_name(self, values: Sequence[str] | None) -> None:
        self._branch_action_to_name_manager.mapping = values

    def validate(self):
        self._branch_action_to_name_manager.validate()
        super().validate()


class ActionsMixin(
    ChoiceToChoiceActionMixin,
    ChoiceActionToNameMixin,
    BranchToBranchActionMixin,
    BranchActionToNameMixin,
):
    def __post_init__(self):
        super().__post_init__()
