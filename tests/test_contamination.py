from kannadallmbench.contamination import exact_overlap_count


def test_exact_overlap_normalizes_whitespace() -> None:
    train = [{"text": "ನಾನು ಮನೆಗೆ ಹೋಗುತ್ತೇನೆ"}, {"text": "ಬೇರೆ ವಾಕ್ಯ"}]
    benchmark = [{"prompt": "  ನಾನು   ಮನೆಗೆ ಹೋಗುತ್ತೇನೆ "}, {"prompt": "ಹೊಸ ಪ್ರಶ್ನೆ"}]
    report = exact_overlap_count(train, benchmark, training_field="text", benchmark_field="prompt")
    assert report.training_records == 2
    assert report.benchmark_records == 2
    assert report.exact_overlaps == 1
