"""Tests for run_with_logs: secret redaction and captured-output contract."""

import json
from pathlib import Path

import pytest

import arf.scripts.utils.run_with_logs as run_with_logs_module
from arf.scripts.utils.run_with_logs import _redact_secrets

# ---------------------------------------------------------------------------
# Key-value patterns
# ---------------------------------------------------------------------------


def test_redacts_api_key_equals() -> None:
    text: str = "curl --data api_key=sk-abc123def456 https://api.example.com"
    result: str = _redact_secrets(text=text)
    assert "sk-abc123def456" not in result
    assert "api_key=<REDACTED>" in result


def test_redacts_instance_api_key() -> None:
    text: str = "instance_api_key=vast_secret_xyz789"
    result: str = _redact_secrets(text=text)
    assert "vast_secret_xyz789" not in result
    assert "instance_api_key=<REDACTED>" in result


def test_redacts_api_key_hyphenated() -> None:
    text: str = "api-key=mykey123"
    result: str = _redact_secrets(text=text)
    assert "mykey123" not in result


def test_redacts_secret_equals() -> None:
    text: str = "secret=topsecret123"
    result: str = _redact_secrets(text=text)
    assert "topsecret123" not in result


def test_redacts_token_equals() -> None:
    text: str = "token=abc123xyz"
    result: str = _redact_secrets(text=text)
    assert "abc123xyz" not in result


def test_redacts_password_equals() -> None:
    text: str = "password=hunter2"
    result: str = _redact_secrets(text=text)
    assert "hunter2" not in result


# ---------------------------------------------------------------------------
# JSON patterns
# ---------------------------------------------------------------------------


def test_redacts_json_api_key() -> None:
    text: str = '{"api_key": "sk-1234567890abcdef"}'
    result: str = _redact_secrets(text=text)
    assert "sk-1234567890abcdef" not in result
    assert '"api_key": "<REDACTED>"' in result


def test_redacts_json_secret() -> None:
    text: str = '{"secret": "mysecretvalue"}'
    result: str = _redact_secrets(text=text)
    assert "mysecretvalue" not in result


def test_redacts_json_password() -> None:
    text: str = '{"password": "pass123"}'
    result: str = _redact_secrets(text=text)
    assert "pass123" not in result


# ---------------------------------------------------------------------------
# Bearer tokens
# ---------------------------------------------------------------------------


def test_redacts_bearer_token() -> None:
    text: str = "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.signature"
    result: str = _redact_secrets(text=text)
    assert "eyJhbGciOiJIUzI1NiJ9" not in result
    assert "Bearer <REDACTED>" in result


# ---------------------------------------------------------------------------
# Non-secret text preserved
# ---------------------------------------------------------------------------


def test_preserves_non_secret_text() -> None:
    text: str = "This is a normal log line with no secrets.\n"
    result: str = _redact_secrets(text=text)
    assert result == text


def test_preserves_normal_equals_signs() -> None:
    text: str = "batch_size=32 learning_rate=0.001"
    result: str = _redact_secrets(text=text)
    assert result == text


def test_multiline_redaction() -> None:
    text: str = (
        'Starting training...\napi_key=sk-secret123\nEpoch 1/10\n{"token": "abc789"}\nDone.\n'
    )
    result: str = _redact_secrets(text=text)
    assert "sk-secret123" not in result
    assert "abc789" not in result
    assert "Starting training..." in result
    assert "Epoch 1/10" in result
    assert "Done." in result


# ---------------------------------------------------------------------------
# Captured stdout trailing newline contract
# ---------------------------------------------------------------------------


