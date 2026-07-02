## Why

OpenPlate currently reprocesses sibling templates that are already tracked in an existing project during later `init` runs. That creates file-collision failures without `--overwrite`, unnecessary rewrites with `--overwrite`, and repeated source fetches for the same template URL within a single command.

## What Changes

- Change recursive init behavior so an already tracked sibling template is still walked for runtime export visibility but does not re-run file-processing work unless the current command explicitly allows a first overwrite pass for that node.
- Add command-scoped template source reuse so init and related recursive walks reuse the same opened template source for repeated references instead of cloning or reopening the same URL on each visit.
- Add focused regression tests for tracked-sibling reuse without `--overwrite`, tracked-sibling reuse with `--overwrite`, and repeated source reuse within a single command.

## Capabilities

### New Capabilities
- `tracked-sibling-init-reuse`: Init-time recursive template traversal for already tracked sibling nodes, including single-run file-work reuse and command-scoped template source reuse.

### Modified Capabilities

## Impact

- Recursive template walk behavior during `openplate init`, especially sibling reuse and overwrite handling.
- Command-scoped template source acquisition and cleanup for URL-backed templates.
- Regression coverage around sibling collisions, overwrite behavior, export visibility, and source reuse.