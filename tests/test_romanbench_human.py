from kannadallmbench.pipelines.romanbench_human import (
    authoring_template_row,
    is_unused_authoring_row,
    romanization_task_rows,
    stable_human_family_id,
    validate_authoring_row,
    validate_romanization_rows,
)


def completed_authoring_row(author_id: str = "author-1") -> dict[str, str]:
    row = authoring_template_row(1)
    row.update(
        {
            "kannada_control": "ಇವತ್ತು ಸಂಜೆ ಮನೆಗೆ ಹೋಗುವ ಮೊದಲು ಅಂಗಡಿಗೆ ಹೋಗಬೇಕು.",
            "domain": "daily_life",
            "author_id": author_id,
            "terms_accepted": "yes",
            "original_work_confirmation": "yes",
            "pii_reviewed": "yes",
            "review_decision": "accept",
            "reviewer_id": "reviewer-1",
        }
    )
    return row


def test_blank_template_row_is_unused_and_valid() -> None:
    row = authoring_template_row(1)
    assert is_unused_authoring_row(row)
    assert validate_authoring_row(row, 2) == []


def test_completed_authoring_row_validates() -> None:
    row = completed_authoring_row()
    assert not is_unused_authoring_row(row)
    assert validate_authoring_row(row, 2) == []


def test_authoring_requires_original_work_and_terms() -> None:
    row = completed_authoring_row()
    row["original_work_confirmation"] = "no"
    errors = validate_authoring_row(row, 2)
    assert any("original_work_confirmation must be yes" in error for error in errors)


def test_human_family_id_is_content_stable() -> None:
    first = stable_human_family_id("ಇವತ್ತು ಸಂಜೆ ಮನೆಗೆ ಹೋಗಬೇಕು.")
    second = stable_human_family_id("  ಇವತ್ತು ಸಂಜೆ ಮನೆಗೆ ಹೋಗಬೇಕು.  ")
    assert first == second
    assert first.startswith("rbh-")


def test_romanization_export_creates_independent_slots() -> None:
    row = completed_authoring_row()
    tasks = romanization_task_rows([row], copies=2)
    assert len(tasks) == 2
    assert tasks[0]["semantic_family_id"] == tasks[1]["semantic_family_id"]
    assert {task["slot"] for task in tasks} == {"1", "2"}
    assert all(task["source_author_id"] == "author-1" for task in tasks)
    assert all(task["romanization"] == "" for task in tasks)


def test_valid_independent_romanizations_pass() -> None:
    tasks = romanization_task_rows([completed_authoring_row()], copies=2)
    tasks[0].update(
        {
            "romanizer_id": "romanizer-1",
            "romanization": "ivattu sanje manege hoguva modalu angadige hogabeku",
            "terms_accepted": "yes",
            "independent_confirmation": "yes",
            "pii_reviewed": "yes",
        }
    )
    tasks[1].update(
        {
            "romanizer_id": "romanizer-2",
            "romanization": "ivattu sanje manege hogoke munche angadige hogbeku",
            "terms_accepted": "yes",
            "independent_confirmation": "yes",
            "pii_reviewed": "yes",
        }
    )
    assert validate_romanization_rows(tasks) == []


def test_romanizer_must_differ_from_author_and_each_other() -> None:
    tasks = romanization_task_rows([completed_authoring_row()], copies=2)
    for task in tasks:
        task.update(
            {
                "romanizer_id": "author-1",
                "romanization": "ivattu sanje manege hogbeku",
                "terms_accepted": "yes",
                "independent_confirmation": "yes",
                "pii_reviewed": "yes",
            }
        )
    errors = validate_romanization_rows(tasks)
    assert any("independent of the Kannada author" in error for error in errors)
    assert any("distinct romanizers" in error for error in errors)
    assert any("duplicate human Romanizations" in error for error in errors)
