# -*- coding: utf-8 -*-
"""Course essay (tieu luan) - Information Systems Analysis and Design, in English (python-docx).

    python build_tieuluan.py <07_Tieu_luan folder> <output .docx>

Content lives in front.py, ch1.py ... ch5.py, back.py (same folder) and is executed in this module's namespace,
so every chapter file can use the helpers below. Layout rules are those of the earlier reports: Times New Roman 13,
line spacing 1.2, figures/tables numbered per chapter and referenced in the text, code blocks never split.
"""
import datetime
import os
import re
import sys

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r"C:\a3cap\toolkit\report")
from omml import frac, limlow, numbered, r, sub, subsup  # noqa: E402,F401

ROOT = sys.argv[1]
OUT = sys.argv[2]
FIGDIR = os.path.join(ROOT, "Anh_bieu_do")

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin, sec.right_margin = Cm(2.5), Cm(2)
sec.top_margin, sec.bottom_margin = Cm(2), Cm(2)

st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(13)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
_lang = OxmlElement("w:lang")
_lang.set(qn("w:val"), "en-US")
st.element.rPr.append(_lang)
st.paragraph_format.space_after = Pt(4)
st.paragraph_format.line_spacing = 1.25

for name, size, before, after in (("Heading 1", 16, 0, 10), ("Heading 2", 13.5, 10, 4), ("Heading 3", 13, 6, 2)):
    hs = doc.styles[name]
    hs.font.name = "Times New Roman"
    hs.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    hs.element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    hs.element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    for theme_attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        hs.element.rPr.rFonts.attrib.pop(qn(theme_attr), None)
    hs.font.size = Pt(size)
    hs.font.bold = True
    hs.font.italic = False
    hs.font.color.rgb = RGBColor(0, 0, 0)
    pf = hs.paragraph_format
    pf.space_before, pf.space_after = Pt(before), Pt(after)
    pf.keep_with_next = True
    pf.line_spacing = 1.15

J = WD_ALIGN_PARAGRAPH.JUSTIFY
C = WD_ALIGN_PARAGRAPH.CENTER
L = WD_ALIGN_PARAGRAPH.LEFT
NB = "\u00a0"
CH = [0]            # current chapter number (0 = front matter)
FIG = [0]
TAB = [0]
PENDING = [0]
FIGURES, TABLES = [], []

MARK = re.compile(r"(?<![\w])([A-Za-zλαβγ])_\{([^}]*)\}")
KEEP_NUM = re.compile(r"\b(Figures?|Tables?|messages?|sections?|Section|Chapters?|equations?|Task|Steps?) (\d)")
BOLD = re.compile(r"\*\*(.+?)\*\*")


def take_pending(pf, before=0):
    if PENDING[0] or before:
        pf.space_before = Pt(max(before, PENDING[0]))
    PENDING[0] = 0


def runs(para, text, bold=False, italic=False, size=None, mono=False):
    text = KEEP_NUM.sub(lambda m: m.group(1) + NB + m.group(2), text)
    text = text.replace(" → ", NB + "→ ")
    # **bold** spans, then S_{x} subscripts inside each span
    spans, pos = [], 0
    for m in BOLD.finditer(text):
        spans.append((text[pos:m.start()], bold))
        spans.append((m.group(1), True))
        pos = m.end()
    spans.append((text[pos:], bold))
    for span, b in spans:
        pieces, pos = [], 0
        for m in MARK.finditer(span):
            pieces.append((span[pos:m.start()], italic, False))
            pieces.append((m.group(1), True, False))
            pieces.append((m.group(2), len(m.group(2)) == 1, True))
            pos = m.end()
        pieces.append((span[pos:], italic, False))
        for chunk, ital, is_sub in pieces:
            if not chunk:
                continue
            run = para.add_run(chunk)
            run.bold, run.italic = b, ital
            run.font.subscript = is_sub or None
            if size:
                run.font.size = Pt(size)
            if mono:
                run.font.name = "Consolas"
                run.font.size = Pt(11)
                run._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")


