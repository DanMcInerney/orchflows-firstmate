# Linux acceptance driver

[tools/linux-acceptance.py](../tools/linux-acceptance.py) runs an isolated,
readonly component through a prepared FirstMate candidate on Herdr. Its current
native observer supports Claude Code. It supports one Work or one explicitly
authorized Review; it does not implement general workflow composition or
Codex authentication.

Run from the repository root inside Ubuntu/WSL. Use a candidate reproduced by
the distribution preparation tool, such as the retained candidate printed by
[the Linux check runner](linux-development.md). All candidate/package bytes are
copied and hashed into a new private Linux filesystem namespace before use.
The default staging root is /tmp/of-accept. Compact private configuration paths
and a pre-launch byte-length check keep Herdr sockets within Linux capacity;
a deeply nested --work-root is refused before any endpoint starts.
Native Linux bash, git, python3, lsof, jq, node, tasks-axi, timeout, Herdr,
Treehouse and Claude must be on the explicitly constructed Linux PATH.

~~~sh
python3 -B tools/linux-acceptance.py doctor \
  --candidate "$FIRSTMATE_CANDIDATE" --package packages/orchflows-firstmate \
  --bin-dir "$LINUX_RUNTIME_BIN"

python3 -B tools/linux-acceptance.py fixture \
  --candidate "$FIRSTMATE_CANDIDATE" --package packages/orchflows-firstmate \
  --bin-dir "$LINUX_RUNTIME_BIN"
~~~

Doctor validates dependencies and paths. Fixture stages exact sources, creates
a committed no-origin repository, prepares the ordinary scout brief and calls
the real attachment owner. It reads no authentication and starts no server,
watcher, endpoint or model. Its receipt says fixture-prepared-no-live-run.

For an actual trial, provide CLAUDE_CODE_OAUTH_TOKEN in the invoking process
environment, or select one credential file with --claude-access-token-file.
The two sources are mutually exclusive. A selected file must be a user-owned
regular file; the driver selects only its Claude access token and expiration.
It never copies a credential file or refresh token, invokes login, or changes
the source cache. There is no implicit machine-specific cache path. An
environment token's known Unix expiration can be supplied with
--access-token-expires-at; otherwise its remaining lifetime is recorded as
unknown. A known expiration must exceed the trial observation timeout by at
least 180 seconds. Authenticated workers use the token in their private process
environment, and the normal watcher environment excludes it.

~~~sh
# Real independent Review with ordinary watcher observation beyond 240 seconds.
python3 -B tools/linux-acceptance.py run \
  --candidate "$FIRSTMATE_CANDIDATE" --package packages/orchflows-firstmate \
  --bin-dir "$LINUX_RUNTIME_BIN" --primitive Review \
  --claude-access-token-file "$SELECTED_CLAUDE_CACHE"

# Separate Work recovery case: replace the root while the child is pending.
python3 -B tools/linux-acceptance.py run \
  --candidate "$FIRSTMATE_CANDIDATE" --package packages/orchflows-firstmate \
  --bin-dir "$LINUX_RUNTIME_BIN" --restart \
  --claude-access-token-file "$SELECTED_CLAUDE_CACHE"
~~~

Omit the credential-file option when using the environment token. No model or
effort override is passed. Review attaches with primitive Review and policy
explicit-audit; the root uses the Review client flag. Unsupported Review
candidates fail rather than falling back to Work.

The ordinary watcher case defaults to a 330-second foreground child sleep,
240 seconds of required observed waiting, and a 900-second observation timeout.
The restart case defaults to a 60-second child sleep and replaces the root
through fm-control.sh after the launched child has been observed for 15 seconds.
Use --component-delay, --replace-after, --minimum-waiting-span and --timeout to
choose another bounded case. The driver sets neither Claude foreground
environment variable: that profile must come from the candidate's launch owner.

A trial asks the real root to submit the same exact request twice, read both
retained files completely, gather, then deliver its normal scout report. The
driver observes native successful submit responses for matching request/child
identities and native full Read completions before the first literal gather
and the durable first owner acknowledgement. Repeated gather updates the
current acknowledging parent generation while preserving that first timestamp. It verifies retained result/report digests, one
component, source facts, unchanged input/worktrees, and ordinary root done.
Recovery additionally requires a changed root generation, the same accepted
child and gather by the replacement generation. This scoped native transcript
observer is an acceptance instrument, not a product transcript-correlation API.

The watcher is armed through the ordinary FirstMate owner and is never
automatically rearmed. Its current-owner samples, beacon ages, lock identity
and filtered execution trace are retained. A steady case fails if the watcher
ends while the component is still pending. Intentional root replacement may
surface attention, so restart mode retains that observation without treating
it as a steady-watcher failure. Passing recovery alone establishes neither
continuous watcher health during replacement nor a supervisor wake/drain/rearm
cycle. Native background commands and detached-process custody remain separate
acceptance work.

All FirstMate task operations use the supplied candidate's owners. The
candidate's named Herdr lab manages the trial endpoint, with a separately
verified private default sentinel for its fleet-state tripwire. Shutdown uses
ordinary task exit, ordinary teardown, guarded lab teardown and the
identity-checked private sentinel. There is no forced task teardown or broad
process kill. Cleanup failures and remaining processes whose current working
directories lie inside the namespace make the run fail and retain the
namespace for investigation; that scoped inventory is not proof about arbitrary
processes that deliberately escape the namespace.

