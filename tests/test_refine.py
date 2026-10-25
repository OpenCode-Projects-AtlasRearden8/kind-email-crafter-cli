"""Refinement client tests against a local mocked OpenAI-compatible endpoint."""

import pytest

from kind_email.draft import draft_email
from kind_email.refine import RefineError, _chat_url, build_messages, parse_reply, refine
from kind_email.voice import Voice


def test_chat_url_variants():
    assert _chat_url("http://localhost:11434/v1") == "http://localhost:11434/v1/chat/completions"
    assert _chat_url("http://localhost:11434/v1/") == "http://localhost:11434/v1/chat/completions"
    assert _chat_url("http://localhost:11434") == "http://localhost:11434/chat/completions"
    assert _chat_url("http://x:9/v1/chat/completions") == "http://x:9/v1/chat/completions"


def test_build_messages_covers_voice_rules_and_tone():
    voice = Voice(signoff="Warmly,", replacements={"asap": "by end of day"})
    draft = draft_email(["hello there"], tone="warm", voice=voice)
    messages = build_messages(f"Subject: {draft['subject']}\n\n{draft['full']}", "warm", voice)
    assert messages[0]["role"] == "system"
    assert "warm" in messages[0]["content"]
    assert "by end of day" in messages[0]["content"]
    assert "SHORT VARIANT" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert draft["full"] in messages[1]["content"]


def test_refine_hits_mock_endpoint_with_post(good_endpoint):
    messages = build_messages("Subject: Hello\n\nHi Pat,\n\nBody.\n\nMe", "warm", Voice())
    full, short = refine(good_endpoint.base_url, "llama3.1", messages, timeout=10)
    assert "Thank you for waiting so kindly." in full
    assert short == ("Hi Pat,\n\nShort thanks.\n\nAll the best,\nMe")


def test_refine_reports_http_error(broken_endpoint):
    with pytest.raises(RefineError, match="HTTP 500"):
        refine(broken_endpoint.base_url, "llama3.1", build_messages("Hi", "warm", Voice()), timeout=10)


def test_refine_rejects_bad_json(nonsense_endpoint):
    with pytest.raises(RefineError, match="unexpected endpoint reply"):
        refine(nonsense_endpoint.base_url, "llama3.1", build_messages("Hi", "warm", Voice()), timeout=10)


def test_refine_empty_choices_is_rejected(make_endpoint):
    endpoint = make_endpoint()
    with pytest.raises(RefineError, match="unexpected endpoint reply"):
        refine(endpoint.base_url, "llama3.1", build_messages("Hi", "warm", Voice()), timeout=10)


def test_refine_unreachable_endpoint():
    with pytest.raises(RefineError, match="cannot reach endpoint"):
        refine("http://127.0.0.1:1/v1", "llama3.1", build_messages("Hi", "warm", Voice()), timeout=2)


def test_parse_reply_variants():
    full, short = parse_reply("A\n\nB")
    assert (full, short) == ("A\n\nB", None)
    full, short = parse_reply("Letter.\n\n## Short variant\n\nCondensed.")
    assert full == "Letter."
    assert short == "Condensed."
    with pytest.raises(RefineError):
        parse_reply("   ")
