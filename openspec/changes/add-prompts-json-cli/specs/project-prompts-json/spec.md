## ADDED Requirements

### Requirement: OpenPlate prints prompt state as template-grouped JSON
OpenPlate SHALL support `--print-prompts-json` for `project init` and `project update`. The command SHALL print a JSON array of template nodes instead of interactive prompt text for the declared prompt document.

`--print-prompts-json` SHALL be a read-only planning/export mode. It MUST NOT write files, update project configuration, or otherwise mutate workspace state.

`--print-prompts-json` SHALL be the only mode that walks the full declared template tree without applying sibling `condition` filters. The printed JSON SHALL include the full declared template tree that can be discovered from the template configuration, including conditional sibling declarations. This export MAY include template nodes that later execution does not process.

Each template node SHALL include `template`, `dest_folder`, and `parameters`. If the template declaration includes a condition, the node SHALL also include `condition`. Template and destination values in this JSON SHALL use the raw templated strings rather than rendered values.

When OpenPlate can inspect a declared template node closely enough to enumerate parameter metadata during `--print-prompts-json`, `parameters` SHALL be an object keyed by parameter name. Each parameter entry SHALL include `value`, `default`, `existing`, `description`, `choices`, `hidden`, and `required` so the printed document can be edited and sent back through the import flow.

If print-mode discovery can enumerate a template declaration but cannot load that template's config closely enough to discover parameter metadata during export, OpenPlate SHALL still include the template node and SHALL emit `parameters` as `null`.

In printed and imported parameter entries, `value: null` SHALL mean no value has been supplied, `value: ""` SHALL mean an explicit blank string, and omission of the `value` field SHALL be invalid on import.

#### Scenario: Print prompts JSON for init
- **WHEN** a user runs `openplate project init <source> --print-prompts-json`
- **THEN** OpenPlate prints a JSON array of template nodes for the declared init template tree
- **AND** each template node groups its parameters beneath the template and destination fields

#### Scenario: Print prompts JSON without mutating the workspace
- **WHEN** a user runs `openplate project update --print-prompts-json`
- **THEN** OpenPlate does not write project files or template output files
- **AND** OpenPlate does not update `.openplate.project.yaml` as part of printing the JSON document

#### Scenario: Include conditional sibling declarations in export
- **WHEN** a template declares a sibling template behind a condition
- **THEN** OpenPlate includes that sibling template node in the printed JSON tree
- **AND** `--print-prompts-json` does not use that condition to prune the export tree

#### Scenario: Export unresolved declaration with null parameters
- **WHEN** print-mode discovery can identify a template declaration but cannot load that template's config to enumerate its parameter metadata
- **THEN** OpenPlate still includes the template node in the printed JSON
- **AND** OpenPlate emits `parameters` as `null` for that node

#### Scenario: Print condition metadata without requiring round-trip use
- **WHEN** a template declaration includes a `condition`
- **THEN** OpenPlate includes that raw `condition` string in the printed JSON node
- **AND** the printed `condition` field is treated as informational metadata rather than required input

### Requirement: OpenPlate accepts prompt answers from JSON without prompting
OpenPlate SHALL support `--prompts-json-file <path>` and `--prompts-json-stdin` for `project init` and `project update`. When either flag is used, OpenPlate MUST consume prompt answers from the provided JSON document and MUST NOT fall back to interactive prompting.

`--prompts-json-file` and `--prompts-json-stdin` SHALL use the normal runtime execution walk. They MUST NOT switch to the full-tree, condition-ignoring discovery behavior that is reserved for `--print-prompts-json`.

If required values remain unresolved after applying supplied JSON, OpenPlate MUST fail instead of prompting. OpenPlate MAY fail on the first unresolved prompt rather than aggregating all missing values.

If template-command confirmation would have prompted during the run and the command has not otherwise been authorized, OpenPlate MUST fail instead of prompting.

Within a single command invocation, OpenPlate MUST NOT fetch or clone the same template source once for prompt validation and then again for actual processing. JSON-input execution MUST reuse fetched template sources for validation and execution.

