"""Bounded local persistence for FirstMate's experimental task-group owner."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile
import time
from fm_task_group_runtime import runtime


class GroupError(RuntimeError):
    pass


def identifier(value, label="identifier"):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", value):
        raise GroupError(f"invalid {label}")
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(value, *, directory=False, exists=True):
    path = Path(os.path.abspath(runtime().native(value) if os.name == "nt" else value))
    for part in (path, *path.parents):
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise GroupError(f"symlink or junction is not allowed: {part}")
    if exists and not path.exists():
        raise GroupError(f"missing path: {path}")
    if directory and path.exists() and not path.is_dir():
        raise GroupError(f"not a directory: {path}")
    if any(c in str(path) for c in "\x00\n\r"):
        raise GroupError("invalid path")
    return path


def read_bytes(path, limit=1024 * 1024):
    path = safe_path(path)
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(descriptor, "rb") as source:
        info = os.fstat(source.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise GroupError(f"not a bounded regular file: {path}")
        data = source.read(limit + 1)
    if len(data) > limit:
        raise GroupError(f"file too large: {path}")
    return data


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise GroupError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def read_json(path):
    try:
        result = json.loads(read_bytes(path).decode("utf-8"), object_pairs_hook=unique_object)
    except (ValueError, UnicodeError) as error:
        raise GroupError(f"invalid JSON: {path}") from error
    if not isinstance(result, dict):
        raise GroupError(f"JSON object required: {path}")
    return result


def sync_directory(path):
    if os.name != "nt":
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def write_bytes(path, data, *, exclusive=False):
    path = safe_path(path, exists=False)
    safe_path(path.parent, directory=True)
    if exclusive and path.exists():
        raise GroupError(f"record already exists: {path}")
    descriptor, temporary = tempfile.mkstemp(prefix=".publish-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as target:
            target.write(data)
            target.flush()
            os.fsync(target.fileno())
        # Group lock serializes all legitimate publishers. No shell sources this JSON.
        os.replace(temporary, path)
        sync_directory(path.parent)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_json(path, value, *, exclusive=False):
    write_bytes(path, canonical(value) + b"\n", exclusive=exclusive)


@contextmanager
def group_lock(group, timeout=10):
    group = safe_path(group, directory=True, exists=False)
    group.mkdir(parents=True, exist_ok=True)
    path = safe_path(group / ".lock", exists=False)
    # OS locks release on owner death. A crashed publisher's launching record
    # remains authoritative; acquiring its released lock never means relaunch.
    with open(path, "a+b") as lock:
        if lock.tell() == 0:
            lock.write(b"0")
            lock.flush()
        deadline = time.monotonic() + timeout
        while True:
            try:
                lock.seek(0)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (OSError, BlockingIOError):
                if time.monotonic() >= deadline:
                    raise GroupError("task group busy; retry status without resubmitting a new request")
                time.sleep(0.05)
        try:
            yield
        finally:
            lock.seek(0)
            if os.name == "nt":
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def metadata(path):
    value = {}
    for line in read_bytes(path, 128 * 1024).decode("utf-8").splitlines():
        if not line:
            continue
        if "=" not in line:
            raise GroupError("malformed FirstMate metadata")
        key, item = line.split("=", 1)
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key) or key in value or "\x00" in item:
            raise GroupError("ambiguous FirstMate metadata")
        value[key] = item
    return value


def git(project, *args, accepted=(0,)):
    try:
        result = subprocess.run(["git", "-C", str(project), *args], capture_output=True,
                                timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise GroupError("could not inspect Git input") from error
    if result.returncode not in accepted:
        raise GroupError(f"Git input check failed: {' '.join(args)}")
    return result.stdout.decode("utf-8").strip()


def clean_commit(project, expected=None):
    project = safe_path(project, directory=True)
    top = safe_path(git(project, "rev-parse", "--show-toplevel"), directory=True)
    if top != project:
        raise GroupError("project must be an exact Git worktree root")
    if git(project, "config", "--get-regexp", r"^remote\.origin\.", accepted=(0, 1)):
        raise GroupError("Stage 1 requires a local Git project without origin")
    if "origin" in git(project, "remote").splitlines():
        raise GroupError("Stage 1 requires a local Git project without origin")
    if git(project, "status", "--porcelain", "--untracked-files=all"):
        raise GroupError("read-only Git input is dirty")
    modes = git(project, "ls-files", "--stage")
    if any(line.startswith(("160000 ", "120000 ")) for line in modes.splitlines()):
        raise GroupError("Stage 1 input cannot contain submodules or symlinks")
    head = git(project, "rev-parse", "--verify", "HEAD^{commit}")
    if not re.fullmatch(r"[0-9a-f]{40,64}", head) or (expected and head != expected):
        raise GroupError("Git input commit changed")
    return head



def clean_descendant(project, input_commit, expected=None):
    """Accept committed writer output only from the exact assigned Git lineage."""
    head = clean_commit(project, expected)
    try:
        git(project, "merge-base", "--is-ancestor", input_commit, head)
    except GroupError as error:
        raise GroupError("Git output must descend from its frozen input commit") from error
    return head



def retained_output_ref(home, root, epoch, child):
    """Archive identity does not depend on a component branch or spawn generation."""
    namespace = digest(canonical([str(safe_path(home, directory=True)),
                                  identifier(root, "root ID"), epoch]))
    return "refs/firstmate/orchflows/" + namespace + "/" + identifier(child, "component ID")


def retained_output_target(project, ref):
    # An owned archive is a direct immutable ref, never a caller-selected symref.
    if git(project, "symbolic-ref", "-q", ref, accepted=(0, 1)):
        raise GroupError("retained writer output ref must not be symbolic")
    return git(project, "rev-parse", "--verify", "--quiet", ref, accepted=(0, 1))


def verify_retained_output(project, ref, output_commit, input_commit):
    if retained_output_target(project, ref) != output_commit:
        raise GroupError("retained writer output ref is missing or changed")
    if git(project, "cat-file", "-t", output_commit) != "commit":
        raise GroupError("retained writer output is not a Git commit")
    git(project, "merge-base", "--is-ancestor", input_commit, output_commit)


def retain_output(project, ref, output_commit, input_commit):
    """Publish once with Git CAS; later result pruning must also own this ref.

    Component and root teardown never remove these refs. They retain the entire
    output ancestry independently of branch deletion, worktree pooling and reflogs.
    """
    current = retained_output_target(project, ref)
    if current and current != output_commit:
        raise GroupError("retained writer output ref is immutable")
    if not current:
        try:
            # --no-deref and the all-zero old value cannot overwrite another ref.
            git(project, "update-ref", "--no-deref", ref, output_commit, "0" * len(output_commit))
        except GroupError:
            # A lost successful reply or same-identity publisher may be retried,
            # but an existing different result is never overwritten.
            if retained_output_target(project, ref) != output_commit:
                raise
    verify_retained_output(project, ref, output_commit, input_commit)
    return ref

def package_inventory(package):
    package = safe_path(package, directory=True)
    files, total = [], 0
    for path in sorted(package.rglob("*")):
        safe_path(path)
        if path.is_dir():
            continue
        data = read_bytes(path, 64 * 1024 * 1024)
        total += len(data)
        if total > 128 * 1024 * 1024 or len(files) >= 5000:
            raise GroupError("package snapshot exceeds Stage 1 bounds")
        files.append({"path": path.relative_to(package).as_posix(), "bytes": len(data),
                      "sha256": digest(data)})
    if not files:
        raise GroupError("package is empty")
    return files


def snapshot_package(source, target):
    manifest = read_json(source / "plugin.json")
    if manifest.get("name") != "orchflows-firstmate":
        raise GroupError("attachment requires the standalone orchflows-firstmate package")
    inventory = package_inventory(source)
    target.mkdir()
    for entry in inventory:
        destination = target / entry["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = read_bytes(source / entry["path"], 64 * 1024 * 1024)
        if digest(payload) != entry["sha256"]:
            raise GroupError("package changed during snapshot")
        write_bytes(destination, payload, exclusive=True)
    if package_inventory(target) != inventory or package_inventory(source) != inventory:
        raise GroupError("package changed during snapshot")
    if os.name != "nt":
        for path in target.rglob("*"):
            path.chmod(0o555 if path.is_dir() else 0o444)
        target.chmod(0o555)
    return digest(canonical(inventory))
