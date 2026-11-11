# Builds the file viewer pages of the showcase.
# Every Markdown document, source or text file and folder that the showcase or a document links to gets a readable
# page in showcase/pages/<path>.html (folders: showcase/pages/<path>/index.html): Markdown is rendered with its tables,
# code has line numbers and colours, and a link such as SearchService.java#L63 marks that line. The pages use the
# showcase style and script (assets/), so pictures open in the lightbox and "Show in File Explorer" works locally.
# Run again after a document changes:  python showcase/build_pages.py
import html
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_for_filename
from pygments.util import ClassNotFound

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "showcase" / "pages"
SEEDS = ["showcase/index.html", "showcase/index.vi.html", "README.md", "README.vi.md"] + sorted(
    p.relative_to(ROOT).as_posix() for p in (ROOT / "docs").glob("*.md"))
# A document X.md may have a Vietnamese translation X.vi.md next to it (same headings in the same order, same links).
# Both get a page with an EN/VI switch; the Vietnamese page takes the heading ids of the English one, so every
# #anchor works in both languages, and its links to other documents lead to their Vietnamese pages.
TEXT = {".md", ".java", ".js", ".mjs", ".py", ".sql", ".ddl", ".txt", ".css", ".tsv", ".csv", ".json", ".html",
        ".ps1", ".bat", ".properties", ".xml", ".yml", ".yaml", ".config", ".gitignore"}
SKIP_DIRS = {"node_modules", "target", "__pycache__", ".git"}
# not project sources (lecturer's material, archive, built essay, run-time data): links to them stay plain links
SKIP_TREES = ("De_bai", "Luu_tru", "Bai_nop", "app/data", "showcase/pages")
MAX_TEXT = 1_000_000

md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")


def kind(rel):
    p = ROOT / rel
    if p.is_dir():
        return "d"
    if p.is_file() and (p.suffix.lower() in TEXT or p.name in TEXT) and p.stat().st_size <= MAX_TEXT:
        return "f"
    return None


def page_of(rel, k):
    """Path of the viewer page of a project path, relative to the project folder."""
    return f"showcase/pages/{rel}/index.html" if k == "d" else f"showcase/pages/{rel}.html"


def url(from_page, target):
    """Relative URL from one project file to another (both relative to the project folder)."""
    r = os.path.relpath(ROOT / target, (ROOT / from_page).parent).replace(os.sep, "/")
    return quote(r, safe="/._-~")


def resolve(base_file, href):
    """Project path that href (written in base_file) points to, or None if it leaves the project."""
    parts = urlsplit(href)
    if parts.scheme or parts.netloc or not parts.path:
        return None, ""
    target = (ROOT / base_file).parent / unquote(parts.path)
    try:
        rel = Path(os.path.normpath(target)).relative_to(ROOT).as_posix()
    except ValueError:
        return None, ""
    return rel, ("#" + parts.fragment if parts.fragment else "")


def links_in(rel, text):
    if rel.endswith(".md"):
        text = md.render(text)
    return re.findall(r'(?:href|src)="([^"]+)"', text)


def slug(text, seen):
    s = re.sub(r"[^\w\- ]", "", text.strip().lower(), flags=re.U).replace(" ", "-")
    n = seen.get(s, 0)
    seen[s] = n + 1
    return s if n == 0 else f"{s}-{n}"


# ---------------------------------------------------------------- collect everything that needs a page
pages = {}
queue = [s for s in SEEDS if (ROOT / s).exists()]
seen = set()
while queue:
    rel = queue.pop(0)
    if rel in seen:
        continue
    seen.add(rel)
    if any(rel == t or rel.startswith(t + "/") for t in SKIP_TREES) or not (ROOT / rel).exists():
        continue
    k = kind(rel)
    if rel.startswith("showcase/index"):
        k = "seed"
    elif k is None:
        continue
    else:
        pages[rel] = k
    if k == "d":
        for child in sorted((ROOT / rel).iterdir()):
            if child.name not in SKIP_DIRS and not child.name.startswith("."):
                queue.append(child.relative_to(ROOT).as_posix())
    elif rel.endswith(".md") or k == "seed":
        for href in links_in(rel, (ROOT / rel).read_text(encoding="utf-8")):
            target, _ = resolve(rel, href)
            if target and not target.startswith("showcase/pages"):
                queue.append(target)

# ---------------------------------------------------------------- page frame


