"""Explicit in-memory representation of a umbfile."""

from dataclasses import dataclass, field, fields

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

    #: group -> name -> applies_to -> values
    annotations: dict[str, dict[str, dict[str, list]]] | None = None
    #: applies_to -> valuations
    valuations: dict[str, list] | None = None
    #: for each entity (index.observations_apply_to), an observation index
    entity_to_observation: list[int] | None = None

    def validate(self):
        self.index.validate()

    def __str__(self) -> str:
        s = f"{self.__class__.__name__}:\n"
        indent_str = "  "
        for f in fields(self):
            value_str = f"{getattr(self, f.name)!r}\n"
            if f.name == "annotations" and self.annotations is not None:
                value_str = "\n"
                for group, name_to_applies_to in self.annotations.items():
                    value_str += f"{indent_str * 2}{group}:\n"
                    for name, applies_to_to_values in name_to_applies_to.items():
                        value_str += f"{indent_str * 3}{name}:\n"
                        for applies_to, values in applies_to_to_values.items():
                            value_str += f"{indent_str * 4}{applies_to}: {values}\n"
            elif f.name == "valuations" and self.valuations is not None:
                value_str = "\n"
                for applies_to, valuations in self.valuations.items():
                    value_str += f"{indent_str * 2}{applies_to}: {valuations}\n"
            s += f"  {f.name}: {value_str}"
        return s
