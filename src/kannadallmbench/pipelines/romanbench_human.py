from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass

from kannadallmbench.pipelines.transforms import kannada_character_ratio, normalize_text

_KANNADA_RE = re.compile(r"[\u0C80-\u0CFF]")
_ALLOWED_DOMAINS = {
    "daily_life",
    "workplace",
    "commerce",
    "travel",
    "education",
    "public_services",
    "culture",
    "other",
}
_ALLOWED_DECISIONS = {"accept", "reject", "hold", ""}
_TERMS_VERSION = "romanbench-contributor-v1"
_LICENSE_GRANT = "CC0-1.0"


@dataclass(frozen=True)
class HumanCollectionPolicy:
    min_chars: int = 12
    max_chars: int = 180
    min_words: int = 3
    max_words: int = 30
    min_kannada_ratio: float = 0.70
    required_romanizations: int = 2


def stable_human_family_id(kannada_control: str) -> str:
    normalized = normalize_text(kannada_control)
    payload = f"romanbench-human-v1|{normalized}".encode("utf-8")
    return f"rbh-{hashlib.sha256(payload).hexdigest()[:16]}"


def authoring_template_row(index: int) -> dict[str, str]:
    return {
        "submission_id": f"RB-AUTH-{index:06d}",
        "kannada_control": "",
        "domain": "",
        "author_id": "",
        "terms_version": _TERMS_VERSION,
        "license_grant": _LICENSE_GRANT,
        "terms_accepted": "",
        "original_work_confirmation": "",
        "pii_reviewed": "",
        "author_notes": "",
        "review_decision": "",
        "reviewer_id": "",
        "review_notes": "",
    }


def is_unused_authoring_row(row: dict[str, str]) -> bool:
    """Return true for a preallocated template row that a contributor never started."""
    user_fields = (
        "kannada_control",
        "domain",
        "author_id",
        "terms_accepted",
        "original_work_confirmation",
        "pii_reviewed",
        "author_notes",
        "review_decision",
        "reviewer_id",
        "review_notes",
    )
    return not any(row.get(field, "").strip() for field in user_fields)


def validate_authoring_row(
    row: dict[str, str], line_number: int, policy: HumanCollectionPolicy | None = None
) -> list[str]:
    if is_unused_authoring_row(row):
        return []
    policy = policy or HumanCollectionPolicy()
    errors: list[str] = []
    prefix = f"line {line_number} ({row.get('submission_id', '').strip() or 'missing-id'})"
    text = normalize_text(row.get("kannada_control", ""))
    decision = row.get("review_decision", "").strip().lower()
    domain = row.get("domain", "").strip()

    if not row.get("submission_id", "").strip():
        errors.append(f"{prefix}: submission_id is required")
    if not row.get("author_id", "").strip():
        errors.append(f"{prefix}: pseudonymous author_id is required")
    if row.get("terms_version", "").strip() != _TERMS_VERSION:
        errors.append(f"{prefix}: terms_version must be {_TERMS_VERSION}")
    if row.get("license_grant", "").strip() != _LICENSE_GRANT:
        errors.append(f"{prefix}: license_grant must be {_LICENSE_GRANT}")
    for field in ("terms_accepted", "original_work_confirmation", "pii_reviewed"):
        if row.get(field, "").strip().lower() != "yes":
            errors.append(f"{prefix}: {field} must be yes")
    if domain not in _ALLOWED_DOMAINS:
        errors.append(f"{prefix}: domain must be one of {', '.join(sorted(_ALLOWED_DOMAINS))}")
    if not text:
        errors.append(f"{prefix}: kannada_control is required")
    else:
        if not (policy.min_chars <= len(text) <= policy.max_chars):
            errors.append(f"{prefix}: Kannada control length is outside policy")
        words = text.split()
        if not (policy.min_words <= len(words) <= policy.max_words):
            errors.append(f"{prefix}: Kannada control word count is outside policy")
        if kannada_character_ratio(text) < policy.min_kannada_ratio:
            errors.append(f"{prefix}: Kannada character ratio is below policy")
    if decision not in _ALLOWED_DECISIONS:
        errors.append(f"{prefix}: review_decision must be accept, reject, hold, or blank")
    if decision and not row.get("reviewer_id", "").strip():
        errors.append(f"{prefix}: reviewer_id is required when a decision is recorded")
    return errors


