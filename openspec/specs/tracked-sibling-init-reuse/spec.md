# tracked-sibling-init-reuse Specification

## Purpose
TBD - created by archiving change fix-sibling-init-reuse-and-source-cache. Update Purpose after archive.
## Requirements
### Requirement: Init reuses already tracked sibling nodes without reapplying files by default
When an `init` run reaches a sibling template node that is already tracked in the project with the same template source and destination folder, OpenPlate SHALL continue the recursive walk for that node without treating it as a fresh init target.

If `--overwrite` is not active for that command, OpenPlate MUST NOT run file-collision prechecks, file creation, file update work, or init commands for that already tracked sibling node. OpenPlate SHALL still make that node's exports available to later nodes reached during the same command.

#### Scenario: Later init does not collide on an already tracked sibling
- **WHEN** a project already tracks sibling template `S` at destination folder `.` from an earlier init run
- **AND** a later `openplate init` run reaches the same sibling template `S` again through another template declaration
- **AND** the later init run does not use `--overwrite`
- **THEN** OpenPlate does not report collisions for `S`'s existing files
- **THEN** OpenPlate does not rewrite `S`'s files
- **THEN** OpenPlate does not add a duplicate tracked template entry for `S`

#### Scenario: Later init can still import from an already tracked sibling
- **WHEN** a project already tracks sibling template `S` at destination folder `.`
- **AND** a later `openplate init` run reaches `S` again through another template declaration
- **AND** the later init run imports an export produced by `S`
- **THEN** OpenPlate resolves that import from `S` during the same command

### Requirement: Overwrite allows at most one file-processing pass per tracked sibling node per command
When `--overwrite` is active and an `init` run reaches an already tracked sibling node, OpenPlate SHALL allow file-processing work for that node at most once for the unique template-node identity reached by that command.

After that first file-processing pass completes for the node, later encounters of the same template source and destination folder during the same command MUST reuse the completed node result without additional file-processing work.

#### Scenario: Overwrite updates an already tracked sibling only once per command
- **WHEN** a project already tracks sibling template `S` at destination folder `.`
- **AND** an `openplate init --overwrite` run reaches `S` more than once through recursive sibling declarations during the same command
- **THEN** OpenPlate performs file-processing work for `S` at most once during that command
- **THEN** later encounters of `S` during that command do not perform additional file-processing work

#### Scenario: Overwrite does not duplicate tracked sibling entries
- **WHEN** a project already tracks sibling template `S` at destination folder `.`
- **AND** a later `openplate init --overwrite` run reaches the same sibling template `S` again
- **THEN** OpenPlate does not add a duplicate tracked template entry for `S`

### Requirement: Repeated template-source visits reuse one opened source per command
Within a single OpenPlate command execution, repeated visits to the same template source identity SHALL reuse one opened template source instance rather than independently reopening or recloning that source for each visit.

OpenPlate MUST keep that source available for the duration of the command and MUST clean it up once when the top-level command finishes, including when the command exits because of an error.

#### Scenario: Recursive sibling visits reuse one opened source
- **WHEN** a single OpenPlate command reaches the same template source URL more than once during recursive processing
- **THEN** OpenPlate reuses one opened source instance for those visits during that command

#### Scenario: Command-scoped source cleanup runs after failure
- **WHEN** a command opens one or more template sources during recursive processing
- **AND** the command later fails before finishing normally
- **THEN** OpenPlate still closes and cleans up the opened template sources before the command exits

