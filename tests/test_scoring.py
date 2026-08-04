from scripts.score_indicgenbench import exact_match, token_f1, rouge_l_f1


def test_kannada_exact_match_normalizes_punctuation():
    assert exact_match("ಬೆಂಗಳೂರು!", ["ಬೆಂಗಳೂರು"]) == 1.0


def test_token_f1_prefers_best_reference():
    assert token_f1("ರಾಜ ಹರಿಶ್ಚಂದ್ರ", ["Harishchandra", "ರಾಜ ಹರಿಶ್ಚಂದ್ರ"]) == 1.0


def test_rouge_l_identity():
    assert rouge_l_f1("ಇದು ಒಂದು ಪರೀಕ್ಷೆ", "ಇದು ಒಂದು ಪರೀಕ್ಷೆ") == 1.0
