"""Readable vector/raster overview; replaces the legacy draw.io export."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

out = Path(__file__).resolve().parent
fig, ax = plt.subplots(figsize=(12, 3.8))
ax.set(xlim=(0, 12), ylim=(0, 3.8)); ax.axis('off')
blue, orange = '#0072B2', '#D55E00'

def box(x, y, w, h, title, body, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.08',
                               facecolor='#FAFAF8', edgecolor=color, linewidth=1.3))
    ax.text(x+.14, y+h-.22, title, fontsize=14, weight='bold', va='top', color=color)
    ax.text(x+.14, y+h-.67, body, fontsize=13, va='top', linespacing=1.4)

box(.1, .65, 3.1, 2.75, '1  Synthetic case files',
    'Logs, reports, testimony\n\nFacts + witness conflicts\nModel-checked, not infallible\n\n100 files; 76 held out', '#333333')
box(3.7, .65, 3.5, 2.75, '2  Vary the requester',
    'N1: neutral text to audit\nA, B: opposed stakeholders\nN2, N3: neutral repeats\nP1, P2: clerk, journalist\n\nSame evidence; 3 models', '#333333')
box(7.7, 2.05, 4.1, 1.35, '3a  Count repetition',
    'Flag claims absent from either text\nOpposed 0.656; repeats 0.704', blue)
box(7.7, .45, 4.1, 1.35, '3b  Read the neutral text',
    'Estimate unwarrantedness, no file\nStrong readers: 0.828 / 0.836', orange)
for x1,y1,x2,y2 in [(3.28,2.0,3.6,2.0),(7.28,2.6,7.6,2.6),(7.28,1.2,7.6,1.2)]:
    ax.annotate('',(x2,y2),(x1,y1),arrowprops={'arrowstyle':'->','lw':1.5,'color':'#555'})
ax.text(.1,.18,'Original-run AUROC; higher is better. Source and output-compliance sensitivity: Appendix E.', fontsize=12, color='#555')
fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
for suffix in ('png','svg'):
    fig.savefig(out/f'fig1_method.{suffix}',dpi=250,facecolor='white')
plt.close(fig)
