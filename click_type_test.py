"""
click-type-test

- click: build a CLI
- type: add annotations
- test: check that the annotations match the `click` usage
"""
from __future__ import annotations

import datetime
import inspect
import types
import typing as t
import uuid

import click


@t.runtime_checkable
class AnnotatedParamType(t.Protocol):
    # conventionally this protocol describes subclasses of click.ParamType
    # however, the type itself does not enforce this
    def get_type_annotation(self, param: click.Parameter) -> type:
        ...


@t.runtime_checkable
class AnnotatedParameter(t.Protocol):
    # conventionally this protocol describes subclasses of click.Option
    # however, the type itself does not enforce this
    def has_explicit_annotation(self) -> bool:
        ...

    @property
    def type_annotation(self) -> type:
        ...


class BadAnnotationError(ValueError):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        if len(errors) == 1:
            super().__init__(errors[0])
        else:
            super().__init__("\n  " + "\n  ".join(errors))


_CLICK_STATIC_TYPE_MAP: dict[type[click.ParamType], type] = {
    click.types.StringParamType: str,
    click.types.BoolParamType: bool,
    click.types.IntParamType: int,
    click.IntRange: int,
    click.types.FloatParamType: float,
    click.FloatRange: float,
    click.DateTime: datetime.datetime,
    click.types.UUIDParameterType: uuid.UUID,
    click.File: t.TextIO,
}


def _is_click_module(mod: types.ModuleType) -> bool:
    modname = mod.__name__
    return modname == "click" or modname.startswith("click.")


def _defined_in_click(obj: object) -> bool:
    mod = inspect.getmodule(obj)
    if mod is None:
        return False
    return _is_click_module(mod)


def _type_of_return_annotation(obj: object) -> type | None:
    mod = inspect.getmodule(obj)
    if mod is None:
        return None
    if _is_click_module(mod):
        mod = click
    annotations = t.get_type_hints(obj, globalns=vars(mod))
    return_annotation = annotations.get("return")
    if return_annotation is not None:
        return t.cast(type, return_annotation)
    return None


def _type_from_param_type(
    param_obj: click.Parameter, *, param_type: click.ParamType | None = None
) -> type:
    """
    Given a Parameter instance, read the 'type' attribute and deduce the type
    or union of possible types which it describes

    Supports both `click` native types and custom types

    For example:
        IntParamType -> int
        IntRange -> int
        MyStringOrBoolType -> str | bool
    """
    if param_type is None:
        param_type = param_obj.type

    # custom types
    if isinstance(param_type, AnnotatedParamType):
        return param_type.get_type_annotation(param_obj)

    # a custom type which defines a `convert()` method outside of `click`
    # note that we check for `convert` itself being inherited
    if not _defined_in_click(param_type.convert):
        convert_returns = _type_of_return_annotation(param_type.convert)
        if convert_returns is not None:
            return convert_returns

    # click types
    if type(param_type) in _CLICK_STATIC_TYPE_MAP:
        return _CLICK_STATIC_TYPE_MAP[type(param_type)]
    if isinstance(param_type, click.Choice):
        return t.Literal[tuple(param_type.choices)]  # type: ignore[return-value]
    if isinstance(param_type, click.Tuple):
        return tuple[  # type: ignore[misc, no-any-return]
            tuple(
                _type_from_param_type(param_obj, param_type=p) for p in param_type.types
            )
        ]
    if isinstance(param_type, click.Path):
        if param_type.type is None:
            return str
        if isinstance(param_type.type, type):
            return param_type.type
        elif callable(param_type.type):
            # NB: `from_callable` defaults to unwrapping any functions wrapped
            # with functools.wraps and looking at the signature of the wrapped
            # function. This could be disabled by allowing a user to request
            # `follow_wrapped=False`, if there is ever user demand
            return_annotation = inspect.Signature.from_callable(
                param_type.type
            ).return_annotation
            if return_annotation is inspect.Signature.empty:
                raise TypeError(
                    "click-type-test encountered a Path where 'path_type' was "
                    "set, but the return type of the converter function was not "
                    "annotated."
                )
            return return_annotation
        else:
            raise TypeError(
                "click-type-test encountered a Path where 'path_type' was "
                "set, but it was not a type or callable"
            )

    raise NotImplementedError(f"unsupported parameter type: {param_type}")


def _is_multi_param(p: click.Parameter) -> bool:
    if isinstance(p, click.Option) and p.multiple:
        return True

    if isinstance(p, click.Argument) and p.nargs != 1:
        return True

    return False


def _multi_param_length(p: click.Parameter) -> int:
    if isinstance(p, click.Option):
        return -1
    if isinstance(p, click.Argument):
        return p.nargs
    # unknown cases, unbounded?
    return -1


def _option_defaults_to_none(o: click.Option) -> bool:
    # if `default=1`, then the default can't be `None`
    if o.default is not None:
        return False

    # a multiple option defaults to () if default is unset or None
    if o.multiple:
        return False

    # if required, then the default can't be `None`
    if o.required:
        return False

    # fallthrough case: True
    return True


def _argument_defaults_to_none(a: click.Argument) -> bool:
    # if required (normal case), then it shouldn't be `None`
    if a.required:
        return False

    # if `default=1`, then the default can't be `None` even if it's not required
    if a.default is not None:
        return False

    # if nargs is -1, then the default is (), like a multiple option
    if a.nargs == -1:
        return False

    # fallthrough case: True
    return True


