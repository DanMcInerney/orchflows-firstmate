"""Declared leaf-authoring request and immutable acceptance input/checks."""
import json

INPUT = {
    "release": "2026.09",
    "changes": [
        {"id": "R-1", "title": "Remember filters", "status": "shipped", "tested": True},
        {"id": "R-2", "title": "Export rows", "status": "shipped", "tested": False},
        {"id": "R-3", "title": "Team presets", "status": "planned", "tested": False},
        {"id": "R-4", "title": "Old experiment", "status": "discarded", "tested": True},
    ],
}
EXPECTED = {"release": "2026.09", "ready": ["R-1"], "needs_checks": ["R-2"], "planned": ["R-3"]}
LIBRARY = "release-library"
SKILL = "skills/triage-release/SKILL.md"
REQUIRED = ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json",
            "README.md", "references/library-context.md", "guidance/release.md",
            SKILL, "trials/request.md", "trials/expected-behavior.md")

# These independent assertions are committed before authoring; the observer
# also verifies their exact bytes at Review, delivery and after cleanup.
TESTS = """import hashlib\nimport json
from pathlib import Path
import unittest

class Delivery(unittest.TestCase):
    def test_complete_library(self):
        root = Path('release-library')
        for name in REQUIRED:
            self.assertTrue((root / name).is_file(), name)
            self.assertTrue((root / name).read_text().strip(), name)
        for name in ('plugin.json', '.claude-plugin/plugin.json', '.codex-plugin/plugin.json'):
            manifest = json.loads((root / name).read_text())
            self.assertEqual(manifest['name'], 'release-triage')
            self.assertEqual(manifest['version'], '0.1.0')
        skill = (root / 'skills/triage-release/SKILL.md').read_text()
        self.assertTrue(skill.startswith('---'))
        self.assertIn('name: triage-release', skill)
        self.assertNotIn('/tmp/', skill)
        self.assertNotIn('/mnt/c/', skill)

    def test_real_trial_output(self):
        output = json.loads(Path('trial-output.json').read_text())
        self.assertEqual(output, EXPECTED)

    def test_distinct_digest_objects(self):
        output = Path('trial-output.json').read_bytes()
        retained = json.loads(Path('trial-result.json').read_text())
        record = json.loads(Path('trial-record.json').read_text())
        canonical = json.dumps(retained, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
        self.assertEqual(record['result_digest'], hashlib.sha256(canonical).hexdigest())
        self.assertEqual(record['report_digest'], hashlib.sha256(output).hexdigest())
        self.assertEqual(record['report_digest'], retained['report_digest'])

    def test_committed_trial_record(self):
        record = json.loads(Path('trial-record.json').read_text())
        for key in ('author_output_commit', 'trial_input_commit', 'trial_child', 'result_digest',
                    'request_id', 'limits', 'findings', 'preparation', 'intervention'):
            self.assertTrue(record.get(key), key)
        self.assertEqual(record['request_id'], 'leaf-trial-v1')
        self.assertIn('same-project', record['limits'])
""" + "\nREQUIRED = " + repr(REQUIRED) + "\nEXPECTED = " + repr(EXPECTED) + "\n"


