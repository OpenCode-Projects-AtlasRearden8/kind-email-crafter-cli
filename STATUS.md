# STATUS.md — kind-email-crafter-cli

Project state as of October 25, 2026.

## What was built

**kind-email** — a pure-Python (stdlib-only) CLI that drafts kind, clear
emails and letters from bullet points.

- `kind_email/cli.py` — argparse CLI with two commands: `craft` (bullets to
  letter; flags for tone, recipient, subject, config, export, refinement) and
  `tones` (tone library preview).
- `kind_email/draft.py` — offline drafting engine: bullet cleanup, tone-shaped
  full draft + short variant, voice-rule post-processing.
- `kind_email/tones.py` — the four tone banks (warm, firm, apology, boundary)
  plus per-tone model guidance used by refinement.
- `kind_email/voice.py` — TOML voice-config loader (`kind-email.toml`,
  defaults, dataclass `Voice`, rules text for the model prompt).
- `kind_email/refine.py` — optional OpenAI-compatible chat-completions client
  (stdlib `urllib`; base_url + model only; **no key/auth support by design**;
  reply parser splits full draft / short variant).
- `kind_email/export.py` — Markdown and plain-text renderers, format
  resolution from output suffix, file export.
- `config.example.toml` — documented voice/endpoint config template.
- `tests/` — 30 pytest tests: draft engine across all tones, TOML config
  loading, refinement protocol against a real local mock HTTP server
  (`http.server`, returns OpenAI-shaped JSON), and CLI end-to-end (stdout,
  md/txt export, config use, refine success and graceful fallback).
- `README.md`, MIT `LICENSE` (Copyright (c) 2026 Asdale Dynamics, LLC),
  `pyproject.toml` with `kind-email` console script entry point.

## How to run it

```bash
pip install .            # or use python -m kind_email directly from the repo
kind-email craft "your bullet" "another bullet" --to Pat --tone warm
kind-email craft "invoice overdue" --tone firm -t Sam -o letter.md
kind-email craft "meeting moved" --tone apology --refine   # optional; needs Ollama or another OpenAI-compatible endpoint
kind-email tones
pytest tests             # test suite
```

Refinement flags: `--refine --endpoint BASE_URL --model NAME --timeout SECS`.
Defaults: `http://localhost:11434/v1` (Ollama), model `llama3.1`.
No API keys are ever read, stored, or sent.

## Verification results (all confirmed in this workspace)

- `python3 -m pytest -q` → **30 passed** (Python 3.13.5, pytest 9.1.1).
- `pip install -e .` → editable install succeeds; `kind-email --version`
  → `kind-email 0.1.0`; `kind-email tones` lists all four tones.
- End-to-end runs verified: warm/firm/apology/boundary drafts printed with
  subject, full draft, and short variant; voice replacements applied
  (`asap` → `when you have a moment`, `just wanted to` → `wanted to`); export
  to `.md` and `.txt` confirmed on disk; `--refine` against an unreachable
  endpoint exits 0 with the local draft plus a stderr note; `--refine`
  against the mocked endpoint returns the polished full + short variant.
- No secrets, keys, or personal data in any tracked file; endpoints are
  configurable base URLs only.

## Known gaps / next steps

- Offline drafts use canned openers/bridges per tone; they are solid but
  clearly templated — a small variation bank would help repeat senders.
- Refinement assumes an endpoint that returns
  `choices[0].message.content`; response-format options (e.g. `response_format`),
  streaming, and non-chat endpoints are not handled.
- Voice rules are phrase-level; no grammar-level rewriting offline and no
  per-tone rule sets in the config yet.
- No localization or HTML email output; plain text and Markdown only.
- Windows console emoji/encoding nuances untested (CI is not set up).
