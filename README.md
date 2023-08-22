# click-type-test

-----

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
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

#### ExplicitlyAnnotatedOption

However, the simplest way to use `AnnotatedOption` is to use the
`ExplicitlyAnnotatedOption` class, which takes an extra init parameter,
`type_annotation`, like so:

```python
import typing
import click
from click_type_test import ExplicitlyAnnotatedOption

def _str_to_bool_callback(
    ctx: click.Context, param: click.Parameter, value: typing.Any
) -> bool | None:
    if value is None:
        return None
    return value.lower() in ("yes", "true", "on", "1")

@click.command
@click.option(
    "--bar",
    callback=_str_to_bool_callback,
    cls=ExplicitlyAnnotatedOption,
    type_annotation=bool,
)
def foo(*, bar: bool | None) -> None:
    ...
```

Note how `type_annotation` is used to override the normal deduction that
`--bar` is a string, but the default for `--bar` is still understood to be
`None`!

#### AnnotatedParamType

If you have a custom `ParamType`, extend it like so and it will have
first-class support in `click-type-test`:

```python
# TODO!
```

#### AnnotatedOption

If you have a custom subclass of `Option` already, you won't be able to use
`cls=ExplicitlyAnnotatedOption`. To handle this case, just have your subclass
of `Option` implement the same `AnnotatedOption` protocol, like so:

```python
# TODO!
```

## License

`click-type-test` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
