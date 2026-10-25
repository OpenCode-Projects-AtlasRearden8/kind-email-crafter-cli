"""Command-line interface for kind-email.

Local by default: drafting runs entirely offline. Networking happens only
when you pass --refine, and the request goes to whatever base_url/model
you configured (default: Ollama on localhost). No API keys are ever read,
stored, or sent.
"""

import argparse
import sys

from . import __version__
from .draft import draft_email
from .export import export, render, resolve_format
from .refine import RefineError, build_messages, refine
from .tones import TONE_DATA, TONE_NAMES
from .voice import DEFAULT_CONFIG_NAME, load_voice


def build_parser():
    parser = argparse.ArgumentParser(
        prog="kind-email",
        description=(
            "Draft kind, clear emails and letters from bullet points. "
            "Pick a tone, get a full draft plus a short variant, shaped by "
            "your voice config. Add --refine to polish via an "
            "OpenAI-compatible endpoint (default Ollama, localhost only)."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    craft = subparsers.add_parser(
        "craft", help="turn bullet points into a tone-shaped letter"
    )
    craft.add_argument(
        "bullets",
        nargs="+",
        metavar="BULLET",
        help="what the letter should say, one point per argument",
    )
    craft.add_argument("-t", "--to", default="", help="recipient name, e.g. Sarah")
    craft.add_argument("-s", "--subject", default=None, help="subject line (default: your first bullet)")
    craft.add_argument(
        "--tone",
        choices=TONE_NAMES,
        default="warm",
        help="warm, firm, apology, or boundary (default: warm)",
    )
    craft.add_argument(
        "-c",
        "--config",
        default=None,
        help=f"voice config TOML (default: {DEFAULT_CONFIG_NAME} in this folder)",
    )
    craft.add_argument("-o", "--out", default=None, help="write the draft to this file (.md or .txt)")
    craft.add_argument(
        "--format", choices=("auto", "md", "txt"), default="auto",
        help="export format; auto picks md, or txt for .txt outputs",
    )
    craft.add_argument(
        "--refine",
        action="store_true",
        help="polish via the configured OpenAI-compatible endpoint (opt-in network use)",
    )
    craft.add_argument("--endpoint", default=None, help="override base_url, e.g. http://localhost:11434/v1")
    craft.add_argument("--model", default=None, help="override model, e.g. llama3.1")
    craft.add_argument("--timeout", type=float, default=None, help="endpoint timeout in seconds")

    tones_cmd = subparsers.add_parser("tones", help="list the available tones")
    tones_cmd.add_argument("-c", "--config", default=None)

    return parser


def _run_tones(config):
    voice = load_voice(config)
    for name in TONE_NAMES:
        bank = TONE_DATA[name]
        effective = voice.signoff if voice.signoff else bank["signoff"]
        print(f"{name}")
        print(f"  opener : {bank['opener']}")
        print(f"  closing: {bank['closing']}")
        print(f"  signoff: {effective}")
    return 0


def _try_refine(args, voice, draft):
    messages = build_messages(render_plain(draft), args.tone, voice)
    base_url = args.endpoint or voice.endpoint
    model = args.model or voice.model
    timeout = args.timeout if args.timeout is not None else voice.timeout
    full, short = refine(base_url, model, messages, timeout=timeout)
    refined = {"subject": draft["subject"], "full": full, "short": short, "tone": draft["tone"]}
    return refined


def render_plain(draft):
    return f"Subject: {draft['subject']}\n\n{draft['full']}"


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "tones":
        return _run_tones(args.config)

    voice = load_voice(args.config)
    try:
        draft = draft_email(
            args.bullets,
            tone=args.tone,
            to=args.to,
            subject=args.subject,
            voice=voice,
        )
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    fmt = resolve_format(args.out, args.format)
    if args.refine:
        try:
            draft = _try_refine(args, voice, draft)
        except RefineError as error:
            print(f"note: refinement unavailable ({error}); showing the local draft", file=sys.stderr)

    text = render(draft, fmt=fmt)
    print(text)
    written = export(text, args.out)
    if written is not None:
        print(f"saved: {written}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
