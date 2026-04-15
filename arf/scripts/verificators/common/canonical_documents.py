from dataclasses import dataclass
from pathlib import Path

from arf.scripts.common.artifacts import (
    CanonicalDocumentPathSelection,
    select_canonical_document_path,
)
from arf.scripts.verificators.common.json_utils import load_json_file


@dataclass(frozen=True, slots=True)
class VerificationDocumentPathResolution:
    logical_path: str | None
    file_path: Path | None
    metadata_field: str
    field_present: bool
    used_fallback: bool


def resolve_document_verification_path(
    *,
    target_kind: str,
    document_kind: str,
    details_path: Path,
    asset_dir: Path,
) -> VerificationDocumentPathResolution | None:
    raw_payload: dict[str, object] | None = load_json_file(file_path=details_path)
    payload: dict[str, object] = raw_payload if raw_payload is not None else {}
    selection: CanonicalDocumentPathSelection | None = select_canonical_document_path(
        target_kind=target_kind,
        payload=payload,
        document_kind=document_kind,
    )
    if selection is None:
        return None
    file_path: Path | None = None
    if selection.logical_path is not None:
        file_path = asset_dir / selection.logical_path
    return VerificationDocumentPathResolution(
        logical_path=selection.logical_path,
        file_path=file_path,
        metadata_field=selection.metadata_field,
        field_present=selection.field_present,
        used_fallback=selection.used_fallback,
    )
