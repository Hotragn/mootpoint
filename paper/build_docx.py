"""Build the paper in the official Apart template from paper.md.

Usage: paper/.venv/bin/python paper/build_docx.py  ->  paper/build/paper.docx
paper.md syntax: %TITLE/%AUTHOR/%AFFIL lines; %ABSTRACT ... %END; '# ' section (Heading 2); '## ' subsection
(Heading 3); '- ' bullet; %FIGURE path|width_in|caption; %FIGROW p1|w1|p2|w2|caption; %TABLE caption, then '| a | b |' rows, %END;
%REFS ... %END (one reference per line); inline **bold**, *italic*, `code`.
"""
import copy
import re
from pathlib import Path

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parents[1] / "claude" / "brainstorm" / "raw" / "template" / "apart_template.docx"
SRC, OUT = HERE / "paper.md", HERE / "build" / "paper.docx"
INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")


def add_inline(p, text, size=None):
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**"):
            r = p.add_run(part[2:-2]); r.bold = True
        elif part.startswith("`"):
            r = p.add_run(part[1:-1]); r.font.name = "Courier New"
        elif part.startswith("*"):
            r = p.add_run(part[1:-1]); r.italic = True
        else:
            r = p.add_run(part)
        if size:
            r.font.size = Pt(size)
    return p


def set_text_runs(par_el, mapping):
    """Replace exact w:t texts inside a paragraph element (keeps formatting)."""
    for t in par_el.iter(qn("w:t")):
        if t.text in mapping:
            t.text = mapping.pop(t.text)


def parse(src):
    meta, blocks, lines, i = {}, [], src.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("%TITLE ") or ln.startswith("%AUTHOR ") or ln.startswith("%AFFIL "):
            k, v = ln[1:].split(" ", 1); meta[k] = v
        elif ln in ("%ABSTRACT", "%REFS") or ln.startswith("%TABLE"):
            j = lines.index("%END", i)
            body = [x for x in lines[i + 1:j] if x.strip()]
            if ln == "%ABSTRACT":
                meta["ABSTRACT"] = " ".join(body)
            elif ln == "%REFS":
                blocks.append(("refs", body))
            else:
                blocks.append(("table", ln[len("%TABLE "):], [[c.strip() for c in r.strip().strip("|").split("|")] for r in body]))
            i = j
        elif ln.startswith("%FIGURE "):
            path, width, cap = ln[len("%FIGURE "):].split("|", 2)
            blocks.append(("figure", path, float(width), cap))
        elif ln.startswith("%FIGROW "):
            p1, w1, p2, w2, cap = ln[len("%FIGROW "):].split("|", 4)
            blocks.append(("figrow", p1, float(w1), p2, float(w2), cap))
        elif ln.startswith("## "):
            blocks.append(("h3", ln[3:]))
        elif ln.startswith("# "):
            blocks.append(("h2", ln[2:]))
        elif ln.startswith("- "):
            blocks.append(("bullet", ln[2:]))
        elif ln.strip():
            blocks.append(("p", ln))
        i += 1
    return meta, blocks


def main():
    meta, blocks = parse(SRC.read_text())
    d = docx.Document(TEMPLATE)
    body = d.element.body
    # --- header: title (keep the footnote run), author, abstract
    hdr = d.tables[0]
    tp = hdr.rows[0].cells[0].paragraphs[1]
    tp.runs[0].text = meta["TITLE"]
    tp.runs[0].font.size = Pt(18)
    cell = hdr.rows[1].cells[0]
    tc = cell.tables[0]._tbl.find(qn("w:tr")).find(qn("w:tc"))
    paras = list(tc.iter(qn("w:p")))
    set_text_runs(paras[1], {"Author name 1": meta["AUTHOR"], "Affiliation": meta["AFFIL"]})
    for p in paras[2:7]:
        p.getparent().remove(p)
    ab = cell.tables[1].rows[0].cells[0].paragraphs[0]
    for r in ab.runs[1:]:
        r._r.getparent().remove(r._r)
    ab.runs[0].text = meta["ABSTRACT"]
    ab.runs[0].italic = False
    # --- drop the guidance box and all template body after the header table
    children = list(body.iterchildren())
    start = children.index(hdr._tbl) + 1
    for el in children[start:]:
        if el.tag != qn("w:sectPr"):
            body.remove(el)
    # --- body
    for b in blocks:
        kind = b[0]
        if kind == "h2":
            d.add_paragraph(b[1], style="Heading 2")
        elif kind == "h3":
            d.add_paragraph(b[1], style="Heading 3")
        elif kind == "p":
            add_inline(d.add_paragraph(style="normal"), b[1]).paragraph_format.space_after = Pt(6)
        elif kind == "bullet":
            p = d.add_paragraph(style="normal")
            p.paragraph_format.left_indent, p.paragraph_format.first_line_indent = Inches(0.25), Inches(-0.15)
            p.paragraph_format.space_after = Pt(3)
            add_inline(p, "•  " + b[1])
        elif kind == "figure":
            _, path, width, cap = b
            img = (HERE / path).resolve()
            assert img.exists(), img
            p = d.add_paragraph(style="normal"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(str(img), width=Inches(width))
            c = add_inline(d.add_paragraph(style="normal"), cap, size=9)
            c.paragraph_format.space_after = Pt(10)
        elif kind == "figrow":
            _, p1, w1, p2, w2, cap = b
            p = d.add_paragraph(style="normal"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for path, w in ((p1, w1), (p2, w2)):
                img = (HERE / path).resolve(); assert img.exists(), img
                p.add_run().add_picture(str(img), width=Inches(w))
            add_inline(d.add_paragraph(style="normal"), cap, size=9).paragraph_format.space_after = Pt(10)
        elif kind == "table":
            _, cap, rows = b
            c = add_inline(d.add_paragraph(style="normal"), "**" + cap.split(".", 1)[0] + ".**" + cap.split(".", 1)[1], size=9)
            c.paragraph_format.space_after = Pt(3)
            t = d.add_table(rows=len(rows), cols=len(rows[0]))
            t.style = d.styles["Table Grid"] if "Table Grid" in [s.name for s in d.styles] else t.style
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            for ri, row in enumerate(rows):
                for ci, val in enumerate(row):
                    cp = t.cell(ri, ci).paragraphs[0]
                    add_inline(cp, f"**{val}**" if ri == 0 else val, size=8.5)
            d.add_paragraph(style="normal").paragraph_format.space_after = Pt(4)
        elif kind == "refs":
            for ref in b[1]:
                p = add_inline(d.add_paragraph(style="normal"), ref, size=9.5)
                p.paragraph_format.left_indent, p.paragraph_format.first_line_indent = Inches(0.3), Inches(-0.3)
                p.paragraph_format.space_after = Pt(3)
    OUT.parent.mkdir(exist_ok=True)
    d.save(OUT)
    words = len(meta["ABSTRACT"].split())
    assert 150 <= words <= 250, f"abstract has {words} words"
    print(f"wrote {OUT} ({len(blocks)} blocks; abstract {words} words)")


if __name__ == "__main__":
    main()
