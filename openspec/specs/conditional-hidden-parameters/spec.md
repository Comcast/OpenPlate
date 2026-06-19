# conditional-hidden-parameters Specification

## Purpose
TBD - created by archiving change add-conditionally-hidden-parameters. Update Purpose after archive.
## Requirements
### Requirement: Template parameters support liquid-driven conditional hiddenness
OpenPlate SHALL allow template parameters to declare a `conditionally_hidden` property in `openplate.template.yaml`. The property MUST be rendered with the same liquid processing model used for parameter defaults, and that rendering MUST have access to built-in template values plus parameter answers that were already resolved earlier in declaration order.

#### Scenario: Earlier parameter answers are available to a later condition
- **WHEN** a template defines parameter `deployment_type` before parameter `instance_type`
- **AND** `instance_type` declares `conditionally_hidden` using a liquid expression that references `deployment_type`
- **THEN** OpenPlate evaluates the condition using the resolved answer for `deployment_type`

#### Scenario: Built-in template values are available to the condition
- **WHEN** a parameter declares `conditionally_hidden` using liquid that references built-in values such as `dest_folder` or `project_folder_name`
- **THEN** OpenPlate evaluates the condition with the same built-in template context available to parameter defaults

### Requirement: Conditional hiddenness uses the requested boolean contract
OpenPlate SHALL require `conditionally_hidden` to render to `true` or `false`. A rendered value of `false` MUST cause the parameter to be treated as hidden, and a rendered value of `true` MUST cause the parameter to be treated as visible.

#### Scenario: Rendered false hides the parameter
- **WHEN** a parameter's `conditionally_hidden` expression renders to `false`
- **THEN** OpenPlate treats the parameter as hidden for prompting purposes

#### Scenario: Rendered true leaves the parameter visible
- **WHEN** a parameter's `conditionally_hidden` expression renders to `true`
- **THEN** OpenPlate treats the parameter as visible for prompting purposes

#### Scenario: Invalid rendered boolean is rejected
- **WHEN** a parameter's `conditionally_hidden` expression renders to a value other than `true` or `false`
- **THEN** OpenPlate rejects the template processing step with an error that identifies the parameter and the invalid boolean result

### Requirement: Conditionally hidden parameters preserve normal hidden-parameter behavior
OpenPlate SHALL use `conditionally_hidden` to change a parameter's hiddenness only, not its existence. When a parameter is treated as hidden, OpenPlate MUST keep using the existing hidden-parameter resolution behavior, including default-based auto-answering and `--ask-hidden` overrides.

#### Scenario: Hidden parameter auto-answers from default
- **WHEN** a parameter is treated as hidden because `conditionally_hidden` rendered to `false`
- **AND** the user does not pass `--ask-hidden`
- **THEN** OpenPlate does not prompt for the parameter
- **THEN** OpenPlate resolves the parameter through its default value path

#### Scenario: Ask-hidden still exposes a conditionally hidden parameter
- **WHEN** a parameter is treated as hidden because `conditionally_hidden` rendered to `false`
- **AND** the user passes `--ask-hidden`
- **THEN** OpenPlate prompts for the parameter using the same behavior as other hidden parameters

### Requirement: Template configuration validates conditional hiddenness rules
OpenPlate SHALL reject invalid parameter declarations involving `conditionally_hidden`. A parameter using `conditionally_hidden` MUST declare a default value, and a parameter MUST NOT declare both `hidden` and `conditionally_hidden` at the same time.

#### Scenario: Missing default is rejected
- **WHEN** a parameter declares `conditionally_hidden` and does not declare `default`
- **THEN** OpenPlate rejects the template configuration with an error explaining that a default is required

#### Scenario: Hidden and conditionally_hidden cannot be combined
- **WHEN** a parameter declares both `hidden` and `conditionally_hidden`
- **THEN** OpenPlate rejects the template configuration with an error explaining that the two properties are mutually exclusive

### Requirement: Template documentation explains conditionally hidden parameters
OpenPlate documentation SHALL describe `conditionally_hidden` in the template authoring guide, including the liquid syntax, ordered access to earlier parameter answers, the required default, the `true` or `false` rendering contract, and the rule that rendered `false` means the parameter is hidden.

#### Scenario: Template docs include authoring guidance
- **WHEN** a template author reads the template documentation for parameters
- **THEN** the documentation includes examples and explanatory text for `conditionally_hidden` and its ordering and validation rules

