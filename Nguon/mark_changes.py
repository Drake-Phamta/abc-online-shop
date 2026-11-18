"""Marks what changed since the previous submission with a change bar: a blue line in the left margin next to every
paragraph, heading and caption of the new essay that contains a sentence the old essay does not have. A table or a
figure is marked at its caption (and the picture beside it) when it is new or mostly changed. The text stays black.
Figure, table, section and chapter numbers are ignored in the comparison, because a renumbering alone is no change.
Code listings and the table of contents are not marked.

usage: python mark_changes.py <new.docx> <old.docx> [--dry]   (the new file is changed in place unless --dry)
"""
import re
import sys

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

BAR_COLOR = "1F5FA8"
SENT = re.compile(r"(?<=[.!?:;])\s+(?=[A-Z0-9\"(«])")
AFTER_PBDR = ("w:shd", "w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap", "w:overflowPunct",
              "w:topLinePunct", "w:autoSpaceDE", "w:autoSpaceDN", "w:bidi", "w:adjustRightInd", "w:snapToGrid",
              "w:spacing", "w:ind", "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap", "w:jc",
              "w:textDirection", "w:textAlignment", "w:textboxTightWrap", "w:outlineLvl", "w:divId", "w:cnfStyle",
              "w:rPr", "w:sectPr", "w:pPrChange")


def norm(s):
    s = s.lower()
    s = re.sub(r"\b(figures?|tables?|sections?|chapters?)\s+\d+(\.\d+)*(\s+(to|and)\s+\d+(\.\d+)*)?", r"\1 #", s)
    s = re.sub(r"[“”\"'’‘]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip(" .;:,")


def all_text(doc):
    parts = [p.text for p in doc.paragraphs]
    for t in doc.tables:
        for row in t.rows:
            parts += [c.text for c in row.cells]
    return " ".join(parts)


def is_skipped(p):
    fonts = {r.font.name for r in p.runs if r.text.strip()}
    return (bool(fonts) and fonts <= {"Consolas", "Courier New"}) or (p.style is not None and "TOC" in p.style.name)


def changed_chars(text, old):
    total = changed = 0
    for sent in SENT.split(text):
        n = norm(sent)
        total += len(sent)
        if n and len(n) > 3 and n not in old:
            changed += len(sent)
    return changed, total


def bar(p):
    pPr = p._p.get_or_add_pPr()
    if pPr.find(qn("w:pBdr")) is not None:
        return
    pbdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    for k, v in (("w:val", "single"), ("w:sz", "18"), ("w:space", "10"), ("w:color", BAR_COLOR)):
        left.set(qn(k), v)
    pbdr.append(left)
    pPr.insert_element_before(pbdr, *AFTER_PBDR)


def main():
    new_path, old_path = sys.argv[1], sys.argv[2]
    dry = "--dry" in sys.argv
    old = norm(all_text(Document(old_path)))
    doc = Document(new_path)
    body = doc.element.body
    marked = paragraphs = 0
    total_chars = changed_total = 0
    blocks = list(body.iterchildren())
    for i, el in enumerate(blocks):
        if el.tag == qn("w:p"):
            p = Paragraph(el, doc)
            text = p.text
            if not text.strip():
                # a picture: marked when the caption under it is marked
                if el.xpath(".//w:drawing") and i + 1 < len(blocks) and blocks[i + 1].tag == qn("w:p"):
                    cap = Paragraph(blocks[i + 1], doc)
                    c, t = changed_chars(cap.text, old)
                    if t and c and not dry:
                        bar(p)
                continue
            if is_skipped(p):
                continue
            c, t = changed_chars(text, old)
            total_chars += t
            changed_total += c
            if c:
                paragraphs += 1
                if not dry:
                    bar(p)
                    marked += 1
        elif el.tag == qn("w:tbl"):
            table = Table(el, doc)
            c = t = 0
            for row in table.rows:
                for cell in row.cells:
                    cc, tt = changed_chars(cell.text, old)
                    c, t = c + cc, t + tt
            total_chars += t
            changed_total += c
            if t and c / t >= 0.3:
                prev = el.getprevious()
                if prev is not None and prev.tag == qn("w:p") and not dry:
                    bar(Paragraph(prev, doc))
                    marked += 1
    print(f"changed text: {changed_total} of {total_chars} characters ({100 * changed_total / max(total_chars, 1):.0f} %), "
          f"{paragraphs} paragraphs")
    if not dry:
        doc.save(new_path)
        print(f"change bars on {marked} paragraphs and captions:", new_path)


if __name__ == "__main__":
    main()
