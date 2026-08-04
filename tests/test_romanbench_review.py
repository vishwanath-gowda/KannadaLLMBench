from scripts.validate_romanbench_review import validate_row


def base_row() -> dict[str, str]:
    return {
        "semantic_family_id": "roman-123",
        "kannada_control": "ಕನ್ನಡ ಭಾಷೆ ಚೆನ್ನಾಗಿದೆ.",
        "human_roman_1": "",
        "human_roman_2": "",
        "review_decision": "",
        "reviewer": "",
        "notes": "",
        "source_key": "indiccorp_v2_kannada",
        "source_revision": "abc123",
        "license_basis": "CC0-1.0",
    }


def test_accept_requires_human_romanization_and_reviewer() -> None:
    row = base_row()
    row["review_decision"] = "accept"
    errors = validate_row(row, 2)
    assert any("reviewer is required" in error for error in errors)
    assert any("require at least one human Romanization" in error for error in errors)


def test_valid_human_review_passes() -> None:
    row = base_row()
    row.update(
        {
            "human_roman_1": "kannada bhaashe chennagide",
            "review_decision": "accept",
            "reviewer": "reviewer-1",
        }
    )
    assert validate_row(row, 2) == []


def test_human_romanization_rejects_kannada_script() -> None:
    row = base_row()
    row.update(
        {
            "human_roman_1": "ಕನ್ನಡ bhaashe",
            "review_decision": "accept",
            "reviewer": "reviewer-1",
        }
    )
    assert any("must use Latin/Roman script" in error for error in validate_row(row, 2))
