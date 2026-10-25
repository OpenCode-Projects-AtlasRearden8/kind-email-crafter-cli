"""Tests for voice-config loading (TOML) and defaults."""

import pytest

from kind_email.voice import Voice, load_voice


def test_missing_file_gives_neutral_defaults(tmp_path):
    voice = load_voice(tmp_path / "nope.toml")
    assert isinstance(voice, Voice)
    assert voice.endpoint == "http://localhost:11434/v1"
    assert voice.model == "llama3.1"
    assert voice.replacements == {}


def test_load_voice_from_file(tmp_path):
    config = tmp_path / "kind-email.toml"
    config.write_text(
        "\n".join(
            [
                "[voice]",
                'name = "Dylan Asdale"',
                'greeting = "Hello"',
                'signoff = "All best,"',
                "plain_words = false",
                'no_exclamation_marks = true',
                "",
                "[voice.replacements]",
                '"asap" = "by end of day"',
                "",
                "[ai]",
                'endpoint = "http://localhost:8080/v1"',
                'model = "qwen2.5"',
                "timeout = 12.0",
            ]
        ),
        encoding="utf-8",
    )
    voice = load_voice(config)
    assert voice.name == "Dylan Asdale"
    assert voice.greeting == "Hello"
    assert voice.signoff == "All best,"
    assert voice.plain_words is False
    assert voice.no_exclamation_marks is True
    assert voice.replacements == {"asap": "by end of day"}
    assert voice.endpoint == "http://localhost:8080/v1"
    assert voice.model == "qwen2.5"
    assert voice.timeout == 12.0


def test_rules_text_accumulates_preferences():
    voice = Voice(signoff="Warmly,", replacements={"very": ""}, no_emojis=True)
    rules = voice.rules_text()
    assert any('"very" -> ""' in rule for rule in rules)
    assert any('"Warmly, Me"' in rule for rule in rules)
