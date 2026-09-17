"""Independent black-box checks against exported, delivered artifacts."""
import csv
import hashlib
import io
import json
from pathlib import Path
import random
import re
import subprocess
import sys
import tempfile


def money(cents):
    sign = "-" if cents < 0 else ""
    whole, fraction = divmod(abs(cents), 100)
    return f"{sign}{whole}.{fraction:02}"


def generated(seed, count=40):
    rng = random.Random(seed)
    rows, totals = [], {}
    for _ in range(count):
        name = rng.choice(["zeta", "Alpha", "café", "東京", "comma,name", "total", "accounts"])
        cents = rng.randrange(-10**22, 10**22)
        rows.append((name, money(cents)))
        totals[name] = totals.get(name, 0) + cents
    out = io.StringIO(newline="")
    writer = csv.writer(out)
    writer.writerow(["account", "amount"])
    writer.writerows(rows)
    return out.getvalue(), {name: money(totals[name]) for name in sorted(totals)}, sum(totals.values())


class ArtifactOracle:
    def __init__(self, project, output, total=False):
        self.project, self.output, self.total = Path(project), Path(output), total
        self.output.mkdir(parents=True, exist_ok=True)
        self.checks = []

    def check(self, name, okay, detail=""):
        self.checks.append({"name": name, "passed": bool(okay), "detail": detail})

    def command(self, name, args, data=None):
        try:
            p = subprocess.run([sys.executable, *args], cwd=self.project,
                               input=data, capture_output=True, timeout=30)
            result = {"name": name, "args": args, "input": None if data is None else data.decode(errors="replace"),
                      "returncode": p.returncode, "stdout": p.stdout.decode(errors="replace"),
                      "stderr": p.stderr.decode(errors="replace")}
        except subprocess.TimeoutExpired:
            result = {"name": name, "args": args, "returncode": None,
                      "stdout": "", "stderr": "Timed out after 30 seconds"}
        with (self.output / "commands.jsonl").open("a") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
        return result

    def success(self, name, data, expected, args=None):
        p = self.command(name, ["moneylog.py", *(args or ["-"])], data.encode())
        try:
            pairs = json.loads(p["stdout"], object_pairs_hook=lambda pairs: pairs)
            decoded = json.loads(p["stdout"])
        except (ValueError, TypeError):
            pairs, decoded = None, None
        self.check(name, p["returncode"] == 0 and decoded == expected and
                   p["stdout"].endswith("\n") and not p["stderr"], json.dumps(p))
        object_pairs = isinstance(pairs, list) and all(
            isinstance(pair, (list, tuple)) and len(pair) == 2 and isinstance(pair[0], str)
            for pair in pairs)
        if isinstance(expected, dict) and "--total" not in (args or []):
            self.check(name + " sorted unique keys", object_pairs and
                       [pair[0] for pair in pairs] == sorted(expected))
        elif isinstance(expected, dict):
            self.check(name + " unique total keys", object_pairs and
                       sorted(pair[0] for pair in pairs) == sorted(expected))
            account_pairs = dict(pairs).get("accounts") if object_pairs else None
            self.check(name + " sorted account keys", isinstance(account_pairs, list) and
                       all(isinstance(pair, (list, tuple)) and len(pair) == 2 for pair in account_pairs) and
                       [pair[0] for pair in account_pairs] == sorted(expected["accounts"]))
        return p

    def failure(self, name, data, line=None, args=None):
        if isinstance(data, str):
            data = data.encode()
        p = self.command(name, ["moneylog.py", *(args or ["-"])], data)
        self.check(name, p["returncode"] == 2 and not p["stdout"] and bool(p["stderr"].strip()), json.dumps(p))
        if line is not None:
            self.check(name + " line diagnostic", bool(re.search(
                rf"\b(?:line|row)\s*[:=#]?\s*{line}\b|(?:stdin|\.csv):{line}\b",
                p["stderr"], re.I)), p["stderr"])

    def run(self):
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.project.rglob("*")
                  if p.is_file() and "__pycache__" not in p.parts}
        self.check("entrypoint delivered", (self.project / "moneylog.py").is_file())
        if not self.checks[-1]["passed"]:
            return self.result()
        self.success("empty ledger", "account,amount\n", {})
        self.success("exact cents and cancellation", "account,amount\nz,0.10\nz,0.20\na,-1.50\na,+1.50\n",
                     {"a": "0.00", "z": "0.30"})
        self.success("trim unicode quoted csv", 'account,amount\n"comma,name", 12.3 \n 東京 ,-2\n café ,+0.05\n',
                     {"café": "0.05", "comma,name": "12.30", "東京": "-2.00"})
        huge = "123456789012345678901234567890123456789012345678901234567890"
        self.success("unbounded precision", f"account,amount\na,{huge}.99\na,0.01\n",
                     {"a": str(int(huge) + 1) + ".00"})
        self.success("precision beyond CSV field limit", "account,amount\na," + "9" * 140000 +
                     ".99\na,0.01\n", {"a": "1" + "0" * 140000 + ".00"})
        self.success("negative zero", "account,amount\na,-0.00\n", {"a": "0.00"})
        self.success("CRLF", "account,amount\r\na,2.5\r\n", {"a": "2.50"})
        for token in ("1.001", "NaN", "Infinity", "1e3", "1,000", ".5", "1.", "", "١.٢", "--1"):
            self.failure("invalid amount " + repr(token), f'account,amount\nok,1.00\nbad,"{token}"\n', 3)
        for name, data, line in (
            ("empty file", "", None),
            ("wrong header", "name,amount\na,1\n", None),
            ("extra header field", "account,amount,note\na,1,x\n", None),
            ("empty account", "account,amount\n ,1\n", 2),
            ("missing field", "account,amount\na\n", 2),
            ("extra field", "account,amount\na,1,extra\n", 2),
            ("unclosed quote", 'account,amount\na,1\n"bad,2\n', 3),
            ("late row failure", "account,amount\na,1\nb,2\nc,3\nd,no\n", 5),
            ("quoted multiline physical line", 'account,amount\n"two\nlines",1\nb,no\n', 4),
        ):
            self.failure(name, data, line)
        self.failure("invalid UTF-8 stdin", b"account,amount\na,1\n\xff,2\n")
        self.failure("unknown option", None, args=["--unknown"])
        p = self.command("missing input argument", ["moneylog.py"])
        self.check("missing input argument", p["returncode"] == 2 and not p["stdout"] and bool(p["stderr"]))
        self.failure("extra positional", None, args=["-", "extra"])
        self.failure("missing file", None, args=[str(self.output / "does-not-exist.csv")])
        p = self.command("help", ["moneylog.py", "--help"])
        self.check("help", p["returncode"] == 0 and bool(p["stdout"].strip()))
        with tempfile.TemporaryDirectory(prefix="oracle-") as directory:
            path = Path(directory) / "ledger with spaces.csv"
            path.write_bytes(b"account,amount\na,1.25\na,0.75\n")
            self.success("file with spaces", "", {"a": "2.00"}, [str(path)])
            if self.total:
                self.success("total from file", "", {"accounts": {"a": "2.00"}, "total": "2.00"},
                             [str(path), "--total"])
            path.write_bytes(b"account,amount\na,1\n\xff,2\n")
            self.failure("invalid UTF-8 file", None, args=[str(path)])
        for seed in range(16):
            data, expected, total = generated(seed)
            self.success(f"generated {seed}", data, expected)
            if self.total:
                self.success(f"total generated {seed}", data,
                             {"accounts": expected, "total": money(total)}, ["--total", "-"])
        if self.total:
            self.success("total empty", "account,amount\n", {"accounts": {}, "total": "0.00"}, ["-", "--total"])
            exact = str(int(huge) + 1) + ".00"
            self.success("unbounded total", f"account,amount\na,{huge}.99\na,0.01\n",
                         {"accounts": {"a": exact}, "total": exact}, ["--total", "-"])
            self.failure("total preserves atomic failure", "account,amount\na,2\nb,bad\n", 3, ["--total", "-"])
        tests = self.command("delivered unit suite", ["-m", "unittest", "discover", "-v"])
        count = re.search(r"Ran (\d+) tests?", tests["stderr"])
        self.check("delivered tests pass and are nonempty", tests["returncode"] == 0 and
                   count is not None and int(count[1]) > 0, tests["stderr"])
        self.readme_sample()
        self.check("delivered files unchanged by checks", all(
            path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == digest
            for path, digest in before.items()))
        return self.result()

    def readme_sample(self):
        sample = self.project / "examples/sample.csv"
        readme = self.project / "README.md"
        self.check("documented sample delivered", sample.is_file() and readme.is_file())
        if not sample.is_file() or not readme.is_file():
            return
        p = self.command("README sample", ["moneylog.py", "examples/sample.csv"])
        try:
            expected = json.loads(p["stdout"])
        except ValueError:
            expected = None
        text = readme.read_text()
        objects = []
        for match in re.finditer(r"\{", text):
            try:
                objects.append(json.JSONDecoder().raw_decode(text[match.start():])[0])
            except ValueError:
                pass
        self.check("README example output matches execution", p["returncode"] == 0 and
                   isinstance(expected, dict) and expected in objects and "examples/sample.csv" in text)
        if self.total:
            p = self.command("README total sample", ["moneylog.py", "--total", "examples/sample.csv"])
            try:
                total = json.loads(p["stdout"])
            except ValueError:
                total = None
            self.check("README total example output matches execution", p["returncode"] == 0 and
                       isinstance(total, dict) and total in objects and "--total" in text)

    def result(self):
        result = {"passed": all(c["passed"] for c in self.checks), "checks": self.checks}
        (self.output / "artifact-results.json").write_text(json.dumps(result, indent=2) + "\n")
        return result
