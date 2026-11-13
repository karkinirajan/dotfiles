"""gen_index, check_migration and check_configs."""
from __future__ import annotations

from pathlib import Path

import pytest
from check_configs import (
    check_json,
    check_manifest,
    check_package_list,
    check_toml,
    check_unit,
    check_yaml,
    strip_jsonc,
)
from check_configs import main as configs_main
from check_migration import base_paths, removed_entries
from check_migration import main as migration_main
from gen_index import HEADER, build_index, build_setup_readme, collect, row
from gen_index import main as index_main


def fm(title="T", topic="t", **extra):
    lines = [f"title: {title}", f"topic: {topic}", "last_verified: 2026-11-12", "status: current"]
    lines += [f"{k}: {v}" for k, v in extra.items()]
    return "---\n" + "\n".join(lines) + "\n---\n# Body\n"


class TestCollect:
    def test_only_files_with_a_title_and_topic_are_chapters(self, repo):
        repo.write("a.md", fm())
        repo.write("no-topic.md", "---\ntitle: X\n---\nbody\n")
        repo.write("plain.md", "# no frontmatter\n")
        assert [p.as_posix() for p, _ in collect(repo.root)] == ["a.md"]

    def test_docs_and_reference_folders_are_not_chapters(self, repo):
        repo.write("docs/x.md", fm())
        repo.write("05-ai/skill/references/y.md", fm())
        repo.write("05-ai/skill/reference/z.md", fm())
        repo.write("keep.md", fm())
        assert [p.as_posix() for p, _ in collect(repo.root)] == ["keep.md"]

    def test_a_file_with_broken_frontmatter_is_skipped_not_fatal(self, repo):
        repo.write("bad.md", "---\ntitle: [oops\n---\nbody\n")
        repo.write("good.md", fm())
        assert [p.as_posix() for p, _ in collect(repo.root)] == ["good.md"]

    def test_chapters_are_sorted_by_path(self, repo):
        for name in ("b.md", "a.md", "03-x/c.md"):
            repo.write(name, fm())
        assert [p.as_posix() for p, _ in collect(repo.root)] == ["03-x/c.md", "a.md", "b.md"]

    def test_chapters_are_in_path_order_whether_or_not_they_are_committed(self, repo):
        # whatever order git lists them in, the chapters come out in path order
        repo.write("b.md", fm())
        repo.commit()
        repo.write("a.md", fm())
        assert [p.as_posix() for p, _ in collect(repo.root)] == ["a.md", "b.md"]


class TestBuild:
    def test_row_links_relative_to_the_root(self):
        meta = {"title": "My Title", "last_verified": "2026-11-12", "status": "current"}
        assert row(Path("a/b.md"), meta, Path()) == "| [My Title](a/b.md) | `a/b.md` | 2026-11-12 | current |"

    def test_row_goes_up_from_a_nested_page(self):
        assert "(../../a/b.md)" in row(Path("a/b.md"), {"title": "T"}, Path("x/y"))

    def test_a_missing_date_or_status_is_blank_not_none(self):
        assert row(Path("a.md"), {"title": "T"}, Path()).endswith("|  |  |")

    def test_index_starts_with_the_generated_marker_and_lists_every_chapter(self, repo):
        text = build_index(repo.root, [(Path("a.md"), {"title": "A"}), (Path("b.md"), {"title": "B"})])
        assert text.startswith(HEADER) and text.endswith("\n")
        assert text.count("\n| [") == 2

    def test_setup_readme_is_none_without_setup_chapters(self, repo):
        assert build_setup_readme(repo.root, [(Path("a.md"), {"title": "A"})]) is None

    def test_setup_readme_lists_only_the_setup_folder_without_its_own_readme(self, repo):
        base = Path("01-system/cachyos/setup")
        items = [(base / "10-a.md", {"title": "A", "chapter": 10}), (base / "README.md", {"title": "R"}),
                 (Path("other/x.md"), {"title": "X"})]
        text = build_setup_readme(repo.root, items)
        assert "| 10 | [A](10-a.md) |" in text and "README.md" not in text and "[X]" not in text


