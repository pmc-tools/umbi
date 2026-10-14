import umbi
from umbi.version import get_pyproject_attribute


def test_nested_format_metadata():
    assert get_pyproject_attribute("format_version", -1, "tool.umbi") == 1
    assert get_pyproject_attribute("format_revision", -1, "tool.umbi") == 0
    assert umbi.__format_version__ == 1
    assert umbi.__format_revision__ == 0


def test_project_metadata():
    assert get_pyproject_attribute("name", "missing") == "umbi"


def test_missing_metadata():
    assert get_pyproject_attribute("missing", -1, "tool.umbi") == -1
    assert get_pyproject_attribute("format_version", -1, "tool.missing") == -1
