"""
Utilities for reading and writing umbfiles.
"""

import pathlib
from enum import Enum
import logging
from dataclasses import dataclass, field

import umbi.binary
import umbi.datatypes
from umbi.datatypes import (
    Numeric,
    AtomicType,
    SizedType,
    BOOL1,
    UINT32,
    UINT64,
)

from umbi.index import Annotation, UmbIndex, ValuationDescription
from .tar_coders import TarDecoder, TarEncoder


logger = logging.getLogger(__name__)


class UmbFile(Enum):
    """Enum for common files in a umbfile."""

    INDEX = "index.json"
    STATE_IS_INITIAL = "state-is-initial.bin"
    STATE_TO_CHOICES = "state-to-choices.bin"
    STATE_TO_PLAYER = "state-to-player.bin"
    STATE_IS_MARKOVIAN = "state-is-markovian.bin"
    STATE_TO_EXIT_RATE = "state-to-exit-rate.bin"
    CHOICE_TO_BRANCHES = "choice-to-branches.bin"
    BRANCH_TO_TARGET = "branch-to-target.bin"
    BRANCH_TO_PROBABILITY = "branch-to-probability.bin"


@dataclass
class ExplicitUmb:
    """Class for an explicit representation of a umbfile. The goal of this class is to have all the data is stored in python lists, rather than binary formats."""

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
    entity_to_observation: list[int] | None = None

    def validate(self):
        self.index.validate()


