from ml.features.text_signals import extract_text_signals


def test_urgency_and_credential_detected_with_evidence():
    s = extract_text_signals("Your account will be suspended within 24 hours. Please verify your password now.")
    assert "urgent" in s and "credential" in s
    assert any("password" in h.lower() for h in s["credential"])


def test_negated_credential_phrase_not_flagged():
    assert "credential" not in extract_text_signals("We will never ask you to confirm your password by email.")


def test_benign_text_has_no_signals():
    assert extract_text_signals("Lunch at one tomorrow? Agenda attached for the meeting.") == {}


def test_advance_fee_needs_two_groups():
    two = extract_text_signals("I am the beneficiary of an inheritance worth 15 million dollars, please assist in the transfer of the funds")
    one = extract_text_signals("The beneficiary list is attached.")
    assert "advance_fee" in two and "advance_fee" not in one


def test_non_string_input_is_safe():
    assert extract_text_signals(None) == {}