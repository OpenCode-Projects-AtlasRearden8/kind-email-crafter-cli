"""Tone presets used by the offline drafting engine.

Each tone provides phrasing for a full draft and a condensed variant.
The wording is deliberately plain and human; the voice config can layer
personal preferences on top.
"""

TONE_NAMES = ("warm", "firm", "apology", "boundary")

TONE_DATA = {
    "warm": {
        "opener": "Thank you for taking the time to read this.",
        "bridge": "Here is what I wanted to put in front of you:",
        "closing": "If anything here needs adjusting, I am happy to work it out together.",
        "signoff": "Warmly,",
        "variant_opener": "The short version:",
        "variant_closing": "Thank you again for reading.",
    },
    "firm": {
        "opener": "I am writing to be clear about where things stand.",
        "bridge": "These are the points that matter:",
        "closing": "I am confident this is the right approach, and I ask for a reply by Friday if anything needs to change.",
        "signoff": "Best regards,",
        "variant_opener": "Bottom line:",
        "variant_closing": "Unless I hear differently, I will move forward on this basis.",
    },
    "apology": {
        "opener": "I am sorry about what happened, and I wanted to address it directly.",
        "bridge": "So you know the full picture:",
        "closing": "I appreciate your patience, and I will make sure this is put right.",
        "signoff": "Sincerely,",
        "variant_opener": "In short:",
        "variant_closing": "Again, I am sorry, and I appreciate your patience.",
    },
    "boundary": {
        "opener": "I want to be upfront about what I can and cannot do.",
        "bridge": "Here is where things stand:",
        "closing": "I hope this is workable for you, and I mean it kindly.",
        "signoff": "Best,",
        "variant_opener": "To keep it simple:",
        "variant_closing": "Thank you for understanding.",
    },
}

TONE_GUIDANCE = {
    "warm": "warm and personal: patient, encouraging, honest rather than flattering",
    "firm": "firm and clear: a strong position stated respectfully, no hedging",
    "apology": "apologetic and accountable: own the mistake plainly and state what happens next",
    "boundary": "kind but bounded: state the limit clearly, no guilt, no over-explaining",
}


def tone_bank(tone):
    if tone not in TONE_DATA:
        raise KeyError(f"unknown tone: {tone!r}")
    return TONE_DATA[tone]
