from __future__ import annotations

import csv

import pytest

from kannadallmbench.annotation_tasks import pair_to_task, romanbench_candidate_to_task, write_tasks_csv


def test_romanbench_candidate_to_task_preserves_provenance() -> None:
    row = {
        "id": "roman-1-ascii",
        "semantic_family_id": "roman-1",
        "kannada_control": "ನಾನು ಮನೆಗೆ ಹೋಗಬೇಕು.",
        "roman_input": "nanu manege hogbeku",
        "variant_type": "ascii_relaxed",
        "provenance": {
            "source_type": "permissive_public_corpus",
            "source_id": "ai4bharat/IndicCorpV2",
            "source_author_id": "",
        },
    }
    task = romanbench_candidate_to_task(row, batch_id="pilot", target_votes=3)
    assert task["task_id"] == "roman-1-ascii"
    assert task["semantic_family_id"] == "roman-1"
    assert task["kannada"] == "ನಾನು ಮನೆಗೆ ಹೋಗಬೇಕು."
    assert task["roman"] == "nanu manege hogbeku"
    assert task["target_votes"] == 3
    assert task["active"] is True
    assert task["source_id"] == "ai4bharat/IndicCorpV2"


def test_pair_to_task_supports_existing_permissive_pairs() -> None:
    row = {"pair_id": "k1", "kn": "ಕನ್ನಡ ಚೆನ್ನಾಗಿದೆ", "latin": "kannada chennagide"}
    task = pair_to_task(
        row,
        task_id_field="pair_id",
        family_id_field="pair_id",
        kannada_field="kn",
        roman_field="latin",
        batch_id="existing-data-pilot",
        source_id="example/permissive-dataset",
    )
    assert task["task_id"] == "k1"
    assert task["semantic_family_id"] == "k1"
    assert task["source_type"] == "existing_pair"
    assert task["source_id"] == "example/permissive-dataset"


def test_invalid_target_votes_rejected() -> None:
    with pytest.raises(ValueError):
        romanbench_candidate_to_task(
            {
                "id": "1",
                "semantic_family_id": "1",
                "kannada_control": "ಕನ್ನಡ",
                "roman_input": "kannada",
            },
            batch_id="pilot",
            target_votes=0,
        )


def test_write_tasks_csv_uses_sheet_schema(tmp_path) -> None:
    output = tmp_path / "tasks.csv"
    count = write_tasks_csv(
        [
            {
                "task_id": "1",
                "semantic_family_id": "f1",
                "kannada": "ಕನ್ನಡ",
                "roman": "kannada",
                "batch_id": "pilot",
                "target_votes": 2,
                "active": True,
            }
        ],
        output,
    )
    assert count == 1
    with output.open(encoding="utf-8", newline="") as handle:
        row = next(csv.DictReader(handle))
    assert row["task_id"] == "1"
    assert row["batch_id"] == "pilot"
    assert row["target_votes"] == "2"
