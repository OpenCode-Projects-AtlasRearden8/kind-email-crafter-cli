"""Render drafts for display and export them as Markdown or plain text."""

from pathlib import Path


def render(draft, fmt="md"):
    if fmt == "txt":
        parts = [
            f"DRAFT (tone: {draft['tone']})",
            f"Subject: {draft['subject']}",
            "",
            draft["full"],
        ]
        if draft.get("short"):
            parts += ["", "-" * 40, "", "SHORT VARIANT", f"Subject: {draft['subject']}", "", draft["short"]]
        return "\n".join(parts) + "\n"

    parts = [
        "# Draft (tone: %s)" % draft["tone"],
        "",
        "**Subject:** %s" % draft["subject"],
        "",
        draft["full"],
    ]
    if draft.get("short"):
        parts += ["", "---", "", "# Short variant", "", "**Subject:** %s" % draft["subject"], "", draft["short"]]
    return "\n".join(parts) + "\n"


def resolve_format(out_path, requested="auto"):
    if requested and requested != "auto":
        return requested
    if out_path is None:
        return "txt"
    suffix = Path(out_path).suffix.lower()
    return "txt" if suffix == ".txt" else "md"


def export(text, out_path):
    if out_path is None:
        return None
    path = Path(out_path)
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
