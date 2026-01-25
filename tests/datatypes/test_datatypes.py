import pytest
from umbi.datatypes import (
    AtomicType,
    atomic_type_of,
    datatype_of,
    common_datatype,
    NumericPrimitiveType,
    IntervalType,
    interval_base_type,
    base_to_interval_type,
    is_json_instance,
    json_remove_none_dict_values,
    json_to_string,
    string_to_json,
    StructPadding,
    StructAttribute,
    SizedType,
    VectorType,
    assert_is_list,
    is_vector_ranges,
    csr_to_ranges,
    ranges_to_csr,
    numeric_primitive_type_of,
    common_numeric_primitive_type,
    validate_type_size,
)


def test_atomic_type_of_bool():
    assert atomic_type_of(True) == AtomicType.BOOL


def test_atomic_type_of_str():
    assert atomic_type_of("abc") == AtomicType.STRING


def test_datatype_of_bool():
    assert datatype_of(True) == AtomicType.BOOL


def test_datatype_of_int():
    assert datatype_of(42) == NumericPrimitiveType.INT


def test_common_datatype():
    assert common_datatype({AtomicType.BOOL, NumericPrimitiveType.INT}) == NumericPrimitiveType.INT


def test_interval_base_type():
    assert interval_base_type(IntervalType.INT) == NumericPrimitiveType.INT


def test_base_to_interval_type():
    assert base_to_interval_type(NumericPrimitiveType.INT) == IntervalType.INT


def test_json_is_json_instance():
    assert is_json_instance({"a": 1, "b": [True, None]})
    assert not is_json_instance({"a": object()})


def test_json_remove_none_dict_values():
    d = {"a": 1, "b": None, "c": {"d": None, "e": 2}}
    cleaned = json_remove_none_dict_values(d)
    assert cleaned == {"a": 1, "c": {"e": 2}}


def test_json_to_string_and_back():
    d = {"a": 1, "b": [2, 3]}
    s = json_to_string(d)
    assert string_to_json(s) == d


def test_struct_padding_validate():
    pad = StructPadding(8)
    pad.validate()
    with pytest.raises(ValueError):
        StructPadding(0).validate()


def test_struct_attribute_validate():
    attr = StructAttribute("x", SizedType(AtomicType.BOOL, 1))
    attr.validate()


def test_vector_type_and_assert_is_list():
    vt = VectorType(SizedType(NumericPrimitiveType.INT, 32))
    # Check that vt has attribute 'type' and its type is correct
    assert hasattr(vt, "type")
    assert vt.type.type == NumericPrimitiveType.INT
    assert_is_list([1, 2, 3])
    with pytest.raises(TypeError):
        assert_is_list(123)


def test_is_vector_ranges():
    assert is_vector_ranges([(0, 2), (2, 3)])
    assert not is_vector_ranges([(1, 0)])


def test_csr_to_ranges_and_back():
    csr = [0, 2, 5]
    ranges = csr_to_ranges(csr)
    assert ranges == [(0, 2), (2, 5)]
    assert ranges_to_csr(ranges) == csr


def test_numeric_primitive_type_of():
    assert numeric_primitive_type_of(1) == NumericPrimitiveType.INT
    assert numeric_primitive_type_of(1.0) == NumericPrimitiveType.DOUBLE


def test_common_numeric_primitive_type():
    assert (
        common_numeric_primitive_type({NumericPrimitiveType.INT, NumericPrimitiveType.DOUBLE})
        == NumericPrimitiveType.DOUBLE
    )


def test_sized_type_defaults():
    st = SizedType(AtomicType.BOOL)
    assert st.size_bits == 1
    st2 = SizedType(NumericPrimitiveType.INT, 32)
    assert st2.size_bytes == 4


def test_validate_type_size():
    validate_type_size(AtomicType.BOOL, 1)
