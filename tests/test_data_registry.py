from pathlib import Path

import pytest

from kannadallmbench.data_registry import load_data_sources, require_approved, validate_registry


REGISTRY = Path(__file__).parents[1] / "config" / "data_sources.yaml"


def test_registry_is_valid_and_has_approved_cc0_source() -> None:
    assert validate_registry(REGISTRY) == []
    sources = load_data_sources(REGISTRY)
    source = sources["indiccorp_v2_kannada"]
    assert source.approved
    assert source.license == "CC0-1.0"
    assert source.revision


def test_unreviewed_source_is_blocked_by_default() -> None:
    source = load_data_sources(REGISTRY)["aya_collection"]
    with pytest.raises(PermissionError):
        require_approved(source)
    require_approved(source, allow_unreviewed=True)
