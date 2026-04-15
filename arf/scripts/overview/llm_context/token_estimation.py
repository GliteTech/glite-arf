"""Token estimation and compatibility helpers for LLM context archives."""

from arf.scripts.overview.llm_context.models import LLMContextWindow

CHARS_PER_TOKEN: float = 4.0

CONTEXT_WINDOWS: list[LLMContextWindow] = [
    LLMContextWindow(
        label="131k-class",
        max_tokens=131_072,
    ),
    LLMContextWindow(
        label="200k-class",
        max_tokens=200_000,
    ),
    LLMContextWindow(
        label="1M-class",
        max_tokens=1_000_000,
    ),
]


def estimate_tokens(*, text: str) -> int:
    return int(len(text) / CHARS_PER_TOKEN)


def compatible_windows(*, estimated_tokens: int) -> list[str]:
    return [window.label for window in CONTEXT_WINDOWS if estimated_tokens <= window.max_tokens]
