"""check_versions and render_versions: version parsing, drift detection, constraints, marker rewriting."""
from __future__ import annotations

import check_versions
import pytest
from check_versions import _compare, check_offline, main, vtuple
from render_versions import main as render_main
from render_versions import render, resolve


class TestVtuple:
    @pytest.mark.parametrize(("text", "expected"), [
        ("1:0.57.0-1", (0, 57, 0)),
        ("6.12.1-arch1-1", (6, 12, 1)),
        ("2.0.0rc1", (2, 0, 0)),
        ("26.13.1", (26, 13, 1)),
        ("1.2.3+git20240101", (1, 2, 3)),
        ("1.0~rc1", (1, 0)),
        ("v1.2", (1, 2)),
        ("2:1.0", (1, 0)),
        ("3", (3,)),
        ("abc", ()),
        ("", ()),
    ])
    def test_the_numeric_prefix(self, text, expected):
        assert vtuple(text) == expected

    def test_width_truncates(self):
        assert vtuple("26.13.1", 2) == (26, 13)

    def test_width_longer_than_the_version_is_harmless(self):
        assert vtuple("1.2", 5) == (1, 2)

    def test_tuples_compare_numerically_not_as_text(self):
        assert vtuple("1.10") > vtuple("1.9")

    def test_a_number_is_accepted(self):
        assert vtuple(3.13) == (3, 13)  # type: ignore[arg-type]


def data(entries=None, constraints=None):
    base = {"a": {"name": "A", "target": "1.2", "source": "arch"}}
    out = {"entries": entries if entries is not None else base}
    if constraints is not None:
        out["constraints"] = constraints
    return out


class TestEntries:
    def test_a_valid_entry_has_no_problems(self, repo):
        assert check_offline(repo.root, data()) == []

    @pytest.mark.parametrize("field", ["name", "target", "source"])
    def test_each_required_field_is_enforced(self, repo, field):
        entry = {"name": "A", "target": "1.2", "source": "arch"}
        del entry[field]
        assert f"versions.yaml: a: missing '{field}'" in check_offline(repo.root, data({"a": entry}))

    def test_an_unknown_source_is_reported(self, repo):
        errs = check_offline(repo.root, data({"a": {"name": "A", "target": "1", "source": "wishful"}}))
        assert any("source 'wishful' not in" in e for e in errs)

    @pytest.mark.parametrize("source", ["arch", "cachyos", "aur", "upstream", "registry", "snapshot"])
    def test_every_documented_source_is_accepted(self, repo, source):
        assert check_offline(repo.root, data({"a": {"name": "A", "target": "1", "source": source}})) == []

    def test_a_target_without_a_number_is_reported(self, repo):
        errs = check_offline(repo.root, data({"a": {"name": "A", "target": "latest", "source": "arch"}}))
        assert any("target 'latest' has no numeric version" in e for e in errs)

    def test_expect_without_verify_is_reported(self, repo):
        errs = check_offline(repo.root, data({"a": {"name": "A", "target": "1", "source": "arch", "expect": "x"}}))
        assert "versions.yaml: a: 'expect' without 'verify'" in errs

    def test_expect_with_verify_is_fine(self, repo):
        entry = {"name": "A", "target": "1", "source": "arch", "expect": "x", "verify": "cmd"}
        assert check_offline(repo.root, data({"a": entry})) == []


