"""check_style: em dashes, fenced block languages, frontmatter."""
from __future__ import annotations

from check_style import check_file, main

GOOD_FM = "---\ntitle: T\ntopic: t\nlast_verified: 2026-11-12\nstatus: current\n---\n"


def check(repo, rel: str, text: str, keys: set[str] | None = None) -> list[str]:
    path = repo.write(rel, text)
    return check_file(path, repo.root, keys or set())


class TestEmDash:
    def test_an_em_dash_is_reported_with_its_line(self, repo):
        assert check(repo, "a.md", "fine\nthis — is not\n") == ["a.md:2: em dash"]

    def test_en_dashes_and_hyphens_are_fine(self, repo):
        assert check(repo, "a.md", "a – b and a - b\n") == []

    def test_the_owners_instructions_file_is_exempt(self, repo):
        assert check(repo, "05-ai/claude-code/CLAUDE.md", "text — here\n") == []

    def test_benchmark_fixtures_are_exempt(self, repo):
        assert check(repo, "05-ai/ollama/claude-code-bench/fixtures/x.md", "a — b\n") == []

    def test_a_similar_path_is_not_exempt(self, repo):
        assert check(repo, "05-ai/claude-code/OTHER.md", "a — b\n") == ["05-ai/claude-code/OTHER.md:1: em dash"]

    def test_every_offending_line_is_reported(self, repo):
        assert len(check(repo, "a.md", "—\nok\n—\n")) == 2


class TestFences:
    def test_a_block_without_a_language_is_reported(self, repo):
        assert check(repo, "a.md", "```\ncode\n```\n") == ["a.md:1: fenced block without a language"]

    def test_a_block_with_a_language_is_fine(self, repo):
        assert check(repo, "a.md", "```sh\ncode\n```\n") == []

    def test_tilde_fences_are_checked_too(self, repo):
        assert check(repo, "a.md", "~~~\ncode\n~~~\n") == ["a.md:1: fenced block without a language"]

    def test_the_closing_fence_needs_no_language(self, repo):
        assert check(repo, "a.md", "```sh\ncode\n```\n\n```py\nmore\n```\n") == []

    def test_a_fence_inside_a_block_does_not_close_it_when_it_is_the_other_kind(self, repo):
        # the inner ``` is content of the ~~~ block, so no second 'without a language' report
        assert check(repo, "a.md", "~~~md\n```\ninner\n```\n~~~\n") == []

    def test_only_the_opening_line_is_reported_for_an_unlabelled_block(self, repo):
        errs = check(repo, "a.md", "text\n\n```\none\n```\n")
        assert errs == ["a.md:3: fenced block without a language"]

    def test_an_indented_fence_is_checked(self, repo):
        assert check(repo, "a.md", "- item\n   ```\n   code\n   ```\n") == ["a.md:2: fenced block without a language"]


class TestFrontmatter:
    def test_a_file_without_frontmatter_has_nothing_to_check(self, repo):
        assert check(repo, "a.md", "# Title\n") == []

    def test_complete_frontmatter_passes(self, repo):
        assert check(repo, "a.md", GOOD_FM + "# T\n") == []

    def test_each_required_field_is_enforced(self, repo):
        for field in ("title", "topic", "last_verified", "status"):
            lines = [ln for ln in GOOD_FM.splitlines() if not ln.startswith(field + ":")]
            errs = check(repo, "a.md", "\n".join(lines) + "\n")
            assert f"a.md: frontmatter missing '{field}'" in errs, field

    def test_a_date_that_is_not_iso_is_reported(self, repo):
        text = GOOD_FM.replace("2026-11-12", "12/11/2026")
        assert any("is not an ISO date" in e for e in check(repo, "a.md", text))

    def test_an_impossible_date_is_reported_as_invalid_frontmatter(self, repo):
        # PyYAML builds the date itself and raises a bare ValueError, which used to escape without the context
        text = GOOD_FM.replace("2026-11-12", "2026-13-45")
        assert check(repo, "a.md", text) == ["a.md: invalid frontmatter: month must be in 1..12"]

    def test_a_quoted_impossible_date_is_reported_as_not_iso(self, repo):
        text = GOOD_FM.replace("2026-11-12", "'2026-13-45'")
        assert any("is not an ISO date" in e for e in check(repo, "a.md", text))

    def test_an_unknown_status_is_reported(self, repo):
        text = GOOD_FM.replace("current", "wip")
        assert any("status 'wip' not in" in e for e in check(repo, "a.md", text))

    def test_every_allowed_status_is_accepted(self, repo):
        for status in ("current", "reference", "archived", "draft"):
            assert check(repo, "a.md", GOOD_FM.replace("current", status)) == [], status

    def test_a_version_key_must_exist(self, repo):
        text = GOOD_FM.replace("---\n#", "---\n#").replace("status: current\n", "status: current\nversions: [linux, nope]\n")
        errs = check(repo, "a.md", text, keys={"linux"})
        assert errs == ["a.md: frontmatter version key 'nope' not in versions.yaml"]

    def test_files_whose_frontmatter_belongs_to_claude_code_are_exempt(self, repo):
        for part in ("skills", "agents", "commands"):
            assert check(repo, f"05-ai/claude-code/{part}/x/SKILL.md", "---\nname: x\n---\nbody\n") == [], part

    def test_broken_frontmatter_is_one_error_and_stops_checking(self, repo):
        errs = check(repo, "a.md", "---\ntitle: [oops\n---\n```\ncode\n```\n")
        assert any("invalid frontmatter" in e for e in errs)

    def test_a_non_mapping_is_reported(self, repo):
        assert any("not a mapping" in e for e in check(repo, "a.md", "---\n- a\n---\nbody\n"))


class TestMain:
    def test_a_clean_repo_passes(self, repo, caplog):
        repo.write("versions.yaml", "entries: {}\n")
        repo.write("a.md", GOOD_FM + "# T\n")
        assert main([]) == 0
        assert "style-checked 1 markdown files, 0 problems" in caplog.text

    def test_a_problem_fails_and_is_reported(self, repo, caplog):
        repo.write("versions.yaml", "entries: {}\n")
        repo.write("a.md", "bad — dash\n")
        assert main([]) == 1
        assert "STYLE a.md:1: em dash" in caplog.text

    def test_generated_inventory_files_are_skipped(self, repo, caplog):
        repo.write("versions.yaml", "entries: {}\n")
        repo.write("docs/modernization/inventory-x.md", "bad — dash\n")
        assert main([]) == 0
        assert "style-checked 0 markdown files" in caplog.text

    def test_the_licence_is_skipped(self, repo):
        repo.write("versions.yaml", "entries: {}\n")
        repo.write("LICENSE.md", "a — b\n")
        assert main([]) == 0

    def test_without_versions_yaml_keys_are_simply_unknown(self, repo):
        repo.write("a.md", GOOD_FM.replace("status: current\n", "status: current\nversions: [x]\n"))
        assert main([]) == 1

    def test_version_keys_come_from_versions_yaml(self, repo):
        repo.write("versions.yaml", "entries:\n  x: {name: X, target: '1', source: arch}\n")
        repo.write("a.md", GOOD_FM.replace("status: current\n", "status: current\nversions: [x]\n"))
        assert main([]) == 0
