#!/usr/bin/env python3
"""Build only the reviewed public documentation and allowlisted local assets."""

import argparse
from html import escape
import json
from pathlib import Path
import stat
import sys
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt


DEFAULT_SOURCE = Path(__file__).resolve().parents[1]
SLUGS = ("index", "data-handling", "security", "faq", "support")
ASSETS = ("site.css", "site.js", "data-flow.svg")
SOURCE_PATHS = (
    "site.json", "content", "assets", "scripts", "tests", ".git", ".github",
    "README.md", "SECURITY.md", "requirements.txt", ".gitignore",
)
CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
    "font-src 'none'; connect-src 'none'; object-src 'none'; "
    "base-uri 'none'; form-action 'none'"
)


class BuildError(ValueError):
    """Invalid source or unsafe output destination."""


def safe_path(path):
    path = path.expanduser().absolute()
    for part in (path, *path.parents):
        if part.is_symlink():
            raise BuildError(f"Symlinks are not allowed: {part}")
    return path.resolve()


def read_file(path):
    path = safe_path(path)
    if not stat.S_ISREG(path.stat().st_mode):
        raise BuildError(f"Expected a regular file: {path.name}")
    return path.read_bytes()


def required_text(mapping, key):
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise BuildError(f"Metadata {key!r} must be nonempty text")
    return value


def load_config(source):
    config = json.loads(read_file(source / "site.json").decode("utf-8"))
    if not isinstance(config, dict):
        raise BuildError("site.json must contain an object")
    for key in ("title", "description", "reviewed_on"):
        required_text(config, key)
    pages = config.get("pages")
    if not isinstance(pages, list) or len(pages) != len(SLUGS):
        raise BuildError("pages must list all five public documentation pages")
    found = set()
    for page in pages:
        if not isinstance(page, dict):
            raise BuildError("Each page must be an object")
        slug = required_text(page, "slug")
        if slug not in SLUGS or slug in found:
            raise BuildError(f"Unsafe, unknown or duplicate page slug: {slug!r}")
        found.add(slug)
        required_text(page, "title")
        required_text(page, "nav")
    return config


def markdown_renderer():
    renderer = MarkdownIt("commonmark", {"html": False}).enable("table")

    def table_open(tokens, index, options, env):
        return ('<div class="table-scroll" role="region" aria-label="Data table" '
                'tabindex="0">\n<table>\n')

    def table_close(tokens, index, options, env):
        return "</table>\n</div>\n"

    renderer.renderer.rules["table_open"] = table_open
    renderer.renderer.rules["table_close"] = table_close
    return renderer


def prepare_tokens(tokens):
    local_targets = {f"{slug}.html" for slug in SLUGS}
    local_assets = {f"assets/{name}" for name in ASSETS}
    for token in tokens:
        if token.type in ("th_open", "td_open"):
            # Markdown table alignment must not require CSP-blocked inline styles.
            alignment = token.attrs.pop("style", "").removeprefix("text-align:")
            if alignment in ("left", "center", "right"):
                token.attrSet("class", f"align-{alignment}")
        if token.type in ("image", "link_open"):
            resource = token.type == "image"
            target = token.attrGet("src" if resource else "href") or ""
            parsed = urlsplit(target)
            external_link = not resource and parsed.scheme in ("https", "http", "mailto")
            if not external_link:
                path = unquote(parsed.path).removeprefix("./")
                allowed = local_assets if resource else local_targets | local_assets | {""}
                if parsed.scheme or parsed.netloc or path not in allowed:
                    raise BuildError(f"Link must use a published relative target: {target!r}")
        if token.children:
            prepare_tokens(token.children)


def navigation(pages, current):
    links = []
    for page in pages:
        active = ' aria-current="page"' if page["slug"] == current else ""
        links.append(f'<li><a href="{page["slug"]}.html"{active}>'
                     f'{escape(page["nav"])}' '</a></li>')
    return '<nav aria-label="Documentation"><ul>\n' + "\n".join(links) + "\n</ul></nav>"


def render_page(config, page, body):
    nav = navigation(config["pages"], page["slug"])
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="Content-Security-Policy" content="{escape(CSP, quote=True)}">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(config["description"], quote=True)}">
  <meta name="referrer" content="no-referrer">
  <title>{escape(page["title"])} | {escape(config["title"])}</title>
  <link rel="stylesheet" href="assets/site.css">
  <script src="assets/site.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to content</a>
  <header class="site-header">
    <a class="site-title" href="index.html">{escape(config["title"])}</a>
    <span class="site-label">Security &amp; Privacy</span>
    <details class="mobile-menu">
      <summary>Documentation</summary>
      {nav}
    </details>
  </header>
  <div class="docs-layout">
    <aside class="sidebar">{nav}</aside>
    <main id="main-content" tabindex="-1">
      <article>
{body}
      </article>
      <footer class="page-footer">
        <p>Reviewed {escape(config["reviewed_on"])}</p>
        <a href="support.html">Support &amp; questions</a>
      </footer>
    </main>
  </div>
</body>
</html>
'''


def check_output(source, output):
    if output == source or output in source.parents:
        raise BuildError("Output must not be the source directory or its ancestor")
    for name in SOURCE_PATHS:
        protected = source / name
        if output == protected or protected in output.parents:
            raise BuildError(f"Output must not overlap source input: {name}")
    if not output.exists():
        return
    if not output.is_dir():
        raise BuildError("Output must be a directory")
    expected = {f"{slug}.html" for slug in SLUGS}
    for child in output.iterdir():
        if child.is_symlink():
            raise BuildError(f"Symlink in output: {child.name}")
        if child.name == "assets" and child.is_dir():
            for asset in child.iterdir():
                check_output_file(asset, ASSETS)
        else:
            check_output_file(child, expected)


def check_output_file(path, allowed):
    info = path.lstat()
    if (path.name not in allowed or not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1):
        raise BuildError(f"Unexpected file in output; use a clean directory: {path.name}")


def build(source, output):
    source = safe_path(source)
    output = safe_path(output)
    check_output(source, output)
    config = load_config(source)
    renderer = markdown_renderer()
    files = {}
    # Validate and render every input before creating or updating the artifact.
    for page in config["pages"]:
        slug = page["slug"]
        markdown = read_file(source / "content" / f"{slug}.md").decode("utf-8")
        tokens = renderer.parse(markdown)
        if sum(t.type == "heading_open" and t.tag == "h1" for t in tokens) != 1:
            raise BuildError(f"{slug}.md must contain exactly one Markdown H1")
        prepare_tokens(tokens)
        body = renderer.renderer.render(tokens, renderer.options, {})
        files[f"{slug}.html"] = render_page(config, page, body).encode("utf-8")
    for name in ASSETS:
        files[f"assets/{name}"] = read_file(source / "assets" / name)
    (output / "assets").mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (output / name).write_bytes(data)
    return len(files)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                        help="Documentation source directory")
    parser.add_argument("--output", type=Path, default=Path("_site"),
                        help="Artifact directory (relative to the working directory)")
    args = parser.parse_args()
    try:
        count = build(args.source, args.output)
    except (BuildError, OSError, ValueError) as error:
        parser.exit(1, f"error: {error}\n")
    print(f"Built {count} public files in {args.output}")


if __name__ == "__main__":
    main()
