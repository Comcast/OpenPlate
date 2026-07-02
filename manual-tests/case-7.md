# Case 7: Reused Shared Sibling Verify

## Purpose / Covered Commands

- `openplate verify`
- `openplate verify --debug`

Matrix facets covered by this case:

- `global --config-file`
- `global --project-root`
- `global --debug`
- `verify` tracked sibling reuse with deleted shared outputs
- recursive template-source reuse during verify

## Prerequisites

- Run from the repository root in `bash`.
- Ensure `bash`, `python`, and `git` are on `PATH`.

## Exact Commands To Run

```bash
bash ./manual-tests/cleanup-manual-tests.sh case-7
bash ./manual-tests/run-manual-tests.sh case-7
```

## Expected Scripted Outputs

- [manual-tests/artifacts/case-7/01-init-first.log](manual-tests/artifacts/case-7/01-init-first.log) records the initial root-template init that tracks the shared sibling at `.`.
- [manual-tests/artifacts/case-7/02-init-composite.log](manual-tests/artifacts/case-7/02-init-composite.log) records the later init that adds two sibling trees which both reuse that shared sibling.
- [manual-tests/artifacts/case-7/03-verify-shared-pass.log](manual-tests/artifacts/case-7/03-verify-shared-pass.log) records the passing `--debug` verify run on the intact tree.
- [manual-tests/artifacts/case-7/04-verify-shared-missing.log](manual-tests/artifacts/case-7/04-verify-shared-missing.log) records the failing `--debug` verify run after the script deletes the tracked shared readonly files.
- [manual-tests/artifacts/case-7/summary.txt](manual-tests/artifacts/case-7/summary.txt) lists the local sources used for the tracked shared sibling and the roots that reference it.
- [manual-tests/work/case-7/verify-shared-project/.openplate.project.yaml](manual-tests/work/case-7/verify-shared-project/.openplate.project.yaml) still contains only one tracked entry for the shared sibling template at `.`.

## Manual Validation Checklist

- Confirm the first verify run succeeds on the intact repeated-shared-sibling tree.
- Confirm [manual-tests/artifacts/case-7/03-verify-shared-pass.log](manual-tests/artifacts/case-7/03-verify-shared-pass.log) contains exactly one `Getting Source from url:` entry for the shared sibling source URL.
- Confirm the script deletes only the tracked shared readonly files before the second verify run.
- Confirm [manual-tests/artifacts/case-7/04-verify-shared-missing.log](manual-tests/artifacts/case-7/04-verify-shared-missing.log) reports `shared/root.txt missing` once and `shared/tracked-shared.txt missing` once.
- Confirm [manual-tests/artifacts/case-7/04-verify-shared-missing.log](manual-tests/artifacts/case-7/04-verify-shared-missing.log) does not mention `shared/service-a-shared.txt missing` or `shared/service-b-shared.txt missing`.
- Confirm [manual-tests/work/case-7/verify-shared-project/.openplate.project.yaml](manual-tests/work/case-7/verify-shared-project/.openplate.project.yaml) contains only one tracked entry whose `src_url` points at the shared sibling template and whose `dest_folder` is `.`.

## Cleanup Notes

- The shared cleanup script removes only [manual-tests/work/case-7](manual-tests/work/case-7) and [manual-tests/artifacts/case-7](manual-tests/artifacts/case-7).