class UmbReader(TarDecoder):
    def __init__(self, tarpath: str | pathlib.Path, strict_mode: bool = False):
        """
        :param tarpath: path to the umbfile
        :param strict_mode: in the strict mode, unknown files will raise an error
        """
        super().__init__(tarpath)
        # to keep track of which files were read
        self.strict_mode = strict_mode
        self.filename_read = {filename: False for filename in self.filenames}
        filenames_str = "\n".join(self.filenames)
        logger.debug(f"found the following files:\n{filenames_str}")

    def list_unread_files(self):
        """Print warning about unread files from the tarfile, if such exist."""
        unread_files = [f for f, read in self.filename_read.items() if not read]
        for f in unread_files:
            logger.warning(f"umbfile contains unrecognized file: {f}")
        if self.strict_mode and len(unread_files) > 0:
            raise ValueError(f"unrecognized files in umbfile: {unread_files}")

    def read(self, filename: str, required: bool = False) -> bytes | None:
        """Read raw bytes from a specific file in the tarball. Mark the file as read."""
        if filename in self.filenames:
            self.filename_read[filename] = True
        return super().read(filename, required)

    def read_index_file(self, umb: ExplicitUmb):
        json_bytes = self.read(UmbFile.INDEX.value, required=True)
        json_obj = umbi.datatypes.string_to_json(
            umbi.binary.bytes_to_value(json_bytes, umbi.datatypes.AtomicType.STRING)
        )
        # pretty_str = umbi.datatypes.json_to_string(json_obj)
        # logger.debug(f"loaded the following index file:\n{pretty_str}")
        idx = UmbIndex.from_json(json_obj)
        idx.validate()
        umb.index = idx

    def read_state_files(self, umb: ExplicitUmb):
        """Read state-related files."""
        ts = umb.index.transition_system

        if ts.num_initial_states == 0:
            umb.state_is_initial = [False] * ts.num_states
        else:
            umb.state_is_initial = self.read_bitvector(UmbFile.STATE_IS_INITIAL.value, ts.num_states)

        umb.state_to_choices = self.read_vector(UmbFile.STATE_TO_CHOICES.value, UINT64, required=False)
        if ts.num_players > 0:
            umb.state_to_player = self.read_vector(UmbFile.STATE_TO_PLAYER.value, UINT32, required=False)

        if ts.time == "discrete":
            # ignore the file, all states are probabilistic
            umb.state_is_markovian = [False] * ts.num_states
        else:
            if UmbFile.STATE_IS_MARKOVIAN.value in self.filenames:
                umb.state_is_markovian = self.read_bitvector(UmbFile.STATE_IS_MARKOVIAN.value, ts.num_states)
            else:
                default = ts.time == "stochastic"
                umb.state_is_markovian = [default] * ts.num_states

        if ts.time == "stochastic" and ts.exit_rate_type is not None:
            if UmbFile.STATE_TO_EXIT_RATE.value in self.filenames:
                umb.state_to_exit_rate = self.read_vector(
                    UmbFile.STATE_TO_EXIT_RATE.value, ts.exit_rate_type, required=True
                )

    def read_actions(self, umb: ExplicitUmb, applies_to: str, num_items: int):
        """
        Read action files for a specific action type (choices or branches).
        :param umb: ExplicitUmb object to populate
        :param applies_to: "choices" or "branches"
        :param num_items: number of items (choices or branches)
        """
        path = f"actions/{applies_to}"
        filename = f"{path}/values.bin"

        if filename not in self.filenames:
            # default: everything maps to action 0
            item_to_actions = [0] * num_items
        else:
            item_to_actions = self.read_vector(filename, UINT32)

        if applies_to == "choices":
            umb.choice_to_choice_action = item_to_actions
        else:  # branches
            umb.branch_to_branch_action = item_to_actions

        filename_csr = f"{path}/string-mapping.bin"
        if filename_csr in self.filenames:
            action_to_string = self.read_strings(f"{path}/strings.bin", required=True, filename_csr=filename_csr)
            if applies_to == "choices":
                umb.choice_action_to_string = action_to_string
            else:  # branches
                umb.branch_action_to_string = action_to_string

    def read_transition_files(self, umb: ExplicitUmb):
        """Read transition-related files."""
        umb.choice_to_branches = self.read_vector(UmbFile.CHOICE_TO_BRANCHES.value, UINT64, required=False)
        umb.branch_to_target = self.read_vector(UmbFile.BRANCH_TO_TARGET.value, UINT64, required=False)
        ts = umb.index.transition_system

        if ts.branch_probability_type is not None:
            umb.branch_to_probability = self.read_vector(
                UmbFile.BRANCH_TO_PROBABILITY.value, ts.branch_probability_type, required=True
            )

        if ts.num_choice_actions > 0:
            self.read_actions(umb, "choices", ts.num_choices)

        if ts.num_branch_actions > 0:
            self.read_actions(umb, "branches", ts.num_branches)

    def read_annotation_files(self, umb: ExplicitUmb):
        if umb.index.annotations is None:
            return
        umb.annotations = dict()
        for group, annotation_map in umb.index.annotations.items():
            umb.annotations[group] = dict()
            for name, annotation in annotation_map.items():
                self.read_annotation(umb, group, name, annotation)

    def read_annotation(self, umb: ExplicitUmb, group: str, name: str, annotation: Annotation):
        """
        Read annotation files for a single annotation.
        :param group: annotation group, e.g. "rewards", "aps", or custom group
        :param name: annotation name
        :param annotation: annotation info (Annotation)
        :return: dict mapping applies_to -> values
        """
        ts = umb.index.transition_system
        assert annotation.type is not None, "annotation.type must be specified"
        assert annotation.applies_to is not None and len(annotation.applies_to) > 0, (
            "annotation.applies_to must be a non-empty list"
        )
        assert umb.annotations is not None, "umb.annotations must be specified"
        assert umb.annotations.get(group) is not None, f"missing annotation group {group} in umb.annotations"
        umb.annotations[group][name] = dict()
        if annotation.probability_type is not None:
            raise NotImplementedError("reading stochastic annotations is not implemented")
        for applies_to in annotation.applies_to:
            path = f"annotations/{group}/{name}/{applies_to}"
            if annotation.type.type != AtomicType.STRING:
                vector = self.read_vector(
                    f"{path}/values.bin",
                    annotation.type,
                    required=True,
                )
                assert vector is not None, "expected non-None vector"
                if annotation.type == BOOL1:
                    num_entries = {
                        "states": ts.num_states,
                        "choices": ts.num_choices,
                        "branches": ts.num_branches,
                    }[applies_to]
                    vector = self.truncate_bitvector(vector, num_entries=num_entries)

            else:
                vector = self.read_strings(
                    f"{path}/strings.bin",
                    required=True,
                    filename_csr=f"{path}/string-mapping.bin",
                )
            assert isinstance(vector, list), "expected a list"
            umb.annotations[group][name][applies_to] = vector

    def read_valuation_files(self, umb: ExplicitUmb):
        """Read valuation-related files."""
        if umb.index.valuations is None:
            return
        umb.valuations = dict()
        for applies_to, valuation_desc in umb.index.valuations.items():
            self.read_valuation_description(umb, applies_to, valuation_desc)

    def read_valuation_description(
        self,
        umb: ExplicitUmb,
        applies_to: str,
        valuation_desc: ValuationDescription,
    ):
        ts = umb.index.transition_system
        num_entries = {
            "states": ts.num_states,
            "choices": ts.num_choices,
            "branches": ts.num_branches,
            "observations": ts.num_observations,
            "players": ts.num_players,
        }[applies_to]
        # valuation_desc.unique is ignored
        if valuation_desc.num_strings is not None:
            raise NotImplementedError("reading string valuations is not implemented")
        if len(valuation_desc.classes) != 1:
            raise NotImplementedError("reading multiple valuation classes is not implemented")
        struct_type = valuation_desc.classes[0]
        assert not struct_type.contains_strings, "reading valuations with strings is not implemented"
        bytes = self.read(f"valuations/{applies_to}/valuations.bin", required=True)
        assert bytes is not None, "expected non-None bytes"
        expected_size = struct_type.size_bytes * num_entries
        assert len(bytes) == expected_size, (
            f"valuation data length does not match expected size for {applies_to}: got {len(bytes)}, expected {expected_size}"
        )
        valuations = umbi.binary.bytes_to_vector(bytes, struct_type)
        assert umb.valuations is not None, "umb.valuations must have been initialized"
        umb.valuations[applies_to] = valuations

    def read_observation_files(self, umb: ExplicitUmb):
        ts = umb.index.transition_system
        if ts.num_observations == 0:
            return
        if ts.observation_probability_type is not None:
            raise NotImplementedError("reading stochastic observations is not implemented")
        applies_to = ts.observations_apply_to
        umb.entity_to_observation = self.read_vector(f"observations/{applies_to}/values.bin", UINT64, required=True)

    def read_umb(self) -> ExplicitUmb:
        logger.info(f"loading umbfile from {self.tarpath} ...")
        umb = ExplicitUmb()
        self.read_index_file(umb)
        self.read_state_files(umb)
        self.read_transition_files(umb)
        self.read_annotation_files(umb)
        self.read_valuation_files(umb)
        self.read_observation_files(umb)
        self.list_unread_files()
        logger.info("umbfile successfully loaded")
        return umb