class TestMarkers:
    def test_a_matching_marker_passes(self, repo):
        repo.write("a.md", "Kernel <!-- v:a -->1.2<!-- /v -->\n")
        assert check_offline(repo.root, data()) == []

    def test_a_stale_marker_names_both_values(self, repo):
        repo.write("a.md", "<!-- v:a -->1.1<!-- /v -->\n")
        assert check_offline(repo.root, data()) == ["a.md: marker 'a' reads '1.1', versions.yaml says '1.2'"]

    def test_an_unknown_key_is_reported(self, repo):
        repo.write("a.md", "<!-- v:zzz -->1<!-- /v -->\n")
        assert check_offline(repo.root, data()) == ["a.md: marker 'zzz:target' has no entry in versions.yaml"]

    def test_an_unknown_field_is_reported(self, repo):
        repo.write("a.md", "<!-- v:a:upstream -->1<!-- /v -->\n")
        assert check_offline(repo.root, data()) == ["a.md: marker 'a:upstream' has no entry in versions.yaml"]

    def test_a_field_marker_is_compared_with_that_field(self, repo):
        d = data({"a": {"name": "A", "target": "1.2", "source": "arch", "upstream": "9.9"}})
        repo.write("ok.md", "<!-- v:a:upstream -->9.9<!-- /v -->\n")
        repo.write("bad.md", "<!-- v:a:upstream -->1.2<!-- /v -->\n")
        assert check_offline(repo.root, d) == ["bad.md: marker 'a' reads '1.2', versions.yaml says '9.9'"]

    def test_a_marker_inside_a_code_fence_is_reported(self, repo):
        repo.write("a.md", "```md\n<!-- v:a -->1.2<!-- /v -->\n```\n")
        assert any("version marker inside a code fence" in e for e in check_offline(repo.root, data()))

    def test_a_marker_after_the_fence_closes_is_fine(self, repo):
        repo.write("a.md", "```sh\ncode\n```\n<!-- v:a -->1.2<!-- /v -->\n")
        assert check_offline(repo.root, data()) == []

    def test_tilde_fences_count_too(self, repo):
        repo.write("a.md", "~~~md\n<!-- v:a -->1.2<!-- /v -->\n~~~\n")
        assert any("inside a code fence" in e for e in check_offline(repo.root, data()))

    def test_the_line_number_is_reported(self, repo):
        repo.write("a.md", "x\n```md\n<!-- v:a -->1.2<!-- /v -->\n```\n")
        assert any(e.startswith("a.md:3:") for e in check_offline(repo.root, data()))

    def test_modernization_records_are_not_checked(self, repo):
        repo.write("docs/modernization/REPORT.md", "<!-- v:a -->WRONG<!-- /v -->\n")
        assert check_offline(repo.root, data()) == []

    def test_the_handoff_in_that_folder_is_checked(self, repo):
        repo.write("docs/modernization/HANDOFF.md", "<!-- v:a -->WRONG<!-- /v -->\n")
        assert len(check_offline(repo.root, data())) == 1


def rule(op, value, *, key="a", field=None, width=None, rid="r1"):
    req = {"key": key, "op": op, "value": value}
    if field:
        req["field"] = field
    if width:
        req["width"] = width
    return {"id": rid, "text": "why", "requires": [req]}


class TestConstraints:
    @pytest.mark.parametrize(
        ("op", "value"),
        [("==", "1.2"), (">=", "1.2"), (">=", "1.1"), ("<=", "1.2"), ("<=", "2"), (">", "1.1"), ("<", "1.3")],
    )
    def test_holding_rules_pass(self, repo, op, value):
        assert check_offline(repo.root, data(constraints=[rule(op, value)])) == []

    @pytest.mark.parametrize(("op", "value"), [("==", "1.3"), (">=", "1.3"), ("<=", "1.1"), (">", "1.2"), ("<", "1.2")])
    def test_violated_rules_are_reported(self, repo, op, value):
        errs = check_offline(repo.root, data(constraints=[rule(op, value)]))
        assert errs == [f"constraint r1 violated: a (1, 2) {op} {tuple(int(x) for x in value.split('.'))} (why)"]

    def test_numeric_not_textual_comparison(self, repo):
        d = data({"a": {"name": "A", "target": "1.10", "source": "arch"}}, [rule(">", "1.9")])
        assert check_offline(repo.root, d) == []

    def test_width_compares_only_the_leading_parts(self, repo):
        d = data({"a": {"name": "A", "target": "6.12.7", "source": "arch"}}, [rule("==", "6.12.0", width=2)])
        assert check_offline(repo.root, d) == []
        d2 = data({"a": {"name": "A", "target": "6.13.0", "source": "arch"}}, [rule("==", "6.12.0", width=2)])
        assert len(check_offline(repo.root, d2)) == 1

    def test_a_rule_can_name_another_field(self, repo):
        d = data({"a": {"name": "A", "target": "1", "source": "arch", "upstream": "5"}}, [rule(">=", "5", field="upstream")])
        assert check_offline(repo.root, d) == []

    def test_an_unknown_key_is_reported(self, repo):
        assert check_offline(repo.root, data(constraints=[rule(">=", "1", key="zzz")])) == ["constraint r1: unknown key 'zzz'"]

    def test_an_unknown_operator_is_a_violation_not_a_pass(self, repo):
        errs = check_offline(repo.root, data(constraints=[rule("~=", "1.2")]))
        assert len(errs) == 1 and "violated" in errs[0]

    def test_a_missing_field_is_reported_not_a_crash(self, repo):
        errs = check_offline(repo.root, data(constraints=[rule(">=", "1", field="upstream")]))
        assert errs == ["constraint r1: 'a' has no field 'upstream'"]

    def test_every_requirement_of_a_rule_is_checked(self, repo):
        r = {"id": "multi", "text": "t", "requires": [
            {"key": "a", "op": ">=", "value": "1"}, {"key": "a", "op": ">=", "value": "9"}]}
        assert len(check_offline(repo.root, data(constraints=[r]))) == 1

    def test_no_constraints_is_fine(self, repo):
        assert check_offline(repo.root, data()) == []


