from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_apps_script_uses_buffered_assignment_leases() -> None:
    code = (ROOT / "annotator" / "apps-script" / "Code.gs").read_text(encoding="utf-8")
    assert "ASSIGNMENTS: 'Assignments'" in code
    assert "DEFAULT_BUNDLE_SIZE = 5" in code
    assert "LEASE_TTL_MS" in code
    assert "function nextTasks_(params)" in code
    assert "status', 'leased_at', 'expires_at'" in code
    assert "setupAnnotationSheets();\n    const annotatorId" not in code


def test_frontend_prefetches_and_advances_before_waiting_for_submit() -> None:
    app = (ROOT / "annotator" / "app.js").read_text(encoding="utf-8")
    config = (ROOT / "annotator" / "config.js").read_text(encoding="utf-8")
    assert "prefetchCount: 5" in config
    assert "refillThreshold: 2" in config
    assert "const pendingSubmissions = new Set();" in app
    assert "const sessionSeenTaskIds = new Set();" in app
    assert "queueSubmission(payload).catch(() => {});" in app
    assert "showNextTask();" in app
    assert 'url.searchParams.set("count", String(count));' in app


def test_named_pilot_annotator_helpers_exist() -> None:
    code = (ROOT / "annotator" / "apps-script" / "Code.gs").read_text(encoding="utf-8")
    assert "function createVishwanathAnnotator()" in code
    assert "function createSharathAnnotator()" in code
    assert "function createPilotAnnotators()" in code
