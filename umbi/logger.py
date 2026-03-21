"""Logging setup for the umbi package."""

import logging


def setup_logging(level: int | str = logging.INFO):
    """Set up logging for umbi.

    :param level: logging level as int (e.g. logging.DEBUG) or string (e.g. "DEBUG")
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger = logging.getLogger("umbi")
    logger.addHandler(handler)
    logger.setLevel(level)


def set_log_level(level: int | str = logging.INFO):
    """Set the logging level for umbi.

    :param level: logging level as int (e.g. logging.DEBUG) or string (e.g. "DEBUG")
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger("umbi")
    logger.setLevel(level)
