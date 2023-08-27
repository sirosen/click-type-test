import typing as t

import click
import pytest

from click_type_test import BadAnnotationError, check_param_annotations


def test_failing_usage_with_custom_name():
    @click.command
    @click.option("--name")
    def foo(name: str) -> None:
        pass

    with pytest.raises(
        BadAnnotationError,
        match=(
            "parameter 'name' has unexpected parameter type "
            "'str' rather than 'MaybeStr'"
        ),
    ):
        check_param_annotations(foo, known_type_names={t.Optional[str]: "MaybeStr"})


@pytest.mark.parametrize("param_is_uniontype", (True, False))
def test_both_union_types_are_handled(param_is_uniontype):
    if param_is_uniontype:

        @click.command
        @click.option("--name", type=int)
        def foo(name: str | None) -> None:
            pass

    else:

        @click.command
        @click.option("--name", type=int)
        def foo(name: t.Union[str, None]) -> None:
            pass

    with pytest.raises(
        BadAnnotationError,
        match=(
            "parameter 'name' has unexpected parameter type "
            "'str | None' rather than 'int | None'"
        ),
    ):
        check_param_annotations(foo)
