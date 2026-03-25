"""Transition system schemas and classes."""

from dataclasses import dataclass
from typing import Literal, Type

from marshmallow import ValidationError, fields, validate, validates_schema

from umbi.binary import SizedType

from .json_schema import (
    FieldUint32,
    FieldUint64,
    JsonSchema,
    JsonSchemaResult,
)
from .type import SizedTypeSchema


class TransitionSystemSchema(JsonSchema):
    """Transition system schema."""

    time = fields.String(
        data_key="time",
        required=True,
        validate=validate.OneOf(["discrete", "stochastic", "urgent-stochastic"]),
    )
    num_players = FieldUint32(data_key="#players", required=True)
    num_states = FieldUint64(data_key="#states", required=True, validate=validate.Range(min=1))
    num_initial_states = FieldUint64(data_key="#initial-states", required=True)
    num_choices = FieldUint64(data_key="#choices", required=True)
    num_choice_actions = FieldUint32(data_key="#choice-actions", required=True)
    num_branches = FieldUint64(data_key="#branches", required=True)
    num_branch_actions = FieldUint32(data_key="#branch-actions", required=True)
    num_observations = FieldUint64(data_key="#observations", required=True)
    observations_apply_to = fields.String(
        data_key="observations-apply-to",
        required=False,
        validate=validate.OneOf(["states", "branches"]),
    )

    branch_probability_type = fields.Nested(SizedTypeSchema, data_key="branch-probability-type", required=False)
    exit_rate_type = fields.Nested(SizedTypeSchema, data_key="exit-rate-type", required=False)
    observation_probability_type = fields.Nested(
        SizedTypeSchema, data_key="observation-probability-type", required=False
    )
    player_to_name = fields.List(fields.String(), data_key="player-names", required=False)

    @validates_schema
    def validate_states(self, data, **kwargs):
        num_states = data.get("num_states")
        num_initial_states = data.get("num_initial_states")
        if num_initial_states > num_states:
            raise ValidationError(
                f"#states is {num_states}, but #initial-states is {num_initial_states}, which cannot exceed #states",
                field_name="num_initial_states",
            )

    @validates_schema
    def validate_branch_probability_type(self, data, **kwargs):
        num_branches = data.get("num_branches")
        branch_probability_type = data.get("branch_probability_type")
        if num_branches == 0 and branch_probability_type is not None:
            raise ValidationError(
                f"#branches is 0 but branch-probability-type is specified",
                field_name="branch_probability_type",
            )
        if branch_probability_type is not None:
            if not branch_probability_type.type.is_continuous:
                raise ValidationError(
                    f"branch-probability-type must be continuous numeric type, got {branch_probability_type}",
                    field_name="branch_probability_type",
                )

    @validates_schema
    def validate_exit_rate_type(self, data, **kwargs):
        time = data.get("time")
        exit_rate_type = data.get("exit_rate_type")
        if time in ["discrete"] and exit_rate_type is not None:
            raise ValidationError(
                f"time is {time} but exit-rate-type is specified",
                field_name="exit_rate_type",
            )
        if exit_rate_type is not None:
            if not exit_rate_type.type.is_continuous:
                raise ValidationError(
                    f"exit-rate-type must be continuous numeric type, got {exit_rate_type}",
                    field_name="exit_rate_type",
                )

    @validates_schema
    def validate_observations(self, data, **kwargs):
        num_observations = data.get("num_observations")
        if num_observations == 0:
            for field_name in ["observations_apply_to", "observation_probability_type"]:
                if data.get(field_name) is not None:
                    raise ValidationError(
                        f"#observations is 0 but {field_name} is specified",
                        field_name=field_name,
                    )
        if num_observations > 0:
            for field_name in ["observations_apply_to"]:
                if data.get(field_name) is None:
                    raise ValidationError(
                        f"#observations is {num_observations} but {field_name} is not specified",
                        field_name=field_name,
                    )

    @validates_schema
    def validate_observation_probability_type(self, data, **kwargs):
        observation_probability_type = data.get("observation_probability_type")
        if observation_probability_type is not None:
            if not observation_probability_type.type.is_continuous:
                raise ValidationError(
                    f"observation-probability-type must be continuous numeric type, got {observation_probability_type}",
                    field_name="observation_probability_type",
                )

    @validates_schema
    def validate_player_names(self, data, **kwargs):
        num_players = data.get("num_players")
        player_to_name = data.get("player_to_name")

        if num_players > 1 and player_to_name is None:
            raise ValidationError(
                "player-names must be specified when #players > 1",
                field_name="player_to_name",
            )

        if player_to_name is None:
            return

        if len(player_to_name) != num_players:
            raise ValidationError(
                f"player-names must have length #players ({num_players}), got {len(player_to_name)}",
                field_name="player_to_name",
            )

        if len(player_to_name) != len(set(player_to_name)):
            raise ValidationError(
                f"player-names must be unique, got {player_to_name}",
                field_name="player_to_name",
            )

    @classmethod
    def schema_class(cls) -> type:
        return TransitionSystem


@dataclass
class TransitionSystem(JsonSchemaResult):
    """Transition system data class.

    Describes the structure of a transition system.

    Common abbreviations:
    - LTS: discrete-time, 1-player, no branch probabilities
    - DTMC: discrete-time, 0-player
    - MDP: discrete-time, 1-player
    - CTMC: stochastic-time, 0-player
    - MA: urgent-stochastic-time, 1-player
    - CTMDP: stochastic-time, 1-player
    - POMDP: discrete-time, 1-player with observations
    - TG: discrete-time, n-player, no branch probabilities
    - TSG: discrete-time, n-player
    Add "I" in front of acronym to make probabilities=interval-probabilistic
    """

    #: time semantics: discrete, stochastic, or urgent-stochastic
    time: Literal["discrete", "stochastic", "urgent-stochastic"] = "discrete"
    #: number of players (0: DTMC/CTMC, 1: LTS/MDP/MA, more: TG/TSG)
    num_players: int = 0
    #: number of states
    num_states: int = 1
    #: number of initial states
    num_initial_states: int = 0
    #: number of choices
    num_choices: int = 0
    #: number of choice actions (not all have to be used)
    num_choice_actions: int = 0
    #: number of branches
    num_branches: int = 0
    #: number of branch actions (not all have to be used)
    num_branch_actions: int = 0
    #: number of observation indices (0 means no observations)
    num_observations: int = 0
    #: where observations apply to (must be present iff num_observations is non-zero)
    observations_apply_to: Literal["states", "branches"] | None = None

    # The types in branch-probability-type, exit-rate-type, and observation-probability-type must be continuous numeric
    # types, and must be of the default size (given explicitly as the value for size or implicitly by omitting size)
    # except for types "rational" and "rational-interval", for which the size must be
    # a positive multiple of 128 and 256, respectively

    #: branch probability type (must be present iff system has probabilities, e.g. DTMC, MDP)
    branch_probability_type: SizedType | None = None
    #: exit rate type (must be present iff system has exit rates, e.g. CTMC, MA)
    exit_rate_type: SizedType | None = None
    #: observation probability type (must be present iff system has observations and they are not deterministic)
    observation_probability_type: SizedType | None = None
    #: player names (must be of length #players if present; can be omitted if #players < 2; names must be unique)
    player_to_name: list[str] | None = None

    @classmethod
    def class_schema(cls) -> Type:
        return TransitionSystemSchema
