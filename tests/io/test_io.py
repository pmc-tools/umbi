import pathlib
import umbi


def test_public_io_exports_are_available():
    assert callable(umbi.umb.read)
    assert callable(umbi.umb.write)
    assert callable(umbi.ats.explicit_umb_to_explicit_ats)
    assert callable(umbi.ats.explicit_ats_to_explicit_umb)
    assert callable(umbi.ats.read)
    assert callable(umbi.ats.write)


def test_explicit_ats_to_umb_and_back_smoke():
    ats = umbi.ats.ExplicitAts()
    umb = umbi.ats.explicit_ats_to_explicit_umb(ats)
    ats_loaded = umbi.ats.explicit_umb_to_explicit_ats(umb)

    assert ats_loaded.num_states == ats.num_states
    assert ats_loaded.num_choices == ats.num_choices
    assert ats_loaded.num_branches == ats.num_branches
    assert ats_loaded.time == ats.time


def test_write_and_read_ats_smoke(tmp_path: pathlib.Path):
    ats = umbi.ats.ExplicitAts()
    output = tmp_path / "basic.umb"

    umbi.ats.write(ats, output)
    loaded = umbi.ats.read(output)

    assert output.exists()
    assert loaded.num_states == 1
    assert loaded.num_choices == 0
    assert loaded.num_branches == 0
