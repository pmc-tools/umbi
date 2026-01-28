from enum import Enum


class EntityClass(str, Enum):
    """Entity type of a transition system the values are usually associated with."""

    STATES = "states"
    CHOICES = "choices"
    BRANCHES = "branches"
    OBSERVATION = "observation"
    PLAYERS = "players"
