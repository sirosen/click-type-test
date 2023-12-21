"""
This example shows an explicitly annotated option type, which allows users to specify
an override or specific annotation via the `type_annotation` argument.

The benefit of this approach is that it lets users specify an annotation explicitly for
cases where the deduced annotation would be incorrect.
"""
from __future__ import annotations

import typing as t

import click


class _SENTINEL:
    """Internal sentinel class."""


class ExplicitlyAnnotatedOption(click.Option):
    def __init__(
        self,
        *args: t.Any,
        type_annotation: type = _SENTINEL,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._type_annotation = type_annotation

    def has_explicit_annotation(self) -> bool:
        if self._type_annotation == _SENTINEL:
            return False
        return True

    @property
    def type_annotation(self) -> type:
        if self._type_annotation == _SENTINEL:
            raise ValueError("cannot get annotation from option when it is not set")

        return t.cast(type, self._type_annotation)


@click.command()
@click.option(
    "--bar",
    type=int,
    callback=lambda ctx, param, value: str(value) if value is not None else None,
    cls=ExplicitlyAnnotatedOption,
    # although 'int | None' is expected, the callback returns 'str | None'
    # but Optional might be used because some python versions need a runtime type
    type_annotation=t.Optional[str],
)
def foo(*, bar: str | None) -> None:
    click.echo(f"bar: {bar}")


if __name__ == "__main__":
    import click_type_test

    click_type_test.check_param_annotations(foo)