def spec(delay, delivery):
    return (
        "Use the retained orch-build-workflow skill for its bounded non-delegating leaf authoring case, "
        "inside the admitted dynamic local-only root. Read the ENTIRE retained Build skill, core "
        "guidance/orchflows.md and guidance/writing.md with native Read before authoring and after any relaunch. "
        "FirstMate owns all Work/Review, worktrees, recovery and delivery. Use only literal standalone "
        "python3 -B ABSOLUTE_RETAINED_CLIENT_PATH submit/status/gather commands with launch context and no "
        "authority flags or shell wrappers. For submit and gather, NO pipeline or output redirection is "
        "allowed: keep their full JSON response visible to the native observer. Request JSON has "
        "request_id,assignment,primitive,writable and "
        "lives in recorded tasktmp. Submit every identical request twice consecutively to prove replay. "
        "After any relaunch, replay each existing accepted request.body twice unchanged with the same "
        "ID and current context, even if already complete or gathered; these return the same component "
        "and do not create another Work or Review. Do this for all three requests before readiness. "
        "Before every first gather, use native Read without offset/limit to read the ENTIRE exact retained "
        "report_path and result_path returned by status.\n\n"
        "First submit author-maker-v1, Work/writable true, owning only release-library/. Ask the maker to "
        "author the complete release-triage 0.1.0 library: root/Claude/Codex manifests, README, "
        "references/library-context.md, guidance/release.md, skills/triage-release/SKILL.md, "
        "trials/request.md and trials/expected-behavior.md. For the three manifests use name, version, "
        "description and skills './skills/' consistently; do not spend the trial surveying example libraries. "
        "This project-scoped leaf loads in the caller "
        "and creates zero children. Its only input is a caller-named release JSON file with release and "
        "changes records containing id,title,status,tested. It returns exactly a JSON object with release "
        "copied from input, ready containing sorted ids of shipped+tested changes, needs_checks containing "
        "sorted ids of shipped+untested changes, and planned containing sorted planned ids. Omit discarded "
        "changes. Put these quality/selection preferences in release guidance; the skill owns input, "
        "dependency loading, applying that guidance and output. No fixed sample answers. Declare retained "
        "orchflows-firstmate writing guidance and the library-local release guidance through the context "
        "reference. Use relative library links and supplied retained core root, never author-machine paths, "
        "global home discovery or native/fleet delegation. Preserve the task worker settings without saving "
        "them as workflow defaults. The maker checks links/manifests, commits only its library and returns "
        "the complete output commit and checks. It does not run its own Review or perform the trial.\n\n"
        "Gather the author result, inspect and cherry-pick its input_commit..output_commit into your worktree. "
        "Read the complete newly joined skill and dependency guidance using native Read. Keep HEAD clean. "
        "Then submit leaf-trial-v1, Work/writable false. This fresh trial assignment must contain only the "
        "following ordinary request and required execution paths/controls, not the expected answer or the "
        "author's preparation: Load release-library/skills/triage-release/SKILL.md and its declared context "
        "and guidance from YOUR OWN worktree, apply it to release-input.json, and return its JSON result as "
        "the ENTIRE component report, without Markdown fences. Use native Read with no offset/limit for the "
        "whole skill, references/library-context.md, guidance/release.md and release-input.json. Resolve core "
        "writing guidance from the retained core root supplied by the component launch. "
        f"Begin with a {delay}-second foreground sleep with timeout at least 420000 ms. "
        "Do not change project files or delegate; follow ordinary component completion. Do not copy the "
        "parent worktree path into this assignment.\n\n"
        "While this trial runs, keep short status polls so the driver can exercise ordinary root relaunch. "
        "After relaunch reread the retained Build skill and the joined leaf/context/guidance before continuing; "
        "use the same accepted requests, children and gathered author result. "
        "Gather the completed trial after full retained reads. Copy its report bytes exactly to trial-output.json "
        "at your worktree root. Write trial-record.json beside it, outside release-library/, containing "
        "author_output_commit, trial_input_commit, trial_child, request_id, result_digest from actual retained "
        "identities. result_digest means the request.result_digest of canonical full result.json, not its "
        "report_digest; add report_digest separately for the raw output bytes. Copy the complete retained "
        "result.json bytes to trial-result.json so the delivered record can be verified independently. Include "
        "preparation, intervention (say none if none), findings, and limits including same-project. "
        "This bounded trial does not establish portable or nested workflow parity. Do not modify release-input.json "
        "or test_delivery.py. Run python3 -B -m unittest discover -v; if trial fails, record the failure honestly "
        "and stop rather than manufacturing its output. Commit output, retained trial-result.json and trial record.\n\n"
        "Now submit final-review-v1, Review/writable false, once (identical replay allowed), for an independent "
        "audit of that exact clean library and committed trial evidence under Orchflows/writing Review guidance. "
        "Give it author/trial identities and limits. It must not repair or delegate. Read/gather its result, "
        "perform the one repair/check pass and commit repairs. Do not change a trialed library and claim its "
        "old trial covers the change: rerun affected leaf behavior as scoped Work if needed, recording limits. "
        "No second Review. Finish with exactly this standalone literal final test command, replacing the path: "
        "python3 -B -m unittest discover -v > ABSOLUTE_TASKTMP/dynamic-final-check.txt 2>&1. Do not append cat or any other command; "
        "read its output in a separate native Read afterward. "
        "Write diagnostic dynamic-delivery.md under tasktmp with author/trial/reviewer identities, exact reviewed "
        "and final commits, findings, repairs and checks. Before completion reread Build and the authored leaf "
        "to check deliverable obligations. No installation into a user home or retained package mutation. "
        + delivery
    )