class TestIndexMain:
    def test_write_then_check_is_clean(self, repo):
        repo.write("a.md", fm("Alpha"))
        assert index_main([]) == 0
        assert "Alpha" in (repo.root / "INDEX.md").read_text()
        assert index_main(["--check"]) == 0

    def test_check_fails_when_the_index_is_missing(self, repo, caplog):
        repo.write("a.md", fm())
        assert index_main(["--check"]) == 1
        assert "STALE INDEX.md" in caplog.text

    def test_check_fails_after_a_chapter_changes(self, repo):
        page = repo.write("a.md", fm("Alpha"))
        index_main([])
        page.write_text(fm("Renamed"))
        assert index_main(["--check"]) == 1

    def test_check_fails_after_a_hand_edit(self, repo):
        repo.write("a.md", fm())
        index_main([])
        index = repo.root / "INDEX.md"
        index.write_text(index.read_text() + "hand edit\n")
        assert index_main(["--check"]) == 1

    def test_check_never_writes(self, repo):
        repo.write("a.md", fm())
        index_main(["--check"])
        assert not (repo.root / "INDEX.md").exists()

    def test_writing_twice_changes_nothing_the_second_time(self, repo, caplog):
        repo.write("a.md", fm())
        index_main([])
        caplog.clear()
        assert index_main([]) == 0
        assert "wrote" not in caplog.text

    def test_the_setup_readme_is_written_when_there_are_setup_chapters(self, repo):
        repo.write("01-system/cachyos/setup/10-a.md", fm("A", chapter=10))
        index_main([])
        assert (repo.root / "01-system/cachyos/setup/README.md").read_text().startswith(HEADER)
        assert index_main(["--check"]) == 0

    def test_no_setup_readme_without_setup_chapters(self, repo):
        repo.write("a.md", fm())
        index_main([])
        assert not (repo.root / "01-system").exists()


@pytest.fixture
def migrated(repo):
    """A repo whose `main` branch holds a tree, then loses some of it on a working branch."""
    for rel in ("keep.txt", "root-old.txt", "dir/b.txt", "gone/c.txt", "pkg/__pycache__/m.cpython-313.pyc"):
        repo.write(rel, "x\n")
    repo.commit("base")
    repo.git("checkout", "-q", "-b", "work")
    for rel in ("root-old.txt", "gone/c.txt", "pkg/__pycache__/m.cpython-313.pyc"):
        (repo.root / rel).unlink()
    repo.write("docs/modernization/REMOVALS.md", "# Removed\n")
    return repo


class TestMigration:
    def test_base_paths_lists_the_files_of_the_base(self, migrated):
        assert set(base_paths(migrated.root, "main")) == {
            "keep.txt", "root-old.txt", "dir/b.txt", "gone/c.txt", "pkg/__pycache__/m.cpython-313.pyc"}

    def test_removed_entries_are_split_into_files_and_directories(self, repo):
        repo.write("docs/modernization/REMOVALS.md", "Removed `a/b.txt`, the folder `old/`, and `root.txt`. Not `two words`.\n")
        exact, prefixes, bytecode = removed_entries(repo.root)
        assert exact == {"a/b.txt", "root.txt"} and prefixes == ["old/"] and bytecode is False

    def test_bytecode_removal_needs_both_words(self, repo):
        repo.write("docs/modernization/REMOVALS.md", "`__pycache__` only\n")
        assert removed_entries(repo.root)[2] is False
        repo.write("docs/modernization/REMOVALS.md", "`__pycache__` and .pyc files\n")
        assert removed_entries(repo.root)[2] is True

    def test_unlisted_removals_fail_and_are_named(self, migrated, caplog):
        assert migration_main(["--base", "main"]) == 1
        for path in ("root-old.txt", "gone/c.txt"):
            assert f"UNRESOLVED {path}" in caplog.text
        assert "5 base paths checked, 3 unresolved" in caplog.text

    def test_everything_listed_passes(self, migrated):
        migrated.write("docs/modernization/REMOVALS.md",
                       "`root-old.txt` was removed, as was the folder `gone/`; Python `__pycache__` .pyc files too.\n")
        assert migration_main(["--base", "main"]) == 0

    def test_a_directory_entry_covers_everything_below_it(self, migrated):
        migrated.write("docs/modernization/REMOVALS.md", "`root-old.txt` `gone/` `pkg/__pycache__/`\n")
        assert migration_main(["--base", "main"]) == 0

    def test_a_directory_entry_is_a_prefix_not_a_substring(self, migrated):
        migrated.write("docs/modernization/REMOVALS.md", "`root-old.txt` `one/` `__pycache__` .pyc\n")
        assert migration_main(["--base", "main"]) == 1  # gone/c.txt is not under one/

    def test_a_path_that_still_exists_needs_no_entry(self, repo):
        repo.write("a.txt")
        repo.write("docs/modernization/REMOVALS.md", "# none\n")
        repo.commit()
        assert migration_main(["--base", "main"]) == 0

    def test_an_unknown_base_is_a_distinct_error(self, migrated, caplog):
        assert migration_main(["--base", "no-such-branch"]) == 2
        assert "cannot read no-such-branch" in caplog.text

    def test_a_missing_removals_file_is_a_clear_error_not_a_crash(self, repo, caplog):
        repo.write("a.txt")
        repo.commit()
        assert migration_main(["--base", "main"]) == 2
        assert "REMOVALS.md" in caplog.text


