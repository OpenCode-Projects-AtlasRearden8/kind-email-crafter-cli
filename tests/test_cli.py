"""End-to-end CLI tests (invoke cli.main directly)."""

import pytest

from kind_email import cli


def test_craft_local_warm(capsys):
    code = cli.main(
        [
            "craft",
            "thanks for the referral",
            "id love to link exchange",
            "--to",
            "Pat",
            "--tone",
            "warm",
        ]
    )
    out = capsys.readouterr()
    assert code == 0
    assert "Hi Pat," in out.out
    assert "Subject:" in out.out
    assert "SHORT VARIANT" in out.out
    assert "- Thanks for the referral." in out.out


def test_craft_firm_apology_boundary(capsys):
    for tone in ("firm", "apology", "boundary"):
        code = cli.main(["craft", "invoice is overdue", "--tone", tone, "-t", "Sam"])
        out = capsys.readouterr()
        assert code == 0
        assert f"DRAFT (tone: {tone})" in out.out


def test_craft_exports_markdown_and_text(tmp_path, capsys):
    md_path = tmp_path / "letter.md"
    txt_path = tmp_path / "letter.txt"
    code = cli.main(["craft", "a quick hello", "-o", str(md_path)])
    assert code == 0
    assert "# Draft" in md_path.read_text(encoding="utf-8")
    cli.main(["craft", "a quick hello", "--tone", "apology", "-o", str(txt_path)])
    content = txt_path.read_text(encoding="utf-8")
    assert content.startswith("DRAFT (tone: apology)")
    assert "SHORT VARIANT" in content
    assert "saved:" in capsys.readouterr().err


def test_craft_with_voice_config(tmp_path, capsys):
    config = tmp_path / "voice.toml"
    config.write_text(
        "[voice]\n"
        'name = "Dylan"\n'
        "[voice.replacements]\n"
        '"asap" = "by end of day"\n',
        encoding="utf-8",
    )
    code = cli.main(["craft", "please reply asap", "-c", str(config), "-t", "Pat"])
    assert code == 0
    out = capsys.readouterr()
    assert "please reply asap" not in out.out.lower()
    assert "by end of day" in out.out
    assert "Dylan" in out.out


def test_craft_refine_with_mocked_endpoint(capsys, make_endpoint):
    endpoint = make_endpoint(
        reply_content=(
            "Hi,\n\nPolished full version.\n\nWarmly,\nMe\n\n"
            "--- SHORT VARIANT ---\nHi,\n\nPolished short version.\n\nWarmly,\nMe"
        )
    )
    code = cli.main(
        [
            "craft",
            "thanks for everything",
            "--refine",
            "--endpoint",
            endpoint.base_url,
            "--timeout",
            "10",
        ]
    )
    out = capsys.readouterr()
    assert code == 0
    assert "Polished full version." in out.out
    assert "Polished short version." in out.out
    assert "refinement unavailable" not in out.err


def test_craft_refine_failure_falls_back_to_local(capsys):
    code = cli.main(
        [
            "craft",
            "thanks for everything",
            "--refine",
            "--endpoint",
            "http://127.0.0.1:1/v1",
            "--timeout",
            "2",
        ]
    )
    out = capsys.readouterr()
    assert code == 0
    assert "refinement unavailable" in out.err
    assert "Hi," in out.out
    assert "SHORT VARIANT" in out.out


def test_output_headers_carry_no_credentials(capsys, make_endpoint):
    endpoint = make_endpoint(reply_content="Hi\n\nBody\n\nMe\n\n--- SHORT VARIANT ---\nHi\n\nShort\n\nMe")
    code = cli.main(
        [
            "craft",
            "thanks",
            "--refine",
            "--endpoint",
            endpoint.base_url,
            "--timeout",
            "10",
        ]
    )
    lowered = capsys.readouterr().out.lower()
    for word in ("bearer", "api-key", "apikey", "authorization:"):
        assert word not in lowered
    assert endpoint.base_url.startswith("http://127.0.0.1:")


def test_tones_command(capsys):
    code = cli.main(["tones"])
    out = capsys.readouterr()
    assert code == 0
    for tone in ("warm", "firm", "apology", "boundary"):
        assert tone in out.out


def test_craft_no_bullets_fails_cleanly():
    with pytest.raises(SystemExit):
        cli.main(["craft"])