def deduce_type_from_parameter(param: click.Parameter) -> type:
    """
    Convert a click.Parameter object to a type or union of types
    """
    # if there is an explicit annotation, use that
    if isinstance(param, AnnotatedParameter) and param.has_explicit_annotation():
        return param.type_annotation

    if param.callback is not None:
        callback_returns = _type_of_return_annotation(param.callback)
        if callback_returns is not None:
            return callback_returns

    possible_types: set[type | None] = set()

    # only implicitly add NoneType to the types if the default is None
    # some possible cases to consider:
    #   '--foo' is a string with an automatic default of None
    #   '--foo/--no-foo' is a bool flag with an automatic default of False
    #   '--foo/--no-foo' is a bool flag with an explicit default of None
    #   '--foo' is a count option with a default of 0
    #   '--foo' uses a param type which converts None to a default value
    if isinstance(param, click.Option):
        if _option_defaults_to_none(param):
            possible_types.add(None)
    # for arguments, typically we do not set the default to None
    # *unless* `required=False` was passed, in which case it could be
    elif isinstance(param, click.Argument):
        if _argument_defaults_to_none(param):
            possible_types.add(None)

    # if a parameter has `multiple=True` or `nargs=-1`, then the type which can be
    # deduced from the parameter should be exposed as an any-length tuple
    if _is_multi_param(param):
        num_params = _multi_param_length(param)
        if num_params == -1:
            param_type = tuple[  # type: ignore[misc, valid-type]
                _type_from_param_type(param), ...
            ]
        else:
            param_type = tuple[  # type: ignore[misc]
                tuple(_type_from_param_type(param) for _ in range(num_params))
            ]
        possible_types.add(param_type)
    # if not multiple, then the type may need to be unioned with `None`
    # but if the type is, itself, a union, then it will need to be unpacked
    else:
        param_type = _type_from_param_type(param)
        if (  # detect Union[X, Y] and "union type expressions" (X | Y)
            isinstance(param_type, types.UnionType)
            or t.get_origin(param_type) == t.Union
        ):
            for member_type in t.get_args(param_type):
                possible_types.add(member_type)
        else:
            possible_types.add(param_type)

    # before returning, convert None -> NoneType
    try:
        possible_types.remove(None)
        possible_types.add(None.__class__)
    except KeyError:
        pass

    # should be unreachable
    if len(possible_types) == 0:
        raise ValueError(f"parameter '{param.name}' had no deduced parameter types")

    # exactly one type: not a union, so unpack the only element
    if len(possible_types) == 1:
        val = possible_types.pop()
        assert val is not None
        return val

    # more than one type: a union of the elements
    return t.Union[tuple(possible_types)]  # type: ignore[return-value]


class _TypeNameMap:
    def __init__(self, data: dict[type, str]) -> None:
        self._data: dict[type, str] = {}
        for k, v in data.items():
            self[k] = v

    def _normkey(self, key: type) -> type:
        if isinstance(key, types.UnionType):
            return t.Union[tuple(t.get_args(key))]  # type: ignore[return-value]
        return key

    def __setitem__(self, key: type, value: str) -> None:
        self._data[self._normkey(key)] = value

    def __getitem__(self, key: type) -> str:
        return self._data[self._normkey(key)]

    def __contains__(self, key: type) -> bool:
        return self._normkey(key) in self._data

    def get_type_name(self, typ: t.Any) -> str:
        if typ in self:
            return self[typ]

        if isinstance(typ, types.UnionType) or t.get_origin(typ) == t.Union:
            return " | ".join(self.get_type_name(x) for x in t.get_args(typ))

        if isinstance(typ, type):
            if typ == (None.__class__):
                return "None"
            return typ.__name__

        return str(typ)


def check_param_annotations(
    f: click.Command, *, known_type_names: dict[type, str] | None = None
) -> bool:
    """
    Check that the type annotations on a command's parameters match the types and
    modes of the click options used.

    For example, the following command would pass the check:

    .. code-block:: python

        @click.command
        @click.argument('FOO')
        @click.option('--bar', type=int)
        @click.option('--baz', type=click.Choice(("a", "b")))
        def goodcmd(*, foo: str, bar: int | None, baz: typing.Literal["a", "b"] | None):
            ...

    while this command would fail:

    .. code-block:: python

        @click.command
        @click.argument('--foo')
        @click.option('--bar', type=click.Choice(("x", "y")))
        def badcmd(*, foo: str, bar: str | None):
            ...

    ``badcmd`` does not match the type of ``foo`` (``str | None``) or the type of
    ``bar`` (``str`` where a ``Literal`` should be used).

    Parameters other than the ones described by the ``click`` parameters are allowed and
    ignored. For example, this usage is considered valid:

    .. code-block:: python

        @click.command
        @click.argument('FOO')
        @my_pass_username_decorator
        def goodcmd(*, foo: str, username: str):
            ...

    A mapping of types to nice names can be provided as `known_type_names`. For example,
    this usage will translate `str | bytes` to 'stringish' and `str | bytes | None` to
    'stringish | None':

    .. code-block:: python

        check_param_annotations(
            some_command,
            known_type_names={
                typing.Union[str, bytes]: "stringish",
                typing.Union[str, bytes, None]: "stringish | None",
            }
        )
    """
    type_names = _TypeNameMap({} if known_type_names is None else known_type_names)

    hints = t.get_type_hints(f.callback)
    errors = []
    for param in f.params:
        # skip params which do not get passed to the callback
        if param.expose_value is False:
            continue
        if param.name not in hints:
            errors.append(f"expected parameter '{param.name}' was not in type hints")
            continue

        expected_type = deduce_type_from_parameter(param)
        annotated_param_type = hints[param.name]

        if annotated_param_type != expected_type:
            errors.append(
                f"parameter '{param.name}' has unexpected parameter type "
                f"'{type_names.get_type_name(annotated_param_type)}' rather than "
                f"'{type_names.get_type_name(expected_type)}'"
            )
            continue

    if errors:
        raise BadAnnotationError(errors)

    return True
