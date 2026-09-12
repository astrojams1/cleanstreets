"""scripts/cs_secrets.py resolution order and scripts/patreon_stats.py summarizing."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import cs_secrets  # noqa: E402
import patreon_stats  # noqa: E402


def test_env_var_wins(monkeypatch):
    monkeypatch.setenv("PATREON_ACCESS_TOKEN", "from-env")
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "op-token")
    assert cs_secrets.resolve("patreon", with_source=True) == ("from-env", "env")


def test_onepassword_used_when_env_missing(monkeypatch):
    monkeypatch.delenv("PATREON_ACCESS_TOKEN", raising=False)
    monkeypatch.setenv("OP_SERVICE_ACCOUNT_TOKEN", "op-token")
    monkeypatch.setattr(cs_secrets, "_from_onepassword", lambda ref: "from-op" if ref.startswith("op://") else None)
    assert cs_secrets.resolve("patreon", with_source=True) == ("from-op", "1password")


def test_file_fallback_and_none(monkeypatch, tmp_path):
    monkeypatch.delenv("PATREON_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("OP_SERVICE_ACCOUNT_TOKEN", raising=False)
    monkeypatch.setattr(cs_secrets, "repo_root", lambda: tmp_path)
    assert cs_secrets.resolve("patreon", with_source=True) == (None, None)
    cfg = tmp_path / ".claude" / "data" / "patreon-config.json"
    cfg.parent.mkdir(parents=True)
    cfg.write_text(json.dumps({"creator_access_token": "from-file"}))
    assert cs_secrets.resolve("patreon", with_source=True) == ("from-file", "file")


def test_check_command_never_prints_the_secret(monkeypatch, capsys):
    monkeypatch.setenv("PATREON_ACCESS_TOKEN", "super-secret-value")
    assert cs_secrets.main(["check", "patreon"]) == 0
    out = capsys.readouterr().out
    assert "super-secret-value" not in out and "env" in out


def test_patreon_stats_summarize_counts_only():
    members = [
        {"patron_status": "active_patron", "currently_entitled_amount_cents": 500},
        {"patron_status": "active_patron", "currently_entitled_amount_cents": 4000},
        {"patron_status": "declined_patron", "currently_entitled_amount_cents": 500},
        {"patron_status": "former_patron"},
        {"patron_status": None, "is_follower": True},
    ]
    s = patreon_stats.summarize(members)
    assert s["active_patrons"] == 2 and s["mrr_usd"] == 45.0
    assert s["declined_patrons"] == 1 and s["former_patrons"] == 1 and s["followers"] == 1
    assert not any(k in s for k in ("email", "full_name"))


def test_patreon_stats_without_token_exits_1(monkeypatch, tmp_path, capsys):
    monkeypatch.delenv("PATREON_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("OP_SERVICE_ACCOUNT_TOKEN", raising=False)
    monkeypatch.setattr(cs_secrets, "repo_root", lambda: tmp_path)
    assert patreon_stats.main([]) == 1
    assert "WARN" in capsys.readouterr().err
