import argparse
import re
import sys

# Prefixes that should be stripped before slug conversion.
_DOI_URL_PREFIXES: tuple[str, ...] = (
    "https://doi.org/",
    "http://doi.org/",
    "https://dx.doi.org/",
    "http://dx.doi.org/",
)

# Only characters that are valid in a DOI after the prefix is removed.
# DOI spec (ANSI/NISO Z39.84-2005) allows printable ASCII after the
# directory indicator, but we reject characters that are unsafe in file
# paths or ambiguous in shell contexts.
_ALLOWED_SLUG_CHARS: re.Pattern[str] = re.compile(r"^[A-Za-z0-9._\-]+$")


def doi_to_slug(*, doi: str) -> str:
    cleaned = doi.strip()
    for prefix in _DOI_URL_PREFIXES:
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix) :]
            break

    if len(cleaned) == 0:
        raise ValueError(f"DOI is empty after stripping prefixes: {doi!r}")

    slug = cleaned.replace("/", "_")

    if not _ALLOWED_SLUG_CHARS.match(slug):
        raise ValueError(
            f"DOI produces a slug with disallowed characters: {slug!r} (from DOI {doi!r})"
        )

    return slug


def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a DOI to a deterministic folder-name slug.",
    )
    parser.add_argument(
        "doi",
        help="The DOI to convert (e.g. '10.18653/v1/E17-1010').",
    )
    args = parser.parse_args()

    try:
        slug = doi_to_slug(doi=args.doi)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(slug)


if __name__ == "__main__":
    _main()
