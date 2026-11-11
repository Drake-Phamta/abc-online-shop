# -*- coding: utf-8 -*-
"""Every relative link of the documents and the showcase pages must open something.

Checks the Markdown files under docs/ and README-like files at the root, the showcase in both languages and the
viewer pages made by showcase/build_pages.py: the target file exists, a #L<n> anchor is inside the file, a #heading
anchor of a Markdown file names an existing heading, and an anchor into an HTML page names an existing id.
Usage: python tests/check_links.py      exit code = number of broken links
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent


def slug(heading):
    """GitHub style anchor of a Markdown heading."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def anchors(md):
    return {slug(m.group(1)) for m in re.finditer(r"^#{1,6} (.+)$", md.read_text(encoding="utf-8"), re.M)}


_ids = {}


def ids(page):
    if page not in _ids:
        _ids[page] = set(re.findall(r'\bid="([^"]+)"', page.read_text(encoding="utf-8")))
    return _ids[page]


def links(path):
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".html":
        return re.findall(r'(?:href|src)="([^"]+)"', text)
    return [m.group(1) or m.group(2) for m in re.finditer(r"\]\(<([^>]+)>\)|\]\(([^)\s]+)\)", text)]


def main():
    files = sorted((ROOT / "docs").glob("*.md")) + sorted(ROOT.glob("*.md"))
    files += [p for p in (ROOT / "showcase" / "index.html", ROOT / "showcase" / "index.vi.html") if p.exists()]
    files += sorted((ROOT / "showcase" / "pages").rglob("*.html"))
    broken, count = [], 0
    for f in files:
        for link in links(f):
            if re.match(r"^(https?:|mailto:|data:|javascript:)", link) or link.startswith("#") and f.suffix == ".html":
                continue
            count += 1
            target, _, frag = unquote(link).partition("#")
            p = (f.parent / target).resolve() if target else f
            if not p.exists():
                broken.append(f"{f.relative_to(ROOT)}: {link} (missing file)")
                continue
            if frag and p.suffix == ".html":
                if frag not in ids(p):
                    broken.append(f"{f.relative_to(ROOT)}: {link} (no element '{frag}')")
            elif frag.startswith("L") and frag[1:].isdigit():
                n = int(frag[1:])
                if p.is_file() and n > len(p.read_text(encoding="utf-8", errors="ignore").splitlines()):
                    broken.append(f"{f.relative_to(ROOT)}: {link} (line {n} past the end)")
            elif frag and p.suffix == ".md" and frag not in anchors(p):
                broken.append(f"{f.relative_to(ROOT)}: {link} (no heading '{frag}')")
    for b in broken:
        print("BROKEN " + b)
    print(f"{count} links checked, {len(broken)} broken")
    return len(broken)


if __name__ == "__main__":
    sys.exit(min(main(), 100))
