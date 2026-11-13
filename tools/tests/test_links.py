"""check_links: slugs, anchors, link extraction, relative-link resolution, URL probing."""
from __future__ import annotations

import urllib.error

import check_links
import pytest
from check_links import anchors_of, check_local, check_url, links_of, main, slugify


class TestSlugify:
    @pytest.mark.parametrize(("heading", "slug"), [
        ("Hello World", "hello-world"),
        ("`code` Heading!", "code-heading"),
        ("A [link](http://x) here", "a-link-here"),
        ("<b>Bold</b> text", "bold-text"),
        ("Under_score *star* ~strike~", "underscore-star-strike"),
        ("C++ & Rust", "c--rust"),
        ("a-b stays", "a-b-stays"),
        ("  padded  ", "padded"),
        ("Ünïcode Ñame", "ünïcode-ñame"),
        ("Step 1: install", "step-1-install"),
    ])
    def test_github_style_slugs(self, heading, slug):
        assert slugify(heading) == slug


class TestAnchors:
    def test_headings_become_anchors(self, tmp_path):
        f = tmp_path / "a.md"
        f.write_text("# One\n## Two Words\n### Three `x`\n")
        assert anchors_of(f, {}) == {"one", "two-words", "three-x"}

    def test_repeated_headings_get_numbered_suffixes(self, tmp_path):
        f = tmp_path / "a.md"
        f.write_text("# Same\n## Same\n### Same\n")
        assert anchors_of(f, {}) == {"same", "same-1", "same-2"}

    def test_headings_inside_code_are_not_anchors(self, tmp_path):
        f = tmp_path / "a.md"
        f.write_text("# Real\n```sh\n# comment\n```\n")
        assert anchors_of(f, {}) == {"real"}

    def test_closing_hashes_are_dropped(self, tmp_path):
        f = tmp_path / "a.md"
        f.write_text("## Title ##\n")
        assert anchors_of(f, {}) == {"title"}

    def test_html_ids_and_names_count(self, tmp_path):
        f = tmp_path / "a.md"
        f.write_text('<a id="manual"></a>\n<a name="other"></a>\n# H\n')
        assert anchors_of(f, {}) == {"manual", "other", "h"}

    def test_a_hash_with_no_space_is_not_a_heading(self, tmp_path):
        f = tmp_path / "a.md"
        f.write_text("#nospace\n")
        assert anchors_of(f, {}) == set()

    def test_results_are_cached(self, tmp_path):
        f = tmp_path / "a.md"
        f.write_text("# One\n")
        cache: dict = {}
        anchors_of(f, cache)
        f.write_text("# Two\n")
        assert anchors_of(f, cache) == {"one"}


class TestLinksOf:
    def links(self, tmp_path, text):
        f = tmp_path / "a.md"
        f.write_text(text)
        return links_of(f)

    def test_inline_links(self, tmp_path):
        assert self.links(tmp_path, "[a](one.md) and [b](two.md#x)") == ["one.md", "two.md#x"]

    def test_images(self, tmp_path):
        assert self.links(tmp_path, "![alt](pic.png)") == ["pic.png"]

    def test_reference_definitions(self, tmp_path):
        assert self.links(tmp_path, "[ref]: target.md\n[other]: <spaced.md> \"title\"\n") == ["target.md", "spaced.md"]

    def test_autolinks(self, tmp_path):
        assert self.links(tmp_path, "see <https://example.com/x>") == ["https://example.com/x"]

    def test_a_title_after_the_target_is_ignored(self, tmp_path):
        assert self.links(tmp_path, '[a](one.md "the title")') == ["one.md"]

    def test_angle_brackets_around_the_target_are_removed(self, tmp_path):
        assert self.links(tmp_path, "[a](<one.md>)") == ["one.md"]

    def test_code_is_ignored(self, tmp_path):
        assert self.links(tmp_path, "`[a](gone.md)`\n```\n[b](gone2.md)\n```\n[c](kept.md)") == ["kept.md"]

    def test_an_image_is_not_also_counted_as_a_link(self, tmp_path):
        assert self.links(tmp_path, "![alt](pic.png)").count("pic.png") == 1

    def test_escaped_brackets_in_the_text_are_allowed(self, tmp_path):
        assert self.links(tmp_path, r"[a \] b](one.md)") == ["one.md"]


