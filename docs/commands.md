# openplate

## Command: config get

Set configuration for the tool (available in ~/.openplate)

```
openplate config get
```

## Command: config set

Set configuration for the tool (available in ~/.openplate)

```
openplate config set --vcs-url https://github.com/my-org
```

### Default Parameters

You can also set default parameters which will override template defaults, example:

```
openplate config set --parameter-default git_org=my-org
```

## Command: init

Add a template to a project

```
openplate init https://github.com/my-org/ot-net-api.git#v1
openplate init git@github.com:my-org/ot-docker.git#v1
openplate init file:///C:/repos/template-catalog#main
```

### Supported Source URL Forms

`init` now uses URL-based sources only.

- Primary syntax: `openplate init <url>`
- Backward-compatible syntax: `openplate init -r <url>`
- Supported URL transports: HTTPS, SSH/scp-style Git URLs, and Git-compatible `file://` URLs
- Optional template sub-folder: append `?path=<relative-template-subdir>`
- Optional branch or tag: append `#<branch-or-tag>`

The legacy nested `project` variant still works for compatibility, but `openplate init` is the documented command.

Examples:

```
openplate init https://github.com/my-org/ot-template.git#v1
openplate init git@github.com:my-org/template-catalog.git?path=python/api#main
openplate init file:///C:/repos/template-catalog#main

# deprecated format
openplate init -r https://github.com/my-org/ot-template.git#v1
```

### Dest Folder

Some templates take advantage of a "sub-folder" to init into.  This allows the template to access both the repo root and the sub-folder for it's files.

- Example:
  
  ```
  openplate init --dest-folder=src git@github.com:my-org/ot-docker.git#v1
  ```

## Command: update

Update the current project with the latest versions of the template

```
openplate update
```

The legacy nested `project` variant still works for compatibility, but `openplate update` is the documented command.

## Prompt JSON Workflow

For machine-driven `init` and `update` runs, OpenPlate can print the prompt state as JSON, let you fill in only the `value` fields you care about, and then consume that JSON without falling back to interactive prompting.

Export the declared prompt tree:

```
openplate init https://github.com/my-org/ot-template.git#v1 --print-prompts-json
openplate update --print-prompts-json
```

Import answers from a file or standard input:

```
openplate init https://github.com/my-org/ot-template.git#v1 --prompts-json-file prompts.json
openplate update --prompts-json-file prompts.json
type prompts.json | openplate init https://github.com/my-org/ot-template.git#v1 --prompts-json-stdin
```

The printed document is a top-level JSON array grouped by template instance. Each template node includes:

- `template`: the raw template reference for that template instance
- `dest_folder`: the raw destination-folder string for that template instance
- `condition`: included when the template declaration has one
- `parameters`: either an object keyed by parameter name or `null` when OpenPlate cannot inspect that template closely enough to enumerate parameter metadata

Each exported parameter entry includes `value`, `default`, `existing`, `description`, `choices`, `hidden`, and `required`.

Hidden parameters are included only when the command uses `--ask-hidden`. Without `--ask-hidden`, hidden parameters are omitted from prompt JSON export and ignored on prompt JSON import.

`value` semantics:

- `null` means do not answer this parameter from JSON; if the parameter is reached, OpenPlate uses the normal runtime fallback such as an existing value or template/default value
- `""` means an intentional blank string answer
- any other non-null string means an explicit supplied answer for that parameter
- omitting `value` is invalid on import

Import semantics:

- OpenPlate uses only `template`, `dest_folder`, and each parameter entry's `value` when importing prompt JSON.
- `condition`, `default`, `existing`, `description`, `choices`, `hidden`, and `required` are informational metadata on import.
- For parameters in scope for the command, any non-null `value` is authoritative even if runtime fallback already has an existing or default value.
- `--ask-again` affects interactive prompting. It does not prevent a non-null prompt JSON `value` from being applied.

Notes:

- `--print-prompts-json` is read-only. It does not update `.openplate.project.yaml` or write template output.
- `--print-prompts-json` is the only mode that walks the full declared sibling tree without applying sibling `condition` filters.
- `condition` is included in exported JSON for visibility only and is ignored on import.
- `--prompts-json-file` and `--prompts-json-stdin` stay on the normal runtime walk and fail instead of prompting if required values or template-command confirmations are still unresolved.
- OpenPlate ignores extra template nodes that are not processed by the run and logs which raw `template` and `dest_folder` entries were ignored.
- OpenPlate warns when supplied parameter values are left unused for a matched template instance.

## Command: project verify

Verify that the project has not drifted from the template. Exit with code -1 if so.

```
openplate project verify
```

## Ask Again

If you want to re-answer questions you can use

```
openplate update --ask-again
```

## Answer "hidden" questions

The answer to some questions are usually assumed, but you have the ability to answer them by specifying the "--ask-hidden" option

```
openplate init --ask-hidden git@github.com:my-org/ot-docker.git#v1
```

or

```
openplate update --ask-hidden
```

The same flag controls prompt JSON scope. With `--ask-hidden`, hidden parameters are included in `--print-prompts-json` output and may be answered through `--prompts-json-file` or `--prompts-json-stdin`. Without it, hidden parameters are omitted from export and ignored on import.

# Template Branches

NOTE: to use a specific branch or tag of a template, append `#branchname` on init. If you omit `#branchname`, you must also pass `--allow-default-branch`.

Examples:

```
openplate init https://github.com/my-org/ot-sometemplate#0.0.9
openplate init --allow-default-branch https://github.com/my-org/ot-sometemplate
```

### Template Catalog Sub-Folders

If a repository stores templates in sub-folders, use `?path=` to select the template root inside the repository clone.

```
openplate init https://github.com/my-org/template-catalog.git?path=templates/net-api#v1
```

## No cache

If you wish for a specific template to be added to this project but not "cached" in the "template cache", specify the `--no-cache` argument.

```
openplate init --no-cache https://github.com/my-org/ot-sometemplate#0.0.9
```

This is useful when you have:

- a template which will use other templates in it's own files
- Needs to NOT send the files of some templates to the child project
- DOES need to pass on some of it's inherited files from particular templates to the child project 
