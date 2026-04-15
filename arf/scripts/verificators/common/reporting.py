import sys

from arf.scripts.verificators.common.types import (
    Diagnostic,
    VerificationResult,
)

ANSI_RED: str = "\033[31m"
ANSI_YELLOW: str = "\033[33m"
ANSI_GREEN: str = "\033[32m"
ANSI_RESET: str = "\033[0m"
ANSI_BOLD: str = "\033[1m"


def format_diagnostic(*, diagnostic: Diagnostic) -> str:
    severity_label: str = diagnostic.code.severity.value
    line: str = f"  {diagnostic.code.text} {severity_label}: {diagnostic.message}"
    if diagnostic.detail is not None:
        line += f"\n    {diagnostic.detail}"
    return line


def print_verification_result(*, result: VerificationResult) -> None:
    print(f"\nVerifying: {result.file_path}\n")

    errors: list[Diagnostic] = result.errors
    warnings: list[Diagnostic] = result.warnings

    if len(errors) > 0:
        print(f"{ANSI_RED}{ANSI_BOLD}ERRORS:{ANSI_RESET}")
        for diagnostic in errors:
            print(f"{ANSI_RED}{format_diagnostic(diagnostic=diagnostic)}{ANSI_RESET}")
        print()

    if len(warnings) > 0:
        print(f"{ANSI_YELLOW}{ANSI_BOLD}WARNINGS:{ANSI_RESET}")
        for diagnostic in warnings:
            print(
                f"{ANSI_YELLOW}{format_diagnostic(diagnostic=diagnostic)}{ANSI_RESET}",
            )
        print()

    error_count: int = len(errors)
    warning_count: int = len(warnings)

    if error_count == 0 and warning_count == 0:
        print(f"{ANSI_GREEN}{ANSI_BOLD}PASSED{ANSI_RESET} — no errors or warnings\n")
    else:
        color: str = ANSI_RED if error_count > 0 else ANSI_YELLOW
        status: str = "FAILED" if error_count > 0 else "PASSED"
        print(
            f"{color}{ANSI_BOLD}{status}{ANSI_RESET}"
            f" — {error_count} error(s), {warning_count} warning(s)\n",
        )

    sys.stdout.flush()


def exit_code_for_result(*, result: VerificationResult) -> int:
    if result.passed:
        return 0
    return 1
