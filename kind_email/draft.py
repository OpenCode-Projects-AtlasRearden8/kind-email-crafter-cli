"""Offline drafting engine: turns bullet points into tone-shaped letters."""

import re

from .tones import TONE_DATA, tone_bank
from .voice import Voice


def _sentence(text):
    text = re.sub(r"\s+", " ", str(text)).strip().strip("-•*").strip()
    if not text:
        return None
    text = text[0].upper() + text[1:]
    if text[-1] not in ".!?:":
        text += "."
    return text


def _normalize_bullets(bullets):
    cleaned = [s for s in (_sentence(b) for b in bullets) if s]
    if not cleaned:
        raise ValueError("draft_email needs at least one bullet point")
    return cleaned


def _topic(first_bullet):
    text = first_bullet.strip()
    if not text:
        return None
    text = text[0].upper() + text[1:]
    return text.rstrip(".!?:")


def draft_email(bullets, *, tone="warm", to=None, subject=None, voice=None):
    bank = tone_bank(tone)
    v = voice if voice is not None else Voice()
    cleaned = _normalize_bullets(bullets)
    if subject:
        subj = _topic(str(subject))
    else:
        subj = _topic(bullets[0])
    subj = subj if subj else "A quick note"
    subj = apply_voice(subj, v)

    recipient = to if to else ""
    greet = f"{v.greeting} {recipient}," if recipient else f"{v.greeting},"

    full_body = "\n\n".join(
        [
            bank["opener"],
            bank["bridge"],
            "\n".join(f"- {bullet}" for bullet in cleaned),
            bank["closing"],
        ]
    )
    signoff_block = f"{v.signoff if v.signoff else bank['signoff']}" + (
        f"\n{v.name}" if v.name else ""
    )
    full = f"{greet}\n\n{full_body}\n\n{signoff_block}"

    short_body = "\n\n".join(
        [
            bank["variant_opener"],
            " ".join(cleaned),
            bank["variant_closing"],
        ]
    )
    short = f"{greet}\n\n{short_body}\n\n{signoff_block}"

    return {
        "subject": subj,
        "full": apply_voice(full, v),
        "short": apply_voice(short, v),
        "tone": tone,
    }


def apply_voice(text, voice=None):
    v = voice if voice is not None else Voice()
    for bad, good in v.replacements.items():
        text = re.sub(re.escape(bad), good, text, flags=re.IGNORECASE)
    if v.no_exclamation_marks:
        text = re.sub(r"!+", ".", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    if text:
        text = text[0].upper() + text[1:]
    return text
