from pathlib import Path
from kannadallmbench.registry import load_registry


def test_external_registry_is_pinned():
    root = Path(__file__).resolve().parents[1]
    registry = load_registry(root / "external" / "registry.json")
    assert set(registry) == {"milu", "indicifeval", "indicgenbench"}
    assert all(len(item.revision) == 40 for item in registry.values())
