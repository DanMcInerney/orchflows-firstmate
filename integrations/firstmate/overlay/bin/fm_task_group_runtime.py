"""Explicit Windows Git Bash/native Python boundary for task-group commands.

No discovery of a Windows bash.exe through PATH: that name can select WSL.
Only typed filesystem values pass through cygpath. Metadata stays verbatim.
"""
import ctypes
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


class RuntimeBoundaryError(ValueError):
    pass


class Runtime:
    def __init__(self, bash=None, python=None):
        self.windows = os.name == "nt"
        if not self.windows:
            self.bash, self.python = "bash", "python3"
            return
        if not bash:
            raise RuntimeBoundaryError("Native Windows task groups require explicit FM_TASK_GROUP_BASH pointing to Git's usr/bin/bash.exe")
        self.bash = self._executable(bash, "bash")
        self.python = self._executable(python or sys.executable, "python")
        if not os.path.samefile(self.python, sys.executable):
            raise RuntimeBoundaryError("FM_TASK_GROUP_PYTHON must match the current native Python interpreter")
        self.cygpath = self._executable(str(Path(self.bash).with_name("cygpath.exe")), "cygpath")
        self.ps = self._executable(str(Path(self.bash).with_name("ps.exe")), "ps")
        probe = self._capture([self.bash, "--noprofile", "--norc", "-c", "uname -s"], timeout=10)
        if not re.fullmatch(r"(?:MINGW\d*|MSYS)_NT-[^\r\n]+", probe.strip()):
            raise RuntimeBoundaryError("Selected shell is not a native Git Bash/MSYS runtime")
        self.identity = {"kind": "windows-git-bash-native-python", "version": 1,
                         "symlinks": "nativestrict",
                         "python_version": sys.version.split()[0],
                         "executables": {name: {"path": str(Path(path).as_posix()),
                                                 "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}
                                         for name, path in (("bash", self.bash), ("cygpath", self.cygpath),
                                                            ("ps", self.ps), ("python", self.python))}}

    @staticmethod
    def _executable(value, label):
        path = Path(value)
        if not path.is_absolute() or not path.is_file() or path.is_symlink():
            raise RuntimeBoundaryError(f"Explicit {label} must be an absolute regular executable path")
        for parent in path.parents:
            if parent.is_symlink() or (hasattr(parent, "is_junction") and parent.is_junction()):
                raise RuntimeBoundaryError(f"{label} runtime path cannot cross a symlink or junction")
        return str(path.resolve())

    @staticmethod
    def _capture(command, timeout=10):
        try:
            environment = dict(os.environ)
            if os.name == "nt":
                environment["PATH"] = str(Path(command[0]).parent) + os.pathsep + environment.get("PATH", "")
            result = subprocess.run(command, capture_output=True, encoding="utf-8", errors="strict",
                                    timeout=timeout, check=False, env=environment)
        except (OSError, subprocess.SubprocessError, UnicodeError) as error:
            raise RuntimeBoundaryError("Selected Windows runtime could not be inspected") from error
        if result.returncode or len(result.stdout) > 32768:
            raise RuntimeBoundaryError("Selected Windows runtime path/process query failed")
        return result.stdout

    def native(self, value):
        value = os.fspath(value)
        if self.windows and value.startswith("/"):
            # UNC and MSYS pseudo-devices are outside this local Stage 1 profile.
            if value.startswith("//") or value.startswith(("/dev/", "/proc/")):
                raise RuntimeBoundaryError("Stage 1 only supports local filesystem paths")
            value = self._capture([self.cygpath, "-w", value]).strip()
        return Path(value)

    def shell(self, value):
        if not self.windows:
            return os.fspath(value)
        native = self.native(value)
        if not native.is_absolute():
            raise RuntimeBoundaryError("Shell filesystem arguments must be absolute")
        return self._capture([self.cygpath, "-u", str(native)]).strip()

    def environment(self, environment=None, *, home=None, code_root=None):
        result = dict(os.environ if environment is None else environment)
        if home is not None:
            result["FM_HOME"] = self.shell(home)
        if code_root is not None:
            result["FM_ROOT_OVERRIDE"] = self.shell(code_root)
        if self.windows:
            result["PATH"] = str(Path(self.bash).parent) + os.pathsep + result.get("PATH", "")
            msys = [part for part in result.get("MSYS", "").split() if not part.startswith("winsymlinks:")]
            result["MSYS"] = " ".join([*msys, "winsymlinks:nativestrict"])
            result["FM_TASK_GROUP_BASH"] = Path(self.bash).as_posix()
            result["FM_TASK_GROUP_PYTHON"] = Path(self.python).as_posix()
            # MSYS otherwise changes these /c/... values when calling native
            # Python, breaking the exact inherited lock-home custody marker.
            excluded = set(filter(None, result.get("MSYS2_ENV_CONV_EXCL", "").split(";")))
            excluded.update(("FM_HOME", "FM_ROOT_OVERRIDE", "FM_TASK_GROUP_LOCK_HOME",
                             "FM_TASK_GROUP_BASH", "FM_TASK_GROUP_PYTHON"))
            result["MSYS2_ENV_CONV_EXCL"] = ";".join(sorted(excluded))
            result["PYTHONDONTWRITEBYTECODE"] = "1"
            result["PYTHONUTF8"] = "1"
            result["PYTHONIOENCODING"] = "utf-8"
        return result

    def run(self, script, arguments=(), *, path_indexes=(), env=None, **kwargs):
        arguments = list(map(os.fspath, arguments))
        for index in path_indexes:
            arguments[index] = self.shell(arguments[index])
        prefix = [self.bash]
        if self.windows:
            prefix += ["--noprofile", "--norc"]
        return subprocess.run([*prefix, self.shell(script), *arguments],
                              env=self.environment(env), **kwargs)

    def native_ancestor(self, msys_owner):
        if not self.windows or not re.fullmatch(r"[1-9][0-9]*", msys_owner):
            raise RuntimeBoundaryError("Native ancestor verification requires a Windows MSYS owner PID")
        output = self._capture([self.ps, "-p", msys_owner]).splitlines()
        if len(output) != 2:
            raise RuntimeBoundaryError("MSYS lock owner has no unambiguous native PID")
        header, row = output[0].split(), output[1].split()
        try:
            if row[header.index("PID")] != msys_owner:
                raise ValueError("owner PID mismatch")
            native_owner = int(row[header.index("WINPID")])
        except (ValueError, IndexError) as error:
            raise RuntimeBoundaryError("Cannot map MSYS lock owner to native PID") from error
        parents = windows_process_parents()
        seen, pid = set(), os.getpid()
        for _ in range(64):
            if pid == native_owner:
                return True
            if pid in seen or pid not in parents:
                break
            seen.add(pid)
            pid = parents[pid]
        return False


def windows_process_parents():
    """Read only process IDs/parents through Win32; no command lines or credentials."""
    from ctypes import wintypes

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                    ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
                    ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", wintypes.LONG),
                    ("dwFlags", wintypes.DWORD), ("szExeFile", wintypes.WCHAR * 260)]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
    kernel.Process32FirstW.restype = wintypes.BOOL
    kernel.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
    kernel.Process32NextW.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.CreateToolhelp32Snapshot(2, 0)
    if handle == ctypes.c_void_p(-1).value:
        raise RuntimeBoundaryError("Native parent-process snapshot unavailable")
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        if not kernel.Process32FirstW(handle, ctypes.byref(entry)):
            raise RuntimeBoundaryError("Native parent-process snapshot is empty")
        parents = {}
        while True:
            parents[entry.th32ProcessID] = entry.th32ParentProcessID
            if not kernel.Process32NextW(handle, ctypes.byref(entry)):
                break
        return parents
    finally:
        kernel.CloseHandle(handle)


@lru_cache(maxsize=4)
def selected_runtime(bash=None, python=None):
    return Runtime(bash, python)


def runtime():
    return selected_runtime(os.environ.get("FM_TASK_GROUP_BASH"), os.environ.get("FM_TASK_GROUP_PYTHON"))


if __name__ == "__main__":
    try:
        if len(sys.argv) == 3 and sys.argv[1] == "ancestor":
            raise SystemExit(0 if runtime().native_ancestor(sys.argv[2]) else 1)
        raise RuntimeBoundaryError("Expected ancestor MSYS_OWNER_PID")
    except (RuntimeBoundaryError, OSError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        raise SystemExit(2)
