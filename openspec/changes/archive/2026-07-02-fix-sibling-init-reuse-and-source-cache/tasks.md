## 1. Command-scoped source reuse

- [x] 1.1 Generalize the existing command-scoped template-source cache/provider so top-level recursive template-processing commands can initialize it once and clean it up from a top-level success-or-failure path.
- [x] 1.2 Thread the command-scoped source provider through the recursive template walk and related callers so repeated visits to the same template source reuse one opened source object instead of recloning or reopening per visit.

## 2. Tracked sibling init reuse

- [x] 2.1 Extend recursive walk runtime state to track node-level file-work eligibility separately from per-run completed export state.
- [x] 2.2 Pre-seed file-work eligibility for already tracked sibling nodes when init runs without `--overwrite`, while allowing a single first file-processing pass per node when `--overwrite` is active.
- [x] 2.3 Gate init prechecks, file update work, and init commands on node-level file-work eligibility while preserving recursive export registration and later import visibility for reused sibling nodes.

## 3. Regression coverage

- [x] 3.1 Add regression tests covering later init reuse without `--overwrite`, including no file collision, no sibling file rewrite, preserved import visibility, and no duplicate tracked-template entry.
- [x] 3.2 Add regression tests covering `--overwrite` single-pass behavior for reused sibling nodes, including at-most-once file processing per command and no duplicate tracked-template entry.
- [x] 3.3 Update source-reuse regression coverage to assert command-scoped template-source reuse and cleanup behavior for repeated visits and failure paths.

## 4. Validation

- [x] 4.1 Run focused automated coverage for the recursive walk, sibling reuse, and source reuse changes.