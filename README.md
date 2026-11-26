# Meeting Pulse Trust

Public security, privacy, data-handling, FAQ and support documentation for
Meeting Pulse. This repository is documentation only. It contains no application
implementation, service runtime, credentials or meeting data.

Read the [public security and privacy site](https://lindawa.github.io/meeting-pulse-trust/).

## Local Build

Python 3.11 or newer is required. From this repository:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/build.py --output _site
```

Open [_site/index.html](_site/index.html) directly in a browser. No local server,
external fonts, CDN or analytics are needed. Links are relative, including under
a GitHub Pages project path. The navigation works without JavaScript.

The default output is `_site` under the working directory. `--source DIR`
selects a different documentation source, primarily for isolated test fixtures;
otherwise the source is this repository, regardless of the working directory.

## Content Contract

`site.json` contains nonempty `title`, `description`, `reviewed_on` strings and a
`pages` list. The review date is display text; ISO and human-readable dates are
both supported. Each page contains `slug`, `title` and `nav` strings.
The five unique slugs are `index`, `data-handling`, `security`, `faq` and
`support`; list order controls navigation order.

Each `content/<slug>.md` becomes `<slug>.html`. Use exactly one Markdown H1 per
page. Page titles are browser metadata, not additional H1s. Markdown tables are
supported and wrapped in keyboard-focusable horizontal scroll regions. Raw HTML
in Markdown is displayed as text, not executed. Link to the output `.html`
filenames rather than Markdown source paths.
Broken local link paths, root-relative paths and remote images fail the build.
External HTTP(S) and email hyperlinks remain available; they are not fetched
during the build.

Only those five pages and `assets/site.css`, `assets/site.js` and
`assets/data-flow.svg` enter the generated artifact. The asset allowlist is a
publication boundary, not a content sanitizer: review all three assets, including
SVG contents, before publication. Never add confidential material to this public
repository, whether or not the builder would copy it.

## Build Safety

Tests use temporary fixtures, not production documentation. They cover the
five-page contract, escaped metadata, disabled raw HTML, semantic markup,
relative links, table wrappers, deterministic builds and unsafe-input rejection.

The builder validates all inputs before writing. It rejects missing inputs,
invalid metadata, unsafe or duplicate slugs, symlinks, output/source collisions,
and unexpected existing artifact files. A successful build has exactly eight
files. It never recursively deletes a destination. Rebuilding the same artifact
is supported; for an unrelated or contaminated destination, choose a new empty
directory. Do not run concurrent builds into the same output directory.

A document-level meta Content Security Policy limits resources to local scripts,
styles and images and blocks network connections from the document. This is not
a claim that GitHub Pages sends custom security response headers, nor a statement
about the Meeting Pulse application's controls.

## Publication

The Pages workflow runs tests, builds, uploads only `_site`, and deploys using
official GitHub Pages actions. It runs on pushes to `main` and manual dispatch;
deployment is restricted to `main` and the `github-pages` environment. Build and
deployment permissions are separate, and checkout does not retain credentials.
Configure the repository's Pages source as **GitHub Actions**. Enable private
vulnerability reporting before publication.

Before publishing, review the entire repository and generated artifact, not just
the rendered pages. Keep documentation high-level: exclude private attachments,
source excerpts, internal addresses, operational instructions, credentials and
real meeting or participant identifiers. Do not imply legal, compliance or
provider approval without verified evidence. Keep `reviewed_on` accurate.

For security reports, follow [SECURITY.md](SECURITY.md). Do not include sensitive
information in public issues or pull requests.
