## Context

OpenPlate already has the two runtime ingredients that make template-to-template data exchange plausible in the current structure: sibling templates are resolved recursively before the current template performs its main work, and liquid-backed template options are recomputed at a few important checkpoints. What it does not have is a first-class runtime registry for values produced by one template instance and consumed by another.

Today template authors can work around this by writing files that later flow through `config_files`, but that couples data exchange to project files and makes sibling coordination depend on intermediate output rather than runtime intent. The new import/export feature needs to fit into the existing command and walker flow without taking on the larger refactor of runtime lifecycle ownership.

Two current constraints drive this design:

- sibling templates are keyed effectively by template source plus rendered destination folder, and later sibling references do not override parameters for an already-known sibling instance
- parameter defaults, conditional hiddenness, sibling declarations, sibling conditions, and prompt JSON export all happen before the post-sibling render phase where imports should become visible

## Goals / Non-Goals

**Goals:**
- Add `imports` and `exports` declarations to template configuration.
- Allow a template to import values only from required siblings, including recursive sibling trees.
- Make imports available only in post-sibling liquid surfaces, not in parameter-related or prompt-export surfaces.
- Register exports after a template instance finishes processing at its rendered location.
- Cache completed template-instance exports within a single command so repeated references to the same template source and rendered destination reuse the same export results.
- Enforce duplicate-key behavior for shared and non-shared exports.
- Document syntax and liquid availability clearly for template authors.

**Non-Goals:**
- Refactor the broader command runtime into a new lifecycle or session architecture.
- Change the existing sibling-parameter precedence model where the first resolved template source and rendered destination instance wins.
- Make imports available during parameter defaults, `conditionally_hidden`, sibling declaration rendering, sibling condition rendering, or prompt JSON export.
- Persist exports into `.openplate.project.yaml` or any other cross-command state.
- Add optional imports or special cycle handling beyond existing sibling behavior.

## Decisions

### 1. Add explicit import/export schema objects in template configuration

`openplate.template.yaml` will gain two new top-level sections:

- `exports`
  - `key`: required, liquid-rendered
  - `value`: required, liquid-rendered
  - `location`: optional, liquid-rendered, defaulting to the current rendered `dest_folder`
  - `shared-export`: optional boolean, default `false`
- `imports`
  - `export-key`: required, liquid-rendered
  - `location`: optional, liquid-rendered, defaulting to the current rendered `dest_folder`
  - `import-key`: required, liquid-rendered local alias used as `imports.<import-key>`

These declarations belong in `src/openplate/cfg/template_config.py` beside the existing sibling, conditional, and multiplex declarations because they are template authoring constructs, not project-state constructs.

Alternatives considered:
- Reuse `config_files` for this feature. Rejected because the user specifically wants to remove file-backed exchange as the primary mechanism.
- Infer imports from export keys automatically. Rejected because visibility must remain explicit and scoped, not ambient.

### 2. Keep the feature inside the current walker flow with a small per-command run-state

Instead of introducing a larger runtime refactor, the command entry points should create a lightweight run-state object and thread it through `source_template_recursive_walk_single()` and `source_template_recursive_walk_all()`.

That run-state should hold:

- a completed-node cache keyed by template source plus rendered destination folder
- cached exports for each completed node
- a command-scoped export registry keyed by rendered `(location, key)`

The key should intentionally match the current sibling identity semantics: template source plus rendered destination folder, not parameters. That preserves the current first-reference-wins sibling behavior while making later export lookups stable.

Alternatives considered:
- Store exports on `ProjectConfig` or `ProjectTemplateConfig`. Rejected because exports are command-scoped runtime data and would create persistence churn.
- Keep exports only in local stack variables during recursion. Rejected because update and verify can revisit the same template instance later in the same command.

### 3. Resolve imports only after sibling recursion and before post-sibling rendering

The current template flow already resolves siblings before the main init, verify, or update work. Imports should hook directly into that boundary:

1. resolve parameters and build the base liquid context as today
2. recurse into sibling templates
3. collect the visible export producers from those sibling subtrees
4. resolve declared imports against those visible producers
5. build post-sibling template options by adding `imports`
6. run init, verify, update, and init-command rendering with that post-sibling context
7. rebuild template options one final time and render/register exports

