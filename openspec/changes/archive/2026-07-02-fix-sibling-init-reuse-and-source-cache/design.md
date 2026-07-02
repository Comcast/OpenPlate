## Context

OpenPlate's recursive template walk currently treats an already tracked sibling node as a configuration reuse but still runs the normal file-processing path for that node during a later `init` command. That mismatch causes file collisions without `--overwrite` and redundant rewrites with `--overwrite`.

At the same time, the recursive walk opens template sources ad hoc. For URL-backed templates that means repeated clone/open/cleanup cycles within a single command, even when the same template source URL is reached multiple times. Prompt-document collection already has a command-scoped source cache, but init and related recursive walks do not use it.

This change needs to correct both behaviors without weakening export visibility for templates that legitimately import from an already tracked sibling during a later init run.

## Goals / Non-Goals

**Goals:**
- Prevent later `init` runs from re-running file work for an already tracked sibling node when `--overwrite` is not active.
- Allow `--overwrite` to perform file work for an already tracked sibling node at most once per unique template node during a command.
- Preserve export registration so a later init run can still import from an already tracked sibling node.
- Reuse opened template sources across a command and clean them up once at the top level, including failure paths.
- Add regression coverage for sibling reuse semantics and command-scoped source reuse.

**Non-Goals:**
- Change prompt JSON identity, import, or export behavior.
- Redefine sibling matching identity beyond the existing source-plus-destination node key.
- Add persistent on-disk source caches across commands.
- Refactor all source consumers to a new abstraction if they are not part of the recursive template-processing flow touched by this fix.

## Decisions

### 1. Separate file-work eligibility from per-run completion

The recursive walk currently has one completion memo, which is sufficient for export reuse within a run but not for deciding whether file work should happen when a node is already tracked before the current command starts.

The runtime state should distinguish:

- whether a node's file work is still eligible during this command
- whether a node has already been fully processed for this command's export visibility

This allows three important cases:

- existing tracked sibling + no overwrite: skip all file work immediately, but still process the node once for exports
- existing tracked sibling + overwrite: allow one file-processing pass during this command, then reuse the completed result on later encounters
- newly discovered sibling: perform normal file work once, then reuse the completed result on later encounters

Alternatives considered:
- Pre-mark existing siblings as fully completed. Rejected because later imports during the same command would lose export registration for those nodes.
- Add special-case sibling branches outside the main walker. Rejected because it would duplicate traversal logic and diverge from the existing node memoization model.

### 2. Keep walking reused siblings, but gate all file phases behind node-level eligibility

When the walker reaches an already tracked sibling node, it should still load template configuration, resolve parameters and imports, discover any nested siblings, and register exports. The change is that init prechecks, update file work, verify-style collision checks, and init commands must run only when that node still has file-work eligibility for the current command.

This preserves the useful runtime contract that later init nodes can import from already tracked siblings while removing the broken behavior of treating those siblings as fresh init targets.

Alternatives considered:
- Skip reused siblings entirely. Rejected because later init runs can validly import from exports produced by an already tracked sibling node.
- Run a reduced verification pass instead of normal file work. Rejected because existing verification semantics still report collisions and do not match the intended sibling reuse contract.

### 3. Scope overwrite to one mutating pass per unique node per command

`--overwrite` should not mean "re-run every reused sibling every time it is encountered." It should mean that a tracked sibling node is allowed one file-processing pass during that command if it is encountered, after which later visits reuse the already completed node result.

The existing template node key based on source identity plus normalized destination folder is the correct command-scoped deduplication key for this behavior.

Alternatives considered:
- Never mutate already tracked siblings, even with `--overwrite`. Rejected because the desired behavior explicitly allows a first overwrite pass.
- Allow every encounter to overwrite. Rejected because it preserves the redundant update behavior and keeps repeated sibling declarations expensive.

### 4. Promote command-scoped source ownership to the top level

Template source lifetime should be owned by a command-scoped provider that is initialized once at the top-level command entry, reused by recursive consumers, and cleaned up in one top-level `finally` path. The existing prompt-document source cache is the right starting point for this abstraction.

Consumers should request an already opened source object from the provider rather than independently cloning or entering a new source each time. The provider should key reuse by the existing source cache key and keep cleanup responsibility centralized.

Alternatives considered:
- Keep per-visit `with source:` ownership in the recursive walker. Rejected because it forces repeated clone/open/cleanup work and defeats source reuse.
- Return only folder paths from the provider. Rejected because callers also need source metadata such as resolved refs and repo SHA.

### 5. Make cleanup unconditional on both success and failure paths

Command-scoped source reuse only helps if cleanup remains reliable. The provider should be closed exactly once by the top-level command orchestration, including when a recursive walk raises an exception.

This aligns init/update recursive processing with the cleanup semantics already used by prompt-document collection.

Alternatives considered:
- Let each consumer close the provider opportunistically. Rejected because it reintroduces ambiguous ownership and risks premature cleanup.

## Risks / Trade-offs

- [File-work state and completion state can diverge if not updated consistently] -> Keep both states inside one runtime-state object keyed by the same template node identity and cover overwrite and non-overwrite cases with focused regression tests.
- [Command-scoped source reuse extends source lifetime] -> Keep provider ownership at the command boundary and always close sources in reverse order from a top-level `finally` path.
- [Broader source reuse can affect commands beyond init if wired incorrectly] -> Limit the initial implementation to the recursive template-processing flows touched by this fix and keep prompt export behavior aligned with the same provider contract.
- [Later imports depend on exports from reused siblings] -> Preserve one full non-file processing pass for reused siblings and add a regression test that imports from an already tracked sibling during a later init run.

## Migration Plan

- Introduce or generalize a command-scoped template source provider and thread it through the relevant top-level command entry points.
- Extend recursive walk runtime state with node-level file-work eligibility separate from node completion.
- Pre-seed file-work eligibility for already tracked sibling nodes when `--overwrite` is not active.
- Gate init/update file phases and init commands on file-work eligibility while keeping export registration active.
- Add focused regression tests for no-overwrite sibling reuse, overwrite single-pass behavior, later-import export visibility, and command-scoped source reuse.

No persisted project-file migration is required.

## Open Questions

- None.