The private evidence directory contains the receipt, briefs, retained reports,
operation logs, watcher samples and filtered trace. Failed and timed-out
operations retain scrubbed stdout/stderr without recording argv or environment. Token values are scrubbed
from driver-written output. Raw native session transcripts remain private and
are not copied into evidence. Preserve useful sanitized evidence under ignored
scratch storage, and record actual outcomes separately from package checks.
The driver never removes historical trial artifacts or installs a package into
an active profile.

## Project enablement and a selected custom workflow

Use --enabled to call the project's enable owner once before ordinary root
spawn. Fixture mode verifies no task attachment was created by enablement;
the actual spawn must create it. --custom-workflow also supplies a complete
acceptance:inspect-facts library, then changes its source after enablement.
The native observer requires a full read of the retained skill before
submission and its receipt marker in the root report.

~~~sh
python3 -B tools/linux-acceptance.py run \
  --candidate "$FIRSTMATE_CANDIDATE" --package packages/orchflows-firstmate \
  --bin-dir "$LINUX_RUNTIME_BIN" --enabled --custom-workflow --restart \
  --claude-access-token-file "$SELECTED_CLAUDE_CACHE"
~~~

Current prepared candidates supply context for both enabled and explicit-attach
trials. Workers use short client calls; the observer verifies the exact retained
client path and rejects manual authority flags in enabled trials. Historical
receipts retain the driver versions that actually produced them.

## Driver verification

~~~sh
python3 -B -m unittest discover -s tools -p test_acceptance.py -v
~~~

The repaired driver passed thirteen focused Linux tests covering explicit
auth selection and expiration, unchanged cache bytes, symlink refusal, output
redaction, snapshot boundaries, replacement identity/gather failures and full
read order across native sessions, hidden early acknowledgement, actual socket
capacity, actual owner-state labels with positive child activity, and scrubbed
failure/timeout diagnostics. A real no-live fixture preparation passed
against a prepared Linux candidate with an ext4 namespace and empty scoped
process inventory after cleanup. Those fixture checks are separate from the actual Work/replacement and
Review results in [increment verification](review-verification.md). The long
Review receipt preserves its original parser failure alongside a separate
corrected assessment; the final short Review and recovery receipts passed.


## Dynamic and composed custom acceptance

The targeted --dynamic case uses the same private runtime, lab, auth and cleanup
owners. It enables the retained package, then explicitly selects dynamic through
ordinary fm-spawn. Two writer Work components implement independent stock/label
helpers with tests and commits. The root reads/gathers each exact result, joins
both outputs with Git, checks, requests one fresh Review of that clean candidate,
and makes its one repair/check pass before ordinary scout completion.

~~~sh
python3 -B tools/linux-acceptance.py run \
  --candidate "$FIRSTMATE_CANDIDATE" --package packages/orchflows-firstmate \
  --bin-dir "$LINUX_RUNTIME_BIN" --dynamic --component-delay 0 \
  --minimum-waiting-span 0 --timeout 1800 \
  --claude-access-token-file "$SELECTED_CLAUDE_CACHE"

python3 -B tools/linux-acceptance.py run \
  --candidate "$FIRSTMATE_CANDIDATE" --package packages/orchflows-firstmate \
  --bin-dir "$LINUX_RUNTIME_BIN" --dynamic --custom-workflow --restart \
  --component-delay 180 --minimum-waiting-span 0 --timeout 1800 \
  --claude-access-token-file "$SELECTED_CLAUDE_CACHE"
~~~

The custom skill composes the retained dynamic skill; no custom execution
adapter is involved. Its source changes after enablement. The observer requires
the retained custom read/marker, per-request replay identity, full reads before
each gather and actual joined helper behavior/tests. Recovery triggers only
after one result is gathered while another accepted Work remains pending, and
requires those identities to survive ordinary fm-control relaunch.

These are targeted composition trials. They record ordinary watcher outcomes
but assert no steady-watcher duration or full supervisor wake/drain/rearm cycle.
The driver executes the four actual reviewed source/test files and compares
maker-owned bytes against each retained writer output, so Review of placeholder
tests cannot pass. It separately tests the final HEAD and observes the root's
successful literal final test command after Review acknowledgement. Both writer
output refs must still resolve after ordinary teardown. The final check receipt
and reviewed/final commits are retained separately.

Nineteen driver checks now include per-request observation, reviewed-placeholder
refusal, actual final-check order, and literal client calls with output-only
pipelines. The native observer identifies the first literal client command; it
rejects shell lists and substitutions and still requires the independent durable
owner acknowledgement. See [dynamic verification](dynamic-verification.md) for the
original failed observer receipt and separate corrected assessment.
Fixture mode remains non-live and reads no authentication.

The recovery fixture explicitly requires short root polls and prompt gathering of
each ready maker. Relaunch eligibility requires a gathered Work and another Work
still running, recorded as pending_work. A later running Review cannot satisfy
this acceptance window. Failed or manually assisted diagnostic runs remain separate
from clean acceptance even when their final artifact is correct.
