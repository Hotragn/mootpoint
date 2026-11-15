"""Render paper.md to PDF with headless Chrome, in the layout of the Apart template (title box, author block,
'With Apart Research', abstract box, sprint footnote, numbered sections). The official .docx is built by build_docx.py
from the same source.

Usage: paper/.venv/bin/python paper/build_pdf.py  ->  paper/build/paper.html, paper/build/paper.pdf
"""
import html
import re
import subprocess
import sys
from pathlib import Path

from build_docx import parse  # same parser as the .docx build

HERE = Path(__file__).resolve().parent
OUT = HERE / "build"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")

CSS = """
@page { size: Letter; margin: 1in; @bottom-center { content: counter(page); } }
body { font-family: Charter, 'Iowan Old Style', 'Times New Roman', serif; font-variant-numeric: lining-nums; font-size: 10.5pt; line-height: 1.32; color: #111; }
.hdr { border: 1px solid #222; margin-bottom: 14pt; }
.title { border-bottom: 1px solid #222; padding: 18pt 24pt; text-align: center; font-family: 'Old Standard TT', Charter, serif;
         font-size: 18pt; font-weight: bold; line-height: 1.25; }
.title sup { font-size: 9pt; font-weight: normal; }
.authors { display: flex; gap: 28pt; padding: 10pt 24pt 0 24pt; align-items: flex-start; }
.author { text-align: center; font-size: 10.5pt; }
.author b { display: block; }
.with { text-align: center; padding: 6pt 0 0 0; font-size: 10.5pt; }
.abs-h { text-align: center; font-weight: bold; font-size: 12pt; margin: 10pt 0 4pt 0; }
.abs { border: 1px solid #222; margin: 0 14pt 14pt 14pt; padding: 8pt 14pt; text-align: justify; font-size: 10pt; }
.fn { font-size: 8pt; color: #333; margin: -6pt 0 10pt 0; }
h2 { font-size: 14pt; margin: 14pt 0 4pt 0; page-break-after: avoid; }
h3 { font-size: 11.5pt; color: #434343; margin: 10pt 0 3pt 0; page-break-after: avoid; }
p { margin: 0 0 6pt 0; text-align: justify; }
ul { margin: 0 0 6pt 0; padding-left: 16pt; } li { margin-bottom: 3pt; text-align: justify; }
figure { margin: 8pt 0 10pt 0; page-break-inside: avoid; text-align: center; }
figure img { max-width: 100%; }
.tcap { page-break-after: avoid; }
figcaption, .tcap { font-size: 9pt; text-align: justify; line-height: 1.25; margin-top: 4pt; }
table { border-collapse: collapse; margin: 3pt auto 10pt auto; font-size: 8.8pt; page-break-inside: avoid; }
th, td { border-top: 1px solid #999; border-bottom: 1px solid #999; padding: 2.5pt 6pt; text-align: left; }
th { border-top: 1.5px solid #222; border-bottom: 1px solid #222; }
tr:last-child td { border-bottom: 1.5px solid #222; }
.refs p { font-size: 9.3pt; padding-left: 18pt; text-indent: -18pt; margin-bottom: 3pt; text-align: left; }
.appendix-break { page-break-before: always; }
"""


def inl(t):
    out = []
    for part in INLINE.split(t):
        if not part:
            continue
        e = html.escape(part, quote=False)
        if part.startswith("**"):
            out.append(f"<b>{html.escape(part[2:-2], quote=False)}</b>")
        elif part.startswith("`"):
            out.append(f"<code>{html.escape(part[1:-1], quote=False)}</code>")
        elif part.startswith("*"):
            out.append(f"<i>{html.escape(part[1:-1], quote=False)}</i>")
        else:
            out.append(e)
    return "".join(out)


def build():
    meta, blocks = parse((HERE / "paper.md").read_text())
    h = [f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(meta['TITLE'])}</title><style>{CSS}</style></head><body>",
         "<div class='hdr'>",
         f"<div class='title'>{html.escape(meta['TITLE'])}<sup>1</sup></div>",
         f"<div class='authors'><div class='author'><b>{html.escape(meta['AUTHOR'])}</b>{html.escape(meta['AFFIL'])}</div></div>",
         "<div class='with'><b>With</b><br>Apart Research</div>",
         "<div class='abs-h'>Abstract</div>",
         f"<div class='abs'>{inl(meta['ABSTRACT'])}</div></div>",
         "<div class='fn'><sup>1</sup> Research conducted at the AI x Epistemics Research Sprint, November 2026.</div>"]
    in_list = False
    for b in blocks:
        kind = b[0]
        if kind != "bullet" and in_list:
            h.append("</ul>"); in_list = False
        if kind == "h2":
            cls = " class='appendix-break'" if b[1].startswith("Appendix A") else ""
            h.append(f"<h2{cls}>{inl(b[1])}</h2>")
        elif kind == "h3":
            h.append(f"<h3>{inl(b[1])}</h3>")
        elif kind == "p":
            h.append(f"<p>{inl(b[1])}</p>")
        elif kind == "bullet":
            if not in_list:
                h.append("<ul>"); in_list = True
            h.append(f"<li>{inl(b[1])}</li>")
        elif kind == "figure":
            _, path, width, cap = b
            img = (HERE / path).resolve()
            assert img.exists(), img
            h.append(f"<figure><img src='{img.as_uri()}' style='width:{width}in'><figcaption>{inl(cap)}</figcaption></figure>")
        elif kind == "figrow":
            _, p1, w1, p2, w2, cap = b
            imgs = []
            for path, w in ((p1, w1), (p2, w2)):
                img = (HERE / path).resolve(); assert img.exists(), img
                imgs.append(f"<img src='{img.as_uri()}' style='width:{w}in'>")
            h.append(f"<figure><div style='display:flex;justify-content:center;align-items:flex-end;gap:6pt'>{''.join(imgs)}</div>"
                     f"<figcaption>{inl(cap)}</figcaption></figure>")
        elif kind == "table":
            _, cap, rows = b
            num, rest = cap.split(".", 1)
            h.append(f"<div class='tcap'><b>{html.escape(num)}.</b>{inl(rest)}</div><table>")
            h.append("<tr>" + "".join(f"<th>{inl(c)}</th>" for c in rows[0]) + "</tr>")
            for r in rows[1:]:
                h.append("<tr>" + "".join(f"<td>{inl(c)}</td>" for c in r) + "</tr>")
            h.append("</table>")
        elif kind == "refs":
            h.append("<div class='refs'>" + "".join(f"<p>{inl(r)}</p>" for r in b[1]) + "</div>")
    if in_list:
        h.append("</ul>")
    h.append("</body></html>")
    OUT.mkdir(exist_ok=True)
    (OUT / "paper.html").write_text("\n".join(h))
    pdf = OUT / "paper.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    f"--print-to-pdf={pdf}", (OUT / "paper.html").as_uri()], check=True, capture_output=True, timeout=120)
    assert pdf.exists() and pdf.stat().st_size > 50_000, "PDF not written"
    print("wrote", pdf)


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    build()