def is_vi(rel):
    return rel.endswith(".vi.md")


def english_of(rel):
    return rel[:-6] + ".md" if is_vi(rel) else rel


def vietnamese_of(rel):
    """The Vietnamese twin of a document, if it has a page."""
    vi = rel[:-3] + ".vi.md" if rel.endswith(".md") and not is_vi(rel) else None
    return vi if vi in pages else None


def frame(rel, k, body, extra_css=""):
    me = page_of(rel, k)
    up = url(me, "")
    up = "" if up == "." else up.rstrip("/") + "/"
    name = rel.rsplit("/", 1)[-1]
    folder = rel.rsplit("/", 1)[0] + "/" if "/" in rel else ""
    lang = "vi" if is_vi(rel) else "en"
    switch = ""
    en, vi = english_of(rel), vietnamese_of(english_of(rel))
    if vi:   # a document in two languages
        cur = ' aria-current="page"'
        switch = (f'<span class="lang vlang" aria-label="Language"><a href="{url(me, page_of(en, "f"))}" lang="en"'
                  f'{cur if lang == "en" else ""}>EN</a><a href="{url(me, page_of(vi, "f"))}" lang="vi"'
                  f'{cur if lang == "vi" else ""}>VI</a></span>')
    # no button to the raw file (a browser shows Markdown and code as plain text); online the page offers GitHub
    github = f'<a class="vbtn" data-github="{html.escape(rel)}" hidden data-i18n="github">View on GitHub</a>'
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(name)} · ABC Online Shop</title>
<link rel="stylesheet" href="{up}app/src/main/resources/static/fonts/fonts.css">
<link rel="stylesheet" href="{up}showcase/assets/showcase.css">{extra_css}
<script src="{up}showcase/pages/manifest.js" defer></script>
<script src="{up}showcase/assets/showcase.js" defer></script>
</head>
<body class="viewer" data-file="{html.escape(rel)}">
<header class="vbar">
  <a class="vback" href="{up}showcase/index.html" data-i18n="back">← Showcase</a>
  <span class="vpath">{html.escape(folder)}<b>{html.escape(name)}{"/" if k == "d" else ""}</b></span>
  <span class="vactions">{switch}
    <button type="button" class="vbtn local-only" data-reveal="{html.escape(rel)}" data-i18n="reveal">Show in File Explorer</button>
    {github}
  </span>
