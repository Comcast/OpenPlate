# Case 6: Reused Shared Sibling Update Recovery

## Purpose / Covered Commands

- `openplate update --update-missing`
- `openplate update --debug`

Matrix facets covered by this case:

- `global --config-file`
- `global --project-root`
- `global --debug`
- `update` tracked sibling reuse with deleted shared outputs
- recursive template-source reuse during update

## Prerequisites

- Run from the repository root in `bash`.
- Ensure `bash`, `python`, and `git` are on `PATH`.

## Exact Commands To Run

```bash
bash ./manual-tests/cleanup-manual-tests.sh case-6
bash ./manual-tests/run-manual-tests.sh case-6
```

## Expected Scripted Outputs

- [manual-tests/artifacts/case-6/01-init-first.log](manual-tests/artifacts/case-6/01-init-first.log) records the initial root-template init that tracks the shared sibling at `.` with the persisted marker parameter.
- [manual-tests/artifacts/case-6/02-init-composite.log](manual-tests/artifacts/case-6/02-init-composite.log) records the later init that adds two sibling trees which both reuse that shared sibling.
- [manual-tests/artifacts/case-6/03-update-shared-reuse.log](manual-tests/artifacts/case-6/03-update-shared-reuse.log) records the `--debug --update-missing` maintenance run after the script deletes the shared sibling outputs.
- [manual-tests/artifacts/case-6/summary.txt](manual-tests/artifacts/case-6/summary.txt) lists the local sources used for the tracked shared sibling and the roots that reference it.
- [manual-tests/work/case-6/update-shared-project/shared/root.txt](manual-tests/work/case-6/update-shared-project/shared/root.txt) and [manual-tests/work/case-6/update-shared-project/shared/tracked-shared.txt](manual-tests/work/case-6/update-shared-project/shared/tracked-shared.txt) are recreated by update after the script deletes them.
- [manual-tests/work/case-6/update-shared-project/service-a/a.txt](manual-tests/work/case-6/update-shared-project/service-a/a.txt) and [manual-tests/work/case-6/update-shared-project/service-b/b.txt](manual-tests/work/case-6/update-shared-project/service-b/b.txt) are recreated and still contain the shared export.
- [manual-tests/work/case-6/update-shared-project/.openplate.project.yaml](manual-tests/work/case-6/update-shared-project/.openplate.project.yaml) still contains only one tracked entry for the shared sibling template at `.`.

## Manual Validation Checklist

- Confirm the script deletes the shared sibling files before update and the update run recreates them successfully.
- Confirm [manual-tests/work/case-6/update-shared-project/shared/tracked-shared.txt](manual-tests/work/case-6/update-shared-project/shared/tracked-shared.txt) exists after update.
- Confirm sibling-specific marker files such as `service-a-shared.txt` and `service-b-shared.txt` do not appear under [manual-tests/work/case-6/update-shared-project/shared](manual-tests/work/case-6/update-shared-project/shared).
- Confirm [manual-tests/work/case-6/update-shared-project/service-a/a.txt](manual-tests/work/case-6/update-shared-project/service-a/a.txt) and [manual-tests/work/case-6/update-shared-project/service-b/b.txt](manual-tests/work/case-6/update-shared-project/service-b/b.txt) both contain `shared-worker` after update.
- Confirm [manual-tests/work/case-6/update-shared-project/.openplate.project.yaml](manual-tests/work/case-6/update-shared-project/.openplate.project.yaml) contains only one tracked entry whose `src_url` points at the shared sibling template and whose `dest_folder` is `.`.
- Confirm [manual-tests/artifacts/case-6/03-update-shared-reuse.log](manual-tests/artifacts/case-6/03-update-shared-reuse.log) contains exactly one `Getting Source from url:` entry for the shared sibling source URL during the update run.

## Cleanup Notes

- The shared cleanup script removes only [manual-tests/work/case-6](manual-tests/work/case-6) and [manual-tests/artifacts/case-6](manual-tests/artifacts/case-6).