def p(text="", bold=False, italic=False, size=None, align=J, before=0, after=None, indent=None, keep=False):
    para = doc.add_paragraph()
    para.alignment = align
    pf = para.paragraph_format
    take_pending(pf, before)
    if after is not None:
        pf.space_after = Pt(after)
    if indent is not None:
        pf.left_indent = Cm(indent)
    if keep:
        pf.keep_with_next = True
    runs(para, text, bold=bold, italic=italic, size=size)
    return para


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def chapter(title):
    """Start a numbered chapter on a new page: 'CHAPTER n. TITLE' as Heading 1."""
    CH[0] += 1
    FIG[0] = TAB[0] = 0
    h = doc.add_heading(f"CHAPTER {CH[0]}. {title.upper()}", level=1)
    h.alignment = L
    # "page break before" on the heading, not a paragraph holding a break: when the previous page is exactly full,
    # that paragraph lands on a page of its own and leaves it empty
    h.paragraph_format.page_break_before = True


def unnumbered(title, new_page=True):
    h = doc.add_heading(title, level=1)
    h.alignment = L
    if new_page:
        h.paragraph_format.page_break_before = True


def h2(text):
    PENDING[0] = 0
    doc.add_heading(text, level=2)


def h3(text):
    PENDING[0] = 0
    doc.add_heading(text, level=3)


def dash(text):
    para = p("- " + text)
    pf = para.paragraph_format
    pf.left_indent = Cm(0.6)
    pf.first_line_indent = Cm(-0.4)
    pf.space_after = Pt(2)
    return para


def num(n, text):
    para = p(f"{n}. " + text)
    pf = para.paragraph_format
    pf.left_indent = Cm(0.7)
    pf.first_line_indent = Cm(-0.5)
    pf.space_after = Pt(2)
    return para


def _label(kind):
    if kind == "fig":
        FIG[0] += 1
        return f"{CH[0]}.{FIG[0]}" if CH[0] else str(FIG[0])
    TAB[0] += 1
    return f"{CH[0]}.{TAB[0]}" if CH[0] else str(TAB[0])


def figure(name, caption, width_cm=16, max_h_cm=21):
    # "vp/png/R2.png", "docs/evidence/e2e/..": the project's own files, one copy for the essay and the project;
    # a plain name is an older figure kept in Anh_bieu_do
    path = os.path.join(ROOT, *name.split("/")) if "/" in name else os.path.join(FIGDIR, name)
    with Image.open(path) as im:
        w, h = im.size
    if h / w * width_cm > max_h_cm:
        width_cm = max_h_cm * w / h
    # Word's PDF export keeps a picture up to about 270 ppi of its printed size and lowers a denser one to 200 ppi
    # (measured: 270 kept, 290 lowered). A large diagram therefore goes in at 265 ppi, scaled here with Lanczos, which
    # keeps a third more detail than Word's 200 ppi for the small text when the reader zooms in.
    max_px = int(width_cm / 2.54 * 265)
    if w > max_px:
        import hashlib
        cache = os.path.join(os.path.dirname(os.path.abspath(OUT)), "_img290")
        os.makedirs(cache, exist_ok=True)
        scaled = os.path.join(cache, hashlib.md5(f"{path}|{max_px}|{os.path.getmtime(path)}".encode()).hexdigest() + ".png")
        if not os.path.exists(scaled):
            with Image.open(path) as im:
                im.convert("RGB").resize((max_px, round(h * max_px / w)), Image.LANCZOS).save(scaled, optimize=True)
        path = scaled
    para = doc.add_paragraph()
    para.alignment = C
    take_pending(para.paragraph_format, 4)
    para.paragraph_format.space_after = Pt(2)
    para.paragraph_format.keep_with_next = True
    para.add_run().add_picture(path, width=Cm(width_cm))
    lab = _label("fig")
    FIGURES.append((lab, caption))
    p(f"Figure {lab}. {caption}", italic=True, size=11, align=C, after=10)
    return lab