class UmbWriter(TarEncoder):
    def add_index_file(self, umb: ExplicitUmb):
        """Add the index file."""
        umb.index.validate()
        json_obj = umb.index.to_json()
        json_str = umbi.datatypes.json_to_string(json_obj)
        json_bytes = umbi.binary.value_to_bytes(json_str, SizedType(AtomicType.STRING))
        self.add(UmbFile.INDEX.value, json_bytes)

    def add_state_files(self, umb: ExplicitUmb):
        """Add state-related files."""
        self.add_bitvector(UmbFile.STATE_IS_INITIAL.value, umb.state_is_initial, required=True)
        self.add_vector(UmbFile.STATE_TO_CHOICES.value, UINT64, umb.state_to_choices)
        if umb.index.transition_system.num_players > 0:
            self.add_vector(UmbFile.STATE_TO_PLAYER.value, UINT32, umb.state_to_player)

        if umb.index.transition_system.time == "discrete":
            # skip writing the file, all states are probabilistic
            pass
        else:
            assert umb.state_is_markovian is not None, "state_is_markovian must be specified"
            self.add_bitvector(UmbFile.STATE_IS_MARKOVIAN.value, umb.state_is_markovian)
            if umb.index.transition_system.exit_rate_type is not None:
                self.add_vector(
                    UmbFile.STATE_TO_EXIT_RATE.value,
                    umb.index.transition_system.exit_rate_type,
                    umb.state_to_exit_rate,
                )

    def add_transition_files(self, umb: ExplicitUmb):
        """Add transition-related files."""
        self.add_vector(UmbFile.CHOICE_TO_BRANCHES.value, UINT64, umb.choice_to_branches)
        self.add_vector(UmbFile.BRANCH_TO_TARGET.value, UINT64, umb.branch_to_target)
        ts = umb.index.transition_system

        if ts.branch_probability_type is not None:
            self.add_vector(
                UmbFile.BRANCH_TO_PROBABILITY.value,
                ts.branch_probability_type,
                umb.branch_to_probability,
            )

        if ts.num_choice_actions > 0:
            self.add_actions(umb, "choices")

        if ts.num_branch_actions > 0:
            self.add_actions(umb, "branches")

    def add_actions(self, umb: ExplicitUmb, applies_to: str):
        """
        Add action files for a specific action type (choices or branches).
        :param umb: ExplicitUmb object to write from
        :param applies_to: "choices" or "branches"
        """
        path = f"actions/{applies_to}"

        if applies_to == "choices":
            item_to_actions = umb.choice_to_choice_action
            action_to_string = umb.choice_action_to_string
        else:  # branches
            item_to_actions = umb.branch_to_branch_action
            action_to_string = umb.branch_action_to_string

        if item_to_actions is not None:
            self.add_vector(f"{path}/values.bin", UINT32, item_to_actions)

        if action_to_string is not None:
            self.add_strings(f"{path}/strings.bin", action_to_string, f"{path}/string-mapping.bin")

    def add_annotation_files(self, umb: ExplicitUmb):
        """Add annotation files."""
        if umb.index.annotations is None:
            return
        assert umb.annotations is not None, "umb.annotations must be specified"
        for group, annotation_map in umb.index.annotations.items():
            assert group in umb.annotations, f"missing annotation group {group} in umb.annotations"
            for name, annotation in annotation_map.items():
                self.add_annotation(umb, group, name, annotation)

    def add_annotation(self, umb: ExplicitUmb, group: str, name: str, annotation: Annotation):
        """
        Add files for a single annotation.
        :param umb: ExplicitUmb object to write from
        :param group: annotation group, e.g. "rewards", "aps"
        :param name: annotation name
        :param annotation: annotation metadata
        """
        assert annotation.type is not None, "annotation.type must be specified"
        assert annotation.applies_to is not None and len(annotation.applies_to) > 0, (
            "annotation.applies_to must be a non-empty list"
        )
        assert umb.annotations is not None, "umb.annotations must be specified"
        assert umb.annotations.get(group) is not None, f"missing annotation group {group} in umb.annotations"
        assert umb.annotations[group].get(name) is not None, f"missing annotation {group}/{name} in umb.annotations"
        for applies_to in annotation.applies_to:
            path = f"annotations/{group}/{name}/{applies_to}"
            if annotation.type.type != AtomicType.STRING:
                values = umb.annotations[group][name][applies_to]
                self.add_vector(f"{path}/values.bin", annotation.type, values, required=True)
            else:
                values = umb.annotations[group][name][applies_to]
                self.add_strings(f"{path}/strings.bin", values, f"{path}/string-mapping.bin", required=True)

    def add_valuation_files(self, umb: ExplicitUmb):
        """Add valuation-related files."""
        if umb.index.valuations is None:
            return
        for applies_to, valuation_desc in umb.index.valuations.items():
            self.add_valuation_description(umb, applies_to, valuation_desc)

    def add_valuation_description(
        self,
        umb: ExplicitUmb,
        applies_to: str,
        valuation_desc: ValuationDescription,
    ):
        ts = umb.index.transition_system
        num_entries = {
            "states": ts.num_states,
            "choices": ts.num_choices,
            "branches": ts.num_branches,
            "observations": ts.num_observations,
            "players": ts.num_players,
        }[applies_to]
        # valuation_desc.unique is ignored
        if valuation_desc.num_strings is not None:
            raise NotImplementedError("writing string valuations is not implemented")
        if len(valuation_desc.classes) != 1:
            raise NotImplementedError("writing multiple valuation classes is not implemented")
        struct_type = valuation_desc.classes[0]
        assert not struct_type.contains_strings, "writing valuations with strings is not implemented"
        assert umb.valuations is not None, "umb.valuations must be specified"
        assert applies_to in umb.valuations, f"missing valuation data for {applies_to}"
        valuations = umb.valuations[applies_to]
        bytes = umbi.binary.vector_to_bytes(valuations, struct_type)
        assert len(bytes) == struct_type.size_bytes * num_entries, "valuation data length does not match expected size"
        self.add(f"valuations/{applies_to}/valuations.bin", bytes)

    def add_observation_files(self, umb: ExplicitUmb):
        """Add observation-related files."""
        ts = umb.index.transition_system
        if ts.num_observations == 0:
            return
        if ts.observation_probability_type is not None:
            raise NotImplementedError("writing stochastic observations is not implemented")
        applies_to = ts.observations_apply_to
        assert umb.entity_to_observation is not None, "umb.entity_to_observation must be specified"
        self.add_vector(f"observations/{applies_to}/values.bin", UINT64, umb.entity_to_observation, required=True)

    def write_umb(self, umb: ExplicitUmb, umbpath: str | pathlib.Path):
        logger.info(f"writing umbfile to {umbpath} ...")
        self.add_index_file(umb)
        self.add_state_files(umb)
        self.add_transition_files(umb)
        self.add_annotation_files(umb)
        self.add_valuation_files(umb)
        self.add_observation_files(umb)
        self.write(umbpath)
        logger.info("finished writing the umbfile")


def read_umb(umbpath: str | pathlib.Path) -> ExplicitUmb:
    """Read UMB from a umbfile."""
    return UmbReader(umbpath).read_umb()


def write_umb(umb: ExplicitUmb, umbpath: str | pathlib.Path):
    """Write UMB to a umbfile."""
    UmbWriter().write_umb(umb, umbpath)
