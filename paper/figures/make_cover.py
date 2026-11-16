"""Project cover image for the submission form (16:9). Numbers are read from the frozen test results.
Usage: .venv/bin/python paper/figures/make_cover.py -> submission/Pettugani_MootPoint_AI-Epistemics-2026_cover.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "analysis" / "results" / "test"
res, rd = json.loads((R / "results.json").read_text()), json.loads((R / "readers.json").read_text())
bars = [("Keep what both opposed\nsides' AI descriptions say", res["auroc"]["OPP"]["estimate"], "#0072B2"),
        ("Keep what two plain\nrepeat requests say", res["auroc"]["SC"]["estimate"], "#56B4E9"),
        ("A strong model reads the\nneutral description", rd["descriptive"]["auroc"]["v_closed_none"]["estimate"], "#D55E00")]

fig = plt.figure(figsize=(16, 9), dpi=120)
fig.patch.set_facecolor("white")
fig.text(0.06, 0.88, "Common Ground Is Not Neutral Ground", fontsize=40, weight="bold", color="#111")
fig.text(0.06, 0.80, "Opposed AI advocates disagree by silence: each leaves out the true facts that hurt it.",
         fontsize=21, color="#333")
ax = fig.add_axes([0.33, 0.17, 0.60, 0.52])
y = range(len(bars))[::-1]
for yi, (lab, v, c) in zip(y, bars):
    ax.barh(yi, v - 0.5, left=0.5, color=c, height=0.62)
    ax.text(v + 0.008, yi, f"{v:.2f}", va="center", fontsize=24, weight="bold", color="#111")
    ax.text(0.485, yi, lab, va="center", ha="right", fontsize=19, color="#222")
ax.set_xlim(0.5, 0.92)
ax.set_yticks([])
ax.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9])
ax.tick_params(labelsize=15, colors="#555")
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.set_xlabel("How well each method spots unwarranted claims: side-taking or invented (AUROC; 0.5 = guessing)", fontsize=16, color="#444")
fig.text(0.06, 0.04, "MootPoint: 100 synthetic case files, 3 model families, 4,486 labelled claims on 76 held-out files.  "
         "Hotragn Pettugani · Apart AI x Epistemics Sprint 2026", fontsize=14, color="#666")
out = ROOT / "submission" / "Pettugani_MootPoint_AI-Epistemics-2026_cover.png"
fig.savefig(out, facecolor="white")
assert out.stat().st_size > 10_000
print(out)