#### Scenario: Supply answers from a file
- **WHEN** a user runs `openplate project update --prompts-json-file prompts.json`
- **THEN** OpenPlate reads prompt answers from `prompts.json`
- **AND** OpenPlate does not prompt for missing values during that run

#### Scenario: Supply answers from stdin
- **WHEN** a user pipes a prompts JSON document to `openplate project init <source> --prompts-json-stdin`
- **THEN** OpenPlate reads prompt answers from standard input
- **AND** OpenPlate does not reuse standard input as an interactive prompt channel

#### Scenario: Missing required value in JSON mode
- **WHEN** JSON-input mode is active and a required parameter still has no resolved value
- **THEN** OpenPlate fails
- **AND** OpenPlate does not ask the user for that value interactively

#### Scenario: JSON input uses the normal runtime walk
- **WHEN** a user runs `openplate project update --prompts-json-file prompts.json`
- **THEN** OpenPlate evaluates sibling conditions as part of the normal runtime execution walk
- **AND** OpenPlate does not switch to the print-only full-tree discovery behavior

#### Scenario: Validation and execution reuse the same source fetch
- **WHEN** a user runs `openplate project init <source> --prompts-json-file prompts.json`
- **THEN** OpenPlate validates prompt input and processes that command without fetching or cloning the same template source twice

### Requirement: OpenPlate validates supplied prompt documents by template instance
OpenPlate SHALL match supplied prompt answers to template instances using the pair `(template, dest_folder)`. The imported JSON document SHALL use the same hierarchical structure that `--print-prompts-json` emits.

During import, OpenPlate MUST use each parameter entry's `value` field as the supplied answer. Other metadata fields in template nodes and parameter entries MAY be present and MUST be ignored for import semantics.

During import, a template node with `parameters: null` MUST be treated as having no supplied parameter values.

During import, OpenPlate MUST reject a parameter entry that omits the `value` field.

OpenPlate MUST reject a supplied JSON document that contains duplicate template nodes with the same `(template, dest_folder)` pair.

If `--print-prompts-json` discovers the same raw `(template, dest_folder)` pair more than once, OpenPlate SHALL emit only the first such node in the exported JSON document.

If a supplied template node does not correspond to a template instance that is actually processed, OpenPlate MUST ignore that supplied node and MUST print a log message that identifies the raw `template` and `dest_folder` that were ignored. If supplied parameter values are present for a matched template instance but are not needed during processing, OpenPlate MUST print warnings for those unused parameters even when debug logging is disabled.

#### Scenario: Round-trip edited prompt document
- **WHEN** a user edits only `value` fields in a document previously printed by `--print-prompts-json`
- **THEN** OpenPlate accepts the document as prompt input
- **AND** OpenPlate ignores unchanged metadata fields such as `condition`, `description`, `default`, and `existing`

#### Scenario: Omitted value field is invalid
- **WHEN** a supplied JSON parameter entry omits the `value` field
- **THEN** OpenPlate fails validation for the imported prompt document

#### Scenario: Blank string is treated as an explicit value
- **WHEN** a supplied JSON parameter entry sets `value` to `""`
- **THEN** OpenPlate treats that parameter as explicitly supplied with a blank string value

#### Scenario: Duplicate template entries in supplied JSON
- **WHEN** a supplied JSON document contains two template nodes with the same `template` and `dest_folder`
- **THEN** OpenPlate fails validation before template processing begins

#### Scenario: Export collapses duplicate discovered template nodes
- **WHEN** `--print-prompts-json` discovers the same raw `template` and `dest_folder` pair more than once
- **THEN** OpenPlate emits only the first discovered node for that pair in the exported JSON document

#### Scenario: Supplied template is not processed
- **WHEN** a supplied JSON document includes a template node that is never processed by the run
- **THEN** OpenPlate ignores that supplied template node
- **AND** OpenPlate prints a log message identifying the raw `template` and `dest_folder` that were ignored

#### Scenario: Supplied parameter is not needed
- **WHEN** a supplied JSON document includes a parameter value for a matched template instance and that parameter is not needed during processing
- **THEN** OpenPlate completes normal processing behavior for the template instance
- **AND** OpenPlate prints a warning about the unused supplied parameter