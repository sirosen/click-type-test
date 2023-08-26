import click
import pytest

from click_type_test import (
    BadAnnotationError,
    check_param_annotations,
    deduce_type_from_parameter,
)


def test_deduce_type_from_parameter_on_non_nullable_flag():
    opt = click.Option(["--foo/--no-foo"], is_flag=True)
    assert deduce_type_from_parameter(opt) == bool


def test_deduce_type_from_parameter_on_nullable_flag():
    opt = click.Option(["--foo/--no-foo"], is_flag=True, default=None)
    assert deduce_type_from_parameter(opt) == (bool | None)


def test_deduce_type_from_multiple_string_opt():
    opt = click.Option(["--foo"], multiple=True)
    assert deduce_type_from_parameter(opt) == tuple[str, ...]


def test_deduce_type_from_int_argument():
    arg = click.Argument(["FOO"], type=int)
    assert deduce_type_from_parameter(arg) == int


def test_deduce_type_from_nargs_many_argument():
    arg = click.Argument(["FOO"], nargs=-1)
    assert deduce_type_from_parameter(arg) == tuple[str, ...]


def test_check_annotations_fails_on_missing_arg():
    @click.command
    @click.option("--foo")
    def mycmd():
        pass

    with pytest.raises(
        BadAnnotationError, match="expected parameter 'foo' was not in type hints"
    ):
        check_param_annotations(mycmd)


def test_check_annotations_fails_on_bad_arg_type():
    @click.command
    @click.option("--foo")
    def mycmd(foo: int):
        pass

    with pytest.raises(
        BadAnnotationError, match="parameter 'foo' has unexpected parameter type"
    ):
        check_param_annotations(mycmd)
