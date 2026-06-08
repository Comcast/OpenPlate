## 1. Template parameter schema

- [x] 1.1 Extend template parameter configuration parsing to accept `conditionally_hidden` and store it on `TemplateConfigParameter`.
- [x] 1.2 Add validation so `conditionally_hidden` requires `default` and cannot be combined with `hidden`.

## 2. Ordered parameter resolution

- [x] 2.1 Update parameter resolution to render `conditionally_hidden` with the same liquid context used for defaults, including earlier parameter answers already resolved in declaration order.
- [x] 2.2 Enforce the runtime boolean contract for `conditionally_hidden`, treating rendered `false` as hidden, rendered `true` as visible, and raising a clear error for any other rendered value.
- [x] 2.3 Reuse the existing hidden-parameter prompt flow so conditionally hidden parameters still honor defaults and `--ask-hidden`.

## 3. Verification and documentation

- [x] 3.1 Add focused tests for schema validation, ordered evaluation against earlier answers, invalid rendered booleans, and `--ask-hidden` behavior for conditionally hidden parameters.
- [x] 3.2 Update the template authoring documentation to explain `conditionally_hidden`, its liquid syntax, ordering rules, default requirement, and the `false => hidden` behavior.