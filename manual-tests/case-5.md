# Case 5: Reused Sibling Init and Source Reuse

## Purpose / Covered Commands

- `openplate init`
- `openplate init --overwrite`
- `openplate init --debug`

Matrix facets covered by this case:

- `global --config-file`
- `global --project-root`
- `global --debug`
- `init` tracked sibling reuse without `--overwrite`
- `init` tracked sibling reuse with `--overwrite`
- recursive template-source reuse within one command

## Prerequisites

- Run from the repository root in `bash`.
- Ensure `bash`, `python`, and `git` are on `PATH`.

## Exact Commands To Run

```bash
bash ./manual-tests/cleanup-manual-tests.sh case-5
bash ./manual-tests/run-manual-tests.sh case-5
```

## Expected Scripted Outputs

- [manual-tests/artifacts/case-5/01-init-first.log](manual-tests/artifacts/case-5/01-init-first.log) records the initial root-template init that materializes the shared sibling at `.`.
- [manual-tests/artifacts/case-5/02-init-reuse-no-overwrite.log](manual-tests/artifacts/case-5/02-init-reuse-no-overwrite.log) records the later init that reuses the already tracked sibling without `--overwrite`.
- [manual-tests/artifacts/case-5/03-init-reuse-overwrite.log](manual-tests/artifacts/case-5/03-init-reuse-overwrite.log) records the `--debug` overwrite run that reaches the same shared sibling through two different sibling trees.
- [manual-tests/artifacts/case-5/summary.txt](manual-tests/artifacts/case-5/summary.txt) lists the local sources used for the initial, importing, and overwrite roots plus the shared sibling source.
- [manual-tests/work/case-5/sibling-project/shared/root.txt](manual-tests/work/case-5/sibling-project/shared/root.txt) preserves the user-modified content after the no-overwrite reuse run and returns to the template content after the overwrite run.
- [manual-tests/work/case-5/sibling-project/shared/tracked-shared.txt](manual-tests/work/case-5/sibling-project/shared/tracked-shared.txt) remains the only shared marker artifact that exists throughout the case.
- [manual-tests/work/case-5/sibling-project/second/b.txt](manual-tests/work/case-5/sibling-project/second/b.txt) contains the export imported from the reused sibling after the no-overwrite reuse run.
- [manual-tests/work/case-5/sibling-project/service-a/a.txt](manual-tests/work/case-5/sibling-project/service-a/a.txt) and [manual-tests/work/case-5/sibling-project/service-b/b.txt](manual-tests/work/case-5/sibling-project/service-b/b.txt) both contain the shared export after the overwrite run.
- [manual-tests/work/case-5/sibling-project/.openplate.project.yaml](manual-tests/work/case-5/sibling-project/.openplate.project.yaml) contains only one tracked entry for the shared sibling template at `.` even after both later init runs.

## Manual Validation Checklist

- Confirm the no-overwrite reuse run succeeds instead of failing on an existing shared sibling file at `.`.
- Confirm [manual-tests/work/case-5/sibling-project/shared/root.txt](manual-tests/work/case-5/sibling-project/shared/root.txt) still contains the user-modified content immediately after the no-overwrite reuse run.
- Confirm [manual-tests/work/case-5/sibling-project/second/b.txt](manual-tests/work/case-5/sibling-project/second/b.txt) contains `shared-worker`, proving the later init could still import from the reused sibling.
- Confirm the overwrite reuse run restores [manual-tests/work/case-5/sibling-project/shared/root.txt](manual-tests/work/case-5/sibling-project/shared/root.txt) to the template content.
- Confirm [manual-tests/work/case-5/sibling-project/shared/tracked-shared.txt](manual-tests/work/case-5/sibling-project/shared/tracked-shared.txt) exists while sibling-specific marker files such as `import-shared.txt`, `service-a-shared.txt`, and `service-b-shared.txt` do not appear.
- Confirm [manual-tests/work/case-5/sibling-project/service-a/a.txt](manual-tests/work/case-5/sibling-project/service-a/a.txt) and [manual-tests/work/case-5/sibling-project/service-b/b.txt](manual-tests/work/case-5/sibling-project/service-b/b.txt) both contain `shared-worker`.
- Confirm [manual-tests/work/case-5/sibling-project/.openplate.project.yaml](manual-tests/work/case-5/sibling-project/.openplate.project.yaml) contains only one tracked entry whose `src_url` points at the shared sibling template and whose `dest_folder` is `.`.
- Confirm [manual-tests/artifacts/case-5/03-init-reuse-overwrite.log](manual-tests/artifacts/case-5/03-init-reuse-overwrite.log) contains exactly one `Getting Source from url:` entry for the shared sibling source URL during the overwrite run.


## Cleanup Notes

- The shared cleanup script removes only [manual-tests/work/case-5](manual-tests/work/case-5) and [manual-tests/artifacts/case-5](manual-tests/artifacts/case-5).