def romanization_task_rows(
    accepted_authoring_rows: list[dict[str, str]], copies: int = 2
) -> list[dict[str, str]]:
    if copies < 1:
        raise ValueError("copies must be >= 1")
    tasks: list[dict[str, str]] = []
    for row in accepted_authoring_rows:
        if row.get("review_decision", "").strip().lower() != "accept":
            continue
        family_id = stable_human_family_id(row["kannada_control"])
        for slot in range(1, copies + 1):
            tasks.append(
                {
                    "semantic_family_id": family_id,
                    "slot": str(slot),
                    "kannada_control": normalize_text(row["kannada_control"]),
                    "domain": row["domain"].strip(),
                    "source_author_id": row["author_id"].strip(),
                    "romanizer_id": "",
                    "romanization": "",
                    "terms_version": _TERMS_VERSION,
                    "license_grant": _LICENSE_GRANT,
                    "terms_accepted": "",
                    "independent_confirmation": "",
                    "pii_reviewed": "",
                    "notes": "",
                }
            )
    return tasks


def validate_romanization_rows(
    rows: list[dict[str, str]], policy: HumanCollectionPolicy | None = None
) -> list[str]:
    policy = policy or HumanCollectionPolicy()
    errors: list[str] = []
    by_family: dict[str, list[dict[str, str]]] = defaultdict(list)

    for line_number, row in enumerate(rows, start=2):
        family_id = row.get("semantic_family_id", "").strip()
        prefix = f"line {line_number} ({family_id or 'missing-family-id'})"
        roman = normalize_text(row.get("romanization", ""))
        romanizer = row.get("romanizer_id", "").strip()
        source_author = row.get("source_author_id", "").strip()
        if not family_id:
            errors.append(f"{prefix}: semantic_family_id is required")
        if not romanizer:
            errors.append(f"{prefix}: romanizer_id is required")
        if romanizer and source_author and romanizer == source_author:
            errors.append(f"{prefix}: romanizer must be independent of the Kannada author")
        if not roman:
            errors.append(f"{prefix}: romanization is required")
        elif _KANNADA_RE.search(roman):
            errors.append(f"{prefix}: romanization must not contain Kannada-script characters")
        if row.get("terms_version", "").strip() != _TERMS_VERSION:
            errors.append(f"{prefix}: terms_version must be {_TERMS_VERSION}")
        if row.get("license_grant", "").strip() != _LICENSE_GRANT:
            errors.append(f"{prefix}: license_grant must be {_LICENSE_GRANT}")
        for field in ("terms_accepted", "independent_confirmation", "pii_reviewed"):
            if row.get(field, "").strip().lower() != "yes":
                errors.append(f"{prefix}: {field} must be yes")
        by_family[family_id].append(row)

    for family_id, family_rows in by_family.items():
        if not family_id:
            continue
        completed = [row for row in family_rows if row.get("romanization", "").strip()]
        if len(completed) < policy.required_romanizations:
            errors.append(
                f"family {family_id}: requires at least {policy.required_romanizations} completed Romanizations"
            )
        romanizers = [row.get("romanizer_id", "").strip() for row in completed]
        if len(set(filter(None, romanizers))) < min(policy.required_romanizations, len(completed)):
            errors.append(f"family {family_id}: Romanizations must come from distinct romanizers")
        normalized_forms = [normalize_text(row.get("romanization", "")).lower() for row in completed]
        duplicates = Counter(normalized_forms)
        if any(count > 1 for form, count in duplicates.items() if form):
            errors.append(f"family {family_id}: duplicate human Romanizations should be independently re-authored")
    return errors


def terms_version() -> str:
    return _TERMS_VERSION


def license_grant() -> str:
    return _LICENSE_GRANT
