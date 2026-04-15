import json
from pathlib import Path


def write_json(*, path: Path, data: dict[str, object] | list[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_text(*, path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_frontmatter_md(
    *,
    path: Path,
    frontmatter: dict[str, str | int],
    body: str,
) -> None:
    lines: list[str] = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, int):
            lines.append(f"{key}: {value}")
        else:
            lines.append(f'{key}: "{value}"')
    lines.append("---")
    lines.append("")
    lines.append(body)
    write_text(path=path, content="\n".join(lines))
