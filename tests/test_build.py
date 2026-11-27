"""Builder contract tests; all publication inputs live in temporary fixtures."""

import json
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build.py"
SLUGS = ("index", "data-handling", "security", "faq", "support")
ASSETS = ("site.css", "site.js", "data-flow.svg")


class Document(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.tags = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.source = self.base / "source"
        self.output = self.base / "published"
        (self.source / "content").mkdir(parents=True)
        (self.source / "assets").mkdir()
        self.config = {
            "title": "Meeting Pulse Trust",
            "description": "Public security and privacy documentation.",
            "reviewed_on": "2026-11-26",
            "pages": [
                {"slug": slug, "title": slug.title(), "nav": slug.title()}
                for slug in SLUGS
            ],
        }
        self.write_config()
        for slug in SLUGS:
            self.write_page(slug, f"# {slug.title()}\n\nReviewed public information.\n")
        self.write_page(
            "index",
            "# Overview\n\n[Data handling](data-handling.html)\n\n"
            "![Data flow](assets/data-flow.svg)\n\n"
            "| Topic | Status |\n| --- | --- |\n| Review | Current |\n",
        )
        for name in ASSETS:
            (self.source / "assets" / name).write_text(
                "<svg xmlns=\"http://www.w3.org/2000/svg\"></svg>"
                if name.endswith("svg") else f"/* {name} */\n",
                encoding="utf-8",
            )

    def write_config(self):
        (self.source / "site.json").write_text(json.dumps(self.config), encoding="utf-8")

    def write_page(self, slug, markdown):
        (self.source / "content" / f"{slug}.md").write_text(markdown, encoding="utf-8")

    def run_build(self, output=None, source=None, default_output=False):
        self.assertTrue(BUILDER.is_file(), "Static site builder has not been implemented")
        args = [sys.executable, str(BUILDER), "--source", str(source or self.source)]
        if not default_output:
            args += ["--output", str(output or self.output)]
        return subprocess.run(args, cwd=self.base, capture_output=True, text=True)

    def assert_success(self, **kwargs):
        result = self.run_build(**kwargs)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def assert_rejected(self, **kwargs):
        result = self.run_build(**kwargs)
        self.assertNotEqual(result.returncode, 0, "Unsafe input was accepted")
        self.assertIn("error:", result.stderr.lower())
        self.assertNotIn("Traceback", result.stderr)
        return result

    def snapshot(self):
        return {
            path.relative_to(self.output).as_posix(): path.read_bytes()
            for path in self.output.rglob("*") if path.is_file()
        }

    def test_builds_exactly_five_pages_and_three_reviewed_assets(self):
        (self.source / "private.pdf").write_bytes(b"not public")
        (self.source / "content" / "notes.md").write_text("private notes")
        (self.source / "assets" / "private.txt").write_text("not public")
        self.assert_success()
        self.assertEqual(
            set(self.snapshot()),
            {f"{slug}.html" for slug in SLUGS} | {f"assets/{name}" for name in ASSETS},
        )
        for name in ASSETS:
            self.assertEqual(
                (self.output / "assets" / name).read_bytes(),
                (self.source / "assets" / name).read_bytes(),
            )

    def test_default_output_is_site_under_working_directory(self):
        self.assert_success(default_output=True)
        self.assertTrue((self.base / "_site" / "index.html").is_file())

    def test_default_source_is_repository_not_current_directory(self):
        result = subprocess.run(
            [sys.executable, str(BUILDER), "--help"],
            cwd=self.base, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--source", result.stdout)
        self.assertIn("--output", result.stdout)
        self.assertIn(str(ROOT), result.stdout)

    def test_markup_has_semantic_navigation_single_markdown_h1_and_skiplink(self):
        self.assert_success()
        for slug in SLUGS:
            with self.subTest(slug=slug):
                markup = (self.output / f"{slug}.html").read_text()
                tags = Document(markup).tags
                self.assertEqual(sum(tag == "h1" for tag, _ in tags), 1)
                for required in ("header", "nav", "main", "article", "footer", "details", "summary"):
                    self.assertTrue(any(tag == required for tag, _ in tags), required)
                self.assertIn(("a", {"class": "skip-link", "href": "#main-content"}), tags)
                self.assertTrue(any(tag == "main" and attrs.get("id") == "main-content"
                                    and attrs.get("tabindex") == "-1" for tag, attrs in tags))
                active = [attrs for tag, attrs in tags if tag == "a" and attrs.get("aria-current")]
                self.assertTrue(active)
                self.assertTrue(all(a["href"] == f"{slug}.html" for a in active))
                self.assertIn("2026-11-26", markup)
        self.assertIn("<h1>Overview</h1>", (self.output / "index.html").read_text())

    def test_navigation_and_assets_resolve_from_file_and_project_paths(self):
        self.assert_success()
        for page in self.output.glob("*.html"):
            tags = Document(page.read_text()).tags
            nav_links = {a["href"] for t, a in tags if t == "a" and "href" in a}
            self.assertTrue({f"{slug}.html" for slug in SLUGS} <= nav_links)
            self.assertTrue(any(t == "script" and a.get("src") == "assets/site.js"
                                and "defer" not in a for t, a in tags))
            self.assertTrue(any(t == "link" and a.get("href") == "assets/site.css"
                                for t, a in tags))
            for tag, attrs in tags:
                for key in ("href", "src"):
                    value = attrs.get(key, "")
                    if not value or value.startswith("#"):
                        continue
                    parsed = urlsplit(value)
                    if parsed.scheme:
                        continue
                    self.assertFalse(value.startswith("/"), value)
                    self.assertTrue((page.parent / unquote(parsed.path)).is_file(), value)

    def test_theme_initializes_before_styles_without_inline_code(self):
        self.assert_success()
        for slug in SLUGS:
            markup = (self.output / f"{slug}.html").read_text()
            tags = Document(markup).tags
            script = next(i for i, (tag, attrs) in enumerate(tags)
                          if tag == "script" and attrs.get("src") == "assets/site.js")
            stylesheet = next(i for i, (tag, attrs) in enumerate(tags)
                              if tag == "link" and attrs.get("rel") == "stylesheet")
            self.assertLess(script, stylesheet)
            self.assertNotIn("defer", tags[script][1])
            self.assertNotIn("async", tags[script][1])

    def test_every_page_has_accessible_theme_choices_hidden_without_javascript(self):
        self.assert_success()
        for slug in SLUGS:
            tags = Document((self.output / f"{slug}.html").read_text()).tags
            group = next((a for t, a in tags if a.get("class") == "theme-switcher"), {})
            self.assertEqual(group.get("role"), "group")
            self.assertEqual(group.get("aria-label"), "Color theme")
            self.assertIn("hidden", group)
            choices = [a for t, a in tags if t == "button" and "data-theme-choice" in a]
            self.assertEqual([a["data-theme-choice"] for a in choices],
                             ["system", "light", "dark"])
            for choice in choices:
                self.assertEqual(choice.get("type"), "button")
                self.assertTrue(choice.get("aria-label"))
                self.assertTrue(choice.get("title"))
                self.assertEqual(choice.get("aria-pressed"),
                                 str(choice["data-theme-choice"] == "system").lower())

    def test_escapes_all_metadata_and_disables_raw_html(self):
        hostile = '\"><script>alert("x")</script>&'
        self.config["title"] = hostile
        self.config["description"] = hostile
        for page in self.config["pages"]:
            page["title"] = hostile
            page["nav"] = hostile
        self.write_config()
        self.write_page("security", '# Security\n\n<script>alert("raw")</script>\n\n'
                        '[unsafe](javascript:alert(1))\n')
        self.assert_success()
        markup = (self.output / "security.html").read_text()
        self.assertNotIn("<script>alert", markup)
        self.assertIn("&lt;script&gt;", markup)
        tags = Document(markup).tags
        description = next(a["content"] for t, a in tags if t == "meta" and a.get("name") == "description")
        self.assertEqual(description, hostile)
        self.assertFalse(any(a.get("href", "").startswith("javascript:") for _, a in tags))

    def test_tables_are_in_keyboard_accessible_scroll_region(self):
        self.assert_success()
        markup = (self.output / "index.html").read_text()
        self.assertIn("<table>", markup)
        wrappers = [a for t, a in Document(markup).tags if a.get("class") == "table-scroll"]
        self.assertEqual(len(wrappers), 1)
        self.assertEqual(wrappers[0].get("tabindex"), "0")
        self.assertEqual(wrappers[0].get("role"), "region")
        self.assertTrue(wrappers[0].get("aria-label"))
        self.assertLess(markup.index('class="table-scroll"'), markup.index("<table>"))
        self.assertIn("</table>\n</div>", markup)

    def test_csp_blocks_external_active_resources_and_inline_code(self):
        self.assert_success()
        tags = Document((self.output / "index.html").read_text()).tags
        csp = next(a["content"] for t, a in tags if t == "meta"
                   and a.get("http-equiv", "").lower() == "content-security-policy")
        for directive in ("default-src 'none'", "script-src 'self'", "style-src 'self'",
                          "img-src 'self'", "connect-src 'none'", "object-src 'none'",
                          "base-uri 'none'", "form-action 'none'"):
            self.assertIn(directive, csp)
        self.assertNotIn("unsafe-inline", csp)
        self.assertFalse(any(t in ("base", "iframe") or any(k.startswith("on") for k in a)
                             for t, a in tags))

    def test_build_is_byte_deterministic_and_updates_existing_artifact(self):
        self.assert_success()
        first = self.snapshot()
        self.assert_success()
        self.assertEqual(first, self.snapshot())
        self.write_page("support", "# Support\n\nUpdated guidance.\n")
        self.assert_success()
        self.assertIn("Updated guidance.", (self.output / "support.html").read_text())

    def test_missing_page_fails_before_writing_output(self):
        (self.source / "content" / "security.md").unlink()
        self.assert_rejected()
        self.assertFalse(self.output.exists())

    def test_missing_reviewed_asset_fails_before_writing_output(self):
        (self.source / "assets" / "data-flow.svg").unlink()
        self.assert_rejected()
        self.assertFalse(self.output.exists())

    def test_requires_each_of_the_five_unique_safe_slugs(self):
        original = json.loads(json.dumps(self.config))
        variants = ("../escape", "/absolute", "faq/child", "faq.html", "FAQ", "", "index", "unknown")
        for slug in variants:
            with self.subTest(slug=slug):
                self.config = json.loads(json.dumps(original))
                self.config["pages"][3]["slug"] = slug
                self.write_config()
                self.assert_rejected()
                self.assertFalse(self.output.exists())
        self.config["pages"] = original["pages"][:-1]
        self.write_config()
        self.assert_rejected()

    def test_rejects_invalid_metadata_cleanly(self):
        original = json.loads(json.dumps(self.config))
        variants = [[], {**original, "title": ""}, {**original, "title": 3},
                    {**original, "description": None}, {**original, "pages": {}},
                    {**original, "reviewed_on": None},
                    {**original, "reviewed_on": ""},
                    {**original, "pages": [None] * 5}]
        for config in variants:
            with self.subTest(config=config):
                self.config = config
                self.write_config()
                self.assert_rejected()
                self.assertFalse(self.output.exists())
        (self.source / "site.json").write_text("not JSON")
        self.assert_rejected()

    def test_requires_exactly_one_markdown_h1_per_page(self):
        for markdown in ("No heading", "## Only a subheading", "# First\n\n# Second"):
            with self.subTest(markdown=markdown):
                self.write_page("faq", markdown)
                self.assert_rejected()
                self.assertFalse(self.output.exists())

    def test_output_must_not_overlap_source_inputs_or_repository_root(self):
        before = (self.source / "site.json").read_bytes()
        for output in (self.source, self.base, self.source / "content",
                       self.source / "assets" / "output", self.source / "scripts",
                       self.source / ".git" / "artifact"):
            with self.subTest(output=output):
                self.assert_rejected(output=output)
        self.assertEqual((self.source / "site.json").read_bytes(), before)

    def test_allows_normal_site_output_inside_source(self):
        self.assert_success(output=self.source / "_site")
        self.assertTrue((self.source / "_site" / "index.html").is_file())

    def test_refuses_unknown_existing_output_instead_of_deleting_it(self):
        self.output.mkdir()
        secret = self.output / "private.txt"
        secret.write_text("preserve me")
        self.assert_rejected()
        self.assertEqual(secret.read_text(), "preserve me")
        self.assertEqual(list(self.output.iterdir()), [secret])

    def test_refuses_unknown_nested_output_files(self):
        self.assert_success()
        private = self.output / "assets" / "private.pdf"
        private.write_bytes(b"preserve me")
        before = self.snapshot()
        self.assert_rejected()
        self.assertEqual(before, self.snapshot())

    def test_refuses_symlinked_source_file_directory_and_root(self):
        for relative in ("site.json", "content/index.md", "assets/site.css", "content", "assets"):
            with self.subTest(relative=relative):
                target = self.source / relative
                saved = self.base / (relative.replace("/", "-") + "-saved")
                target.rename(saved)
                target.symlink_to(saved, target_is_directory=saved.is_dir())
                self.assert_rejected()
                self.assertFalse(self.output.exists())
                target.unlink()
                saved.rename(target)
        link = self.base / "source-link"
        link.symlink_to(self.source, target_is_directory=True)
        self.assert_rejected(source=link)

    def test_refuses_symlinked_output_or_output_ancestor(self):
        external = self.base / "external"
        external.mkdir()
        link = self.base / "output-link"
        link.symlink_to(external, target_is_directory=True)
        self.assert_rejected(output=link)
        self.assert_rejected(output=link / "nested")
        self.assertEqual(list(external.iterdir()), [])

    def test_refuses_symlinked_existing_output_file_and_assets_directory(self):
        self.assert_success()
        sentinel = self.base / "sentinel"
        sentinel.write_text("preserve")
        (self.output / "index.html").unlink()
        (self.output / "index.html").symlink_to(sentinel)
        self.assert_rejected()
        self.assertEqual(sentinel.read_text(), "preserve")
        (self.output / "index.html").unlink()
        (self.output / "assets").rename(self.base / "saved-assets")
        (self.output / "assets").symlink_to(self.base / "saved-assets", target_is_directory=True)
        self.assert_rejected()

    def test_invalid_source_does_not_modify_an_existing_artifact(self):
        self.assert_success()
        before = self.snapshot()
        self.write_page("index", "# Changed but not published\n")
        (self.source / "content" / "support.md").unlink()
        self.assert_rejected()
        self.assertEqual(before, self.snapshot())

    def test_invalid_utf8_is_reported_without_traceback(self):
        (self.source / "content" / "support.md").write_bytes(b"\xff\xfe")
        self.assert_rejected()
        self.assertFalse(self.output.exists())

    def test_refuses_hardlinked_output_file_without_modifying_external_file(self):
        self.assert_success()
        external = self.base / "external.html"
        external.write_text("preserve")
        (self.output / "index.html").unlink()
        (self.output / "index.html").hardlink_to(external)
        self.assert_rejected()
        self.assertEqual(external.read_text(), "preserve")

    def test_rejects_external_resource_links_in_markdown(self):
        self.write_page("index", "# Overview\n\n![Tracking](https://example.com/pixel.gif)\n")
        self.assert_rejected()
        self.assertFalse(self.output.exists())

    def test_rejects_broken_local_markdown_links_before_writing(self):
        for destination in ("missing.html", "security.md", "../private.pdf", "/security.html"):
            with self.subTest(destination=destination):
                self.write_page("index", f"# Overview\n\n[Link]({destination})\n")
                self.assert_rejected()
                self.assertFalse(self.output.exists())

    def test_allows_public_hyperlinks_but_not_remote_images(self):
        self.write_page("support", "# Support\n\n[Report](https://example.com/security)\n\n"
                        "[Email](mailto:security@example.com)\n")
        self.assert_success()
        markup = (self.output / "support.html").read_text()
        self.assertIn('href="https://example.com/security"', markup)
        self.assertIn('href="mailto:security@example.com"', markup)

    def test_table_alignment_uses_local_css_instead_of_blocked_inline_styles(self):
        self.write_page("index", "# Overview\n\n| Left | Center | Right |\n"
                        "| :--- | :---: | ---: |\n| A | B | C |\n")
        self.assert_success()
        tags = Document((self.output / "index.html").read_text()).tags
        cells = [a for t, a in tags if t in ("td", "th")]
        self.assertEqual(len(cells), 6)
        self.assertTrue(all("style" not in a for a in cells))
        self.assertEqual({a.get("class") for a in cells},
                         {"align-left", "align-center", "align-right"})

    def test_accepts_human_readable_review_date(self):
        self.config["reviewed_on"] = "26 November 2026"
        self.write_config()
        self.assert_success()
        self.assertIn("Reviewed 26 November 2026", (self.output / "index.html").read_text())

    def test_review_date_is_escaped_like_other_metadata(self):
        self.config["reviewed_on"] = '<script>alert("date")</script>'
        self.write_config()
        self.assert_success()
        markup = (self.output / "index.html").read_text()
        self.assertNotIn('<script>alert("date")</script>', markup)
        self.assertIn("&lt;script&gt;", markup)


if __name__ == "__main__":
    unittest.main()
