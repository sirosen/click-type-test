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
