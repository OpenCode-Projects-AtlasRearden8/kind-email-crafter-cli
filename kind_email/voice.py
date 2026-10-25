"""Voice preferences loaded from an optional TOML config file.

Default file name is kind-email.toml in the working directory. If the file
is missing, a neutral default voice is used. The file never stores secrets:
only wording preferences and, optionally, a base_url/model for refinement.
"""

from dataclasses import dataclass, field
import tomllib
from pathlib import Path

DEFAULT_ENDPOINT = "http://localhost:11434/v1"
DEFAULT_MODEL = "llama3.1"
DEFAULT_TIMEOUT = 30.0
DEFAULT_CONFIG_NAME = "kind-email.toml"


@dataclass
class Voice:
    name: str = "Me"
    greeting: str = "Hi"
    signoff: str = ""
    replacements: dict = field(default_factory=dict)
    plain_words: bool = True
    no_exclamation_marks: bool = False
    no_emojis: bool = True

    endpoint: str = DEFAULT_ENDPOINT
    model: str = DEFAULT_MODEL
    timeout: float = DEFAULT_TIMEOUT

    def rules_text(self):
        rules = []
        if self.replacements:
            pairs = "; ".join(f'"{bad}" -> "{good}"' for bad, good in self.replacements.items())
            rules.append("Phrasing preferences, apply everywhere: " + pairs)
        if self.plain_words:
            rules.append("Prefer short sentences and everyday words; no corporate jargon.")
        if self.no_exclamation_marks:
            rules.append("Do not use exclamation marks.")
        if self.no_emojis:
            rules.append("Do not use emojis.")
        if self.signoff:
            rules.append(f'Sign off with "{self.signoff} {self.name}".')
        return rules


def load_voice(path=None):
    if path is None:
        path = Path.cwd() / DEFAULT_CONFIG_NAME
    else:
        path = Path(path)
    if not path.is_file():
        return Voice()
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    voice_data = data.get("voice", {})
    ai_data = data.get("ai", {})
    return Voice(
        name=str(voice_data.get("name", "Me")),
        greeting=str(voice_data.get("greeting", "Hi")),
        signoff=str(voice_data.get("signoff", "")),
        replacements={
            str(bad): str(good) for bad, good in voice_data.get("replacements", {}).items()
        },
        plain_words=bool(voice_data.get("plain_words", True)),
        no_exclamation_marks=bool(voice_data.get("no_exclamation_marks", False)),
        no_emojis=bool(voice_data.get("no_emojis", True)),
        endpoint=str(ai_data.get("endpoint", DEFAULT_ENDPOINT)).rstrip("/"),
        model=str(ai_data.get("model", DEFAULT_MODEL)),
        timeout=float(ai_data.get("timeout", DEFAULT_TIMEOUT)),
    )
