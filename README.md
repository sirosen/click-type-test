# click-type-test

[![PyPI - Version](https://img.shields.io/pypi/v/click-type-test.svg)](https://pypi.org/project/click-type-test)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/click-type-test.svg)](https://pypi.org/project/click-type-test)

-----

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [API](#api)
- [License](#license)

## Overview

`click-type-test` allows you to test that your
[`click`](https://github.com/pallets/click) options and arguments
match your type annotations.

It is named by the trio of things which it supports:

- `click`: build a CLI
- `type`: add type annotations
- `test`: test that the first two match

## Installation

`click-type-test` only works on Python 3.10+ .

On supported python versions, it should be installed with

```console
pip install click-type-test
```

## Usage

Install the package and then use `click_type_test` to extract annotation data
and check it against your commands.

```python
from click_type_test import check_param_annotations
from foopkg import mycommand

def test_mycommand_annotations():
    check_param_annotations(mycommand)
```

`check_param_annotations` raises a
`click_type_test.BadAnnotationError` if an annotation does not match.

### Version Guarding

Just because `click-type-test` only works on certain pythons does not mean that
your application, tested with it, is also restricted to those python versions.

You can guard your usage like so (under `pytest`):

```python
import pytest
import sys
from foopkg import mycommand

@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="click-type-test requires py3.10+",
)
def test_mycommand_annotations():
    from click_type_test import check_param_annotations
    check_param_annotations(mycommand)
```

### Type Determination Logic

`click-type-test` makes its best effort to determine what type will be passed
to the command at runtime, based on the available information.

1.  If the parameter implements `AnnotatedParameter` and has an explicit
    annotation, that value will always be used.

    This makes this value the highest precedence override.

2.  If there is a `callback` function with a return type annotation, the return
    type of the `callback` will be used.
    This makes the `callback` return type the second highest precedence value.

3.  After this, `click-type-test` must inspect the parameter type which has been
    used, any `default` value which has been set, `multiple=True` for options and
    `nargs=-1` for arguments, and generally try to infer the type correctly.

For parameter type evaluation, users can control the behavior of custom types
in two significant ways:

- annotate `convert` with a return type annotation (this will be used if
  available)

- implement `AnnotatedOption` and define a type annotation (this is used as the
  highest precedence value for a parameter type, so it can be used as an
  override)

As a simple example, `click-type-test` is able to handle the following comma
delimited list type definition correctly correctly:

```python
class CommaDelimitedList(click.ParamType):
    def get_metavar(self, param: click.Parameter) -> str:
        return "TEXT,TEXT,..."

    def convert(
        self, value: str, param: click.Parameter | None, ctx: click.Context | None
    ) -> list[str]:
        value = super().convert(value, param, ctx)
        return value.split(",") if value else []
```

### Extending And Adjusting With AnnotatedParamType and AnnotatedOption

The type deductions made by `click-type-test` are not always going to be
correct. But rather than skipping options or parameters, it's better to
pass along the information needed if possible.

Custom parameter types can support usage with `click-type-test` by implementing
the `AnnotatedParamType` protocol.

Similarly, custom `click.Option` subclasses can support specialized usage by
implementing the `AnnotatedOption` protocol.

The path you take will depend a bit on the precise needs of your CLI, but it
generally should be possible to tune `click-type-test` to correctly understand
your CLI.

#### AnnotatedParamType

If you have a custom `ParamType`, extend it to implement the
`AnnotatedParamType` protocol and it will have first-class support in
`click-type-test`.

This requires that there be a method, `get_type_annotation`, which takes the
`click.Parameter` which was used and returns the type which should be expected
as an annotation.

You can check that a `ParamType` implements `AnnotatedParamType` with
a simple `isinstance` check:
```python
import click_type_test

isinstance(myparamtype, click_type_test.AnnotatedParamType)
```

#### AnnotatedParameter

If you have a subclass of `Option` or `Argument` which produces specialized
values, it may be necessary to provide type information from that class.
To handle this case, just have your parameter class implement the
`AnnotatedParameter` protocol.

This requires a method, `has_explicit_annotation`, and a property
`type_annotation`.
`has_explicit_annotation` takes no arguments and returns a bool.
`type_annotation` returns a `type`.

See
[`examples/explicitly_annotation_option.py`](https://github.com/sirosen/click-type-test/blob/main/examples/explicitly_annotated_option.py) for an example.

You can check that a `Parameter` implements `AnnotatedParameter` with
a simple `isinstance` check:
```python
import click_type_test

isinstance(myparam, click_type_test.AnnotatedParameter)
```

## API

The following values are the consumable API for `click-type-test`.
No other values are part of the interface.

- `AnnotatedParamType`: a protocol for `click.ParamType` subclasses which
  provide explicit type information. It is runtime checkable.

- `AnnotatedParameter`: a protocol for `click.Parameter` subclasses which
  provide explicit type information. It is runtime checkable.

- `deduce_type_from_parameter`: a function which takes a `click.Parameter` and
  returns a type. Used internally but useful for unit testing custom classes.

- `check_param_annotations`: a function which takes a `click.Command` and
  checks the type annotations on its callback against its parameter list.

- `BadAnnotationError`: the error type raised if checking annotations fails.

## License

`click-type-test` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
