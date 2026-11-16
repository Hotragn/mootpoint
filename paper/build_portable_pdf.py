"""Offline ReportLab fallback retaining the official template's main layout.

No browser, API, or desktop application required. Reads the same paper.md parser.
"""
from pathlib import Path
import html
import json
import re

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether, PageBreak
from build_docx import parse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE/'build'
FONTDIR = next((ROOT/'.venv/lib').glob('python*/site-packages/matplotlib/mpl-data/fonts/ttf'))
for name, file in [('Paper','DejaVuSerif.ttf'),('PaperBold','DejaVuSerif-Bold.ttf'),
                   ('PaperItalic','DejaVuSerif-Italic.ttf'),('PaperBoldItalic','DejaVuSerif-BoldItalic.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONTDIR/file)))
pdfmetrics.registerFontFamily('Paper',normal='Paper',bold='PaperBold',italic='PaperItalic',boldItalic='PaperBoldItalic')

def inline(text):
    t=html.escape(text)
    t=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',t)
    t=re.sub(r'(?<!\*)\*([^*]+)\*',r'<i>\1</i>',t)
    return re.sub(r'`([^`]+)`',r'\1',t)

ST = {
    'body': ParagraphStyle('body',fontName='Paper',fontSize=9.5,leading=12.25,spaceAfter=5.3,alignment=4),
    'h2': ParagraphStyle('h2',fontName='PaperBold',fontSize=13,leading=16,spaceBefore=10,spaceAfter=5,keepWithNext=True),
    'h3': ParagraphStyle('h3',fontName='PaperBold',fontSize=10.8,leading=14,spaceBefore=8,spaceAfter=4,keepWithNext=True),
    'cap': ParagraphStyle('cap',fontName='Paper',fontSize=8.2,leading=10.3,spaceAfter=6),
    'cell': ParagraphStyle('cell',fontName='Paper',fontSize=7.5,leading=9.5),
    'ref': ParagraphStyle('ref',fontName='Paper',fontSize=8.2,leading=10.5,spaceAfter=4,leftIndent=14,firstLineIndent=-14),
}

def para(text,kind='body'):
    return Paragraph(inline(text),ST[kind])

def img(path,width):
    im=Image(str((HERE/path).resolve()))
    im.drawHeight=width*im.imageHeight/im.imageWidth; im.drawWidth=width
    return im

class PaperDoc(SimpleDocTemplate):
    references_page=None
    def afterFlowable(self,flowable):
        if isinstance(flowable,Paragraph) and flowable.getPlainText()=='References':
            self.references_page=self.page

def footer(c,doc):
    c.saveState();c.setFont('Paper',9);c.drawCentredString(306,34,str(doc.page));c.restoreState()

def build():
    meta,blocks=parse((HERE/'paper.md').read_text());OUT.mkdir(exist_ok=True)
    title=Paragraph(html.escape(meta['TITLE'])+'<super>1</super>',ParagraphStyle('title',fontName='PaperBold',fontSize=16,leading=20,alignment=1))
    author=Paragraph('<b>'+html.escape(meta['AUTHOR'])+'</b><br/>'+html.escape(meta['AFFIL'])+'<br/><br/><b>With</b><br/>Apart Research',ParagraphStyle('author',fontName='Paper',fontSize=9.5,leading=13,alignment=1))
    abst=Paragraph(inline(meta['ABSTRACT']),ParagraphStyle('abstract',fontName='Paper',fontSize=9,leading=11.4,alignment=4))
    titlebox=Table([[title],[author],[Paragraph('<b>Abstract</b>',ParagraphStyle('ah',fontName='Paper',fontSize=11,alignment=1))],[abst]],colWidths=[468])
    titlebox.setStyle(TableStyle([('BOX',(0,0),(-1,-1),.6,colors.black),('LINEBELOW',(0,0),(-1,0),.6,colors.black),('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),14),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9)]))
    story=[titlebox,Spacer(1,7),para('1 Research conducted at the AI x Epistemics Research Sprint, November 2026.','cap')]
    for b in blocks:
        kind=b[0]
        if kind in ('h2','h3'):
            if b[1].startswith(('Appendix A.','Appendix D.','Appendix E.')):story.append(PageBreak())
            story.append(para(b[1],kind))
        elif kind=='p':story.append(para(b[1]))
        elif kind=='bullet':
            story.append(Paragraph('• '+inline(b[1]),ParagraphStyle('bullet',parent=ST['body'],leftIndent=10,firstLineIndent=-10)))
        elif kind=='figure':story.append(KeepTogether([Spacer(1,4),img(b[1],min(b[2]*72,450)),para(b[3],'cap')]))
        elif kind=='figrow':
            widths=[b[2]*72,b[4]*72];total=sum(widths);scale=min(1,456/total)
            row=Table([[img(b[1],widths[0]*scale),img(b[3],widths[1]*scale)]],colWidths=[widths[0]*scale+3,widths[1]*scale+3])
            row.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'BOTTOM'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0)]))
            story.append(KeepTogether([row,para(b[5],'cap')]))
        elif kind=='table':
            _,caption,rows=b;n=len(rows[0])
            if n==5:widths=[159,58,132,47,72]
            elif n==4:widths=[132,56,140,140]
            elif n==3:widths=[124,101,243]
            else:widths=[468/n]*n
            cells=[[para(('**'+t+'**') if i==0 else t,'cell') for t in r] for i,r in enumerate(rows)]
            table=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEABOVE',(0,0),(-1,0),.8,colors.black),('LINEBELOW',(0,0),(-1,0),.6,colors.black),('LINEBELOW',(0,-1),(-1,-1),.8,colors.black),('LINEBELOW',(0,1),(-1,-2),.25,colors.HexColor('#bbbbbb')),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
            cap=para(caption,'cap');cap.keepWithNext=True
            story.extend([cap,table,Spacer(1,7)])
        elif kind=='refs':story.extend(para(r,'ref') for r in b[1])
    doc=PaperDoc(str(OUT/'paper.pdf'),pagesize=(612,792),rightMargin=72,leftMargin=72,topMargin=62,bottomMargin=55,title=meta['TITLE'],author=meta['AUTHOR'])
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    assert doc.references_page and doc.references_page<=8, f'Main text over budget: references start p{doc.references_page}'
    print('PDF built; references start on page',doc.references_page)

if __name__=='__main__':build()
