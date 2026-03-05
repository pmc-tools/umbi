from importlib import import_module
from typing import TYPE_CHECKING

from .logger import set_log_level, setup_logging
from .version import __format_revision__, __format_version__, __toolname__, __version__

# Static analyzers (Pylance/mypy) evaluate this block to learn exported submodules,
# while runtime skips it to avoid eager imports and potential import cycles.
if TYPE_CHECKING:
    from . import ats as ats
    from . import binary as binary
    from . import datatypes as datatypes
    from . import index as index
    from . import io as io
    from . import version as version


_SUBMODULES = {"ats", "binary", "datatypes", "index", "io", "version"}


def __getattr__(name: str):
    if name in _SUBMODULES:
        module = import_module(f".{name}", __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(list(globals().keys()) + list(_SUBMODULES))


__all__ = [
    "set_log_level",
    "setup_logging",
    "__toolname__",
    "__version__",
    "__format_version__",
    "__format_revision__",
    "datatypes",
    "binary",
    "io",
    "index",
    "ats",
    "version",
]
