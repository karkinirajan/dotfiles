"""Shared helpers: frontmatter, code stripping, version markers, file listing."""
from __future__ import annotations

import pytest
from _lib import MARKER_RE, load_versions, markdown_files, repo_root, split_frontmatter, strip_code, tracked_files


class TestSplitFrontmatter:
    def test_no_frontmatter_returns_the_text_unchanged(self):
        assert split_frontmatter("# Title\n\nbody\n") == ({}, "# Title\n\nbody\n")

    def test_frontmatter_is_parsed_and_removed_from_the_body(self):
        meta, body = split_frontmatter("---\ntitle: A\ntopic: b\n---\n# Heading\n")
        assert meta == {"title": "A", "topic": "b"}
        assert body == "# Heading\n"

    def test_empty_frontmatter_is_an_empty_mapping(self):
        assert split_frontmatter("---\n\n---\nbody\n") == ({}, "body\n")

    def test_it_must_start_the_file(self):
        meta, body = split_frontmatter("\n---\ntitle: A\n---\nbody\n")
        assert meta == {} and body.startswith("\n---")

    def test_invalid_yaml_is_an_error(self):
        with pytest.raises(ValueError, match="invalid frontmatter"):
            split_frontmatter("---\ntitle: [unclosed\n---\nbody\n")

    def test_a_list_is_not_a_mapping(self):
        with pytest.raises(ValueError, match="not a mapping"):
            split_frontmatter("---\n- a\n- b\n---\nbody\n")


class TestStripCode:
    def test_a_fenced_block_is_blanked_line_for_line(self):
        text = "before\n```sh\nrm -rf /\n```\nafter\n"
        assert strip_code(text) == "before\n\n\n\nafter\n"

    def test_the_line_count_is_preserved_so_line_numbers_stay_valid(self):
        text = "a\n~~~\nb\nc\n~~~\nd\n"
        assert strip_code(text).count("\n") == text.count("\n")

    def test_a_tilde_fence_is_not_closed_by_backticks(self):
        # the text between is still code, so the link in it must stay hidden
        text = "~~~\n```\n[x](gone)\n~~~\n[y](kept)\n"
        assert "gone" not in strip_code(text) and "kept" in strip_code(text)

    def test_a_backtick_fence_is_not_closed_by_tildes(self):
        text = "```\n~~~\n[x](gone)\n```\n[y](kept)\n"
        assert "gone" not in strip_code(text) and "kept" in strip_code(text)

    def test_an_indented_fence_still_counts(self):
        assert "gone" not in strip_code("   ```\n   [x](gone)\n   ```\n")

    def test_an_unclosed_fence_hides_the_rest_of_the_file(self):
        assert "gone" not in strip_code("```\n[x](gone)\nmore\n")

    def test_inline_code_is_blanked_but_keeps_its_width(self):
        out = strip_code("see `[x](gone)` and [y](kept)\n")
        assert "gone" not in out and "kept" in out
        assert len(out) == len("see `[x](gone)` and [y](kept)\n")

    def test_plain_text_is_untouched(self):
        assert strip_code("just text\n") == "just text\n"


class TestMarkerRegex:
    def test_a_plain_marker(self):
        m = MARKER_RE.search("Kernel <!-- v:linux -->6.12<!-- /v --> here")
        assert (m.group(1), m.group(2), m.group(3)) == ("linux", None, "6.12")

    def test_a_marker_with_a_field(self):
        m = MARKER_RE.search("<!-- v:linux:arch -->6.11<!-- /v -->")
        assert (m.group(1), m.group(2), m.group(3)) == ("linux", "arch", "6.11")

    def test_spacing_inside_the_comment_is_tolerated(self):
        assert MARKER_RE.search("<!--v:a-->1<!--/v-->").group(3) == "1"

    def test_it_does_not_run_across_two_markers(self):
        found = MARKER_RE.findall("<!-- v:a -->1<!-- /v --> and <!-- v:b -->2<!-- /v -->")
        assert [f[2] for f in found] == ["1", "2"]

    def test_keys_may_contain_dots_dashes_and_underscores(self):
        assert MARKER_RE.search("<!-- v:python-3.13_x -->3.13<!-- /v -->").group(1) == "python-3.13_x"


class TestLoadVersions:
    def test_a_valid_file(self, repo):
        repo.write("versions.yaml", "entries:\n  a: {name: A, target: '1', source: arch}\n")
        assert "a" in load_versions(repo.root)["entries"]

    def test_a_missing_file_is_a_clear_exit(self, repo):
        with pytest.raises(SystemExit, match="cannot read"):
            load_versions(repo.root)

    def test_invalid_yaml_is_a_clear_exit(self, repo):
        repo.write("versions.yaml", "entries: [unclosed\n")
        with pytest.raises(SystemExit, match="cannot read"):
            load_versions(repo.root)

    def test_a_file_without_entries_is_rejected(self, repo):
        repo.write("versions.yaml", "other: 1\n")
        with pytest.raises(SystemExit, match="'entries' key"):
            load_versions(repo.root)

    def test_a_list_at_the_top_is_rejected(self, repo):
        repo.write("versions.yaml", "- a\n- b\n")
        with pytest.raises(SystemExit, match="'entries' key"):
            load_versions(repo.root)


class TestFileListing:
    def test_untracked_files_are_included_and_ignored_ones_are_not(self, repo):
        repo.write(".gitignore", "ignored.md\n")
        repo.write("a.md")
        repo.write("ignored.md")
        names = {p.name for p in tracked_files(repo.root)}
        assert "a.md" in names and "ignored.md" not in names

    def test_a_pattern_filters(self, repo):
        repo.write("a.md")
        repo.write("b.txt")
        assert [p.name for p in tracked_files(repo.root, "*.md")] == ["a.md"]

    def test_a_deleted_tracked_file_is_not_listed(self, repo):
        gone = repo.write("gone.md")
        repo.commit()
        gone.unlink()
        assert "gone.md" not in {p.name for p in tracked_files(repo.root)}

    def test_markdown_files_are_only_markdown(self, repo):
        repo.write("docs/a.md")
        repo.write("docs/b.py")
        assert [p.name for p in markdown_files(repo.root)] == ["a.md"]

    def test_paths_are_absolute(self, repo):
        repo.write("a.md")
        assert all(p.is_absolute() for p in tracked_files(repo.root))

    def test_repo_root_is_the_git_toplevel_from_a_subdirectory(self, repo, monkeypatch):
        sub = repo.root / "deep" / "er"
        sub.mkdir(parents=True)
        monkeypatch.chdir(sub)
        assert repo_root().resolve() == repo.root.resolve()
