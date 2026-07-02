## 1. Template configuration schema

- [x] 1.1 Add `imports` and `exports` declaration models and deserialization support in `src/openplate/cfg/template_config.py`, including `shared-export` parsing and default-location handling.
- [x] 1.2 Add configuration validation for required import/export fields and any invalid shared-export combinations that can be detected before runtime.

## 2. Recursive walk runtime behavior

- [x] 2.1 Introduce a lightweight command-scoped run-state for recursive walks that tracks completed template instances, cached exports, and the global export registry by rendered `(location, key)`.
- [x] 2.2 Thread that run-state through init, update, and verify recursive walk entry points without changing the existing sibling identity contract for template source plus rendered destination folder.
- [x] 2.3 Resolve declared imports only after sibling recursion, limit visible producers to the recursive sibling tree, and inject resolved imports into post-sibling template options as `imports.<import-key>`.
- [x] 2.4 Register exports only after the current template instance finishes processing at its rendered location, rebuild template options before export rendering, and reuse cached exports when the same template source and rendered destination folder are reached again in the same command.
- [x] 2.5 Enforce export collision rules so duplicate non-shared exports fail, shared exports aggregate into lists, and any shared/non-shared mix at the same rendered `(location, key)` fails.
- [x] 2.6 Raise clear runtime errors for unresolved imports when no visible export matches the rendered location and export key.

## 3. Focused verification

- [x] 3.1 Add parsing and validation tests for template import/export declarations, including omitted locations and shared-export parsing.
- [x] 3.2 Add recursive-walk tests covering direct sibling imports, recursive sibling imports, and the rule that unrelated earlier exports do not satisfy imports.
- [x] 3.3 Add runtime tests covering repeated sibling reuse, post-processing export registration timing, unresolved imports, duplicate non-shared export failures, shared list aggregation, and shared/non-shared conflict failures.
- [x] 3.4 Add regression coverage showing that imports are not injected into parameter defaults, conditional hiddenness, sibling declaration rendering, sibling condition rendering, or prompt JSON export.

## 4. Documentation

- [x] 4.1 Update `docs/templates.md` with import/export syntax, examples, conflict rules, and a liquid-availability matrix that highlights post-sibling-only import visibility.
- [x] 4.2 Update `docs/template-parameters.md` with a note that `imports` is a runtime object whose availability is documented in the template authoring guide.