#!/usr/bin/env python3
"""QA checks for the qtan-tran.github.io static site.

Usage:
    python3 qa/check_site.py /path/to/site           # offline checks
    python3 qa/check_site.py /path/to/site --online  # + external link check

Checks:
  1. HTML tag balance (void elements respected).
  2. Internal links, stylesheet hrefs and #anchors resolve.
  3. publications.bib <-> index.html cross-check via data-key attributes.
  4. Suspicious characters (mojibake, replacement chars, control chars,
     markdown leakage).
  5. --online: HTTP status of every external link.

Exit code 1 on any ERROR, 0 otherwise. WARN lines do not fail the run.
Standard library only.
"""

import html.parser
import re
import sys
import urllib.request
import urllib.error
import pathlib

# Hosts known to block automated requests (Cloudflare etc.). A 403 from
# these is reported as WARN ("bot-blocked, check manually"), not an error.
BOT_BLOCKED_HOSTS = {
    "taylorfrancis.com",
    "tandfonline.com",
    "medium.com",
}

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class TagChecker(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_ELEMENTS:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in VOID_ELEMENTS:
            return
        if not self.stack:
            self.errors.append(f"unexpected </{tag}> at line {self.getpos()[0]}")
            return
        open_tag, pos = self.stack.pop()
        if open_tag != tag:
            self.errors.append(
                f"mismatch: <{open_tag}> (line {pos[0]}) closed by </{tag}> "
                f"at line {self.getpos()[0]}")


class LinkCollector(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []   # (href_or_src, line)
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.links.append((value.strip(), self.getpos()[0]))
            if name == "id" and value:
                self.ids.add(value.strip())


def check_site(site: pathlib.Path, online: bool):
    errors, warnings = [], []
    html_files = sorted(site.rglob("*.html"))
    if not html_files:
        errors.append("no HTML files found")

    all_external = {}

    for path in html_files:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(site)

        # 1. tag balance
        tc = TagChecker()
        tc.feed(text)
        tc.close()
        leftover = [t for t, _ in tc.stack if t != "html"]
        for tag, pos in tc.stack:
            errors.append(f"{rel}: unclosed <{tag}> from line {pos[0]}")
        for msg in tc.errors:
            errors.append(f"{rel}: {msg}")

        # 2. links + anchors
        lc = LinkCollector()
        lc.feed(text)
        for href, line in lc.links:
            if href.startswith(("mailto:", "tel:")):
                continue
            if href.startswith("#"):
                if href[1:] not in lc.ids:
                    errors.append(f"{rel}:{line}: anchor {href} has no matching id")
                continue
            if re.match(r"^[a-z][a-z0-9+.-]*://", href):
                all_external.setdefault(href, []).append(f"{rel}:{line}")
                continue
            # relative link
            target_part, _, frag = href.partition("#")
            if target_part:
                target = (path.parent / target_part).resolve()
                if not target.exists():
                    errors.append(f"{rel}:{line}: missing local target {target_part}")
                    continue
                if frag:
                    target_text = target.read_text(encoding="utf-8")
                    ids = set(re.findall(r'id="([^"]+)"', target_text))
                    if frag not in ids:
                        errors.append(
                            f"{rel}:{line}: anchor #{frag} missing in {target_part}")
            elif frag and frag not in lc.ids:
                errors.append(f"{rel}:{line}: anchor #{frag} has no matching id")

        # 4. suspicious characters
        for pat, what in [
            ("\ufffd", "replacement character U+FFFD"),
            ("Ã", "mojibake 'A-tilde' (broken UTF-8)"),
            ("â€", "mojibake 'a-ellipsis' (broken UTF-8)"),
            ("](", "markdown link leakage ']' + '('"),
            ("**", "markdown bold leakage '**'"),
        ]:
            for m in re.finditer(re.escape(pat), text):
                warnings.append(
                    f"{rel}: line {text[:m.start()].count(chr(10)) + 1}: {what}")
        for ch in text:
            if ord(ch) < 32 and ch not in "\t\n\r":
                errors.append(f"{rel}: control character U+{ord(ch):04X}")

    # 3. bib cross-check
    bib = site / "publications.bib"
    index = site / "index.html"
    if bib.exists() and index.exists():
        bib_text = bib.read_text(encoding="utf-8")
        bib_keys = re.findall(r"^@\w+\{([^,\s]+),", bib_text, re.M)
        html_text = index.read_text(encoding="utf-8")
        html_keys = re.findall(r'data-key="([^"]+)"', html_text)
        missing = [k for k in bib_keys if k not in html_keys]
        extra = [k for k in html_keys if k not in bib_keys]
        for k in missing:
            errors.append(f"publications.bib entry not rendered in index.html: {k}")
        for k in extra:
            errors.append(f"index.html data-key not in publications.bib: {k}")
        dupes = {k for k in bib_keys if bib_keys.count(k) > 1}
        for k in dupes:
            errors.append(f"publications.bib: duplicate entry key {k}")
    else:
        warnings.append("publications.bib or index.html not found; skipped bib check")

    # 5. online check
    if online:
        ua = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120 Safari/537.36")
        for url in sorted(all_external):
            req = urllib.request.Request(url, headers={"User-Agent": ua})
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    status = resp.status
                    final = resp.url
            except urllib.error.HTTPError as e:
                status = e.code
                final = getattr(e, "url", None) or url
            except Exception as e:  # noqa: BLE001
                errors.append(f"link {url}: request failed ({e})")
                continue
            host = urllib.request.urlparse(final).hostname or ""
            if status == 200:
                print(f"  OK   {url}")
            elif any(host.endswith(h) for h in BOT_BLOCKED_HOSTS) and status in (403, 503):
                warnings.append(
                    f"link {url}: {status} from bot-blocking host {host} "
                    f"(check manually in a browser)")
            else:
                errors.append(f"link {url}: HTTP {status} (final: {final})")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    site = pathlib.Path(sys.argv[1]).resolve()
    online = "--online" in sys.argv[2:]
    print(f"QA checks on {site}{' (online)' if online else ''}")
    errors, warnings = check_site(site, online)
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(warnings)} warning(s), {len(errors)} error(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