class TestCompare:
    def run(self, target, found, where="arch/extra", hold=""):
        notes: list[str] = []
        _compare(notes, "k", where, target, found, hold)
        return notes

    def test_a_newer_upstream_is_behind(self):
        assert self.run("1.2", "1.3") == ["k: target 1.2 is behind arch/extra 1.3"]

    def test_a_deliberate_hold_is_labelled_not_behind(self):
        assert self.run("1.2", "1.3", hold="why") == ["k: target 1.2 is held behind arch/extra 1.3 [hold: why]"]

    def test_a_target_ahead_of_the_distro_is_a_lag_note(self):
        assert self.run("1.3", "1.2") == ["k: target 1.3 is ahead of arch/extra 1.2 (distro lag)"]

    def test_equal_versions_say_nothing(self):
        assert self.run("1.2", "1.2") == []

    def test_a_testing_repository_is_ignored(self):
        assert self.run("1.2", "9.9", where="arch/extra-testing") == []

    def test_only_the_numeric_part_is_compared(self):
        assert self.run("1.2", "1.2-3") == []


class TestMain:
    def test_a_clean_repo_passes(self, repo, caplog):
        repo.write("versions.yaml", "entries:\n  a: {name: A, target: '1.2', source: arch}\n")
        assert main([]) == 0
        assert "1 entries, 0 offline problems" in caplog.text

    def test_drift_fails_and_is_labelled(self, repo, caplog):
        repo.write("versions.yaml", "entries:\n  a: {name: A, target: '1.2', source: arch}\n")
        repo.write("a.md", "<!-- v:a -->0.1<!-- /v -->\n")
        assert main([]) == 1
        assert "DRIFT a.md: marker 'a' reads '0.1'" in caplog.text

    def _live(self, repo, monkeypatch, notes):
        repo.write("versions.yaml", "entries:\n  a: {name: A, target: '1.2', source: arch}\n")
        monkeypatch.setattr(check_versions, "check_live", lambda d: notes)

    def test_live_notes_are_informational_by_default(self, repo, monkeypatch, caplog):
        self._live(repo, monkeypatch, ["a: target 1.2 is behind arch 1.3"])
        assert main(["--live"]) == 0
        assert "LIVE a: target 1.2 is behind arch 1.3" in caplog.text
        assert "1 live notes, 1 behind or failed" in caplog.text

    def test_strict_fails_on_a_behind_note(self, repo, monkeypatch):
        self._live(repo, monkeypatch, ["a: target 1.2 is behind arch 1.3"])
        assert main(["--live", "--strict"]) == 1

    def test_strict_fails_on_a_failed_lookup(self, repo, monkeypatch):
        self._live(repo, monkeypatch, ["a: lookup failed (boom)"])
        assert main(["--live", "--strict"]) == 1

    def test_strict_ignores_a_deliberate_hold_and_distro_lag(self, repo, monkeypatch):
        notes = ["a: target 1.2 is held behind arch 1.3 [hold: x]", "a: target 1.2 is ahead of aur 1.1 (distro lag)"]
        self._live(repo, monkeypatch, notes)
        assert main(["--live", "--strict"]) == 0

    def test_strict_without_live_does_nothing_extra(self, repo):
        repo.write("versions.yaml", "entries:\n  a: {name: A, target: '1.2', source: arch}\n")
        assert main(["--strict"]) == 0

    def test_live_is_not_called_without_the_flag(self, repo, monkeypatch):
        repo.write("versions.yaml", "entries:\n  a: {name: A, target: '1.2', source: arch}\n")
        monkeypatch.setattr(check_versions, "check_live", lambda d: pytest.fail("network path used"))
        assert main([]) == 0


ENTRIES = {"a": {"name": "A", "target": "1.2", "source": "arch", "upstream": "9.9"}}


