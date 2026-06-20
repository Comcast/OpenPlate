# Case 3: Prompt JSON Export and Import

## Purpose / Covered Commands

- `openplate project print-init-json`
- `openplate project print-init-json --verbose`
- `openplate project print-init-json --dest-folder`
- `openplate project print-update-json`
- `openplate init --prompts-json-file`
- `openplate init --prompts-json-stdin`
- `openplate update --prompts-json-file`
- `openplate update --prompts-json-stdin`

Matrix facets covered by this case:

- `global --config-file`
- `global --project-root`
- `global --debug`
- `global --ask-hidden`
- `prompt JSON compact export`
- `prompt JSON verbose export`
- `prompt JSON file import`
- `prompt JSON stdin import`
- `prompt JSON hidden-scope behavior`
- `prompt JSON init placement consistency`
- `prompt JSON update project-context consistency`
- `prompt JSON ignored extra node behavior`
- `prompt JSON ignored extra answer behavior`
- `prompt JSON invalid-choice rejection`
- `project print-init-json read-only behavior`
- `project print-update-json read-only behavior`

## Prerequisites

- Run from the repository root in `bash`.
- Ensure `bash`, `python`, and `git` are on `PATH`.

## Exact Commands To Run

```bash
bash ./manual-tests/cleanup-manual-tests.sh case-3
bash ./manual-tests/run-manual-tests.sh case-3
```

## Expected Scripted Outputs

- [manual-tests/artifacts/case-3/prompts-compact.json](manual-tests/artifacts/case-3/prompts-compact.json) is a JSON array that omits `info` metadata and is printed with the same explicit init `--dest-folder` later used for file import.
- [manual-tests/artifacts/case-3/prompts-verbose.json](manual-tests/artifacts/case-3/prompts-verbose.json) includes `info`, hidden parameter metadata, and sibling declaration metadata for the same explicit init placement.
- [manual-tests/artifacts/case-3/update-prompts.json](manual-tests/artifacts/case-3/update-prompts.json) includes structured update answer entries with `supplied` plus `value`, hidden parameters, and `current` metadata.
- [manual-tests/work/case-3/export-workspace/.openplate.project.yaml](manual-tests/work/case-3/export-workspace/.openplate.project.yaml) does not exist after either export command.
- [manual-tests/artifacts/case-3/03-init-prompts-json-file.log](manual-tests/artifacts/case-3/03-init-prompts-json-file.log) contains both ignored-node and ignored-extra-answer warnings because the import intentionally includes one unmatched node and one unused parameter.
- [manual-tests/work/case-3/file-import-project/generated/imported/root/managed/root.txt](manual-tests/work/case-3/file-import-project/generated/imported/root/managed/root.txt) contains `service=json-file-service` and `hidden=json-hidden`, proving the file import used prompt answers and that print and init used the same explicit init `--dest-folder`.
- [manual-tests/work/case-3/file-import-project/generated/worker/json-file-service/managed/worker.txt](manual-tests/work/case-3/file-import-project/generated/worker/json-file-service/managed/worker.txt) exists because the imported prompt data kept the sibling condition enabled.
- [manual-tests/work/case-3/stdin-import-project/generated/stdin/root/managed/root.txt](manual-tests/work/case-3/stdin-import-project/generated/stdin/root/managed/root.txt) contains `service=json-stdin-service`.
- [manual-tests/work/case-3/stdin-import-project/generated/worker/json-stdin-service/managed/worker.txt](manual-tests/work/case-3/stdin-import-project/generated/worker/json-stdin-service/managed/worker.txt) is intentionally absent because the stdin import disabled the sibling branch.
- [manual-tests/artifacts/case-3/05-print-update-json-file.log](manual-tests/artifacts/case-3/05-print-update-json-file.log) captures the update prompt export for the file-import project before any update answers are changed.
- [manual-tests/artifacts/case-3/06-update-prompts-json-file.log](manual-tests/artifacts/case-3/06-update-prompts-json-file.log) shows update prompt JSON file import completing without interactive prompts while applying hidden values and warning about any intentionally unused supplied answers.
- [manual-tests/artifacts/case-3/07-print-update-json-stdin.log](manual-tests/artifacts/case-3/07-print-update-json-stdin.log) captures the update prompt export for the stdin-import project and proves the export still includes the full declared tree for later edits.
- [manual-tests/artifacts/case-3/08-update-prompts-json-invalid-choice.log](manual-tests/artifacts/case-3/08-update-prompts-json-invalid-choice.log) shows update prompt JSON rejecting an invalid choice value under the same rules as init.
- [manual-tests/artifacts/case-3/09-update-prompts-json-stdin.log](manual-tests/artifacts/case-3/09-update-prompts-json-stdin.log) shows update prompt JSON stdin import completing without interactive prompts and restoring the sibling branch with the supplied answers.

## Manual Validation Checklist

- Open the compact and verbose init artifacts side by side and confirm only the verbose export carries `info` metadata.
- Confirm the export workspace remained read-only from OpenPlate’s perspective by checking that [manual-tests/work/case-3/export-workspace](manual-tests/work/case-3/export-workspace) has no project config or generated template files.
- Confirm the file-import log includes the warning text for both ignored unmatched nodes and ignored unused prompt parameters.
- Confirm the init prompt export and init import commands use the same explicit `--dest-folder` in the recorded steps.
- Confirm the update prompt export and update import commands use the same selected project root and tracked project state.
- Confirm the update prompt JSON artifact includes hidden parameters and structured `supplied` plus `value` entries.
- Confirm the invalid-choice log shows update prompt JSON rejecting an unsupported choice value.
- Confirm all recorded source URLs inside the JSON artifacts still point at the local materialized catalog repo for this case.

## Cleanup Notes

- The shared cleanup script removes only [manual-tests/work/case-3](manual-tests/work/case-3) and [manual-tests/artifacts/case-3](manual-tests/artifacts/case-3).