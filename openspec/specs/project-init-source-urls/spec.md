# project-init-source-urls Specification

## Purpose
TBD - created by archiving change simplify-project-init-sources. Update Purpose after archive.
## Requirements
### Requirement: Project init accepts exactly one URL source
The `openplate project init` command SHALL accept exactly one template source reference, supplied either as a positional URL argument or through `-r` / `--url`. The command MUST reject invocations that provide both forms at the same time. The command MUST continue to require an explicit branch or tag fragment in the source reference unless `--allow-default-branch` is supplied.

#### Scenario: Positional URL source
- **WHEN** a user runs `openplate project init <repo-url>#<ref>`
- **THEN** OpenPlate treats the positional argument as the template source reference

#### Scenario: Legacy URL flag
- **WHEN** a user runs `openplate project init -r <repo-url>#<ref>`
- **THEN** OpenPlate accepts the source reference and initializes from the same URL-based source flow as the positional form

#### Scenario: Conflicting URL inputs
- **WHEN** a user supplies both a positional source reference and `-r` / `--url`
- **THEN** OpenPlate rejects the command and reports that only one URL source may be provided

#### Scenario: Missing ref without override
- **WHEN** a user supplies a URL source reference without `#<ref>` and does not pass `--allow-default-branch`
- **THEN** OpenPlate rejects the command and reports that a branch or tag is required

### Requirement: Removed init source options are rejected with migration guidance
The `openplate project init` command MUST reject `-n` / `--name` and `-f` / `--folder` source options. The rejection message MUST direct users to the supported URL-based replacements.

#### Scenario: Removed name source option
- **WHEN** a user runs `openplate project init -n <template-name>#<ref>`
- **THEN** OpenPlate rejects the command and explains that explicit URL sources must be used instead

#### Scenario: Removed folder source option
- **WHEN** a user runs `openplate project init -f <folder>`
- **THEN** OpenPlate rejects the command and explains that local Git repositories must be referenced with `file://`

### Requirement: URL source references support optional template paths
OpenPlate SHALL support URL source references in the form `<repo-location>[?path=<relative-template-subdir>][#<ref>]`. When `path` is present, OpenPlate MUST normalize it as a relative path and MUST reject values that are empty, absolute, or resolve outside the cloned repository.

#### Scenario: Remote repository sub-folder
- **WHEN** a user runs `openplate project init "https://github.com/my-org/template-catalog.git?path=python/api#v1"`
- **THEN** OpenPlate clones the repository at `https://github.com/my-org/template-catalog.git`
- **THEN** OpenPlate uses `python/api` inside the clone as the template root

#### Scenario: Invalid template path
- **WHEN** a user supplies `?path=../outside`
- **THEN** OpenPlate rejects the source reference and reports that the template path must stay within the repository

### Requirement: URL source references support file URLs
OpenPlate SHALL accept Git-compatible `file://` URLs anywhere a URL source reference is accepted, including positional invocation and `-r` / `--url` invocation.

#### Scenario: File URL source
- **WHEN** a user runs `openplate project init "file:///C:/repos/template-catalog?path=python/api#main"`
- **THEN** OpenPlate clones the repository from the `file://` location
- **THEN** OpenPlate uses the selected template path inside that cloned repository

### Requirement: Documentation describes supported project init URL formats
OpenPlate documentation SHALL describe the supported `project init` URL forms, including positional URL usage, `-r` / `--url` compatibility, SSH and HTTPS Git URLs, `file://` URLs, optional `?path=` sub-folder selection, `#<ref>` selection, and `--allow-default-branch` behavior.

#### Scenario: Command documentation examples
- **WHEN** a user reads the `project init` command documentation
- **THEN** the documentation includes examples for remote Git URLs, `file://` URLs, positional URL invocation, and repository sub-folder selection with `?path=`

### Requirement: Persisted project template references use URL sources only
OpenPlate SHALL treat URL source references as the only supported persisted template source form in project configuration.

When loading `.openplate.project.yaml`, OpenPlate SHALL ignore `src_name`, `src_folder`, and `template_src_folder` when those values are missing, null, or blank.

When loading `.openplate.project.yaml`, OpenPlate MUST fail with a runtime error if `src_name`, `src_folder`, or `template_src_folder` contains a non-blank value. The error MUST explain that URL-backed template references are required.

OpenPlate runtime state MUST NOT retain populated `src_name`, `src_folder`, or `template_src_folder` values after load.

#### Scenario: Blank legacy template source fields are ignored
- **WHEN** a persisted project config includes `src_name: ""`, `src_folder: ""`, or `template_src_folder: ""`
- **THEN** OpenPlate loads the project config successfully
- **THEN** OpenPlate ignores those blank legacy fields

#### Scenario: Populated src_name is rejected on load
- **WHEN** a persisted project config includes `src_name: legacy-template`
- **THEN** OpenPlate fails to load the project config
- **THEN** the error explains that persisted template sources must use `src_url`

#### Scenario: Populated src_folder is rejected on load
- **WHEN** a persisted project config includes `src_folder: ./templates/example`
- **THEN** OpenPlate fails to load the project config
- **THEN** the error explains that local template repos must be referenced by URL instead

#### Scenario: Populated template_src_folder is rejected on load
- **WHEN** a persisted project config includes `template_src_folder: ./templates/example`
- **THEN** OpenPlate fails to load the project config
- **THEN** the error explains that URL-backed template references are required

### Requirement: Documentation omits legacy source-resolution configuration
OpenPlate documentation SHALL describe URL-backed template source references as the only supported source contract. Documentation MUST NOT present `vcs_url`, `template_prefix`, `src_name`, or `src_folder` as supported runtime configuration for project template resolution.

#### Scenario: Source configuration documentation uses URL-only guidance
- **WHEN** a user reads the command documentation or README guidance for template source selection
- **THEN** the documentation describes URL-backed template references only
- **THEN** the documentation does not describe legacy name-based or folder-based template source resolution as supported runtime behavior## ADDED Requirements

### Requirement: Persisted project template references remain URL-backed only
Project configuration data SHALL store and load template references through `src_url` only.

OpenPlate MUST reject non-blank legacy name- or folder-based source fields when loading persisted project configuration.

#### Scenario: Persisted blank legacy source fields are tolerated
- **WHEN** a tracked template entry contains blank `src_name` or `src_folder` values
- **THEN** OpenPlate ignores those blank fields and continues loading the template entry from `src_url`

#### Scenario: Persisted non-blank name source is rejected
- **WHEN** a tracked template entry contains a non-empty `src_name`
- **THEN** OpenPlate halts with a runtime error explaining that URL-backed template references are now required

#### Scenario: Persisted non-blank folder source is rejected
- **WHEN** a tracked template entry contains a non-empty `src_folder`
- **THEN** OpenPlate halts with a runtime error explaining that URL-backed template references are now required

