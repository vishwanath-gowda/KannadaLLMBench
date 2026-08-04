import pytest

from kannadallmbench.pipelines.dedup import deduplicate_records
from kannadallmbench.pipelines.slice import slice_records
from kannadallmbench.pipelines.transforms import normalize_text


def test_normalize_text_is_conservative() -> None:
    assert normalize_text("  ನಾನು\n  ಚೆನ್ನಾಗಿದ್ದೇನೆ  ") == "ನಾನು ಚೆನ್ನಾಗಿದ್ದೇನೆ"


def test_dedup_uses_normalized_text() -> None:
    rows = [{"text": "ನಮಸ್ಕಾರ"}, {"text": "  ನಮಸ್ಕಾರ  "}, {"text": "ಹೇಗಿದ್ದೀರಿ"}]
    assert list(deduplicate_records(rows, "text")) == [rows[0], rows[2]]


def test_slice_by_record_count() -> None:
    rows = [{"text": str(i)} for i in range(10)]
    assert list(slice_records(rows, max_records=3)) == rows[:3]


def test_slice_by_bytes_keeps_at_least_one_record() -> None:
    rows = [{"text": "x" * 100}, {"text": "second"}]
    assert list(slice_records(rows, max_bytes=1)) == rows[:1]


def test_slice_requires_a_bound() -> None:
    with pytest.raises(ValueError):
        list(slice_records([{"text": "x"}]))