def test_captured_stdout_ends_with_newline_when_output_lacks_one(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks_dir: Path = tmp_path / "tasks"
    task_dir: Path = tasks_dir / "t0099_newline_test"
    task_dir.mkdir(parents=True)
    monkeypatch.setattr(
        target=run_with_logs_module,
        name="TASKS_DIR",
        value=tasks_dir,
    )

    exit_code: int = run_with_logs_module.run_command_with_logging(
        task_id="t0099_newline_test",
        command_tokens=[
            "python3",
            "-c",
            "import sys; sys.stdout.write('hello-no-newline')",
        ],
    )
    assert exit_code == 0

    commands_dir: Path = task_dir / "logs" / "commands"
    stdout_files: list[Path] = sorted(commands_dir.glob("*.stdout.txt"))
    assert len(stdout_files) == 1

    content: str = stdout_files[0].read_text(encoding="utf-8")
    assert len(content) > 0
    assert content.endswith("\n")
    assert "hello-no-newline" in content


def test_captured_stdout_preserves_existing_trailing_newline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks_dir: Path = tmp_path / "tasks"
    task_dir: Path = tasks_dir / "t0099_newline_test"
    task_dir.mkdir(parents=True)
    monkeypatch.setattr(
        target=run_with_logs_module,
        name="TASKS_DIR",
        value=tasks_dir,
    )

    exit_code: int = run_with_logs_module.run_command_with_logging(
        task_id="t0099_newline_test",
        command_tokens=["python3", "-c", "print('hello')"],
    )
    assert exit_code == 0

    commands_dir: Path = task_dir / "logs" / "commands"
    stdout_files: list[Path] = sorted(commands_dir.glob("*.stdout.txt"))
    assert len(stdout_files) == 1

    content: str = stdout_files[0].read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert content.endswith("\n\n") is False
    assert "hello" in content


def test_subprocess_env_has_virtual_env_scrubbed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``run_command_with_logging`` must not leak the parent's ``VIRTUAL_ENV``
    into the child process. Otherwise ``uv run`` inside a worktree prints a
    noisy warning on every wrapped invocation because the inherited
    ``VIRTUAL_ENV`` from the outer shell points at a different ``.venv``.
    """
    tasks_dir: Path = tmp_path / "tasks"
    task_dir: Path = tasks_dir / "t0099_env_test"
    task_dir.mkdir(parents=True)
    monkeypatch.setattr(
        target=run_with_logs_module,
        name="TASKS_DIR",
        value=tasks_dir,
    )
    monkeypatch.setenv(
        name="VIRTUAL_ENV",
        value="/some/stale/path/.venv",
    )

    exit_code: int = run_with_logs_module.run_command_with_logging(
        task_id="t0099_env_test",
        command_tokens=[
            "python3",
            "-c",
            'import json, os; print(json.dumps({"virtual_env": os.environ.get("VIRTUAL_ENV")}))',
        ],
    )
    assert exit_code == 0

    commands_dir: Path = task_dir / "logs" / "commands"
    stdout_files: list[Path] = sorted(commands_dir.glob("*.stdout.txt"))
    assert len(stdout_files) == 1
    payload: dict[str, object] = json.loads(stdout_files[0].read_text(encoding="utf-8"))
    assert payload["virtual_env"] is None, (
        f"child process still saw VIRTUAL_ENV: {payload['virtual_env']}"
    )


def test_subprocess_env_preserves_other_variables(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The ``VIRTUAL_ENV`` scrub must be narrow: ``PATH`` and other env vars
    must still reach the child process unchanged.
    """
    tasks_dir: Path = tmp_path / "tasks"
    task_dir: Path = tasks_dir / "t0099_env_keep"
    task_dir.mkdir(parents=True)
    monkeypatch.setattr(
        target=run_with_logs_module,
        name="TASKS_DIR",
        value=tasks_dir,
    )
    monkeypatch.setenv(name="VIRTUAL_ENV", value="/some/stale/.venv")
    monkeypatch.setenv(name="ARF_KEEP_THIS", value="preserved-value")

    exit_code: int = run_with_logs_module.run_command_with_logging(
        task_id="t0099_env_keep",
        command_tokens=[
            "python3",
            "-c",
            (
                "import json, os; "
                'print(json.dumps({"keep": os.environ.get("ARF_KEEP_THIS"),'
                ' "path_present": "PATH" in os.environ}))'
            ),
        ],
    )
    assert exit_code == 0

    commands_dir: Path = task_dir / "logs" / "commands"
    stdout_files: list[Path] = sorted(commands_dir.glob("*.stdout.txt"))
    assert len(stdout_files) == 1
    payload: dict[str, object] = json.loads(stdout_files[0].read_text(encoding="utf-8"))
    assert payload["keep"] == "preserved-value"
    assert payload["path_present"] is True


def test_captured_stdout_empty_stays_empty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tasks_dir: Path = tmp_path / "tasks"
    task_dir: Path = tasks_dir / "t0099_newline_test"
    task_dir.mkdir(parents=True)
    monkeypatch.setattr(
        target=run_with_logs_module,
        name="TASKS_DIR",
        value=tasks_dir,
    )

    exit_code: int = run_with_logs_module.run_command_with_logging(
        task_id="t0099_newline_test",
        command_tokens=["python3", "-c", "pass"],
    )
    assert exit_code == 0

    commands_dir: Path = task_dir / "logs" / "commands"
    stdout_files: list[Path] = sorted(commands_dir.glob("*.stdout.txt"))
    assert len(stdout_files) == 1

    content: str = stdout_files[0].read_text(encoding="utf-8")
    assert len(content) == 0
