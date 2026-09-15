schema=fm-task-inbox.v1
at=2026-09-15T20:13:04Z
--
This is the repair phase of orch-dynamic-workflow (one repair pass). An independent reviewer audited fm/tally-build @7bbb08c. Read its report in full: /tmp/orchflows-e2e/home/data/tally-review/report.md . Verdict: ready with one listed repair.
Repairs to make:
1. Invalid UTF-8 input currently escapes the file-error handling (tally.py opens inputs as UTF-8 but main catches only OSError), producing a UnicodeDecodeError traceback. Report a decode failure as a concise file-read error on stderr with the same exit code as other file-read failures (1), distinct from usage errors (2). Handle it for standard input as well as named files. Document the accepted encoding (UTF-8) in the README. Add a unit test covering an invalid-UTF-8 input.
No findings deferred. Make no other changes.
Then run python3 -m unittest from the repo root (all must pass), commit on fm/tally-build with a clear message, and append a fresh line to your status file: done: ready in branch fm/tally-build
