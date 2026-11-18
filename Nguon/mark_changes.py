"""Marks in red what changed since the previous submission, as the lecturer's reference essay does: every sentence of
the new essay (body text, lists, table cells, captions, headings) that the old essay does not contain is coloured red.
Figure, table, section and chapter numbers are ignored in the comparison, because the renumbering alone is no change.
Code listings and the table of contents are left black.

usage: python mark_changes.py <new.docx> <old.docx> [--dry]   (the new file is changed in place unless --dry)
"""
import copy
import re
import sys

from docx import Document
from docx.shared import RGBColor

RED = RGBColor(0xC0, 0x10, 0x10)
SENT = re.compile(r"(?<=[.!?:;])\s+(?=[A-Z0-9\"(«])")


def norm(s):
    s = s.lower()
    s = re.sub(r"\b(figures?|tables?|sections?|chapters?)\s+\d+(\.\d+)*(\s+(to|and)\s+\d+(\.\d+)*)?", r"\1 #", s)
    s = re.sub(r"[“”\"'’‘]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip(" .;:,")


def paragraphs(doc):
    for p in doc.paragraphs:
        yield p
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    yield p


def is_code(p):
    fonts = {r.font.name for r in p.runs if r.text.strip()}
    return bool(fonts) and fonts <= {"Consolas", "Courier New"} or (p.style is not None and "TOC" in p.style.name)


def spans(text, old):
    """(start, end, changed) for each sentence of text."""
    out, pos = [], 0
    for sent in SENT.split(text):
        start = text.index(sent, pos)
        end = start + len(sent)
        n = norm(sent)
        out.append((start, end, bool(n) and len(n) > 3 and n not in old))
        pos = end
    return out


def recolor(p, sp):
    """Splits the runs of p at the sentence borders and colours the changed parts."""
    pos = 0
    for r in list(p.runs):
        t = r.text
        a, b = pos, pos + len(t)
        pos = b
        if not t or r._r.xpath(".//w:drawing|.//w:fldChar|.//w:instrText"):
            continue
        cuts = sorted({a, b} | {s for s, e, c in sp if a < s < b} | {e for s, e, c in sp if a < e < b})
        pieces = []
        for x, y in zip(cuts, cuts[1:]):
            changed = any(c and s <= x and y <= e for s, e, c in sp)
            pieces.append((t[x - a:y - a], changed))
        if len(pieces) == 1:
            if pieces[0][1]:
                r.font.color.rgb = RED
            continue
        anchor = r._r
        for text, changed in pieces:
            el = copy.deepcopy(r._r)
            anchor.addnext(el)
            anchor = el
            from docx.text.run import Run
            nr = Run(el, p)
            nr.text = text
            if changed:
                nr.font.color.rgb = RED
        r._r.getparent().remove(r._r)


def main():
    new_path, old_path = sys.argv[1], sys.argv[2]
    dry = "--dry" in sys.argv
    old = norm(" ".join(p.text for p in paragraphs(Document(old_path))))
    doc = Document(new_path)
    total = changed = 0
    for p in paragraphs(doc):
        text = p.text
        if not text.strip() or is_code(p):
            continue
        sp = spans(text, old)
        for s, e, c in sp:
            total += e - s
            changed += (e - s) if c else 0
        if not dry and any(c for _, _, c in sp):
            before = p.text
            recolor(p, sp)
            if p.text != before:
                raise SystemExit("text changed while colouring: " + before[:80])
    print(f"changed text: {changed} of {total} characters ({100 * changed / max(total, 1):.0f} %)")
    if not dry:
        doc.save(new_path)
        print("marked", new_path)


if __name__ == "__main__":
    main()
