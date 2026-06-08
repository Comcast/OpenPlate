## Context

OpenPlate parameter prompting already has two useful pieces that this change needs to join together. First, parameters can declare static `hidden` and `default` values, and defaults are rendered through the liquid processor with the built-in template context. Second, parameter resolution already runs in declaration order and writes each resolved value back into `config_project_template.parameters`, which means later default rendering can already see earlier answers through `compile_template_options()`.

What is missing is a parameter-level way to decide hiddenness from that same liquid context. Today template authors can make sibling templates and files conditional, but they cannot conditionally hide or reveal later parameters based on answers already given during the same init/update flow.

## Goals / Non-Goals

**Goals:**
- Add a template parameter property named `conditionally_hidden` that accepts the same liquid syntax already used in defaults and sibling template conditions.
- Guarantee that `conditionally_hidden` is evaluated during parameter resolution with access to built-in template values and any earlier parameter answers.
- Enforce the requested validation rules: `conditionally_hidden` cannot be combined with `hidden`, it requires a default, and it must render to `true` or `false`.
- Make conditional hiddenness affect prompting behavior only, not whether the parameter exists in project state.
- Document the syntax, ordering, and boolean semantics clearly for template authors.

**Non-Goals:**
- Add dependency resolution across parameters beyond the existing declaration-order model.
- Remove or redefine the existing static `hidden` flag.
- Make later parameters available to earlier parameters during evaluation.
- Introduce broader truthy/falsy parsing such as `yes`, `no`, `1`, or `0` for this new property.

## Decisions

### 1. Add `conditionally_hidden` as a YAML parameter property with an internal optional field

Template YAML will accept `conditionally_hidden` on individual parameters. Internally, `TemplateConfigParameter` should carry a matching optional field that stores the raw liquid expression so the runtime can evaluate it later.

This keeps the external contract aligned with the requested template syntax while avoiding a separate parameter-conditions structure.

Alternatives considered:
- Reuse `hidden` for both booleans and liquid strings. Rejected because it muddies the existing schema and weakens validation.
- Put parameter conditions under a separate top-level section. Rejected because the user wants the rule declared alongside the parameter it controls.

### 2. Evaluate `conditionally_hidden` inside ordered parameter resolution

The condition should be rendered in `resolve_parameter()` after computing the default value context and before deciding whether to auto-answer or prompt. This lets the implementation reuse `compile_template_options()` and `template_processor.process()` so the condition sees the same built-in variables as defaults plus any earlier parameter answers already stored in `config_project_template.parameters`.

This explicitly ties the feature to declaration order: earlier parameters are available, later ones are not yet guaranteed.

Alternatives considered:
- Precompute all conditions before parameter prompting. Rejected because the needed context depends on answers gathered during the same pass.
- Evaluate conditions during template deserialization. Rejected because the runtime values do not exist yet.

### 3. Treat rendered `false` as hidden and rendered `true` as visible

The runtime should derive an effective hiddenness value from the rendered condition using the semantics requested for this change: `false` means the parameter is hidden, `true` means it remains visible. Once the effective hiddenness is computed, the existing hidden-parameter behavior should continue to apply, including `--ask-hidden` support.

This means the feature changes whether a parameter is treated as hidden, not whether the parameter is present or stored.

Alternatives considered:
- Use the more intuitive `true => hidden` mapping. Rejected because it does not match the requested contract.
- Skip `--ask-hidden` for conditionally hidden parameters. Rejected because the user explicitly wants the feature to affect hiddenness only.

### 4. Split validation between configuration parsing and runtime evaluation

Static constraints should be enforced when deserializing or constructing `TemplateConfigParameter`:
- `hidden` and `conditionally_hidden` cannot both be specified
- `conditionally_hidden` requires a default, including an empty-string default when needed

Dynamic validation should happen when the liquid expression is rendered during parameter resolution: the final result must normalize to either `true` or `false`, otherwise OpenPlate should raise a clear error pointing to the parameter.

Alternatives considered:
- Validate everything at parse time. Rejected because the rendered boolean cannot be known until runtime.
- Validate everything at runtime. Rejected because schema conflicts such as `hidden` plus `conditionally_hidden` are better caught early.

### 5. Document the ordering and boolean contract in template docs

`docs/templates.md` should explain that:
- `conditionally_hidden` uses liquid syntax
- it can use the same built-in values as `default`
- earlier parameter answers are available because parameters are processed in order
- it must render to `true` or `false`
- rendered `false` means the parameter is treated as hidden
- a default is required whenever `conditionally_hidden` is used

## Risks / Trade-offs

- [The requested `false => hidden` mapping is counterintuitive] -> Call it out explicitly in docs and examples so template authors do not infer the opposite behavior.
- [Templates may accidentally depend on later parameters] -> Document the declaration-order rule and test only the guaranteed earlier-parameter case.
- [Liquid output may include unexpected strings] -> Enforce strict boolean validation and return a parameter-specific error.
- [Static and dynamic hiddenness rules could drift apart] -> Reuse the existing hidden prompting flow after computing an effective hidden flag instead of creating a second prompt path.

## Migration Plan

- Add the new parameter property and validation to template configuration loading.
- Update parameter resolution to render `conditionally_hidden` in order and derive effective hiddenness before prompting.
- Add focused tests for ordering, validation, boolean rendering, and hidden prompting behavior.
- Update template documentation with examples and caveats.

## Open Questions

- None.