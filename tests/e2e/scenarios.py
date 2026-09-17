"""Captain requests, not worker instructions. All composition belongs to FirstMate."""

CONTRACT = """Build moneylog.py using only Python's standard library. The interface is
python3 moneylog.py INPUT, where INPUT is a UTF-8 CSV path or - for stdin.
Require exactly the header account,amount and exactly two fields per data row.
Trim surrounding whitespace from account and amount; reject an empty account.
Amounts must match [+-]?[0-9]+(?:\\.[0-9]{1,2})? using ASCII digits; no exponent,
NaN, infinity, thousands separators or rounding. Aggregate exact cents per
account, preserving arbitrary integer precision. Output one JSON object mapping
accounts to strings with exactly two decimal places, with keys sorted by Unicode
code point, a final newline, and normalized zero (never -0.00). A header-only
input yields {}. Proper CSV quoting, commas in names, and non-ASCII names work.
On any malformed row, invalid header/amount, missing file or invalid UTF-8,
exit 2, emit a useful error on stderr, and emit no stdout at all, even when valid
rows preceded the error. A data error identifies its 1-based physical CSV line.
No arguments or extra positional arguments exit 2; --help exits 0.
Include unittest-discoverable tests, a README with runnable examples, and a
committed examples/sample.csv whose documented result is accurate.
Do not add packaging, third-party dependencies or unrelated features."""

AUTHORITY = """These are disposable E2E projects. Their registered local-only +yolo
posture authorizes you to merge green, in-scope changes through your normal
guarded local delivery. Do not modify FirstMate or the core plugin. Use normal
FirstMate dispatch for every assignment and retain its normal records. Do not
invent model rules for these tests. When the entire request has been delivered,
reviews and any repairs are complete, and native cleanup is done, reply with
the completion marker below on its own line. Never print it for a blocked or
partial result."""


def requests(core, home):
    library = home / "projects/orchflows-home/libraries/cashflow"
    return {
        "dynamic": f"""In cashbook-dynamic: {CONTRACT}
{AUTHORITY}
Completion marker: E2E_CASE_DONE dynamic""",
        "author": f"""Use orch-build-workflow by reading
{core}/skills/orch-build-workflow/SKILL.md. In orchflows-home create the cashflow
library and its reusable cashflow:change workflow for small Python CLI changes.
Save it at libraries/cashflow/skills/change/SKILL.md. It must first obtain a
separate read-only planning result covering edge cases and acceptance checks,
then have one maker implement using that plan, then a fresh independent reviewer
check the exact candidate. Compose the core Work/Review primitives; the workflow
defines these assignments and their dependencies. Require the maker to preserve
the applied plan in docs/change-plan.md. Return actionable review findings to
the maker for one repair pass when needed. Keep execution settings wholly with
FirstMate: do not save harness, model, effort or vendor preferences. Include the
usual manifests, manual-only invocation policy, dependency declaration and a
trial record. Use portable dependencies, with no absolute machine paths in
reusable instructions. Availability by explicit name/path is sufficient; no
global plugin registration is needed. Trial the authored workflow through
FirstMate on the fresh cashbook-trial project before final library review.
The exact trial request is: {CONTRACT}
Return observed trial findings to the author, record limits honestly, and give
the final library reviewer the trial evidence. Refresh the home catalogs in an
author worker before delivery if needed. {AUTHORITY}
Completion marker: E2E_CASE_DONE author""",
        "saved": f"""Run cashflow:change by reading
{library}/skills/change/SKILL.md. Use the saved composition as written on the
fresh cashbook-saved project. Core dependency root: {core}.
This is a separate reuse of the saved library, not another authoring task.
Request: {CONTRACT}
{AUTHORITY}
Completion marker: E2E_CASE_DONE saved""",
        "regression": f"""In cashbook-dynamic, add an optional --total flag to moneylog.py.
When present, output a JSON object with exactly two keys: accounts (the existing
sorted account-to-amount mapping) and total (the exact sum as a two-decimal
string). Without the flag keep the existing interface, output and errors
unchanged. The flag works with both stdin and file input. An empty ledger's
total is 0.00; account names such as accounts and total remain ordinary names.
Update tests and the README with a runnable --total example. {AUTHORITY}
Completion marker: E2E_CASE_DONE regression""",
    }
