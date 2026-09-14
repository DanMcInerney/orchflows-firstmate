# Bounded leaf workflow authoring

The dev.8 increment uses the existing dynamic ship/local-only profile to author
a complete non-delegating leaf workflow or guidance library, trial it in a fresh
Work component, and deliver the library with committed trial evidence. It adds
no workflow executor, protocol field, capability flag or workspace owner.

The [package client contract](../packages/orchflows-firstmate/docs/firstmate-client.md#bounded-leaf-authoring)
owns the exact scope. The retained Build skill supplies composition:
author Work, ordinary root Git join, fresh leaf trial Work, recorded findings,
one exact-candidate Review and one repair/check pass. A component loads the leaf
in its own context and cannot call Work, Review or fleet commands. General
composing Build, nesting and SelfImprove remain gated.

New authored source lives in the assigned repository. Its exact clean commit
reaches the trial through ordinary FirstMate component positioning. Resolve
library-relative paths inside that component's own worktree and core dependencies
from its immutable retained package. The authored source is a trial input;
it does not mutate the retained launch catalog or register a skill by name.

The root gathers the complete trial output and commits output and provenance
outside the deliverable library before Review. Relaunch keeps the accepted
author/trial identities, gathered results and joined files. The replacement
rereads the selected authoring and leaf instructions and checks the remaining
obligations. Ordinary local-only landing and teardown preserve the library and
trial record; writer output refs retain their existing archival contract.

A same-project leaf trial proves that bounded use. A portability claim requires
an unrelated-project trial with an ordinary brief and declared dependencies
before final Review, arranged by FirstMate's existing outer owners. User-home
installation, general composed workflow authoring and nested trials are separate.

## Targeted acceptance

The existing Linux acceptance driver accepts --authoring, which selects dynamic
local-only delivery. It reuses its current namespace, authentication, lab,
watcher, root relaunch, full-result reads, landing and cleanup owners.

~~~sh
python3 -B tools/linux-acceptance.py run \
  --candidate "$FIRSTMATE_CANDIDATE" --package packages/orchflows-firstmate \
  --bin-dir "$LINUX_RUNTIME_BIN" --authoring --restart \
  --component-delay 90 --minimum-waiting-span 0 --timeout 1500 \
  --model claude-sonnet-5 --effort high \
  --claude-access-token-file "$SELECTED_CLAUDE_CACHE"
~~~

The bounded fixture authors a complete release-triage leaf library and its
layered guidance. A fresh read-only Work reads that library and its declared
release input, and returns the actual JSON output. Root replacement occurs
after gathering the author while the leaf trial is running. The root commits
the exact trial output and provenance, requests one Review and delivers.

The observer checks native complete reads in the fresh trial and replacement
root, exact authored/trialed/reviewed/final library trees, immutable validation
inputs, trial output and identities, Review ordering, ready-branch landing,
post-cleanup behavior and archival refs. This targeted acceptance expects one
unchanged authored library, one leaf trial and one Review; it does not certify
repair-and-retrial sequences, portability or every valid Build composition.
Fixture mode reads no authentication and launches no worker.

Executed checks and actual worker outcomes belong in
[verification](leaf-authoring-verification.md); a prepared fixture is not a
runtime pass.
