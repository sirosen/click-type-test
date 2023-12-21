# CHANGELOG

## Unreleased

## 0.0.6

- The type annotation used as the return type of a `callback` on a parameter
  will now be treated as an override which takes precedence over any deduction
  about the parameter type
- The type annotation used as the return type of a custom type's `convert`
  method will be checked and used as the annotated value for parameter types
  which do not implement `AnnotatedParamType`
- The documentation is more explicit about type evaluation logic and order of
  overrides

## 0.0.5

- Fix handling for required options, non-required arguments, `nargs=-1`, and
  `nargs=N` for `N>1`

## 0.0.4

- Enhance documentation and examples
- Add support for `click.Path(path_type=...)` as a type or a callable with an
  annotated return type. Unsupported `path_type` values will raise `TypeError`.
- A new parameter is supported for `check_param_annotations`,
  `known_type_names`, a mapping of type values to strings.
  `check_param_annotations` will use this mapping in a best-effort fashion to
  display the names of types in `BadAnnotation` errors.

## 0.0.3

- Remove `ExplicitlyAnnotatedOption` from the library due to issues with
  usability. It is now kept in the `examples/` directory
- Rename `AnnotatedOption` to `AnnotatedParameter` to encompass `Argument`
  subclasses as well

## 0.0.2

- Fix release process to include build artifacts in github releases

## 0.0.1

- Initial release
