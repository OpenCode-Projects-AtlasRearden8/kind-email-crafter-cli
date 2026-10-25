"""Optional refinement via any OpenAI-compatible chat-completions endpoint.

Uses only a base_url and a model name. The client deliberately has no
support for API keys or auth headers; point it at a local or trusted
endpoint (default: Ollama at http://localhost:11434/v1).
"""

import json
import urllib.error
import urllib.request

from .tones import TONE_GUIDANCE
from .voice import Voice


class RefineError(Exception):
    pass


def _chat_url(base_url):
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


def build_messages(draft_text, tone, voice):
    v = voice if voice is not None else Voice()
    rules = "\n".join(f"- {r}" for r in v.rules_text())
    system = (
        "You are a letter-editing assistant. Rewrite the draft you are given "
        "so it keeps every detail but reads naturally, in plain everyday language. "
        f"Target tone: {TONE_GUIDANCE[tone]}.\n"
        "Style rules:\n"
        f"{rules or '- Keep the wording simple and direct.'}\n"
        "Return exactly the revised full letter, then a line that reads "
        "'--- SHORT VARIANT ---', then a condensed version. No commentary."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": draft_text},
    ]


def parse_reply(content):
    if not content or not content.strip():
        raise RefineError("model returned an empty answer")
    lowered = content.lower()
    marker = lowered.find("short variant")
    if marker == -1:
        return content.strip(), None
    head = content[:marker].rstrip(" -#\n\t").strip()
    tail = content[marker + len("short variant"):].lstrip(" :#-\n\t")
    return head, tail.strip() if tail.strip() else None


def refine(base_url, model, messages, timeout=30.0):
    url = _chat_url(str(base_url))
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "stream": False,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "kind-email-crafter/0.1",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as error:
        raise RefineError(f"endpoint returned HTTP {error.code}") from error
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise RefineError(f"cannot reach endpoint: {error}") from error
    try:
        data = json.loads(raw.decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError, TypeError, UnicodeDecodeError) as error:
        raise RefineError(f"unexpected endpoint reply: {error}") from error
    return parse_reply(content)
