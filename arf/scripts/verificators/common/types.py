from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class DiagnosticCode:
    prefix: str
    severity: Severity
    number: int

    @property
    def text(self) -> str:
        severity_char: str = "E" if self.severity is Severity.ERROR else "W"
        return f"{self.prefix}-{severity_char}{self.number:03d}"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: DiagnosticCode
    message: str
    file_path: Path
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class VerificationResult:
    file_path: Path
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def errors(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.code.severity is Severity.ERROR]

    @property
    def warnings(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.code.severity is Severity.WARNING]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0
