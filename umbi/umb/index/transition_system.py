"""
Transition system schemas and classes.
"""

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

    # TODO validate that the type is stochastic
    branch_probability_type = fields.Nested(SizedTypeSchema, data_key="branch-probability-type", required=False)
    # TODO validate that the type is stochastic
    exit_rate_type = fields.Nested(SizedTypeSchema, data_key="exit-rate-type", required=False)
    # TODO validate that the type is stochastic
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
                "#initial-states cannot exceed #states",
                field_name="num_initial_states",
            )

    @validates_schema
    def validate_observations(self, data, **kwargs):
        num_observations = data.get("num_observations")
        observations_apply_to = data.get("observations_apply_to")
        if num_observations == 0 and observations_apply_to is not None:
            raise ValidationError(
                "#observations is 0 but observations_apply_to is specified",
                field_name="observations_apply_to",
            )
        if num_observations > 0 and observations_apply_to is None:
            raise ValidationError(
                "#observations > 0 but observations_apply_to is not specified",
                field_name="observations_apply_to",
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
    """Transition system data class."""

    time: Literal["discrete", "stochastic", "urgent-stochastic"] = "discrete"
    num_players: int = 0
    num_states: int = 1
    num_initial_states: int = 0
    num_choices: int = 0
    num_choice_actions: int = 0
    num_branches: int = 0
    num_branch_actions: int = 0
    num_observations: int = 0
    observations_apply_to: Literal["states", "branches"] | None = None

    branch_probability_type: SizedType | None = None
    exit_rate_type: SizedType | None = None
    observation_probability_type: SizedType | None = None
    player_to_name: list[str] | None = None

    @classmethod
    def class_schema(cls) -> Type:
        return TransitionSystemSchema
