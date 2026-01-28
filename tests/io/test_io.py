# import tempfile

# import pytest
# import logging
# import umbi

# from umbi.examples.ats import grid_ats_from_string, random_walk_ats

# log = logging.getLogger(__name__)

# constructors = [
#     lambda: random_walk_ats(num_states=5),
#     lambda: random_walk_ats(num_states=10),
#     lambda: ats_from_grid_string(
#         """
#         ....x..g
#         ...x....
#         i.......
#         ...x.x..
#         ..xxxx..
#         """
#     ),
#     lambda: ats_from_grid_string(
#         """
#         xxxxxxxg
#         ...xxxx.
#         i..xxx..
#         .......i
#         ..xxxx..
#         """
#     ),
# ]


# @pytest.mark.parametrize("constructor", constructors)
# def test_validate_function_output(constructor):
#     ats = constructor()
#     log.debug("Created ATS with %s states and %s choices", ats.num_states, ats.num_choices)

#     with tempfile.NamedTemporaryFile() as f:
#         # write to file and read back
#         umbi.io.write_ats(ats, f.name)
#         ats_loaded = umbi.io.read_ats(f.name)

#     log.debug("Loaded ATS with %s states and %s choices", ats_loaded.num_states, ats_loaded.num_choices)

#     assert ats.equal(ats_loaded, debug=True)
