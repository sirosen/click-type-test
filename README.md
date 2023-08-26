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

#### AnnotatedParamType

If you have a custom `ParamType`, extend it like so and it will have
first-class support in `click-type-test`:

```python
# TODO!
```

#### AnnotatedParameter

If you have a subclass of `Option` or `Argument` which produces specialized
values, it may be necessary to provide type information from that class.
To handle this case, just have your parameter class implement the
`AnnotatedParameter` protocol, like so:

```python
# TODO!
```

## API

The following values are the consumable API for `click-type-test`.
No other values are part of the interface.

- `AnnotatedParamType`: a protocol for `click.ParamType` subclasses which
  provide explicit type information.

- `AnnotatedParameter`: a protocol for `click.Parameter` subclasses which
  provide explicit type information.

- `deduce_type_from_parameter`: a function which takes a `click.Parameter` and
  returns a type. Used internally but useful for unit testing custom classes.

- `check_param_annotations`: a function which takes a `click.Command` and
  checks the type annotations on its callback against its parameter list.

- `BadAnnotationError`: the error type raised if checking annotations fails.

## License

`click-type-test` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
