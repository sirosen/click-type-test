import click
import pytest

from click_type_test import BadAnnotationError, check_param_annotations


def test_simple_passing_usage():
    @click.command
    @click.option("--name")
    def foo(name: str | None) -> None:
        pass

    check_param_annotations(foo)


def test_simple_failing_usage():
    @click.command
    @click.option("--name")
    def foo(name: str) -> None:
        pass

    with pytest.raises(BadAnnotationError):
        check_param_annotations(foo)