def table(caption, rows, widths, size=11, center_cols=(), merge_first=False, header=True):
    lab = None
    if caption:
        lab = _label("tab")
        TABLES.append((lab, caption))
        p(f"Table {lab}. {caption}", italic=True, size=11, align=C, after=2, keep=True, before=4)
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            cell.width = Cm(widths[j])
            cell.text = ""
            para = cell.paragraphs[0]
            para.paragraph_format.space_after = Pt(0)
            para.paragraph_format.line_spacing = 1.0
            if j in center_cols or (header and i == 0) or (merge_first and j == 0):
                para.alignment = C
            runs(para, val, bold=(header and i == 0), size=size)
            if header and i == 0:
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:fill"), "E7ECF3")
                cell._tc.get_or_add_tcPr().append(shd)
        if i < len(rows) - 1 and len(rows) <= 6:
            for cell in t.rows[i].cells:
                for para in cell.paragraphs:
                    para.paragraph_format.keep_with_next = True
        tr_pr = t.rows[i]._tr.get_or_add_trPr()
        tr_pr.append(tr_pr.makeelement(qn("w:cantSplit"), {}))
        if header and i == 0:
            tr_pr.append(tr_pr.makeelement(qn("w:tblHeader"), {}))
    if merge_first:
        i = 1
        while i < len(rows):
            j = i
            while j + 1 < len(rows) and rows[j + 1][0] == "":
                j += 1
            if j > i:
                merged = t.cell(i, 0).merge(t.cell(j, 0))
                for extra in merged.paragraphs[1:]:
                    extra._element.getparent().remove(extra._element)
                merged.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            i = j + 1
    PENDING[0] = 8
    return lab


def next_tab():
    """Label the next table will get (to reference it in the lead sentence)."""
    return f"{CH[0]}.{TAB[0] + 1}"


def next_fig():
    return f"{CH[0]}.{FIG[0] + 1}"


