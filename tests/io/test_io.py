from pathlib import Path

import umbi.ats
import umbi.io


def test_public_io_exports_are_available():
    assert callable(umbi.io.read_umb)
    assert callable(umbi.io.write_umb)
    assert callable(umbi.io.explicit_umb_to_explicit_ats)
    assert callable(umbi.io.explicit_ats_to_explicit_umb)
    assert callable(umbi.io.read_ats)
    assert callable(umbi.io.write_ats)


def test_explicit_ats_to_umb_and_back_smoke():
    ats = umbi.ats.ExplicitAts()
    umb = umbi.io.explicit_ats_to_explicit_umb(ats)
    ats_loaded = umbi.io.explicit_umb_to_explicit_ats(umb)

    assert ats_loaded.num_states == ats.num_states
    assert ats_loaded.num_choices == ats.num_choices
    assert ats_loaded.num_branches == ats.num_branches
    assert ats_loaded.time == ats.time


def test_write_and_read_ats_smoke(tmp_path: Path):
    ats = umbi.ats.ExplicitAts()
    output = tmp_path / "basic.umb"

    umbi.io.write_ats(ats, output)
    loaded = umbi.io.read_ats(output)

    assert output.exists()
    assert loaded.num_states == 1
    assert loaded.num_choices == 0
    assert loaded.num_branches == 0
