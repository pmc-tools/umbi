import importlib.metadata

import umbi


def test_package_metadata():
    assert umbi.__toolname__ == "umbi"
    assert umbi.__version__ == importlib.metadata.version("umbi")
