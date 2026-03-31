"""Reading and writing umbfiles into ExplicitUmb."""

import logging
import pathlib
from enum import Enum

import umbi.binary
import umbi.datatypes
import umbi.tar
from umbi.binary import UINT32, UINT64
from umbi.datatypes import PrimitiveType

from .explicit_umb import ExplicitUmb
from .index import (
    AnnotationDescription,
    UmbIndex,
    ValuationDescription,
    umbi_file_data,
)

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


class UmbDecoder(umbi.tar.TarCoder):
    """Converting tarfiles to ExplicitUmb."""

    #: to keep track of which files were read; reset upon calling decode() and modified upon calling read_file()
    filename_read: dict[str, bool] | None = None

    def __init__(self, umbpath: str | pathlib.Path | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if umbpath is not None:
            self.read(umbpath)

    def reset_read_tracking(self):
        """Reset the read tracking for all files in the tarfile."""
        self.filename_read = {filename: False for filename in self.filenames}

    # def read(self, tarpath: str | pathlib.Path) -> None:
    #     """Load tarfile contents from a tarball."""
    #     super().read(tarpath)
    #     self.reset_read_tracking()

    def read_file(self, filename: str, optional: bool = False) -> bytes | None:
        """Read raw bytes from a specific file in the tarball. Mark the file as read."""
        if self.filename_read is not None and self.has_file(filename):
            self.filename_read[filename] = True
        return super().read_file(filename, optional)

    def list_unread_files(self, strict: bool = False):
        """
        List unread files from the tarfile.

        :raises ValueError: if strict is True and there are any unread files
        """
        if self.filename_read is None:
            return
        unread_files = [f for f, read in self.filename_read.items() if not read]
        for f in unread_files:
            logger.warning(f"umbfile contains unread file: {f}")
        if len(unread_files) > 0 and strict:
            raise ValueError(f"unread files in umbfile: {unread_files}")

    def read_index_file(self, umb: ExplicitUmb):
        json_obj = self.read_json(UmbFile.INDEX.value, optional=False)
        pretty_str = umbi.datatypes.json_to_string(json_obj)
        logger.debug(f"loaded the following index file:\n{pretty_str}")
        idx = UmbIndex.from_json(json_obj)
        idx.validate()
        umb.index = idx

    def read_state_files(self, umb: ExplicitUmb):
        """Read state-related files."""
        ts = umb.index.transition_system

        if ts.num_initial_states == 0:
            umb.state_is_initial = [False] * ts.num_states
        else:
            bitvector = self.read_bitvector(UmbFile.STATE_IS_INITIAL.value, ts.num_states, optional=False)
            assert bitvector is not None
            umb.state_is_initial = bitvector

        umb.state_to_choices = self.read_vector(UmbFile.STATE_TO_CHOICES.value, UINT64, optional=True)
        if ts.num_players > 0:
            umb.state_to_player = self.read_vector(UmbFile.STATE_TO_PLAYER.value, UINT32, optional=True)

        if ts.time == "urgent-stochastic":
            if self.has_file(UmbFile.STATE_IS_MARKOVIAN.value):
                umb.state_is_markovian = self.read_bitvector(
                    UmbFile.STATE_IS_MARKOVIAN.value, ts.num_states, optional=False
                )
            else:
                umb.state_is_markovian = [False] * ts.num_states

        if ts.exit_rate_type is not None:
            umb.state_to_exit_rate = self.read_vector(
                UmbFile.STATE_TO_EXIT_RATE.value, ts.exit_rate_type, optional=True
            )

    def read_action_files(self, umb: ExplicitUmb, applies_to: str, num_items: int):
        """Read action files for a specific action type (choices or branches).

        :param umb: ExplicitUmb object to populate
        :param applies_to: "choices" or "branches"
        :param num_items: number of items (choices or branches)
        """
        path = f"actions/{applies_to}"
        filename = f"{path}/values.bin"

        if not self.has_file(filename):
            # default: everything maps to action 0
            item_to_actions = [0] * num_items
        else:
            item_to_actions = self.read_vector(filename, UINT32, optional=True)

        if applies_to == "choices":
            umb.choice_to_choice_action = item_to_actions
        else:  # branches
            umb.branch_to_branch_action = item_to_actions

        filename_csr = f"{path}/string-mapping.bin"
        if self.has_file(filename_csr):
            action_to_string = self.read_strings(f"{path}/strings.bin", optional=False, filename_csr=filename_csr)
            if applies_to == "choices":
                umb.choice_action_to_string = action_to_string
            else:  # branches
                umb.branch_action_to_string = action_to_string

    def read_transition_files(self, umb: ExplicitUmb):
        """Read transition-related files."""
        umb.choice_to_branches = self.read_vector(UmbFile.CHOICE_TO_BRANCHES.value, UINT64, optional=True)
        umb.branch_to_target = self.read_vector(UmbFile.BRANCH_TO_TARGET.value, UINT64, optional=True)
        ts = umb.index.transition_system

        if ts.branch_probability_type is not None:
            umb.branch_to_probability = self.read_vector(
                UmbFile.BRANCH_TO_PROBABILITY.value, ts.branch_probability_type, optional=False
            )

        if ts.num_choice_actions > 0:
            self.read_action_files(umb, "choices", ts.num_choices)

        if ts.num_branch_actions > 0:
            self.read_action_files(umb, "branches", ts.num_branches)

    def read_annotation_files(self, umb: ExplicitUmb):
        if umb.index.annotations is None:
            return
        umb.annotations = dict()
        for group, annotation_map in umb.index.annotations.items():
            umb.annotations[group] = dict()
            for name, annotation in annotation_map.items():
                self.read_annotation(umb, group, name, annotation)

    def read_annotation(
        self,
        umb: ExplicitUmb,
        group: str,
        name: str,
        annotation: AnnotationDescription,
    ):
        """Read annotation files for a single annotation.

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
            if annotation.type.type == PrimitiveType.STRING:
                vector = self.read_strings(
                    f"{path}/strings.bin",
                    optional=False,
                    filename_csr=f"{path}/string-mapping.bin",
                )
            elif annotation.type.type == PrimitiveType.BOOL:
                num_entries = {
                    "states": ts.num_states,
                    "choices": ts.num_choices,
                    "branches": ts.num_branches,
                }[applies_to]
                vector = self.read_bitvector(f"{path}/values.bin", num_entries=num_entries, optional=False)
            else:
                vector = self.read_vector(f"{path}/values.bin", annotation.type, optional=False)
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
        bytes = self.read_file(f"valuations/{applies_to}/valuations.bin", optional=False)
        assert bytes is not None, "expected non-None bytes"
        expected_size = struct_type.size_bytes * num_entries
        assert len(bytes) == expected_size, (
            f"valuation data length does not match expected size: got {len(bytes)}, expected #num_{applies_to}*(struct_size_bytes)={num_entries}*{struct_type.size_bytes} = {expected_size}"
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
        umb.entity_to_observation = self.read_vector(f"observations/{applies_to}/values.bin", UINT64, optional=False)

    def decode(self, strict: bool = False) -> ExplicitUmb:
        """Decode the tarfile contents into an ExplicitUmb object.

        :param strict: in the strict mode, error is raised if there are any unread files in the umbfile
        """
        umb = ExplicitUmb()
        self.reset_read_tracking()
        self.read_index_file(umb)
        self.read_state_files(umb)
        self.read_transition_files(umb)
        self.read_annotation_files(umb)
        self.read_valuation_files(umb)
        self.read_observation_files(umb)
        self.list_unread_files(strict=strict)
        return umb


class UmbEncoder(umbi.tar.TarCoder):
    def add_index_file(self, umb: ExplicitUmb):
        """Add the index file."""
        umb.index.validate()
        json_obj = umb.index.to_json()
        self.add_json(UmbFile.INDEX.value, json_obj, optional=False)

    def add_state_files(self, umb: ExplicitUmb):
        """Add state-related files."""
        self.add_bitvector(UmbFile.STATE_IS_INITIAL.value, umb.state_is_initial, optional=False)
        self.add_vector(UmbFile.STATE_TO_CHOICES.value, UINT64, umb.state_to_choices, optional=True)
        if umb.index.transition_system.num_players > 0:
            self.add_vector(UmbFile.STATE_TO_PLAYER.value, UINT32, umb.state_to_player, optional=True)

        if umb.index.transition_system.time == "urgent-stochastic":
            state_is_markovian = (
                umb.state_is_markovian
                if umb.state_is_markovian is not None
                else [True] * umb.index.transition_system.num_states
            )
            self.add_bitvector(UmbFile.STATE_IS_MARKOVIAN.value, state_is_markovian, optional=True)
        if umb.index.transition_system.time != "discrete":
            if umb.index.transition_system.exit_rate_type is not None:
                self.add_vector(
                    UmbFile.STATE_TO_EXIT_RATE.value,
                    umb.index.transition_system.exit_rate_type,
                    umb.state_to_exit_rate,
                    optional=True,
                )

    def add_transition_files(self, umb: ExplicitUmb):
        """Add transition-related files."""
        self.add_vector(UmbFile.CHOICE_TO_BRANCHES.value, UINT64, umb.choice_to_branches, optional=True)
        self.add_vector(UmbFile.BRANCH_TO_TARGET.value, UINT64, umb.branch_to_target, optional=True)
        ts = umb.index.transition_system

        if ts.branch_probability_type is not None:
            self.add_vector(
                UmbFile.BRANCH_TO_PROBABILITY.value,
                ts.branch_probability_type,
                umb.branch_to_probability,
            )

        if ts.num_choice_actions > 0:
            self.add_action_files("choices", umb.choice_to_choice_action, umb.choice_action_to_string)

        if ts.num_branch_actions > 0:
            self.add_action_files("branches", umb.branch_to_branch_action, umb.branch_action_to_string)

    def add_action_files(
        self, applies_to: str, item_to_actions: list | None = None, action_to_string: list[str] | None = None
    ):
        """Add action files for a specific action type (choices or branches).

        :param applies_to: "choices" or "branches"
        :param item_to_actions: list mapping each item (choice or branch) to an action index
        :param action_to_string: list mapping each action index to a string (e.g. action name), or None if no string mapping is provided
        """
        path = f"actions/{applies_to}"

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

    def add_annotation(
        self,
        umb: ExplicitUmb,
        group: str,
        name: str,
        annotation: AnnotationDescription,
    ):
        """Add files for a single annotation.

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
            values = umb.annotations[group][name][applies_to]
            if annotation.type.type == PrimitiveType.STRING:
                self.add_strings(f"{path}/strings.bin", values, f"{path}/string-mapping.bin", optional=False)
            elif annotation.type.type == PrimitiveType.BOOL:
                self.add_bitvector(f"{path}/values.bin", values, optional=False)
            else:
                self.add_vector(f"{path}/values.bin", annotation.type, values, optional=False)

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
        self.add_file(f"valuations/{applies_to}/valuations.bin", bytes)

    def add_observation_files(self, umb: ExplicitUmb):
        """Add observation-related files."""
        ts = umb.index.transition_system
        if ts.num_observations == 0:
            return
        if ts.observation_probability_type is not None:
            raise NotImplementedError("writing stochastic observations is not implemented")
        applies_to = ts.observations_apply_to
        assert umb.entity_to_observation is not None, "umb.entity_to_observation must be specified"
        self.add_vector(f"observations/{applies_to}/values.bin", UINT64, umb.entity_to_observation, optional=False)

    def encode(self, umb: ExplicitUmb, insert_umbi_metadata: bool = True):
        """Encode ExplicitUmb into tarfile contents."""
        original_file_data = None
        if insert_umbi_metadata:
            original_file_data = umb.index.file_data
            umb.index.file_data = umbi_file_data()
        try:
            self.clear()
            self.add_index_file(umb)
            self.add_state_files(umb)
            self.add_transition_files(umb)
            self.add_annotation_files(umb)
            self.add_valuation_files(umb)
            self.add_observation_files(umb)
        finally:
            if insert_umbi_metadata:
                umb.index.file_data = original_file_data


# API


def read(umbpath: str | pathlib.Path, strict: bool = False) -> ExplicitUmb:
    """Read ExplicitUmb from a umbfile.

    :param umbpath: path to the umbfile
    :param strict: in the strict mode, unread files will raise an error
    :return: ExplicitUmb object containing the data from the umbfile
    """
    logger.info(f"loading umbfile from {umbpath} ...")
    decoder = UmbDecoder(umbpath=umbpath)
    filenames_str = "\n".join(decoder.filenames)
    logger.debug(f"found the following files in the umbfile:\n{filenames_str}")
    umb = decoder.decode(strict=strict)
    logger.info(f"finished loading umbfile from {umbpath}")
    return umb


def write(umb: ExplicitUmb, umbpath: str | pathlib.Path, insert_umbi_metadata: bool = True) -> None:
    """Write ExplicitUmb to a umbfile.

    :param umb: ExplicitUmb object to write
    :param umbpath: path to the umbfile to write to
    :param insert_umbi_metadata: if True, insert umbi's file metadata instead; the input ExplicitUmb object will not be modified
    """
    logger.info(f"writing umbfile to {umbpath} ...")
    encoder = UmbEncoder()
    encoder.encode(umb, insert_umbi_metadata=insert_umbi_metadata)
    encoder.write(umbpath)
    logger.info(f"finished writing umbfile {umbpath}")
