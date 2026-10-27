"""Version information for umbi package."""

import importlib.metadata

__toolname__ = "umbi"
try:
    __version__ = importlib.metadata.version(__toolname__)
except importlib.metadata.PackageNotFoundError:  # running from an uninstalled checkout
    __version__ = "unknown"
