# top-level-init-update-commands Specification

## Purpose
TBD - created by archiving change add-top-level-init-update-commands. Update Purpose after archive.
## Requirements
### Requirement: Top-level init is the primary initialization command
OpenPlate SHALL provide `openplate init` as a first-class top-level command for project initialization. `openplate init` MUST expose the init options and shared project-runtime options required to perform the same initialization workflow currently handled by the project init runtime path.

The shared root-selection option for init SHALL be named `--project-root`.

#### Scenario: Top-level init parses a template source
- **WHEN** a user runs `openplate init https://example.com/template.git#main`
- **THEN** OpenPlate parses the command successfully
- **THEN** OpenPlate routes the invocation through the existing project-init execution flow

#### Scenario: Top-level init accepts shared project options
- **WHEN** a user runs `openplate init --project-root ./workspace --ask-hidden https://example.com/template.git#main`
- **THEN** OpenPlate accepts the shared project-runtime options on the top-level init command

### Requirement: Top-level update is the primary update command
OpenPlate SHALL provide `openplate update` as a first-class top-level command for project updates. `openplate update` MUST expose the update options and shared project-runtime options required to perform the same update workflow currently handled by the project update runtime path.

The shared root-selection option for update SHALL be named `--project-root`.

#### Scenario: Top-level update parses successfully
- **WHEN** a user runs `openplate update`
- **THEN** OpenPlate parses the command successfully
- **THEN** OpenPlate routes the invocation through the existing project-update execution flow

#### Scenario: Top-level update accepts shared project options
- **WHEN** a user runs `openplate update --project-root ./workspace --ask-again`
- **THEN** OpenPlate accepts the shared project-runtime options on the top-level update command

### Requirement: Legacy project init and update commands remain supported
OpenPlate SHALL continue to accept `openplate project init` and `openplate project update` as backward-compatible command forms. The legacy commands MUST preserve the behavior and option set of the corresponding top-level commands, including the renamed `--project-root` shared option.

#### Scenario: Legacy project init remains valid
- **WHEN** a user runs `openplate project init https://example.com/template.git#main`
- **THEN** OpenPlate parses the command successfully
- **THEN** OpenPlate performs the same initialization behavior as `openplate init https://example.com/template.git#main`

#### Scenario: Legacy project update remains valid
- **WHEN** a user runs `openplate project update --update-full`
- **THEN** OpenPlate parses the command successfully
- **THEN** OpenPlate performs the same update behavior as `openplate update --update-full`

#### Scenario: Legacy command accepts the renamed root option
- **WHEN** a user runs `openplate project update --project-root ./workspace --update-full`
- **THEN** OpenPlate accepts the renamed shared root-selection option on the legacy command form

### Requirement: Top-level help advertises only the new primary commands
OpenPlate top-level help SHALL advertise `init`, `update`, `verify`, and `info` as the supported project workflow commands. The legacy `project` command MUST remain functional but MUST NOT appear in top-level help output.

#### Scenario: Top-level help shows init, update, verify, and info
- **WHEN** a user runs `openplate --help`
- **THEN** the help output lists `init`, `update`, `verify`, and `info` as available commands

#### Scenario: Top-level help hides project compatibility command
- **WHEN** a user runs `openplate --help`
- **THEN** the help output does not list `project` as an available top-level command

### Requirement: Documentation presents top-level init and update as the supported syntax
OpenPlate documentation SHALL show `openplate init` and `openplate update` in command examples and primary usage guidance. Documentation MAY mention `openplate project init` and `openplate project update` only as backward-compatible legacy forms.

Documentation SHALL use `--project-root` when showing the shared root-selection option.

#### Scenario: Command documentation uses top-level examples
- **WHEN** a user reads the command documentation or README examples for initialization and update
- **THEN** the examples use `openplate init` and `openplate update` as the primary syntax

#### Scenario: Command documentation uses the renamed root option
- **WHEN** a user reads the shared project-runtime option documentation
- **THEN** the documentation uses `--project-root` rather than `--project-folder`

### Requirement: Top-level verify is the primary verification command
OpenPlate SHALL provide `openplate verify` as a first-class top-level command for project verification. `openplate verify` MUST expose the shared project-runtime options required to perform the same verification workflow currently handled by the existing project verify execution path.

#### Scenario: Top-level verify parses successfully
- **WHEN** a user runs `openplate verify`
- **THEN** OpenPlate parses the command successfully
- **THEN** OpenPlate routes the invocation through the existing project-verify execution flow

#### Scenario: Top-level verify accepts shared project root option
- **WHEN** a user runs `openplate verify --project-root ./workspace`
- **THEN** OpenPlate accepts the shared project-runtime options on the top-level verify command

### Requirement: Legacy project verify command remains supported
OpenPlate SHALL continue to accept `openplate project verify` as a backward-compatible command form. The legacy command MUST preserve the behavior and option set of `openplate verify`.

#### Scenario: Legacy project verify remains valid
- **WHEN** a user runs `openplate project verify --project-root ./workspace`
- **THEN** OpenPlate parses the command successfully
- **THEN** OpenPlate performs the same verification behavior as `openplate verify --project-root ./workspace`

### Requirement: Legacy project-folder option is rejected with migration guidance
OpenPlate SHALL reject `--project-folder` on top-level and legacy init, update, and verify command paths. The rejection message MUST tell the user to use `--project-root` instead.

#### Scenario: Top-level init rejects project-folder
- **WHEN** a user runs `openplate init --project-folder ./workspace https://example.com/template.git#main`
- **THEN** OpenPlate rejects the command
- **THEN** the error message tells the user to use `--project-root`

#### Scenario: Top-level update rejects project-folder
- **WHEN** a user runs `openplate update --project-folder ./workspace`
- **THEN** OpenPlate rejects the command
- **THEN** the error message tells the user to use `--project-root`

#### Scenario: Legacy verify rejects project-folder
- **WHEN** a user runs `openplate project verify --project-folder ./workspace`
- **THEN** OpenPlate rejects the command
 - **THEN** the error message tells the user to use `--project-root`

### Requirement: Top-level info is the primary inspection command
OpenPlate SHALL provide `openplate info` as a first-class top-level command for project inspection. `openplate info` MUST expose the shared project-runtime options required to inspect a project.

The shared root-selection option for info SHALL be named `--project-root`.

#### Scenario: Top-level info parses successfully
- **WHEN** a user runs `openplate info`
- **THEN** OpenPlate parses the command successfully
- **AND** OpenPlate routes the invocation through the project-info execution flow

#### Scenario: Top-level info accepts the shared root option
- **WHEN** a user runs `openplate info --project-root ./workspace`
- **THEN** OpenPlate accepts the shared project-runtime option on the top-level info command

### Requirement: Legacy project info command remains supported
OpenPlate SHALL continue to accept `openplate project info` as a backward-compatible command form. The legacy command MUST preserve the behavior and option set of `openplate info`, including the shared `--project-root` option.

#### Scenario: Legacy project info remains valid
- **WHEN** a user runs `openplate project info --project-root ./workspace`
- **THEN** OpenPlate parses the command successfully
- **AND** OpenPlate performs the same inspection behavior as `openplate info --project-root ./workspace`

