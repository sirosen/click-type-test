"""
When the default has a value for a param, we are trying to add a concrete value->type
deduction to the inferred type for a parameter.
"""

import typing as t

import click
import pytest

from click_type_test import deduce_type_from_parameter


def test_deduce_type_from_default_int():
    # NB: 'default' without 'type' can cause a type to be inferred by click
    opt = click.Option(["--foo"], type=str, default=1)
    assert deduce_type_from_parameter(opt) == t.Union[str, int]


def test_deduce_type_from_default_sentinel_object():
    class MySentinel:
        pass

    SENTINEL = MySentinel()

    opt = click.Option(["--foo"], default=SENTINEL)
    assert deduce_type_from_parameter(opt) == t.Union[str, MySentinel]


def test_deduce_type_from_default_tuple():
    # NB: 'default' without 'type' can cause a type to be inferred by click
    opt = click.Option(["--foo"], type=str, default=(1, "2"))
    assert deduce_type_from_parameter(opt) == t.Union[str, tuple[int, str]]


def test_deduce_type_from_default_list():
    # NB: 'default' without 'type' can cause a type to be inferred by click
    opt = click.Option(["--foo"], type=str, default=[1, "2", None])
    assert (
        deduce_type_from_parameter(opt) == t.Union[str, list[t.Union[int, str, None]]]
    )


def test_deduce_type_from_default_dict():
    # this test is a classic proof of correctness: "Sufficiently Intimidating Example"
    #
    # NB: 'default' without 'type' can cause a type to be inferred by click
    opt = click.Option(
        ["--foo"],
        type=str,
        default={
            "x": 1,
            2: (object(),),
        },
    )
    assert (
        deduce_type_from_parameter(opt)
        == t.Union[str, dict[t.Union[int, str], t.Union[int, tuple[object]]]]
    )


def test_deduce_type_warns_and_uses_any_on_infinite_recursive_list_default():
    x = []
    x.append(x)
    opt = click.Option(["--foo"], type=str, default=x)

    with pytest.warns(
        UserWarning,
        match=(
            r"Depth limit for type deduction on concrete value reached, "
            r"suspected cycle\."
        ),
    ):
        type_ = deduce_type_from_parameter(opt)

    assert t.get_origin(type_) is t.Union
    args = t.get_args(type_)
    assert len(args) == 2
    assert str in args

    # it's first or second
    nested_type = args[0]
    if nested_type is str:
        nested_type = args[1]

    assert t.get_origin(nested_type) is list
    circuit_breaker = 0
    while circuit_breaker < 100 and t.get_origin(nested_type) is list:
        circuit_breaker += 1
        nested_type = t.get_args(nested_type)[0]
    assert nested_type is t.Any