class TestStripJsonc:
    @pytest.mark.parametrize(("text", "expected"), [
        ('{"a": 1} // trailing', '{"a": 1} '),
        ('{"a": /* inline */ 1}', '{"a":  1}'),
        ('{"url": "http://x//y"}', '{"url": "http://x//y"}'),
        ('{"s": "a \\" // not a comment"}', '{"s": "a \\" // not a comment"}'),
        ('{"a": [1, 2,]}', '{"a": [1, 2]}'),
        ('{"a": 1,\n}', '{"a": 1\n}'),
        ('{"a": 1} /* never closed', '{"a": 1} '),
        ('// only a comment', ''),
        ('{"s": "/* kept */"}', '{"s": "/* kept */"}'),
    ])
    def test_comments_and_trailing_commas(self, text, expected):
        assert strip_jsonc(text) == expected

    @pytest.mark.parametrize("text", ['{"s": ",}"}', '{"s": "a, ]"}', '{"s": ",\\n}"}', '["x,", "y,]"]'])
    def test_comma_like_text_inside_a_string_is_left_alone(self, text):
        assert strip_jsonc(text) == text

    def test_a_trailing_comma_before_a_comment_and_a_brace_is_removed(self):
        assert strip_jsonc('{"a": 1, // c\n}') == '{"a": 1 \n}'

    def test_a_comma_between_values_is_kept(self):
        assert strip_jsonc('{"a": 1, "b": [1, 2]}') == '{"a": 1, "b": [1, 2]}'

    def test_nested_trailing_commas(self):
        assert strip_jsonc('{"a": [1, {"b": 2,},],}') == '{"a": [1, {"b": 2}]}'

    def test_the_result_parses_as_json(self):
        import json
        assert json.loads(strip_jsonc('{\n // c\n "a": [1, 2,], /* x */\n "s": ",}",\n}')) == {"a": [1, 2], "s": ",}"}


class TestParsers:
    def test_toml(self, tmp_path):
        good, bad = tmp_path / "a.toml", tmp_path / "b.toml"
        good.write_text('a = 1\n[t]\nb = "x"\n')
        bad.write_text("a = \n")
        assert check_toml(good) is None
        assert check_toml(bad).startswith("TOML:")

    def test_toml_that_is_not_utf8_is_reported(self, tmp_path):
        f = tmp_path / "a.toml"
        f.write_bytes(b"a = '\xff'\n")
        assert check_toml(f).startswith("TOML:")

    def test_plain_json_rejects_comments(self, tmp_path):
        f = tmp_path / "config.json"
        f.write_text('{"a": 1 // no\n}')
        assert check_json(f).startswith("JSON:")

    def test_jsonc_files_accept_comments_and_trailing_commas(self, tmp_path):
        f = tmp_path / "settings.json"
        f.write_text('{\n  // c\n  "a": 1,\n}\n')
        assert check_json(f) is None

    def test_json_syntax_errors_are_reported(self, tmp_path):
        f = tmp_path / "x.json"
        f.write_text('{"a": }')
        assert check_json(f).startswith("JSON:")

    def test_yaml_allows_multiple_documents_and_rejects_bad_syntax(self, tmp_path):
        good, bad = tmp_path / "a.yaml", tmp_path / "b.yaml"
        good.write_text("a: 1\n---\nb: 2\n")
        bad.write_text("a: [unclosed\n")
        assert check_yaml(good) is None
        assert check_yaml(bad).startswith("YAML:")

    def test_a_service_unit(self, tmp_path):
        f = tmp_path / "x.service"
        f.write_text("[Unit]\nDescription=x\n[Service]\nExecStart=/bin/true --a=b\n")
        assert check_unit(f) is None

    def test_a_service_needs_a_service_section(self, tmp_path):
        f = tmp_path / "x.service"
        f.write_text("[Unit]\nDescription=x\n")
        assert check_unit(f) == "service unit has no [Service] section"

    def test_a_timer_needs_a_timer_section(self, tmp_path):
        f = tmp_path / "x.timer"
        f.write_text("[Unit]\nDescription=x\n")
        assert check_unit(f) == "timer unit has no [Timer] section"

    def test_a_valid_timer(self, tmp_path):
        f = tmp_path / "x.timer"
        f.write_text("[Timer]\nOnCalendar=daily\n")
        assert check_unit(f) is None

    def test_a_path_unit_needs_no_particular_section(self, tmp_path):
        f = tmp_path / "x.path"
        f.write_text("[Path]\nPathChanged=/x\n")
        assert check_unit(f) is None

    def test_keys_keep_their_case_and_repeats_are_allowed(self, tmp_path):
        f = tmp_path / "x.service"
        f.write_text("[Service]\nExecStart=/a\nExecStart=/b\nEnvironment=A=1\n")
        assert check_unit(f) is None

    def test_text_before_any_section_is_a_syntax_error(self, tmp_path):
        f = tmp_path / "x.service"
        f.write_text("stray line\n[Service]\n")
        assert check_unit(f).startswith("unit syntax:")


