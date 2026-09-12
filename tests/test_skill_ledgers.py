"""Every repository skill must have a SKILL.md with valid frontmatter and a
well-formed LEDGER.md. See .claude/skills/README.md for the convention."""
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".claude" / "skills"
LEDGER_PY = ROOT / "scripts" / "ledger.py"

sys.path.insert(0, str(ROOT / "scripts"))
import ledger  # noqa: E402

SKILL_DIRS = sorted(p for p in SKILLS.iterdir() if p.is_dir() and not p.name.startswith((".", "_")))


def test_at_least_one_skill_exists():
    assert SKILL_DIRS, "no skills found under .claude/skills"


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda p: p.name)
def test_skill_has_required_files(skill_dir):
    assert (skill_dir / "SKILL.md").exists(), f"{skill_dir.name}: missing SKILL.md"
    assert (skill_dir / "LEDGER.md").exists(), (
        f"{skill_dir.name}: missing LEDGER.md; run scripts/ledger.py init --skill {skill_dir.name}"
    )


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda p: p.name)
def test_skill_frontmatter(skill_dir):
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, f"{skill_dir.name}: SKILL.md must start with YAML frontmatter"
    fm = m.group(1)
    name = re.search(r"^name:\s*(\S+)\s*$", fm, re.M)
    assert name and name.group(1) == skill_dir.name, "frontmatter name must equal the directory name"
    assert re.search(r"^description:", fm, re.M), "frontmatter needs a description"
    assert re.search(r'^\s+version:\s*"?\d+\.\d+"?\s*$', fm, re.M), "frontmatter needs metadata.version"


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda p: p.name)
def test_skill_mentions_ledger(skill_dir):
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert "scripts/ledger.py add" in text, f"{skill_dir.name}: SKILL.md must end the run with a ledger entry"


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda p: p.name)
def test_ledger_parses(skill_dir):
    text = (skill_dir / "LEDGER.md").read_text(encoding="utf-8")
    assert text.startswith(f"# Ledger: {skill_dir.name}"), "ledger title must name the skill"
    ledger.parse(text)  # raises ValueError on malformed content


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda p: p.name)
def test_ledger_has_no_email_addresses(skill_dir):
    text = (skill_dir / "LEDGER.md").read_text(encoding="utf-8")
    hits = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
    allowed = {"james@cleanstreets.io"}
    assert not [h for h in hits if h not in allowed], f"{skill_dir.name}: ledger contains email addresses: {hits}"


def test_ledger_check_command_passes():
    proc = subprocess.run([sys.executable, str(LEDGER_PY), "check"], capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 0, proc.stderr


def test_ledger_roundtrip(tmp_path, monkeypatch):
    skills = tmp_path / ".claude" / "skills"
    (skills / "demo").mkdir(parents=True)
    (skills / "demo" / "SKILL.md").write_text("---\nname: demo\n---\n")
    monkeypatch.setattr(ledger, "repo_root", lambda: tmp_path)
    assert ledger.main(["init", "--skill", "demo"]) == 0
    assert ledger.main([
        "add", "--skill", "demo", "--outcome", "success", "--actions", "2",
        "--summary", "did things", "--metric", "a=1", "--detail", "msg:abc | replied",
        "--next", "follow up",
    ]) == 0
    assert ledger.main(["add", "--skill", "demo", "--outcome", "noop", "--actions", "0", "--summary", "quiet"]) == 0
    _, entries = ledger.parse((skills / "demo" / "LEDGER.md").read_text())
    assert [e["run"] for e in entries] == [1, 2]
    assert entries[0]["metrics"] == {"a": "1"}
    assert entries[0]["details"] == ["msg:abc | replied"]
    assert ledger.main(["seen", "--skill", "demo", "--key", "msg:abc"]) == 0
    assert ledger.main(["seen", "--skill", "demo", "--key", "msg:abcd"]) == 1
    assert ledger.main(["check"]) == 0
