import logging
from dataclasses import dataclass, fields

logger = logging.getLogger(__name__)


@dataclass
class BaseMixin:
    def __post_init__(self):
        pass

    def validate(self) -> None:
        """Validate the internal consistency of the base mixin."""
        try:
            super().validate()  # type: ignore
        except AttributeError:
            # Parent class doesn't have validate(), stop here
            pass

    def equals(self, other: object, debug: bool = False) -> bool:
        """Check equality by comparing all fields.

        Each class (Observable, EntitySpace, etc.) handles its own equality semantics.
        Chains super().equals() to compare parent mixin fields.
        """
        if other is None:
            return False

        # Compare this mixin's fields
        for field in fields(self.__class__):
            attr_self = getattr(self, field.name, None)
            attr_other = getattr(other, field.name, None)

            try:
                if attr_self != attr_other:
                    if debug:
                        logger.debug(f"{self.__class__.__name__}.equals: field {field.name} differs")
                    return False
            except RecursionError:
                if debug:
                    logger.debug(f"{self.__class__.__name__}.equals: skipping field {field.name} (recursion)")
                continue

        # Chain to parent classes
        try:
            return super().equals(other, debug)  # type: ignore
        except AttributeError:
            return True


@dataclass
class CompositeMixin(BaseMixin):
    def __post_init__(self):
        super().__post_init__()
