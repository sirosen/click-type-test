# CHANGELOG

## Unreleased

- Enhance documentation and examples
- Add support for `click.Path(path_type=...)` as a type or a callable with an
  annotated return type. Unsupported `path_type` values will raise `TypeError`.

## 0.0.3

- Remove `ExplicitlyAnnotatedOption` from the library due to issues with
  usability. It is now kept in the `examples/` directory
- Rename `AnnotatedOption` to `AnnotatedParameter` to encompass `Argument`
  subclasses as well

## 0.0.2

- Fix release process to include build artifacts in github releases

## 0.0.1

- Initial release
