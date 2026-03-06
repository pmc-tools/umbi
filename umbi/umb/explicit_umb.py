"""Explicit in-memory representation of a umbfile."""

from dataclasses import dataclass, field

from umbi.datatypes import Numeric

from .index.umb_index import UmbIndex


@dataclass
class ExplicitUmb:
    """Explicit representation of a umbfile using Python collections."""

    index: UmbIndex = field(default_factory=UmbIndex)

    state_is_initial: list[bool] = field(default_factory=list)
    state_to_choices: list[int] | None = None
    state_to_player: list[int] | None = None

    state_is_markovian: list[bool] | None = None
    state_to_exit_rate: list[Numeric] | None = None

    choice_to_branches: list[int] | None = None
    branch_to_target: list[int] | None = None
    branch_to_probability: list[Numeric] | None = None

    choice_to_choice_action: list[int] | None = None
    choice_action_to_string: list[str] | None = None

    branch_to_branch_action: list[int] | None = None
    branch_action_to_string: list[str] | None = None

    annotations: dict[str, dict[str, dict[str, list]]] | None = None  # group -> name -> applies_to -> values
    valuations: dict[str, list] | None = None  # applies_to -> valuations
    entity_to_observation: list[int] | None = (
        None  # for each entity (index.observations_apply_to), an observation index
    )

    def validate(self):
        self.index.validate()
