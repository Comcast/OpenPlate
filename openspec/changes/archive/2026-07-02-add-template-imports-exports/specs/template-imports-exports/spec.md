## ADDED Requirements

### Requirement: Templates can declare imports and exports
OpenPlate SHALL allow templates to declare `exports` and `imports` in `openplate.template.yaml`. Each export MUST declare `key` and `value`, MAY declare `location`, and MAY declare `shared-export`. Each import MUST declare `export-key` and `import-key` and MAY declare `location`. Export and import `location` values MUST default to the current template instance's rendered `dest_folder` when omitted.

#### Scenario: Omitted export location uses the current destination folder
- **WHEN** a template export omits `location`
- **THEN** OpenPlate scopes that export to the current template instance's rendered `dest_folder`

#### Scenario: Omitted import location uses the current destination folder
- **WHEN** a template import omits `location`
- **THEN** OpenPlate resolves that import against exports scoped to the current template instance's rendered `dest_folder`

#### Scenario: Imported values are exposed under the requested alias
- **WHEN** a template declares an import with `import-key: "worker_name"`
- **THEN** OpenPlate exposes the resolved imported value to supported liquid rendering as `imports.worker_name`

### Requirement: Imports resolve only from the recursive sibling tree
OpenPlate SHALL resolve imports only from template instances reached through the current template instance's required sibling declarations, including those siblings' recursive sibling trees. Exports produced by unrelated template instances that happened to run earlier in the same command MUST NOT satisfy an import.

#### Scenario: Direct sibling export can satisfy an import
- **WHEN** template A requires sibling template B
- **AND** template B exports a value matching template A's declared import key and location
- **THEN** OpenPlate resolves template A's import from template B's export

#### Scenario: Recursive sibling export can satisfy an import
- **WHEN** template A requires sibling template B
- **AND** template B requires sibling template C
- **AND** template C exports a value matching template A's declared import key and location
- **THEN** OpenPlate resolves template A's import from template C's export

#### Scenario: Unrelated earlier template export is not visible
- **WHEN** a template instance outside the current template's recursive sibling tree exports a matching key at the same location earlier in the command
- **THEN** OpenPlate does not use that export to satisfy the current template's import

### Requirement: Imports are available only in post-sibling rendering
OpenPlate SHALL make imported values available only after sibling processing completes for the current template instance. OpenPlate SHALL NOT add imported values to the liquid context used for parameter defaults, `conditionally_hidden`, sibling declaration rendering, sibling condition rendering, or prompt JSON export.

#### Scenario: Imports are available to post-sibling liquid rendering
- **WHEN** sibling processing for a template instance has completed and its declared imports have resolved
- **THEN** OpenPlate includes the imported values in supported post-sibling liquid rendering for that template instance

#### Scenario: Parameter defaults do not receive imported values
- **WHEN** OpenPlate renders a parameter default for a template instance
- **THEN** imported values are not included in that liquid context

#### Scenario: Prompt JSON export does not receive imported values
- **WHEN** OpenPlate exports prompt JSON metadata for a template instance
- **THEN** imported values are not included in that liquid context

### Requirement: Exports register after template processing and are reused per template instance
OpenPlate SHALL render and register a template instance's exports only after that template instance finishes processing at its rendered location for the current command. Within a single command, when the same template source and rendered destination folder are reached again, OpenPlate MUST reuse the previously completed export results for that template instance instead of processing it again to produce exports.

#### Scenario: Parent template sees exports only after sibling completion
- **WHEN** template A requires sibling template B
- **AND** template B declares exports used by template A imports
- **THEN** OpenPlate resolves template A's imports only after template B has completed processing at its rendered location

#### Scenario: Repeated sibling references reuse cached exports
- **WHEN** two template instances in the same command both require the same sibling template source at the same rendered destination folder
- **THEN** OpenPlate reuses the completed exports from the first processed sibling instance
- **THEN** OpenPlate does not process that sibling instance again solely to recompute exports

### Requirement: Export collisions obey shared and non-shared rules
OpenPlate SHALL identify exports by rendered `(location, key)`. Non-shared exports MUST be unique for that identity. Shared exports MUST aggregate all values for that identity into a list. If any exporters for the same identity mix shared and non-shared modes, OpenPlate MUST fail template processing.

#### Scenario: Duplicate non-shared export fails
- **WHEN** two template instances export the same rendered `location` and `key`
- **AND** neither export is marked `shared-export: true`
- **THEN** OpenPlate fails template processing with a duplicate export error

#### Scenario: Shared exports aggregate into a list
- **WHEN** multiple template instances export the same rendered `location` and `key`
- **AND** all of those exports are marked `shared-export: true`
- **THEN** OpenPlate aggregates the exported values into a list for that identity

#### Scenario: Mixed shared and non-shared exports fail
- **WHEN** one template instance exports a rendered `location` and `key` as shared
- **AND** another template instance exports the same rendered `location` and `key` as non-shared
- **THEN** OpenPlate fails template processing with an error explaining that shared and non-shared exports cannot be mixed

#### Scenario: Imported shared exports are exposed as a list
- **WHEN** a template imports a rendered `location` and `key` backed by shared exports
- **THEN** OpenPlate exposes the imported value to liquid as a list rather than a scalar string

### Requirement: Unresolved imports fail template processing
OpenPlate SHALL fail template processing when a declared import cannot be satisfied by a visible export with the rendered `location` and `export-key`.

#### Scenario: Missing visible export causes an error
- **WHEN** a template declares an import whose rendered `location` and `export-key` do not match any visible export in its recursive sibling tree
- **THEN** OpenPlate fails template processing with an unresolved import error

### Requirement: Template documentation explains imports, exports, and liquid availability
OpenPlate documentation SHALL describe import and export syntax, location defaults, sibling-scoped visibility, shared versus non-shared collision rules, unresolved import behavior, and which liquid surfaces can access imported values.

#### Scenario: Template docs include an availability guide
- **WHEN** a template author reads the template documentation
- **THEN** the documentation includes guidance showing that imports are available only in post-sibling rendering and are unavailable in parameter defaults, sibling declarations, and prompt JSON export

#### Scenario: Template docs include shared export guidance
- **WHEN** a template author reads the template documentation for exports
- **THEN** the documentation explains that shared exports import as lists and that mixing shared and non-shared exports for the same location and key fails