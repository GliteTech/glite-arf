#!/usr/bin/env python3
"""Check if the environment is properly set up for ARF-based research project development.

This is interactive documentation as code: run it with any Python (no dependencies needed)
and it will guide you through the repository setup step by step.

Usage:
    python3 doctor.py
    uv run doctor.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# ANSI color sequences
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"


def red(s: str) -> str:
    return f"{RED}{s}{RESET}"


def green(s: str) -> str:
    return f"{GREEN}{s}{RESET}"


def good(s: str) -> str:
    return green(f"✅ {s}")


def bad(s: str) -> str:
    return red(f"❌ {s}")


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    check_func: Callable[[], Ok | Error]
    help_text: str | None = None


@dataclass(frozen=True, slots=True)
class Ok:
    text: str


@dataclass(frozen=True, slots=True)
class Error:
    text: str
    details: str | None = None


@dataclass(frozen=True, slots=True)
class Assertion:
    """Unlike Check, this is an unexpected state -- a warning, not a blocker."""

    name: str
    check_func: Callable[[], Ok | Error]
    help_text: str | None = None


def check_python_version() -> Ok | Error:
    major, minor = sys.version_info[:2]
    version_str = f"{major}.{minor}.{sys.version_info.micro}"
    if (major, minor) >= (3, 12):
        return Ok(f"Python {version_str}")
    else:
        return Error(f"Python {version_str} (need >= 3.12)")


def check_executable(executable: str) -> Ok | Error:
    if shutil.which(executable) is not None:
        return Ok(f"{executable} is available")
    else:
        return Error(f"{executable} not found in PATH")


def check_direnv_hook() -> Ok | Error:
    shell = Path(os.environ.get("SHELL", "")).name

    if len(shell) == 0:
        return Ok("SHELL environment variable is not set but OK")

    config_paths: dict[str, Path] = {
        "fish": Path.home() / ".config/fish/config.fish",
        "bash": Path.home() / ".bashrc",
        "zsh": Path.home() / ".zshrc",
    }

    config = config_paths.get(shell)
    if config is None:
        return Ok(f"Unknown shell {shell}, skipping hook check")

    if not config.exists():
        return Error(f"Shell config {config} does not exist")

    content = config.read_text()
    if f"direnv hook {shell}" in content:
        return Ok(f"direnv hook is in {config}")
    else:
        return Error(f"direnv hook not found in {config}")


def check_direnv_allowed() -> Ok | Error:
    try:
        result = subprocess.run(
            ["direnv", "status"],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if "Found RC allowed 0" in result.stdout or "Found RC allowed true" in result.stdout:
            return Ok("direnv is allowed for this directory")
        else:
            return Error("direnv is not allowed for this directory")
    except subprocess.CalledProcessError as e:
        return Error("Failed to check direnv status", details=str(e))


def check_venv_exists() -> Ok | Error:
    if (REPO_ROOT / ".venv").exists():
        return Ok(".venv exists")
    else:
        return Error(".venv does not exist")


def check_env_variable(var_name: str) -> Ok | Error:
    value = os.getenv(var_name)
    if value is None:
        return Error(f"Environment variable {var_name} is not set")
    return Ok(f"Environment variable {var_name} is set")


def check_deps_installed() -> Ok | Error:
    try:
        import pydantic  # noqa: F401

        return Ok("Dependencies seem to be installed (pydantic is available)")
    except ImportError:
        return Error("pydantic can't be imported, dependencies are likely not installed")


def check_precommit_installed() -> Ok | Error:
    hook_path = REPO_ROOT / ".git" / "hooks" / "pre-commit"
    if hook_path.exists():
        return Ok("pre-commit hooks are installed")
    else:
        return Error("pre-commit hooks are not installed")


def check_git_lfs_installed() -> Ok | Error:
    if shutil.which("git-lfs") is None:
        return Error("git-lfs is not installed")
    lfs_hook = REPO_ROOT / ".git" / "hooks" / "post-checkout"
    if not lfs_hook.exists():
        return Error("git-lfs hooks are not installed (run: git lfs install)")
    try:
        content = lfs_hook.read_text()
        if "git-lfs" in content or "git lfs" in content:
            return Ok("Git LFS is installed and hooks are configured")
        return Error("git-lfs hooks are not installed (run: git lfs install)")
    except OSError:
        return Error("Could not read git hooks")


# Checks are executed sequentially and stop on the first failure.
# Later checks can rely on earlier ones passing.
CHECKS: list[Check | Assertion] = [
    # System tools
    Check(
        "Python version is 3.12+",
        check_python_version,
        help_text="Install Python 3.12 or later. Consider using pyenv or uv python install.",
    ),
    Check(
        "git is available",
        partial(check_executable, "git"),
        help_text="Install git using your package manager.",
    ),
    Check(
        "uv is available",
        partial(check_executable, "uv"),
        help_text=(
            "Install uv. For instructions, see:\n"
            "  https://docs.astral.sh/uv/getting-started/installation/"
        ),
    ),
    Check(
        "direnv is available",
        partial(check_executable, "direnv"),
        help_text=(
            "Install direnv. For instructions, see:\n  https://direnv.net/docs/installation.html"
        ),
    ),
    Check(
        "direnv shell hook is configured",
        check_direnv_hook,
        help_text=(
            "Add the direnv hook to your shell's RC file. For instructions, see:\n"
            "  https://direnv.net/docs/hook.html"
        ),
    ),
    Check(
        "direnv .envrc is allowed",
        check_direnv_allowed,
        help_text="Allow direnv for this directory. Run:\n  direnv allow",
    ),
    # Python environment
    Check(
        ".venv exists",
        check_venv_exists,
        help_text="Create the virtual environment. Run:\n  uv sync",
    ),
    Check(
        "virtual environment is activated",
        partial(check_env_variable, "VIRTUAL_ENV"),
        help_text=(
            "Activate the virtual environment. Run:\n"
            "  source .venv/bin/activate\n"
            "Or restart your shell (direnv will activate it automatically)."
        ),
    ),
    Check(
        "dependencies are installed",
        check_deps_installed,
        help_text="Install dependencies. Run:\n  uv sync",
    ),
    Check(
        "Git LFS is installed",
        check_git_lfs_installed,
        help_text=(
            "Install Git LFS and initialize it:\n"
            "  brew install git-lfs   # or your package manager\n"
            "  git lfs install"
        ),
    ),
    Check(
        "pre-commit hooks are installed",
        check_precommit_installed,
        help_text="Install pre-commit hooks. Run:\n  uv run pre-commit install",
    ),
    # Dev tools (assertions -- warn but don't block)
    Assertion(
        "ruff is available",
        partial(check_executable, "ruff"),
        help_text=(
            "ruff should be available after uv sync. Try:\n  uv sync\n  source .venv/bin/activate"
        ),
    ),
    Assertion(
        "mypy is available",
        partial(check_executable, "mypy"),
        help_text=(
            "mypy should be available after uv sync. Try:\n  uv sync\n  source .venv/bin/activate"
        ),
    ),
]


def add_spacing(spacing: int, s: str) -> str:
    return "\n".join(f"{' ' * spacing}{line}" for line in s.splitlines())


def main() -> None:
    for check in CHECKS:
        print(f"\nChecking if {check.name}...")
        result = check.check_func()
        if isinstance(result, Ok):
            print(add_spacing(2, good(result.text)))
        elif isinstance(result, Error):
            print(add_spacing(2, bad(result.text)))
            if result.details is not None:
                print(add_spacing(4, result.details))
            if check.help_text is not None:
                print(add_spacing(2, check.help_text))
            if isinstance(check, Assertion):
                print(add_spacing(2, "(this is a warning, continuing...)"))
            else:
                print("\nAfter fixing the problem, run `python3 doctor.py` again.")
                exit(1)

    print("\nAll checks passed! Environment is properly set up.")


if __name__ == "__main__":
    main()
