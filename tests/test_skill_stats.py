"""scripts/skill_stats.py: ledger-derived stats and skill lint."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ledger  # noqa: E402
import skill_stats  # noqa: E402


def make_repo(tmp_path: Path) -> Path:
    skills = tmp_path / ".claude" / "skills"
    for name in ("alpha-processor", "beta-growth"):
        (skills / name / "references").mkdir(parents=True)
        (skills / name / "SKILL.md").write_text(
            f'---\nname: {name}\ndescription: "x"\nmetadata:\n  version: "1.0"\n---\n'
            "# x\n\nRun `python3 scripts/ledger.py add` at the end.\n"
        )
        (skills / name / "LEDGER.md").write_text(ledger.ledger_header(name))
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "ledger.py").write_text("")
    return tmp_path


def test_stats_counts_outcomes_trends_and_stuck_next(tmp_path, monkeypatch):
    root = make_repo(tmp_path)
    monkeypatch.setattr(ledger, "repo_root", lambda: root)
    for i, (outcome, actions, roll) in enumerate([("success", 3, 100), ("noop", 0, 101), ("success", 2, 104)], 1):
        assert ledger.main([
            "add", "--skill", "beta-growth", "--outcome", outcome, "--actions", str(actions),
            "--summary", f"run {i}", "--metric", f"roll_total={roll}", "--next", "ask James for token",
            "--started", f"2030-01-0{i}T09:00-08:00",
        ]) == 0
    out = [s for s in (skill_stats.skill_stats(d, None) for d in skill_stats.skill_dirs(root)) if s["skill"] == "beta-growth"][0]
    assert out["runs_total"] == 3
    assert out["outcomes"] == {"success": 2, "noop": 1}
    assert out["zero_action_runs"] == 1
    assert out["metric_trend"]["roll_total"]["first"] == 100
    assert out["metric_trend"]["roll_total"]["last"] == 104
    assert out["stuck_next"] == ["ask James for token"]


def test_lint_flags_missing_paths_and_unknown_skills(tmp_path, capsys):
    root = make_repo(tmp_path)
    md = root / ".claude" / "skills" / "alpha-processor" / "SKILL.md"
    md.write_text(md.read_text() + "\nSee `scripts/does_not_exist.sh` and hand off to gamma-growth.\n")
    rc = skill_stats.main(["--root", str(root), "lint", "--json"])
    findings = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert any("does_not_exist.sh" in f for f in findings)
    assert any("gamma-growth" in f for f in findings)


def test_lint_clean_repo_passes(tmp_path, capsys):
    root = make_repo(tmp_path)
    rc = skill_stats.main(["--root", str(root), "lint"])
    assert rc == 0
    assert "no lint findings" in capsys.readouterr().out


def test_real_repo_lint_is_clean():
    rc = skill_stats.main(["--root", str(ROOT), "lint", "--json"])
    assert rc == 0, "skill lint findings in this repository; run scripts/skill_stats.py lint"
