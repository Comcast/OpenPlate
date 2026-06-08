## Why

OpenPlate parameters currently support a static `hidden` flag and liquid-backed defaults, but they cannot decide at prompt time whether a parameter should be hidden based on earlier answers. Templates need a first-class way to make a parameter hidden or visible from liquid conditions without removing the parameter itself or splitting logic across sibling templates and file conditions.

## What Changes

- Add a `conditionally_hidden` parameter property in template declarations that accepts project liquid syntax and evaluates during parameter resolution.
- Define the evaluation contract so `conditionally_hidden` can use the same built-in template context as parameter defaults plus any parameter answers that were already resolved earlier in the file.
- Require `conditionally_hidden` values to render to `true` or `false`, treat rendered `false` as hidden, and reject configurations that combine `conditionally_hidden` with static `hidden`.
- Require parameters using `conditionally_hidden` to declare a default value, including an empty-string default when needed, so hidden resolution still has an answer path.
- Expand template documentation to explain syntax, ordering rules, boolean semantics, validation constraints, and how `--ask-hidden` interacts with conditionally hidden parameters.

## Capabilities

### New Capabilities
- `conditional-hidden-parameters`: Defines liquid-driven parameter hiddenness, ordered evaluation against earlier answers, validation rules for `hidden` and defaults, and the documentation contract for template authors.

### Modified Capabilities

## Impact

Affected areas include template configuration deserialization and validation in `src/openplate/cfg/template_config.py`, parameter resolution in `src/openplate/project_config_resolver.py`, template documentation in `docs/templates.md`, and focused tests for conditional hiddenness and ordered liquid evaluation.