class TestManifest:
    def write(self, repo, text):
        repo.write("src/a", "x")
        repo.write("manifest.conf", text)
        return check_manifest(repo.root)

    def test_valid_rows_comments_and_blank_lines(self, repo):
        assert self.write(repo, "# comment\n\nlink src/a ~/.a\nseed src/a ~/.b\n") == []

    def test_wrong_field_count(self, repo):
        assert self.write(repo, "link src/a\n") == ["manifest.conf:1: expected '<type> <src> <dst>', got 2 fields"]

    def test_too_many_fields(self, repo):
        assert "got 4 fields" in self.write(repo, "link src/a ~/.a extra\n")[0]

    def test_unknown_type(self, repo):
        assert self.write(repo, "copy src/a ~/.a\n") == ["manifest.conf:1: type 'copy' is not link|seed"]

    def test_missing_source(self, repo):
        assert self.write(repo, "link src/nope ~/.a\n") == ["manifest.conf:1: source missing: src/nope"]

    def test_duplicate_destination_names_the_first_line(self, repo):
        errors = self.write(repo, "link src/a ~/.a\nlink src/a ~/.a\n")
        assert errors == ["manifest.conf:2: destination ~/.a already used at line 1"]

    def test_a_missing_manifest_is_an_error_not_a_crash(self, repo):
        assert check_manifest(repo.root) == ["manifest.conf: missing"]


class TestPackageList:
    def lines(self, tmp_path, text):
        f = tmp_path / "pkgs.txt"
        f.write_text(text)
        return check_package_list(f)

    def test_names_and_aur_marker(self, tmp_path):
        assert self.lines(tmp_path, "# c\n\nvim\npython-yaml\nzed-bin (AUR)\nlib32-x.y+z\n") == []

    def test_uppercase_is_rejected(self, tmp_path):
        assert self.lines(tmp_path, "Vim\n") == ["pkgs.txt:1: not 'name' or 'name (AUR)': 'Vim'"]

    def test_a_trailing_comment_is_rejected(self, tmp_path):
        assert len(self.lines(tmp_path, "vim  # editor\n")) == 1

    def test_duplicates_are_reported_at_the_second_line(self, tmp_path):
        assert self.lines(tmp_path, "vim\nnano\nvim\n") == ["pkgs.txt:3: duplicate package vim"]

    def test_the_aur_marker_does_not_hide_a_duplicate(self, tmp_path):
        assert len(self.lines(tmp_path, "vim\nvim (AUR)\n")) == 1


class TestConfigsMain:
    def base(self, repo):
        repo.write("manifest.conf", "")

    def test_a_clean_repo_counts_what_it_parsed(self, repo, caplog):
        self.base(repo)
        repo.write("a.toml", "a = 1\n")
        repo.write("b.json", "{}")
        repo.write("c.yml", "a: 1\n")
        assert configs_main([]) == 0
        assert "parsed 3 config files plus manifest.conf, 0 problems" in caplog.text

    def test_a_bad_file_fails_and_is_named(self, repo, caplog):
        self.base(repo)
        repo.write("a.toml", "a = \n")
        assert configs_main([]) == 1
        assert "INVALID a.toml: TOML:" in caplog.text

    def test_units_are_only_checked_inside_a_systemd_folder(self, repo):
        self.base(repo)
        repo.write("elsewhere/x.service", "garbage\n")
        assert configs_main([]) == 0
        repo.write("systemd/x.service", "garbage\n")
        assert configs_main([]) == 1

    def test_package_lists_are_found_by_path_and_extension(self, repo):
        self.base(repo)
        repo.write("setup/packages/core.txt", "Bad Name\n")
        assert configs_main([]) == 1

    def test_host_snapshots_are_not_held_to_the_list_format(self, repo):
        self.base(repo)
        repo.write("setup/packages/host-snapshot.txt", "Bad Name\n")
        assert configs_main([]) == 0

    def test_a_text_file_outside_a_packages_folder_is_ignored(self, repo):
        self.base(repo)
        repo.write("notes/other.txt", "Bad Name\n")
        assert configs_main([]) == 0

    def test_manifest_problems_fail_the_run(self, repo, caplog):
        repo.write("manifest.conf", "link nowhere ~/.x\n")
        assert configs_main([]) == 1
        assert "INVALID manifest.conf:1: source missing: nowhere" in caplog.text

    def test_a_missing_manifest_fails_cleanly(self, repo):
        assert configs_main([]) == 1