</header>
{body}
</body>
</html>
"""


def fix_links(rel, k, rendered):
    """Point the links of a rendered document to the viewer pages (or to the original files) from its new place."""
    me = page_of(rel, k)

    def sub(m):
        attr, href = m.group(1), html.unescape(m.group(2))
        if href.startswith("#"):
            return m.group(0)
        target, frag = resolve(rel, href)
        if target is None:
            return m.group(0)
        if attr == "href" and is_vi(rel) and vietnamese_of(target):   # Vietnamese documents lead to Vietnamese ones
            target = vietnamese_of(target)
        if attr == "href" and target in pages:
            return f'{attr}="{url(me, page_of(target, pages[target]))}{html.escape(frag)}"'
        return f'{attr}="{url(me, target)}{html.escape(frag)}"'

    return re.sub(r'(href|src)="([^"]+)"', sub, rendered)


def heading_ids(rel):
    tokens = md.parse((ROOT / rel).read_text(encoding="utf-8"))
    seen = {}
    return [slug(tokens[i + 1].content, seen) for i, tok in enumerate(tokens) if tok.type == "heading_open"]


def markdown_page(rel):
    tokens = md.parse((ROOT / rel).read_text(encoding="utf-8"))
    ids = heading_ids(rel)
    if is_vi(rel):
        english = heading_ids(english_of(rel))
        if len(english) == len(ids):
            ids = english
        else:
            print(f"WARNING {rel}: {len(ids)} headings, the English document has {len(english)}; anchors differ")
    n = 0
    for tok in tokens:
        if tok.type == "heading_open":
            tok.attrSet("id", ids[n])
            n += 1
    body = md.renderer.render(tokens, md.options, {})
    body = re.sub(r"<table>", '<div class="tablewrap"><table>', body).replace("</table>", "</table></div>")
    body = re.sub(r'(<img [^>]*src="([^"]+)"[^>]*>)', r'<a href="\2">\1</a>', body)
    return frame(rel, "f", f'<main class="doc">\n{fix_links(rel, "f", body)}</main>')


FORMATTER = HtmlFormatter(nowrap=True)


def code_page(rel):
    data = (ROOT / rel).read_bytes()
    text = data.decode("utf-8", errors="replace")
    try:
        lexer = get_lexer_for_filename(rel, stripnl=False, ensurenl=False)
    except ClassNotFound:
        lexer = TextLexer(stripnl=False, ensurenl=False)
    src_lines = text.split("\n")
    if src_lines and src_lines[-1] == "":
        src_lines.pop()
    out = highlight(text, lexer, FORMATTER).split("\n")
    if out and out[-1] == "":
        out.pop()
    if len(out) != len(src_lines):  # never shift the line numbers: fall back to plain text
        out = [html.escape(s) for s in src_lines]
    rows = "\n".join(f'<div class="ln" id="L{i}"><a href="#L{i}">{i}</a><span>{line or " "}</span></div>'
                     for i, line in enumerate(out, 1))
    info = (f'<span data-num="{len(out)}" data-i18n="lines">{len(out)} lines</span> · {len(data):,} bytes · '
            f'{html.escape(lexer.name)}')
    body = f'<div class="codewrap"><p class="codeinfo">{info}</p><div class="code">\n{rows}\n</div></div>'
    css = f'\n<link rel="stylesheet" href="{url(page_of(rel, "f"), "showcase/assets/code.css")}">'
    return frame(rel, "f", body, css)


def folder_page(rel):
    me = page_of(rel, "d")
    items = []
    children = sorted((ROOT / rel).iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    for child in children:
        crel = child.relative_to(ROOT).as_posix()
        if child.name in SKIP_DIRS or child.name.startswith(".") or any(crel == t or crel.startswith(t + "/") for t in SKIP_TREES):
            continue
        if child.is_dir():
            n = sum(1 for _ in child.rglob("*") if _.is_file())
            href = url(me, page_of(crel, "d")) if crel in pages else url(me, crel)
            size = f'<span data-num="{n}" data-i18n="files">{n} files</span>'
            label = child.name + "/"
        else:
            href = url(me, page_of(crel, "f")) if crel in pages else url(me, crel)
            size, label = f"{child.stat().st_size:,} bytes", child.name
        items.append(f'<tr><td><a href="{href}">{html.escape(label)}</a></td><td class="note">{size}</td></tr>')
    body = (f'<main class="doc"><h1>{html.escape(rel)}/</h1>'
            f'<div class="tablewrap"><table><tr><th data-i18n="name">Name</th><th data-i18n="size">Size</th></tr>'
            f'{"".join(items)}</table></div></main>')
    return frame(rel, "d", body)


# ---------------------------------------------------------------- write
written = 0
for rel, k in pages.items():
    target = ROOT / page_of(rel, k)
    target.parent.mkdir(parents=True, exist_ok=True)
    page = folder_page(rel) if k == "d" else markdown_page(rel) if rel.endswith(".md") else code_page(rel)
    target.write_text(page, encoding="utf-8", newline="\n")
    written += 1

entries = ",\n".join(f'  "{rel}": "{k}"' for rel, k in sorted(pages.items()))
(OUT / "manifest.js").write_text(
    "// Made by showcase/build_pages.py: project paths that have a viewer page (f = file, d = folder).\n"
    f"window.ABC_PAGES = {{\n{entries}\n}};\n", encoding="utf-8", newline="\n")
(ROOT / "showcase" / "assets" / "code.css").write_text(
    "/* Made by showcase/build_pages.py from the Pygments style 'friendly' (colours of the code viewer). */\n"
    + HtmlFormatter(style="friendly").get_style_defs(".code").replace("background: #f0f0f0", "background: transparent")
    + "\n", encoding="utf-8", newline="\n")
current = {ROOT / page_of(rel, k) for rel, k in pages.items()} | {OUT / "manifest.js"}
stale = [p for p in OUT.rglob("*.html") if p not in current]
if stale:
    print(f"{len(stale)} old pages in showcase/pages are no longer linked (not deleted), e.g. {stale[0].relative_to(ROOT)}")
counts = {}
for rel, k in pages.items():
    key = "folder" if k == "d" else Path(rel).suffix or Path(rel).name
    counts[key] = counts.get(key, 0) + 1
print(f"{written} pages in showcase/pages:", ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
