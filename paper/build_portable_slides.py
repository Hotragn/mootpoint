"""Render the revised eight-slide narrative offline with ReportLab."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib import colors
from build_portable_pdf import ROOT, HERE, OUT, inline

W,H=960,540
BLUE='#0072B2'; ORANGE='#D55E00'

def build():
    OUT.mkdir(exist_ok=True)
    c=canvas.Canvas(str(OUT/'slides.pdf'),pagesize=(W,H))
    c.setTitle('MootPoint — Common Ground Is Not Neutral Ground')
    c.setAuthor('Hotragn Pettugani')
    def text(t,x,y,w=840,size=19,color='#222',bold=False):
        p=Paragraph(inline(t).replace('\n','<br/>'),ParagraphStyle('slide',fontName='PaperBold' if bold else 'Paper',fontSize=size,leading=size*1.32,textColor=colors.HexColor(color)))
        _,h=p.wrap(w,H);assert y-h>=45,(t,y,h)
        p.drawOn(c,x,y-h);return y-h
    def start(title,n):
        text(title,55,490,size=28,bold=True)
        c.setStrokeColor(colors.HexColor(BLUE));c.setLineWidth(2);c.line(55,433,905,433)
        c.setFont('Paper',9);c.setFillColor(colors.HexColor('#777'))
        c.drawString(55,24,'MootPoint · AI x Epistemics Research Sprint · November 2026')
        c.drawRightString(905,24,str(n))
    def picture(path,x,y,w,h):
        c.drawImage(str(path),x,y,width=w,height=h,preserveAspectRatio=True,anchor='c',mask='auto')

    start('Common Ground Is Not Neutral Ground',1)
    text('Opposed AI advocates disagree by silence',55,390,size=27,color=ORANGE)
    text('Can agreement across opposed requesters identify claims that overstate evidence?',55,300,size=25)
    text('A controlled benchmark study with a negative result, a rerun, and a disclosed validity audit.',55,210,size=20)
    text('Hotragn Pettugani · Independent Researcher\nWith Apart Research',55,110,size=15)
    c.showPage()
    start('The same evidence can produce different “facts”',2)
    text('At the sprint: one investigator described the same protest video prompted as an activist and as a prosecutor, producing opposing narratives.',55,393,size=22)
    text('**Tempting rule:** ask both sides, keep only claims repeated by both.',55,275,size=25,color=BLUE)
    text('**Test:** does this identify unwarranted claims better than two neutral repeat requests?',55,173,size=23)
    text('This tests an AI intersection filter—not Community Notes itself.',55,89,size=14,color='#555')
    c.showPage()
    start('MootPoint and two detector families',3)
    picture(HERE/'figures/fig1_method.png',55,150,850,270)
    text('100 synthetic cases · 76 held out · 4,486 neutral claims · 327 labelled unwarranted',55,123,size=17)
    text('Confirmatory analyses frozen before judging; later audits reported separately.',55,83,size=15,color='#555')
    c.showPage()
    start('Requester framing shifts the side taken',4)
    picture(ROOT/'analysis/figures/test/fig3_sidetaking.png',55,115,420,290)
    text('+0.145',520,355,w=370,size=45,color=ORANGE,bold=True)
    text('Requester-aligned share of side-taking\n95% CI [0.100, 0.191]',520,276,w=365,size=20)
    text('Rerun: +0.137\nFive-dossier exclusion: +0.137',520,170,w=365,size=18)
    c.showPage()
    start('Opposition shows no reliable advantage',5)
    text('**0.66** opposed agreement\n**0.70** neutral resampling\n**0.75** clerk + journalist',55,392,w=370,size=26,color=BLUE)
    picture(ROOT/'analysis/figures/test/fig4_mechanism.png',430,185,475,210)
    text('Original OPP − SC: −0.048 [−0.073, −0.024]\nRerun: −0.021 [−0.055, 0.015] — inconclusive',55,162,size=18)
    text('Opposed texts omit 39% of warranted claims (resamples: 29%); contradict 1.3%. Contradiction counting: 0.51.',55,100,size=16)
    c.showPage()
    start('Strong readers help prioritize evidence review',6)
    text('0.83–0.84',55,385,w=400,size=47,color=ORANGE,bold=True)
    text('AUROC from the neutral text alone\n0.91 with the file; weaker reader 0.67',55,300,w=420,size=19)
    text('Opposed context adds +0.035\n[0.012, 0.059]. A unique benefit\nof opposition is not established.',55,200,w=420,size=19)
    text('**Review 20% of claims**\nFind 77% of labelled errors\nBut 72% of flags are warranted.',535,365,w=360,size=22)
    text('Flags are prompts to check the source—not verdicts.',535,190,w=350,size=23,color=ORANGE)
    c.showPage()
    start('Audit the benchmark, not just the detector',7)
    text('**Found:** five suspect dossiers, two meta-description claims, and GLM outputs exceeding the requested word limit.',55,395,size=22)
    text('**Sensitivity:** excluding all five dossiers leaves OPP − SC at −0.050 [−0.077, −0.025]; rerun −0.025 [−0.063, 0.014]. Original deficit also persists without GLM.',55,278,size=21)
    text('**AI review:** 99/100 labels; agreement 88/99 (κ 0.778) with judge 1, 80/99 (κ 0.603) with judge 2. Stratified sample; not human validation.',55,145,size=18)
    c.showPage()
    start('Use agreement cautiously; use readers for triage',8)
    y=392
    for line in ['**Finding:** opposed agreement shows no reliable advantage over neutral repeats; it retains fewer warranted claims.',
                 '**Robustness:** frozen analyses, rerun, second judge κ = 0.81, second matcher, cross-family reader, and source/compliance exclusions.',
                 '**Limits:** synthetic evidence, imperfect AI labels, no human validation, and unconstrained output format.',
                 '**Next:** representative human adjudication and format-controlled generation before deployment claims.']:
        y=text(line,55,y,size=19)-20
    text('Offline reproduction bundle includes code, outputs, labels, audit evidence and a checksum manifest.',55,78,size=13,color='#555')
    c.showPage();c.save()
    print('Built eight slides:',OUT/'slides.pdf')

if __name__=='__main__':build()
