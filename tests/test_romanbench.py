import pytest

from kannadallmbench.data_registry import DataSource
from kannadallmbench.pipelines.romanbench import (
    RomanBenchFilter,
    build_candidate_rows,
    construct_candidate_dataset,
    contains_kannada,
    iast_to_ascii_phonemic,
    is_candidate_sentence,
    relax_ascii_spelling,
    romanization_variants,
    split_candidate_sentences,
    stable_family_id,
)


def source(status: str = "approved") -> DataSource:
    return DataSource(
        key="fixture",
        name="Fixture",
        dataset_id="example/kannada",
        license="CC0-1.0",
        status=status,
        revision="abc123",
        provenance_url="https://example.test",
    )


def test_sentence_split_preserves_newline_boundaries() -> None:
    text = "ಇದು ಮೊದಲ ಸರಳ ಕನ್ನಡ ವಾಕ್ಯವಾಗಿದೆ\nಇದು ಎರಡನೇ ಸರಳ ಕನ್ನಡ ವಾಕ್ಯವಾಗಿದೆ."
    assert split_candidate_sentences(text) == [
        "ಇದು ಮೊದಲ ಸರಳ ಕನ್ನಡ ವಾಕ್ಯವಾಗಿದೆ",
        "ಇದು ಎರಡನೇ ಸರಳ ಕನ್ನಡ ವಾಕ್ಯವಾಗಿದೆ.",
    ]


def test_candidate_filter_rejects_english_and_urls() -> None:
    config = RomanBenchFilter(min_chars=10, min_words=3)
    assert is_candidate_sentence("ಇದು ಪರೀಕ್ಷೆಗೆ ಬಳಸುವ ಸರಳ ಕನ್ನಡ ವಾಕ್ಯವಾಗಿದೆ.", config)
    assert not is_candidate_sentence("This is only an English sentence for testing.", config)
    assert not is_candidate_sentence("ಹೆಚ್ಚಿನ ಮಾಹಿತಿಗೆ https://example.com ವೆಬ್ ಸೈಟ್ ನೋಡಿ.", config)


def test_ascii_conversion_and_relaxation() -> None:
    assert iast_to_ascii_phonemic("kannāḍa bhāṣe") == "kannaada bhaashe"
    assert relax_ascii_spelling("kannaada bhaashe") == "kannada bhashe"


def test_romanization_variants_are_latin_for_kannada_input() -> None:
    variants = romanization_variants("ಕನ್ನಡ ಭಾಷೆ ಚೆನ್ನಾಗಿದೆ")
    assert {"iast", "ascii_phonemic"}.issubset(variants)
    assert all(value for value in variants.values())
    assert all(not contains_kannada(value) for value in variants.values())
    assert variants["ascii_phonemic"].isascii()


def test_stable_family_id_is_deterministic() -> None:
    item = source()
    first = stable_family_id(item, "ಕನ್ನಡ ಭಾಷೆ ಚೆನ್ನಾಗಿದೆ")
    second = stable_family_id(item, "ಕನ್ನಡ ಭಾಷೆ ಚೆನ್ನಾಗಿದೆ")
    assert first == second
    assert first.startswith("roman-")


def test_candidate_rows_share_family_and_preserve_provenance() -> None:
    item = source()
    rows = build_candidate_rows(
        source=item,
        source_record_index=7,
        sentence_index=2,
        kannada_text="ಕನ್ನಡ ಭಾಷೆ ಮಾತನಾಡಲು ನನಗೆ ತುಂಬ ಇಷ್ಟವಾಗಿದೆ.",
    )
    assert len(rows) >= 2
    assert len({row["semantic_family_id"] for row in rows}) == 1
    assert all(row["review_status"] == "pending" for row in rows)
    assert all(row["split"] == "candidate" for row in rows)
    assert all(row["provenance"]["source_revision"] == "abc123" for row in rows)
    assert all(row["provenance"]["human_reviewed"] is False for row in rows)


def test_construct_candidate_dataset_is_bounded_and_deduplicated() -> None:
    records = [
        {"text": "ಇದು ಪರೀಕ್ಷೆಗೆ ಬಳಸುವ ಮೊದಲ ಸರಳ ಕನ್ನಡ ವಾಕ್ಯವಾಗಿದೆ. ಇದು ಇನ್ನೊಂದು ಸರಳ ಕನ್ನಡ ವಾಕ್ಯವಾಗಿದೆ."},
        {"text": "ಇದು ಪರೀಕ್ಷೆಗೆ ಬಳಸುವ ಮೊದಲ ಸರಳ ಕನ್ನಡ ವಾಕ್ಯವಾಗಿದೆ."},
    ]
    rows, stats = construct_candidate_dataset(
        records,
        source=source(),
        max_families=2,
        config=RomanBenchFilter(min_chars=10, min_words=3),
    )
    assert stats.families == 2
    assert stats.records == len(rows)
    assert len({row["semantic_family_id"] for row in rows}) == 2
    assert sum(stats.variant_counts.values()) == len(rows)


def test_construct_candidate_dataset_rejects_unreviewed_source() -> None:
    with pytest.raises(PermissionError):
        construct_candidate_dataset(
            [{"text": "ಇದು ಪರೀಕ್ಷೆಗೆ ಬಳಸುವ ಸರಳ ಕನ್ನಡ ವಾಕ್ಯವಾಗಿದೆ."}],
            source=source("review_required"),
            max_families=1,
            config=RomanBenchFilter(min_chars=10, min_words=3),
        )
