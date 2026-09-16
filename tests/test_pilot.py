from __future__ import annotations

from kannadallmbench.pilot import analyze_annotations, disagreement_rows, select_pilot_tasks


def _candidate(family: int, variant: str) -> dict:
    return {
        "id": f"id-{family}-{variant}",
        "semantic_family_id": f"family-{family:03d}",
        "kannada_control": f"ಕನ್ನಡ {family}",
        "roman_input": f"roman-{family}-{variant}",
        "variant_type": variant,
        "romanization_source": "synthetic_controlled",
        "provenance": {"source_type": "corpus", "source_id": "test"},
    }


def test_select_pilot_tasks_is_deterministic_and_one_per_family() -> None:
    rows = []
    for family in range(40):
        for variant in ("ascii_phonemic", "ascii_relaxed", "iast"):
            rows.append(_candidate(family, variant))

    forward = select_pilot_tasks(rows, families=30, seed="fixed")
    reverse = select_pilot_tasks(reversed(rows), families=30, seed="fixed")

    assert forward == reverse
    assert len(forward) == 30
    assert len({row["semantic_family_id"] for row in forward}) == 30
    assert all(row["target_votes"] == 2 for row in forward)
    assert all(row["batch_id"] == "pilot-v1" for row in forward)

    counts = {}
    for row in forward:
        counts[row["variant_type"]] = counts.get(row["variant_type"], 0) + 1
    assert counts == {"ascii_phonemic": 10, "ascii_relaxed": 10, "iast": 10}


def test_select_pilot_tasks_requires_enough_families() -> None:
    rows = [_candidate(0, "ascii_phonemic")]
    try:
        select_pilot_tasks(rows, families=2)
    except ValueError as exc:
        assert "only 1 are available" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_analyze_annotations_respects_conditional_typing_question() -> None:
    rows = [
        {
            "task_id": "t1",
            "semantic_family_id": "f1",
            "annotator_id": "a1",
            "meaning_correct": "yes",
            "typeable_romanization": "yes",
            "skipped": "false",
        },
        {
            "task_id": "t1",
            "semantic_family_id": "f1",
            "annotator_id": "a2",
            "meaning_correct": "yes",
            "typeable_romanization": "yes",
            "skipped": "false",
        },
        {
            "task_id": "t2",
            "semantic_family_id": "f2",
            "annotator_id": "a1",
            "meaning_correct": "yes",
            "typeable_romanization": "no",
            "skipped": "false",
        },
        {
            "task_id": "t2",
            "semantic_family_id": "f2",
            "annotator_id": "a2",
            "meaning_correct": "yes",
            "typeable_romanization": "yes",
            "skipped": "false",
        },
        {
            "task_id": "t3",
            "semantic_family_id": "f3",
            "annotator_id": "a1",
            "meaning_correct": "no",
            "typeable_romanization": "",
            "skipped": "false",
        },
        {
            "task_id": "t3",
            "semantic_family_id": "f3",
            "annotator_id": "a2",
            "meaning_correct": "no",
            "typeable_romanization": "",
            "skipped": "false",
        },
        {
            "task_id": "t4",
            "semantic_family_id": "f4",
            "annotator_id": "a1",
            "meaning_correct": "",
            "typeable_romanization": "",
            "skipped": "true",
        },
    ]

    summary = analyze_annotations(rows)

    assert summary["annotations"] == 7
    assert summary["skipped_annotations"] == 1
    assert summary["meaning"]["pairwise_agreement"] == 1.0
    assert summary["roman_typing"]["pairwise_agreement"] == 0.5
    assert summary["roman_typing"]["eligible_judgments"] == 4
    assert summary["meaning_yes_typing_no"]["count"] == 1
    assert summary["meaning_yes_typing_no"]["rate_among_meaning_yes"] == 0.25

    disagreements = disagreement_rows(rows)
    assert disagreements == [
        {
            "task_id": "t2",
            "semantic_family_id": "f2",
            "dimension": "roman_typing",
            "labels": "no|yes",
            "annotators": "a1|a2",
        }
    ]