class TestRender:
    def test_resolve_defaults_to_the_target(self):
        assert resolve(ENTRIES, "a", None) == "1.2"

    def test_resolve_a_field(self):
        assert resolve(ENTRIES, "a", "upstream") == "9.9"

    def test_resolve_always_returns_text(self):
        assert resolve({"a": {"target": 3.13}}, "a", None) == "3.13"

    def test_resolve_an_unknown_key_or_field_raises(self):
        with pytest.raises(KeyError):
            resolve(ENTRIES, "zzz", None)
        with pytest.raises(KeyError):
            resolve(ENTRIES, "a", "nope")

    def test_a_current_file_is_untouched(self, tmp_path):
        f = tmp_path / "a.md"
        f.write_text("x <!-- v:a -->1.2<!-- /v --> y\n")
        before = f.stat().st_mtime_ns
        assert render(f, ENTRIES, write=True) == []
        assert f.stat().st_mtime_ns == before

    def test_drift_is_reported_without_writing_in_check_mode(self, tmp_path):
        f = tmp_path / "a.md"
        f.write_text("<!-- v:a -->0.1<!-- /v -->\n")
        problems = render(f, ENTRIES, write=False)
        assert len(problems) == 1 and "reads '0.1', versions.yaml says '1.2'" in problems[0]
        assert f.read_text() == "<!-- v:a -->0.1<!-- /v -->\n"

    def test_drift_is_fixed_in_write_mode(self, tmp_path):
        f = tmp_path / "a.md"
        f.write_text("keep <!-- v:a -->0.1<!-- /v --> and <!-- v:a:upstream -->0<!-- /v --> text\n")
        render(f, ENTRIES, write=True)
        assert f.read_text() == "keep <!-- v:a -->1.2<!-- /v --> and <!-- v:a:upstream -->9.9<!-- /v --> text\n"

    def test_an_unknown_key_is_reported_and_left_alone(self, tmp_path):
        f = tmp_path / "a.md"
        f.write_text("<!-- v:zzz -->old<!-- /v -->\n")
        problems = render(f, ENTRIES, write=True)
        assert len(problems) == 1 and "unknown version key or field 'zzz'" in problems[0]
        assert f.read_text() == "<!-- v:zzz -->old<!-- /v -->\n"

    def test_an_unknown_field_is_named_with_its_field(self, tmp_path):
        f = tmp_path / "a.md"
        f.write_text("<!-- v:a:nope -->x<!-- /v -->\n")
        assert "'a:nope'" in render(f, ENTRIES, write=False)[0]

    def test_text_between_markers_is_preserved_exactly(self, tmp_path):
        f = tmp_path / "a.md"
        body = "# T\n\n- item <!-- v:a -->0<!-- /v -->\n\ntrailing  spaces  \n"
        f.write_text(body)
        render(f, ENTRIES, write=True)
        assert f.read_text() == body.replace("0<!--", "1.2<!--")


class TestRenderMain:
    def setup_repo(self, repo, marker="0.1"):
        repo.write("versions.yaml", "entries:\n  a: {name: A, target: '1.2', source: arch}\n")
        return repo.write("a.md", f"<!-- v:a -->{marker}<!-- /v -->\n")

    def test_check_mode_fails_on_drift_and_changes_nothing(self, repo, caplog):
        f = self.setup_repo(repo)
        assert render_main(["--check"]) == 1
        assert "DRIFT a.md" in caplog.text
        assert "0.1" in f.read_text()

    def test_check_mode_passes_when_current(self, repo):
        self.setup_repo(repo, "1.2")
        assert render_main(["--check"]) == 0

    def test_write_mode_fixes_and_succeeds(self, repo, caplog):
        f = self.setup_repo(repo)
        assert render_main([]) == 0
        assert "FIXED a.md" in caplog.text
        assert f.read_text() == "<!-- v:a -->1.2<!-- /v -->\n"

    def test_modernization_records_are_left_alone(self, repo):
        self.setup_repo(repo, "1.2")
        rec = repo.write("docs/modernization/REPORT.md", "<!-- v:a -->OLD<!-- /v -->\n")
        render_main([])
        assert rec.read_text() == "<!-- v:a -->OLD<!-- /v -->\n"

    def test_the_handoff_is_rewritten(self, repo):
        self.setup_repo(repo, "1.2")
        rec = repo.write("docs/modernization/HANDOFF.md", "<!-- v:a -->OLD<!-- /v -->\n")
        render_main([])
        assert rec.read_text() == "<!-- v:a -->1.2<!-- /v -->\n"
