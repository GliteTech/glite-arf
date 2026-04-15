"""Shared CLI argument definitions for asset aggregators."""

import argparse

OUTPUT_FORMAT_JSON: str = "json"
OUTPUT_FORMAT_MARKDOWN: str = "markdown"
OUTPUT_FORMAT_IDS: str = "ids"

DETAIL_LEVEL_SHORT: str = "short"
DETAIL_LEVEL_FULL: str = "full"


def add_output_format_arg(*, parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format",
        choices=[OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_MARKDOWN, OUTPUT_FORMAT_IDS],
        default=OUTPUT_FORMAT_JSON,
        help="Output format (default: json)",
    )


def add_detail_level_arg(*, parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--detail",
        choices=[DETAIL_LEVEL_SHORT, DETAIL_LEVEL_FULL],
        default=DETAIL_LEVEL_SHORT,
        help="Detail level (default: short)",
    )


def add_filter_args(*, parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--categories",
        nargs="+",
        default=None,
        help="Filter by category slugs (papers matching ANY of them)",
    )
    parser.add_argument(
        "--ids",
        nargs="+",
        default=None,
        help="Filter by asset IDs (exact match)",
    )
