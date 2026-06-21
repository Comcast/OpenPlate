## Why

OpenPlate templates can already coordinate through sibling relationships and file-backed `config_files`, but they do not have a first-class way to publish runtime data from one template instance and consume it from another without writing intermediate files into the project. Templates need a built-in import/export mechanism so sibling templates can share resolved values directly while keeping visibility and collision rules predictable.

## What Changes

- Add template-level `exports` declarations that publish rendered values under a key scoped to a rendered project location after a template instance finishes processing at that location.
- Add template-level `imports` declarations that let a template opt in to named values from sibling templates at a rendered location and expose those values to post-sibling liquid rendering as `imports.<import-key>`.
- Define sibling-only visibility rules so imports can resolve values from required siblings, including recursive sibling trees, but not from unrelated templates that happened to run earlier.
- Define conflict semantics for exports: non-shared keys fail on duplicates, shared keys append into lists, and any mix of shared and non-shared exports for the same location and key fails.
- Keep import visibility out of parameter resolution, sibling declarations, and prompt JSON export, and document exactly which template surfaces can and cannot access imports.
- Expand template documentation with syntax, lifecycle, collision behavior, scope rules, and examples for both imports and exports.

## Capabilities

### New Capabilities
- `template-imports-exports`: Defines template import/export declarations, sibling-scoped visibility, post-sibling liquid availability, duplicate-key behavior, shared list aggregation, and documentation requirements for template authors.

### Modified Capabilities

## Impact

Affected areas include template configuration parsing in `src/openplate/cfg/template_config.py`, runtime template option assembly in `src/openplate/template_processor.py`, recursive sibling processing in `src/openplate/walk/source_template_recursive_walk.py`, command flows that invoke recursive walks, template documentation in `docs/templates.md` and `docs/template-parameters.md`, and focused tests for import/export lifecycle, sibling scoping, and collision handling.