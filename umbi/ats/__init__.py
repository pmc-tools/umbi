"""
umbi.ats: Collection of interfaces over a umbfile.
"""

from . import examples
from .annotations import (
    Annotation,
    AtomicPropositionAnnotation,
    ObservationAnnotation,
    RewardAnnotation,
)
from .ats_to_umb import (
    explicit_ats_to_explicit_umb,
    explicit_umb_to_explicit_ats,
    read,
    write,
)
from .entity_space import EntityClass
from .model_info import ModelInfo
from .simple_ats import SimpleAts
from .time_type import TimeType
from .variable_valuations import (
    EntityClassValuations,
    EntityValuation,
    EntityValuations,
    EntityVariableValuations,
    Variable,
)

__all__ = [
    "examples",
    # annotation
    "Annotation",
    "AtomicPropositionAnnotation",
    "ObservationAnnotation",
    "RewardAnnotation",
    # model_info
    "ModelInfo",
    # time_type
    "TimeType",
    # explicit_ats
    "SimpleAts",
    # variable_valuations
    "EntityVariableValuations",
    "Variable",
    "EntityValuation",
    "EntityValuations",
    "EntityClassValuations",
    # entity_class
    "EntityClass",
    # ats_to_umb
    "explicit_ats_to_explicit_umb",
    "explicit_umb_to_explicit_ats",
    "read",
    "write",
]
