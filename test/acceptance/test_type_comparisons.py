import typing as t

import click
import pytest

from click_type_test import BadAnnotationError, check_param_annotations


class CommaSplitType(click.ParamType):
    def convert(
        self,
        value: str,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> tuple[str, str]:
        return ("a", "b")


def test_tuple_types_match_trivially():
    @click.command
    @click.option("--bar", type=CommaSplitType())
    def foo(bar: t.Tuple[str, str] | None) -> None:
        pass

    check_param_annotations(foo)


def test_distinct_tuple_types_can_mismatch():
    @click.command
    @click.option("--bar", type=CommaSplitType())
    def foo(bar: t.Tuple[str, ...] | None) -> None:
        pass

    with pytest.raises(BadAnnotationError):
        check_param_annotations(foo)


def test_choice_with_default_is_inferred_as_literal():
    @click.command
    @click.option("--mode", type=click.Choice(["a", "b", "c"]), default="a")
    def foo(mode: t.Literal["a", "b", "c"]) -> None:
        pass

    check_param_annotations(foo)


def test_choice_with_unrecognized_default_is_inferred_as_union():
    @click.command
    @click.option("--mode", type=click.Choice(["a", "b", "c"]), default="d")
    def foo(mode: t.Literal["a", "b", "c"] | str) -> None:
        pass

    check_param_annotations(foo)


def test_multiple_choice_with_default_is_inferred_as_ntuple_literal():
    @click.command
    @click.option(
        "--mode", type=click.Choice(["a", "b", "c"]), default=("a",), multiple=True
    )
    def foo(mode: tuple[t.Literal["a", "b", "c"], ...]) -> None:
        pass

    check_param_annotations(foo)
