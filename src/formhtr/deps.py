from __future__ import annotations

import ctypes.util
import platform
import shutil


def _install_hint(dep_name: str) -> str:
    system = platform.system().lower()
    if system == "darwin":
        return f"brew install {dep_name}"
    if system == "linux":
        if dep_name == "zbar":
            return "apt: sudo apt-get install libzbar0  |  dnf: sudo dnf install zbar"
        return f"apt: sudo apt-get install {dep_name}  |  dnf: sudo dnf install {dep_name}"
    return f"Install {dep_name} using your system package manager."


def check_system_dependencies() -> list[tuple[str, str]]:
    missing: list[tuple[str, str]] = []

    if shutil.which("qpdf") is None:
        missing.append(("qpdf", _install_hint("qpdf")))

    if ctypes.util.find_library("zbar") is None:
        missing.append(("zbar", _install_hint("zbar")))

    return missing


def ensure_system_dependencies(required: set[str]) -> None:
    missing = check_system_dependencies()
    missing_required = [(name, hint) for name, hint in missing if name in required]
    if not missing_required:
        return

    lines = ["Missing required system dependencies:"]
    for name, hint in missing_required:
        lines.append(f"- {name}: {hint}")
    lines.append("Run `formhtr doctor` for a full dependency report.")
    raise RuntimeError("\n".join(lines))

