from importlib import import_module

from .logger import set_log_level, setup_logging
from .version import __format_revision__, __format_version__, __toolname__, __version__

_SUBMODULES = {"ats", "binary", "datatypes", "io", "umb", "version"}


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
    "version",
]
