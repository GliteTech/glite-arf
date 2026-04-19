"""Tests for ``arf.scripts.overview.common.write_file`` EOF normalization.

Spec: ``write_file`` currently appends ``\\n`` unconditionally, producing
double trailing newlines when ``content`` itself already ends in ``\\n``
or ``\\n\\n``. The pre-commit ``end-of-file-fixer`` hook then rewrites the
file and breaks the commit.

New behavior: ``write_file`` must normalize trailing newlines — strip all
trailing ``\\n`` characters from ``content``, then append exactly one
``\\n``. Non-newline trailing whitespace (e.g. trailing spaces) is
preserved — only trailing newlines are collapsed.

Empty content (``""``) is a special case: it should still produce exactly
one ``\\n`` byte (one empty trailing line), because zero-byte files are
bad for EOL-fixer hooks.
"""

from pathlib import Path

from arf.scripts.overview.common import write_file


def test_no_trailing_newline_gets_exactly_one(tmp_path: Path) -> None:
    file_path: Path = tmp_path / "a.txt"
    write_file(file_path=file_path, content="a\nb")
    assert file_path.read_bytes() == b"a\nb\n"


def test_single_trailing_newline_preserved_as_one(tmp_path: Path) -> None:
    file_path: Path = tmp_path / "b.txt"
    write_file(file_path=file_path, content="a\nb\n")
    assert file_path.read_bytes() == b"a\nb\n"


def test_multiple_trailing_newlines_collapsed_to_one(tmp_path: Path) -> None:
    file_path: Path = tmp_path / "c.txt"
    write_file(file_path=file_path, content="a\nb\n\n\n")
    assert file_path.read_bytes() == b"a\nb\n"


def test_empty_content_becomes_single_newline(tmp_path: Path) -> None:
    file_path: Path = tmp_path / "d.txt"
    write_file(file_path=file_path, content="")
    assert file_path.read_bytes() == b"\n"


def test_trailing_spaces_preserved(tmp_path: Path) -> None:
    file_path: Path = tmp_path / "e.txt"
    write_file(file_path=file_path, content="a   ")
    assert file_path.read_bytes() == b"a   \n"
