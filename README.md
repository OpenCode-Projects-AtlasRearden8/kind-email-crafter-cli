# kind-email

A friendly Python CLI that turns your rough bullet points into kind, clear
emails and letters. Pick a tone, get a full draft plus a short variant, and
have your own voice rules applied from a simple config file. Everything runs
locally on purpose: your drafts never leave your machine unless you ask.

Part of the family of practical, beginner-friendly tools and guides published
by **Asdale Dynamics, LLC** — the company of Dylan Asdale, author of *The
Massive AI Manual* (https://dylanasdale.github.io), who explains AI the way a
friend would: plain English, step by step, never condescending.

## What it does

- Turns bullet points into a complete letter: greeting, tone-shaped openers,
  bullet body, closing line, sign-off.
- Four tones: `warm`, `firm`, `apology`, `boundary` — each with its own
  phrasing, so a firm email never accidentally reads cold or mean.
- Always two outputs: a **full draft** and a **short variant** for busy people.
- Applies **voice rules** from `kind-email.toml` (your signature, phrases to
  avoid, exclamation marks, emoji, plain-words style).
- Optional refinement through any **OpenAI-compatible** endpoint. Default is
  Ollama on your own computer (`http://localhost:11434/v1`), any model name,
  any base_url. **There is no API-key support in this tool, on purpose.**
- Exports to **Markdown or plain text**, or just prints both drafts to the
  terminal for copy-paste into your mail client.

## Install

```bash
pip install .
```

No runtime dependencies beyond Python 3.11+ — this is a pure-stdlib CLI.
Run tests with `pytest` if you clone the repo.

## Quick start

```bash
# A warm letter from three bullet points
kind-email craft "thanks for the referral" "the intro to michelle worked out great" "id love to link exchange" --to Pat

# Same kind of notes, firm tone
kind-email craft "invoice 102 is overdue" "please resolve by friday" --tone firm -t Sam

# An apology
kind-email craft "your order shipped late" "shoes arrive on tuesday instead" --tone apology

# Set a clear, kind boundary
kind-email craft "calls are better after 3 pm" --tone boundary -t "the team"
```

Useful flags:

| Flag | Meaning |
|---|---|
| `-t/--to` | recipient name |
| `-s/--subject` | override the subject (default: your first bullet) |
| `--tone` | warm, firm, apology, or boundary |
| `-c/--config` | path to your voice config |
| `-o/--out FILE` | write the draft to a file (.md or .txt) |
| `--refine` | polish via the configured endpoint (the only networking flag) |
| `--endpoint` | override base_url, e.g. `http://localhost:11434/v1` |
| `--model` | model name, e.g. `llama3.1` |

You can also run it as a module: `python -m kind_email craft ...`, or preview
the tone library with `kind-email tones`.

## Your voice, your rules

Create `kind-email.toml` in your working folder (or pass `--config`). See
`config.example.toml` for a full example:

```toml
[voice]
name = "Dylan"
greeting = "Hi"
signoff = "Warmly,"

[voice.replacements]
"just wanted to" = "wanted to"
"asap" = "when you have a moment"

no_exclamation_marks = false
no_emojis = true
plain_words = true

[ai]
endpoint = "http://localhost:11434/v1"
model = "llama3.1"
timeout = 30.0
```

The rules apply to the subject, body, and both variants, so every draft sounds
like you instead of like a tool. If no config file exists, a neutral default
voice is used.

## Refinement (optional, local-first)

Without `--refine`, nothing ever touches the network. With it, the tool sends
your draft to a chat-completions endpoint you configured and asks for a polished
rewrite plus a condensed variant:

```bash
# With Ollama already running on your machine (pull a model first: ollama pull llama3.1)
kind-email craft "meeting moved to tuesday" --tone apology --refine
```

If the endpoint is unreachable, returns errors, or speaks nonsense, the CLI
prints a short note and shows the offline draft — you always walk away with a
letter.

**Privacy promise:** drafts are created locally and stay local. Refinement
traffic goes only to whatever server *you* point at, carrying a base_url and a
model name and nothing else. The tool never reads, stores, or transmits an API
key or any credential. Save drafts with `-o FILE` into folders you control.

## Testing

```bash
pytest tests
```

The suite covers the offline drafting engine (all four tones), voice-config
loading, the refinement protocol (via a real local mock server speaking the
OpenAI chat-completions JSON), and the CLI end to end (exports, config use,
and the fallback when refinement is unavailable).

## Why this exists

Writing to people is stressful, especially when it matters: a kind follow-up, a
firm invoice, an apology, a boundary. kind-email takes the things you already
know (your bullet points) and shapes the letter around them, so you can send
sooner and sound like yourself. It is intentionally simple and boring, like the
best tools.

## License

MIT, © **Asdale Dynamics, LLC**. See the LICENSE file in the repository.
