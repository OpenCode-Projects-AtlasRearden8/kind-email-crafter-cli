"""Tests for the offline drafting engine."""

import pytest

from kind_email.draft import apply_voice, draft_email
from kind_email.tones import TONE_NAMES


def bullets():
    return [
        "thanks for the referral",
        "the michelle pollack intro worked out great",
        "id love to link exchange",
    ]


@pytest.mark.parametrize("tone", TONE_NAMES)
def test_every_tone_produces_full_and_short(tone):
    draft = draft_email(bullets(), tone=tone, to="Pat")
    assert draft["tone"] == tone
    assert draft["subject"]
    assert "Hi Pat," in draft["full"]
    assert "- Thanks for the referral." in draft["full"]
    assert "- The michelle pollack intro worked out great." in draft["full"]
    assert draft["full"].rstrip().endswith("Me")
    assert "Hi Pat," in draft["short"]
    assert "Thanks for the referral." in draft["short"]


def test_short_variant_is_shorter_and_paragraph_style():
    draft = draft_email(bullets(), tone="warm")
    assert len(draft["short"]) < len(draft["full"])
    assert "- " not in draft["short"]


def test_empty_bullets_raise():
    with pytest.raises(ValueError):
        draft_email([], tone="warm")
    with pytest.raises(ValueError):
        draft_email(["- ", "  ", "*"], tone="warm")


def test_budget_overrides_tone_signoff():
    from kind_email.voice import Voice

    voice = Voice(signoff="All my best,")
    draft = draft_email(["quick hello"], tone="firm", voice=voice)
    assert draft["full"].endswith("All my best,\nMe")


def test_custom_subject_and_generic_recipient():
    draft = draft_email(bullets(), subject="re: the pollack intro", to=None)
    assert draft["subject"] == "Re: the pollack intro"
    assert draft["full"].startswith("Hi,\n")


def test_voice_replacements_flow_into_draft():
    from kind_email.voice import Voice

    voice = Voice(name="Dylan", replacements={"just wanted to": "wanted to"})
    draft = draft_email(["just wanted to follow up"], tone="warm", voice=voice)
    combined = draft["subject"] + draft["full"] + draft["short"]
    assert "just wanted to" not in combined.lower()


def test_apply_voice():
    from kind_email.voice import Voice

    voice = Voice(replacements={"asap": "when you have a moment"}, no_exclamation_marks=True)
    assert apply_voice("Please reply ASAP!!", voice) == "Please reply when you have a moment."
    assert apply_voice("done!", voice) == "Done."
