from __future__ import annotations

import hashlib
import re
import unicodedata
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from kannadallmbench.data_registry import DataSource, require_approved
from kannadallmbench.pipelines.transforms import kannada_character_ratio, normalize_text

_SENTENCE_RE = re.compile(r"[^.!?।॥\n]+(?:[.!?।॥]+|(?=\n)|$)")
_URL_OR_EMAIL_RE = re.compile(r"(?:https?://|www\.|\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b)", re.IGNORECASE)
_REPEAT_RE = re.compile(r"(.)\1{5,}")
_KANNADA_RE = re.compile(r"[\u0C80-\u0CFF]")

_ASCII_REPLACEMENTS = (
    ("r̥̄", "rr"),
    ("l̥̄", "ll"),
    ("r̥", "r"),
    ("l̥", "l"),
    ("ā", "aa"),
    ("ī", "ii"),
    ("ū", "uu"),
    ("ē", "ee"),
    ("ō", "oo"),
    ("ṛ", "r"),
    ("ṝ", "rr"),
    ("ḷ", "l"),
    ("ḹ", "ll"),
    ("ṅ", "ng"),
    ("ñ", "ny"),
    ("ṭ", "t"),
    ("ḍ", "d"),
    ("ṇ", "n"),
    ("ś", "sh"),
    ("ṣ", "sh"),
    ("ḻ", "l"),
    ("ṃ", "m"),
    ("ṁ", "m"),
    ("ḥ", "h"),
)


@dataclass(frozen=True)
class RomanBenchFilter:
    min_chars: int = 20
    max_chars: int = 180
    min_words: int = 4
    max_words: int = 30
    min_kannada_ratio: float = 0.75
    max_digit_ratio: float = 0.20


@dataclass(frozen=True)
class ConstructionStats:
    families: int
    records: int
    source_records_scanned: int
    rejected_sentences_or_records: int
    variant_counts: dict[str, int]


def split_candidate_sentences(text: str) -> list[str]:
    """Split corpus text conservatively without language-model rewriting."""
    value = unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))
    if not value.strip():
        return []
    return [normalize_text(match.group(0)) for match in _SENTENCE_RE.finditer(value) if match.group(0).strip()]


def is_candidate_sentence(text: str, config: RomanBenchFilter | None = None) -> bool:
    config = config or RomanBenchFilter()
    text = normalize_text(text)
    if not (config.min_chars <= len(text) <= config.max_chars):
        return False
    words = text.split()
    if not (config.min_words <= len(words) <= config.max_words):
        return False
    if _URL_OR_EMAIL_RE.search(text) or _REPEAT_RE.search(text):
        return False
    if kannada_character_ratio(text) < config.min_kannada_ratio:
        return False
    alnum = [ch for ch in text if ch.isalnum()]
    if alnum:
        digit_ratio = sum(ch.isdigit() for ch in alnum) / len(alnum)
        if digit_ratio > config.max_digit_ratio:
            return False
    return True


def to_iast(text: str) -> str:
    """Transliterate Kannada script to a scholarly Latin baseline using indic-transliteration."""
    try:
        from indic_transliteration import sanscript
        from indic_transliteration.sanscript import transliterate
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Install RomanBench dependencies: pip install -e '.[romanbench]'") from exc
    return normalize_text(transliterate(text, sanscript.KANNADA, sanscript.IAST))


def iast_to_ascii_phonemic(text: str) -> str:
    """Convert IAST-like output to deterministic ASCII while retaining vowel length with doubling."""
    value = text.lower()
    for source, target in _ASCII_REPLACEMENTS:
        value = value.replace(source, target)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.encode("ascii", "ignore").decode("ascii")
    return normalize_text(value)


def relax_ascii_spelling(text: str) -> str:
    """Remove selected vowel-length distinctions as an explicit controlled perturbation."""
    value = text
    for source, target in (("aa", "a"), ("ii", "i"), ("uu", "u"), ("ee", "e"), ("oo", "o")):
        value = value.replace(source, target)
    return normalize_text(value)


def romanization_variants(kannada_text: str) -> dict[str, str]:
    iast = to_iast(kannada_text)
    ascii_phonemic = iast_to_ascii_phonemic(iast)
    variants = {"iast": iast, "ascii_phonemic": ascii_phonemic}
    relaxed = relax_ascii_spelling(ascii_phonemic)
    if relaxed != ascii_phonemic:
        variants["ascii_relaxed"] = relaxed
    return variants


def stable_family_id(source: DataSource, kannada_text: str) -> str:
    normalized = normalize_text(kannada_text)
    payload = f"{source.dataset_id}|{source.revision or ''}|{normalized}".encode("utf-8")
    return f"roman-{hashlib.sha256(payload).hexdigest()[:16]}"


def build_candidate_rows(
    *,
    source: DataSource,
    source_record_index: int,
    sentence_index: int,
    kannada_text: str,
) -> list[dict[str, Any]]:
    """Build one synthetic RomanBench semantic family from a Kannada control sentence."""
    require_approved(source)
    control = normalize_text(kannada_text)
    family_id = stable_family_id(source, control)
    rows: list[dict[str, Any]] = []
    for variant_type, roman_input in romanization_variants(control).items():
        rows.append(
            {
                "id": f"{family_id}-{variant_type}",
                "semantic_family_id": family_id,
                "track": "romanbench",
                "task": "transliteration_normalization",
                "kannada_control": control,
                "roman_input": roman_input,
                "reference_answer": control,
                "variant_type": variant_type,
                "romanization_source": "synthetic_controlled",
                "author_type": "automatic",
                "review_status": "pending",
                "split": "candidate",
                "provenance": {
                    "source_type": "permissive_public_corpus",
                    "source_key": source.key,
                    "source_id": source.dataset_id,
                    "source_revision": source.revision,
                    "source_record_index": source_record_index,
                    "sentence_index": sentence_index,
                    "license_basis": source.license,
                    "human_reviewed": False,
                },
            }
        )
    return rows


def construct_candidate_dataset(
    records: Iterable[dict[str, Any]],
    *,
    source: DataSource,
    text_field: str = "text",
    max_families: int = 2000,
    config: RomanBenchFilter | None = None,
) -> tuple[list[dict[str, Any]], ConstructionStats]:
    """Construct a bounded RomanBench candidate dataset from an approved record stream."""
    require_approved(source)
    if max_families <= 0:
        raise ValueError("max_families must be > 0")
    config = config or RomanBenchFilter()
    seen_controls: set[str] = set()
    output: list[dict[str, Any]] = []
    rejected = 0
    source_records_scanned = 0

    for record_index, record in enumerate(records):
        source_records_scanned += 1
        raw = record.get(text_field)
        if not isinstance(raw, str):
            rejected += 1
            continue
        for sentence_index, sentence in enumerate(split_candidate_sentences(raw)):
            if not is_candidate_sentence(sentence, config):
                rejected += 1
                continue
            if sentence in seen_controls:
                continue
            seen_controls.add(sentence)
            output.extend(
                build_candidate_rows(
                    source=source,
                    source_record_index=record_index,
                    sentence_index=sentence_index,
                    kannada_text=sentence,
                )
            )
            if len(seen_controls) >= max_families:
                break
        if len(seen_controls) >= max_families:
            break

    variants = Counter(row["variant_type"] for row in output)
    stats = ConstructionStats(
        families=len(seen_controls),
        records=len(output),
        source_records_scanned=source_records_scanned,
        rejected_sentences_or_records=rejected,
        variant_counts=dict(sorted(variants.items())),
    )
    return output, stats


def contains_kannada(text: str) -> bool:
    return bool(_KANNADA_RE.search(text))
