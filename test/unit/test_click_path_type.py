import pathlib
import typing as t

import click
import pytest

from click_type_test import deduce_type_from_parameter


def test_deduce_type_from_basic_path_parameter():
    opt = click.Argument(["foo"], type=click.Path())
    assert deduce_type_from_parameter(opt) == str


def test_deduce_type_from_pathlib_path_parameter():
    opt = click.Argument(["foo"], type=click.Path(path_type=pathlib.Path))
    assert deduce_type_from_parameter(opt) == pathlib.Path


def test_deduce_type_from_path_parameter_errors_on_bad_path_type():
    opt = click.Option(["--foo"], type=click.Path(path_type=1))
    with pytest.raises(
        TypeError,
        match="'path_type' was set, but it was not a type or callable",
    ):
        deduce_type_from_parameter(opt)


def test_deduce_type_from_callable_parameter():
    def foo_type(value) -> bytes:
        return b""

    opt = click.Option(["--foo"], type=click.Path(path_type=foo_type))
    assert deduce_type_from_parameter(opt) == t.Optional[bytes]


def test_deduce_type_from_callable_parameter_errors_on_missing_return_annotation():
    def foo_type(value):
        return b""

    opt = click.Option(["--foo"], type=click.Path(path_type=foo_type))
    with pytest.raises(
        TypeError,
        match=(
            "'path_type' was set, but the return type "
            "of the converter function was not annotated"
        ),
    ):
        deduce_type_from_parameter(opt)


def test_deduce_type_from_callable_parameter_returning_optional():
    def foo_type(value) -> str | None:
        if value:
            return str(value)
        return None

    opt = click.Argument(["foo"], type=click.Path(path_type=foo_type))
    assert deduce_type_from_parameter(opt) == t.Optional[str]