def repair_spec(delay, delivery):
    """Keep the strict pre-Review fixture and exercise one bounded repair trial."""
    initial, _ = spec(delay, "").split("Now submit final-review-v1, ", 1)
    return initial.replace("all three requests", "all four requests") + (
        "This repair case requires exactly four logical requests, in order: author-maker-v1, "
        "leaf-trial-v1, final-review-v1 and repair-trial-v1. Identical submit replays do not add "
        "requests. Keep the same literal standalone submit-twice, full native Read and gather "
        "requirements for all four requests, including unchanged request.body replay after replacement. "
        "Now submit final-review-v1, Review/writable false, once (identical replay required), for an "
        "independent audit of that exact clean library and committed original trial evidence under "
        "Orchflows/writing Review guidance. Give it author/trial identities and limits. It must not "
        "repair or delegate. Use native Read without offset/limit for its entire exact retained report "
        "and result, then gather it. Preserve that original reviewed commit and reviewer identity.\n\n"
        "Perform the one bounded repair/check pass after Review gathering. Address its findings and "
        "make one portable prose clarification in release-library/guidance/release.md: explicitly "
        "explain that classification is independent of input order and each output id list uses ascending "
        "lexicographic order. This is consistent with the initial sorted-id requirement. Make that "
        "post-Review prose refinement even if Review finds no issue or sorting is already described: "
        "clarify the explanation while preserving behavior. Do not intentionally weaken the initial "
        "library or introduce a defect to arrange this repair. Preserve every original trial-output.json, "
        "trial-result.json and trial-record.json byte exactly. Do not change release-input.json or "
        "test_delivery.py. Commit the repaired library; record its clean input commit as a descendant "
        "of the exact reviewed commit. Do not claim the original trial covers the changed library.\n\n"
        "Read the entire repaired leaf and declared context/guidance, then submit repair-trial-v1, "
        "Work/writable false, through the same retained client. This must be a fresh component on "
        "that exact clean repaired commit. Give it only this ordinary request and required execution "
        "paths/controls, without the expected output, author preparation or previous trial answer: "
        "Load release-library/skills/triage-release/SKILL.md and its declared context and guidance "
        "from YOUR OWN worktree, apply it to release-input.json, and return its JSON result as the "
        "ENTIRE component report without Markdown fences. Use native Read without offset/limit for "
        "the whole skill, references/library-context.md, guidance/release.md and release-input.json. "
        "Read complete core writing guidance from the retained core root supplied by the component "
        "launch. Do not change project files or delegate; follow ordinary component completion. "
        "Do not copy the parent worktree path into this assignment. Submit its identical request twice "
        "consecutively. Poll, read the ENTIRE exact retained report_path and result_path with native "
        "Read without offset/limit, and gather repair-trial-v1 with a literal standalone client command. "
        "No pipeline, output redirection, shell wrapper or authority flag may hide its submit/gather JSON. "
        "Record any failure honestly and stop; do not manufacture a passing output.\n\n"
        "After gathering the repair trial, copy its exact retained report bytes to repair-trial-output.json "
        "and its complete retained result.json bytes to repair-trial-result.json at the worktree root, "
        "outside release-library/. Write repair-trial-record.json beside them, using actual retained "
        "identities: author_output_commit, trial_input_commit (the repaired commit), trial_child (the "
        "fresh repair child), request_id repair-trial-v1, result_digest (request.result_digest of canonical "
        "full result.json), report_digest (SHA-256 of raw report bytes), reviewed_commit and review_child. "
        "Include preparation, intervention (say none if none), findings and limits including same-project. "
        "Copy the Review's exact retained report bytes to final-review-report.md and complete retained "
        "result.json bytes to final-review-result.json, also outside release-library/. Keep the original "
        "trial files byte-for-byte unchanged and preserve Review evidence; never replace the original "
        "record with repair identities or claim another Review. Commit these five additional evidence "
        "files together. After the repair trial input commit, change only these five new evidence files; "
        "the final delivered library must match the fresh repair trial input exactly. No second Review "
        "or additional Work. This same-project case does not establish portability or nested workflow parity.\n\n"
        "After repair gathering and committing all evidence, finish with exactly this standalone literal "
        "final test command, replacing the path: python3 -B -m unittest discover -v > "
        "ABSOLUTE_TASKTMP/dynamic-final-check.txt 2>&1. Do not append cat or any other command; read its "
        "output in a separate native Read afterward. Write diagnostic dynamic-delivery.md under tasktmp "
        "with author/original-trial/reviewer/repair-trial identities, exact reviewed, repaired-input and "
        "final commits, findings, repairs and checks. Before completion reread Build and the authored leaf "
        "to check deliverable obligations. No installation into a user home or retained package mutation. "
        + delivery
    )