class TestCheckLocal:
    @pytest.fixture
    def tree(self, tmp_path):
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "a.md").write_text("# Top\n## Sub Heading\n")
        (tmp_path / "docs" / "b.md").write_text("# B\n")
        (tmp_path / "docs" / "data.txt").write_text("x\n")
        (tmp_path / "docs" / "dir").mkdir()
        return tmp_path

    def check(self, tree, target, src="docs/b.md"):
        return check_local(tree / src, target, tree, {})

    def test_a_good_relative_link(self, tree):
        assert self.check(tree, "a.md") is None

    def test_a_missing_file(self, tree):
        assert self.check(tree, "nope.md") == "missing path: nope.md"

    def test_a_good_anchor(self, tree):
        assert self.check(tree, "a.md#sub-heading") is None

    def test_a_missing_anchor(self, tree):
        assert self.check(tree, "a.md#nope") == "missing anchor #nope in docs/a.md"

    def test_a_fragment_only_link_checks_the_same_file(self, tree):
        assert self.check(tree, "#b") is None
        assert self.check(tree, "#nope") == "missing anchor #nope in docs/b.md"

    def test_an_anchor_into_a_non_markdown_file_is_not_checked(self, tree):
        assert self.check(tree, "data.txt#anything") is None

    def test_a_directory_is_a_valid_target(self, tree):
        assert self.check(tree, "dir") is None

    def test_a_root_relative_link_resolves_from_the_repo_root(self, tree):
        assert self.check(tree, "/docs/a.md") is None
        assert self.check(tree, "/nope.md") == "missing path: /nope.md"

    def test_parent_directory_links(self, tree):
        (tree / "top.md").write_text("# Top\n")
        assert self.check(tree, "../top.md") is None

    def test_a_link_out_of_the_repository_is_reported(self, tree):
        assert self.check(tree, "../../elsewhere.md") == "escapes repo: ../../elsewhere.md"

    def test_percent_encoding_is_decoded(self, tree):
        (tree / "docs" / "with space.md").write_text("# S\n")
        assert self.check(tree, "with%20space.md") is None

    def test_an_encoded_anchor_is_decoded(self, tree):
        assert self.check(tree, "a.md#sub%2Dheading") is None


class FakeResponse:
    def __init__(self, status):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def script(monkeypatch, *outcomes):
    """Replace urlopen with a script of outcomes (an int status, or an exception to raise); returns the methods called."""
    calls: list[str] = []
    queue = list(outcomes)

    def fake(req, timeout=None):
        calls.append(req.get_method())
        outcome = queue.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return FakeResponse(outcome)

    monkeypatch.setattr(check_links.urllib.request, "urlopen", fake)
    return calls


def http(code, url="https://example.com/x"):
    return urllib.error.HTTPError(url, code, "msg", {}, None)  # type: ignore[arg-type]


URL = "https://example.com/x"


