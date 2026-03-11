from fractions import Fraction

import pytest

from umbi import datatypes as dt


def test_exported_type_constructors_and_aliases():
    assert dt.PrimitiveType.BOOL.value == "bool"
    assert dt.NumericPrimitiveType.DOUBLE.value == "double"

    interval_type = dt.IntervalType(dt.NumericPrimitiveType.INT)
    assert str(interval_type) == "int-interval"

    interval = dt.Interval(1, 3)
    assert interval.left == 1
    assert interval.right == 3


def test_scalar_promotion_and_vector_promotion():
    assert dt.scalar_promotion_type([dt.PrimitiveType.BOOL, dt.NumericPrimitiveType.INT]) == dt.NumericPrimitiveType.INT
    assert dt.scalar_promotion_type([dt.PrimitiveType.STRING, dt.NumericPrimitiveType.INT]) == dt.PrimitiveType.STRING

    target, values = dt.promote_vector([1, 2.5])
    assert target == dt.NumericPrimitiveType.DOUBLE
    assert values == [1.0, 2.5]


def test_collection_promotion_and_targeted_promotion():
    assert dt.collection_promotion_type([1, 2.0, Fraction(3, 2)]) == dt.NumericPrimitiveType.RATIONAL
    assert dt.promote_vector_to([1, 2], dt.NumericPrimitiveType.DOUBLE) == [1.0, 2.0]


def test_interval_type_and_interval_basic_behavior():
    interval_type = dt.IntervalType.from_string("double-interval")
    assert str(interval_type) == "double-interval"

    interval = dt.Interval(1, 3)
    assert 2 in interval
    assert interval.type == dt.IntervalType(dt.NumericPrimitiveType.INT)

    with pytest.raises(ValueError):
        dt.Interval(3, 1)


def test_json_helpers():
    payload: dt.JsonLike = {"a": 1, "b": None, "nested": {"x": None, "y": 2}, "arr": [1, None]}
    cleaned = dt.json_remove_none_dict_values(payload)
    assert cleaned == {"a": 1, "nested": {"y": 2}, "arr": [1, None]}

    encoded = dt.json_to_string(cleaned, indent=None)
    decoded = dt.string_to_json(encoded)
    assert decoded == cleaned
