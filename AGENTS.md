Before proposing or running end-to-end OpenPlate commands, read [manual-tests/index.md](manual-tests/index.md) and the relevant numbered case document under [manual-tests](manual-tests).

Use the checked-in commands, fixtures, and validation checklists in [manual-tests/case-1.md](manual-tests/case-1.md), [manual-tests/case-2.md](manual-tests/case-2.md), [manual-tests/case-3.md](manual-tests/case-3.md), and [manual-tests/case-4.md](manual-tests/case-4.md) instead of reconstructing workflows from memory.

When a checked-in manual workflow needs to seed git repos, set repo-local git identity, change branch state, or create commits, use the sandboxed runner behavior described in [manual-tests/index.md](manual-tests/index.md) and do not target the live OpenPlate checkout for those git mutations.

Do not commit or push changes unless the user explicitly asks for that action in the current request or you first confirm that they want you to do it now. A previous request to commit or push does not carry forward to later work.