class TestCheckUrl:
    def test_a_good_url_is_one_head_request(self, monkeypatch):
        calls = script(monkeypatch, 200)
        assert check_url(URL) is None
        assert calls == ["HEAD"]

    def test_a_404_is_broken_and_stops_at_the_first_answer(self, monkeypatch):
        calls = script(monkeypatch, http(404))
        assert check_url(URL) == f"HTTP 404: {URL}"
        assert calls == ["HEAD"]

    def test_a_server_error_is_broken(self, monkeypatch):
        script(monkeypatch, http(500))
        assert check_url(URL) == f"HTTP 500: {URL}"

    @pytest.mark.parametrize("code", [405, 403])
    def test_head_refused_falls_back_to_get(self, monkeypatch, code):
        calls = script(monkeypatch, http(code), 200)
        assert check_url(URL) is None
        assert calls == ["HEAD", "GET"]

    def test_head_not_implemented_falls_back_to_get(self, monkeypatch):
        calls = script(monkeypatch, http(501), 200)
        assert check_url(URL) is None
        assert calls == ["HEAD", "GET"]

    def test_get_forbidden_on_an_ordinary_host_is_broken(self, monkeypatch):
        script(monkeypatch, http(403), http(403))
        assert check_url(URL) == f"HTTP 403: {URL}"

    def test_get_forbidden_on_a_bot_hostile_host_is_not_broken(self, monkeypatch):
        script(monkeypatch, http(403), http(403))
        assert check_url("https://www.linkedin.com/in/x") is None

    @pytest.mark.parametrize("code", [401, 429])
    def test_rate_limited_or_unauthorised_head_is_not_broken(self, monkeypatch, code):
        calls = script(monkeypatch, http(code))
        assert check_url(URL) is None
        assert calls == ["HEAD"]

    def test_a_connection_error_on_head_still_tries_get(self, monkeypatch):
        calls = script(monkeypatch, urllib.error.URLError("boom"), 200)
        assert check_url(URL) is None
        assert calls == ["HEAD", "GET"]

    def test_unreachable_on_both_is_reported(self, monkeypatch):
        script(monkeypatch, urllib.error.URLError("boom"), urllib.error.URLError("boom"))
        assert check_url(URL).startswith("unreachable (")

    def test_a_timeout_counts_as_unreachable(self, monkeypatch):
        script(monkeypatch, TimeoutError("slow"), TimeoutError("slow"))
        assert check_url(URL).startswith("unreachable (")

    def test_get_404_after_head_405_is_broken(self, monkeypatch):
        script(monkeypatch, http(405), http(404))
        assert check_url(URL) == f"HTTP 404: {URL}"


class TestMain:
    def test_a_clean_repo_passes(self, repo, caplog):
        repo.write("a.md", "# A\n[b](b.md)\n")
        repo.write("b.md", "# B\n")
        assert main([]) == 0
        assert "checked 2 markdown files, 0 external urls (not fetched), 0 broken" in caplog.text

    def test_a_broken_link_fails_and_names_the_file(self, repo, caplog):
        repo.write("a.md", "[x](missing.md)\n")
        assert main([]) == 1
        assert "BROKEN a.md: missing path: missing.md" in caplog.text

    def test_a_broken_anchor_fails(self, repo, caplog):
        repo.write("a.md", "[x](b.md#nope)\n")
        repo.write("b.md", "# B\n")
        assert main([]) == 1
        assert "missing anchor #nope in b.md" in caplog.text

    @pytest.mark.parametrize("target", ["mailto:a@b.c", "tel:123", "data:x", "javascript:void(0)"])
    def test_non_http_schemes_are_skipped(self, repo, target):
        repo.write("a.md", f"[x]({target})\n")
        assert main([]) == 0

    def test_template_placeholders_are_skipped(self, repo):
        repo.write("a.md", "[x]({{ site.url }}/x)\n")
        assert main([]) == 0

    def test_urls_are_counted_but_not_fetched_by_default(self, repo, caplog, monkeypatch):
        monkeypatch.setattr(check_links, "check_url", lambda u: pytest.fail("must not fetch"))
        repo.write("a.md", "[x](https://example.com/a) and <https://example.com/b>\n")
        assert main([]) == 0
        assert "2 external urls (not fetched)" in caplog.text

    def test_external_mode_fetches_and_reports_broken_urls(self, repo, caplog, monkeypatch):
        monkeypatch.setattr(check_links, "check_url", lambda u: "HTTP 404: " + u if u.endswith("/bad") else None)
        repo.write("a.md", "[x](https://example.com/bad) [y](https://example.com/ok)\n")
        assert main(["--external"]) == 1
        assert "BROKEN a.md: HTTP 404: https://example.com/bad" in caplog.text
        assert "(not fetched)" not in caplog.text

    def test_trailing_punctuation_does_not_make_a_second_url(self, repo, caplog):
        repo.write("a.md", "<https://example.com/x> and <https://example.com/x.>\n")
        main([])
        assert "1 external urls" in caplog.text

    def test_a_link_in_a_code_block_is_not_checked(self, repo):
        repo.write("a.md", "```md\n[x](missing.md)\n```\n")
        assert main([]) == 0

    def test_an_image_with_a_missing_file_fails(self, repo):
        repo.write("a.md", "![alt](missing.png)\n")
        assert main([]) == 1