def code(text, size=9, indent=0.4):
    lines = text.rstrip("\n").split("\n")
    for i, line in enumerate(lines):
        para = doc.add_paragraph()
        para.alignment = L
        pf = para.paragraph_format
        pf.space_after = Pt(0)
        pf.space_before = Pt(0)
        if i == 0:
            take_pending(pf, 2)
        pf.line_spacing = 1.0
        pf.left_indent = Cm(indent)
        pf.keep_with_next = i < len(lines) - 1
        pf.keep_together = True
        run = para.add_run(line if line else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(size)
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
    PENDING[0] = 8


def eq(parts, number, keep=False):
    para = doc.add_paragraph()
    take_pending(para.paragraph_format, 2)
    para.paragraph_format.space_after = Pt(4)
    para.paragraph_format.keep_with_next = keep
    para._p.append(parse_xml(numbered(parts, number)))


def landscape():
    s = doc.add_section(WD_SECTION.NEW_PAGE)
    s.orientation = WD_ORIENT.LANDSCAPE
    s.page_width, s.page_height = Cm(29.7), Cm(21)
    s.left_margin = s.right_margin = Cm(1.5)
    s.top_margin = s.bottom_margin = Cm(1.5)


def portrait():
    s = doc.add_section(WD_SECTION.NEW_PAGE)
    s.orientation = WD_ORIENT.PORTRAIT
    s.page_width, s.page_height = Cm(21), Cm(29.7)
    s.left_margin, s.right_margin = Cm(2.5), Cm(2)
    s.top_margin, s.bottom_margin = Cm(2), Cm(2)


def field(para, instr, size=11):
    run = para.add_run()
    b = run._r.makeelement(qn("w:fldChar"), {qn("w:fldCharType"): "begin"})
    t = run._r.makeelement(qn("w:instrText"), {})
    t.text = instr
    t.set(qn("xml:space"), "preserve")
    sep = run._r.makeelement(qn("w:fldChar"), {qn("w:fldCharType"): "separate"})
    e = run._r.makeelement(qn("w:fldChar"), {qn("w:fldCharType"): "end"})
    for el in (b, t, sep):
        run._r.append(el)
    holder = para.add_run(" ")
    holder.font.size = Pt(size)
    run2 = para.add_run()
    run2._r.append(e)
    run.font.size = Pt(size)


def toc():
    para = doc.add_paragraph()
    field(para, 'TOC \\o "1-2" \\h \\z \\u', size=12)


def footer_setup():
    """Running header + centred page number on every section; the cover (first page) has neither."""
    for i, s in enumerate(doc.sections):
        s.different_first_page_header_footer = (i == 0)
        s.footer.is_linked_to_previous = False
        s.header.is_linked_to_previous = False
        fp = s.footer.paragraphs[0]
        fp.alignment = C
        field(fp, "PAGE", size=11)
        hp = s.header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hr = hp.add_run("Information Systems Analysis and Design: ABC Online Shop")
        hr.italic = True
        hr.font.size = Pt(9.5)
        hr.font.color.rgb = RGBColor(0x55, 0x55, 0x55)


# TL_PARTS / TL_CH_START / TL_TITLE build a single chapter as its own document (design_04: front_design, ch4, back_design)
PARTS = os.environ.get("TL_PARTS", "front.py,ch1.py,ch2.py,ch3.py,ch4.py,ch5.py,back.py").split(",")
CH[0] = int(os.environ.get("TL_CH_START", "0"))
for part in PARTS:
    path = os.path.join(HERE, part)
    if os.path.exists(path):
        exec(compile(open(path, encoding="utf-8").read(), path, "exec"))

footer_setup()
cp = doc.core_properties
cp.author = "Phạm Tuấn Anh"
cp.last_modified_by = "Phạm Tuấn Anh"
cp.title = os.environ.get("TL_TITLE", "From Requirements to Code: Analysis and Design of the ABC Online Shop with AI-Assisted Search")
cp.subject = "Information Systems Analysis and Design - course essay"
cp.comments = ""
cp.keywords = ""
cp.language = "en-US"
cp.revision = 1
cp.created = cp.modified = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None, microsecond=0)
APP_XML = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
           'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
           '<Template>Normal.dotm</Template><TotalTime>0</TotalTime><Application>Microsoft Office Word</Application>'
           '<DocSecurity>0</DocSecurity><ScaleCrop>false</ScaleCrop><LinksUpToDate>false</LinksUpToDate>'
           '<SharedDoc>false</SharedDoc><HyperlinksChanged>false</HyperlinksChanged><AppVersion>16.0000</AppVersion>'
           '</Properties>')
for rel in doc.part.package.rels.values():
    if rel.reltype == RT.EXTENDED_PROPERTIES:
        rel.target_part._blob = APP_XML.encode("utf-8")
# "Do not compress images in file": without it Word lowers the diagrams to 200 ppi when it saves and exports the PDF,
# and the small text of the large diagrams blurs when the reader zooms in. Placed where the settings schema expects it
# (after clrSchemeMapping, before the trailing elements), so Word opens the file without a repair.
_settings = doc.settings.element
if _settings.find(qn("w:doNotAutoCompressPictures")) is None:
    _flag = OxmlElement("w:doNotAutoCompressPictures")
    _after = [qn("w:forceUpgrade"), qn("w:captions"), qn("w:readModeInkLockDown"), qn("w:smartTagType"),
              qn("w:schemaLibrary"), qn("w:shapeDefaults"), qn("w:doNotEmbedSmartTags"), qn("w:decimalSymbol"), qn("w:listSeparator")]
    _next = next((c for c in _settings if c.tag in _after), None)
    if _next is not None:
        _next.addprevious(_flag)
    else:
        _settings.append(_flag)
doc.save(OUT)
print("saved", OUT, "| figures", len(FIGURES), "| tables", len(TABLES))