The final rebuild before export registration is important because `compile_template_options()` may observe destination-backed `config_files`, and exports are meant to run after the template has finished processing at that location.

Alternatives considered:
- Inject imports into all liquid contexts globally. Rejected because it conflicts with the agreed scope and would drag parameter and prompt flows into the feature.
- Register exports before the current template runs. Rejected because the user wants exports to use resolved config and post-processing state.

### 4. Enforce sibling-only visibility by filtering imports through recursive sibling producers

The command-scoped export registry is global for conflict detection, but import resolution must not be global. Each template instance should resolve imports only against exports produced by its required siblings and those siblings' recursive sibling trees.

Practically, each recursive sibling call should return or populate the set of producer nodes that became visible through that subtree. The current template then resolves its declared imports by filtering the global export registry to entries produced by those visible nodes.

This preserves the rule that unrelated templates cannot satisfy an import merely because they ran earlier in the command.

Alternatives considered:
- Resolve imports from the entire export registry. Rejected because it makes run order visible and breaks sibling scoping.
- Require every recursive sibling producer to be declared directly. Rejected because the requested behavior includes recursive sibling visibility.

### 5. Cache completed node exports and skip duplicate processing within a command

When the same template source and rendered destination folder are referenced again during the same command, OpenPlate should reuse the cached exports for that completed node instead of processing that template instance again. This is necessary for two reasons:

- it keeps import resolution order-independent when multiple templates rely on the same sibling
- it prevents update and verify from re-registering the same exports when they encounter a template instance both recursively and as a tracked top-level template

This cache is command-scoped only and does not alter the persisted project configuration.

Alternatives considered:
- Let repeated nodes run and de-duplicate registry writes afterward. Rejected because side effects such as init commands, update writes, and repeated validation would still happen twice.
- Include parameters in the cache key. Rejected because it would conflict with the current sibling identity contract.

### 6. Define strict shared and non-shared export collision semantics

Export identity is rendered `(location, key)`.

- Non-shared exports must be unique at that identity.
- Shared exports append values into a list at that identity.
- Any mix of shared and non-shared exporters at the same identity is an error, regardless of which one appears first.

Imported shared values are exposed to liquid as lists. Imported non-shared values are exposed as scalar strings.

Alternatives considered:
- Let shared exports overwrite non-shared exports or vice versa. Rejected because the user explicitly wants mixed modes to fail.
- Merge non-shared duplicates by first-wins behavior. Rejected because collisions must fail for predictability.

### 7. Document liquid availability explicitly in the template docs

`docs/templates.md` should add a concise matrix showing which liquid contexts can access:

- built-in template values
- resolved parameter answers
- `config_files`
- `imports`

This matrix should call out that imports are available only after sibling resolution and are not available in parameter defaults, conditional hiddenness, sibling declarations, sibling conditions, or prompt JSON export. `docs/template-parameters.md` should add a short note pointing template authors back to the template guide for `imports` availability.

## Risks / Trade-offs

- [The current command flow still threads several runtime arguments through multiple layers] -> Keep the new run-state narrow and local to recursive walk entry points instead of broadening scope further.
- [Existing sibling identity ignores parameter differences for repeated template source and destination pairs] -> Preserve that behavior intentionally and document it as unchanged rather than attempting a larger refactor in this change.
- [Liquid use in unsupported surfaces may appear blank rather than erroring if authors reference `imports` directly there] -> Document availability clearly and keep unresolved-import errors tied to explicit `imports` declarations.
- [Shared export list ordering will reflect command traversal order] -> Treat order as execution order and keep documentation focused on membership rather than stable sorting guarantees.
- [Cycles that depend on upstream exports may still fail through normal sibling ordering] -> Keep this out of scope and rely on existing sibling behavior; unresolved imports surface the problem clearly.

## Migration Plan

- Add template-config schema support for `imports` and `exports`.
- Thread a lightweight run-state through init, update, and verify recursive walk entry points.
- Resolve sibling-scoped imports after sibling recursion, inject them into post-sibling template options, and register exports after the current template finishes processing.
- Add focused tests for direct siblings, recursive siblings, unresolved imports, repeated sibling reuse, shared/non-shared collisions, and shared list imports.
- Update template documentation with syntax, lifecycle, and liquid-availability guidance.

No persisted project migration is required because imports and exports are command-scoped runtime behavior.

## Open Questions

- None.