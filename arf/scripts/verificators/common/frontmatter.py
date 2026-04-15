import re
from dataclasses import dataclass
from typing import Any

import yaml

_FRONTMATTER_PATTERN: re.Pattern[str] = re.compile(
    pattern=r"\A---\s*\n(.*?\n)---\s*\n",
    flags=re.DOTALL,
)


@dataclass(frozen=True, slots=True)
class FrontmatterResult:
    raw_yaml: str
    body: str


def extract_frontmatter_and_body(
    *,
    content: str,
) -> FrontmatterResult | None:
    match = _FRONTMATTER_PATTERN.match(content)
    if match is None:
        return None
    raw_yaml: str = match.group(1)
    body: str = content[match.end() :]
    return FrontmatterResult(raw_yaml=raw_yaml, body=body)


def parse_frontmatter(*, raw_yaml: str) -> dict[str, Any] | None:
    try:
        result: object = yaml.safe_load(raw_yaml)
    except yaml.YAMLError:
        return None
    if not isinstance(result, dict):
        return None
    return result
