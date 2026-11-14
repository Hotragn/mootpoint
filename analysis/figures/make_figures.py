"""Data figures for the paper, read only from frozen-analysis outputs.

Usage: .venv/bin/python analysis/figures/make_figures.py --split test
Writes analysis/figures/<split>/fig2_detectors.png, fig3_sidetaking.png, fig4_mechanism.png.
Palette: Okabe-Ito blue/orange (validated for CVD with the dataviz validator); gray = reference only.
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
COUNT, READ, REF = "#0072B2", "#D55E00", "#7F7F7F"
INK, MUTED = "#222222", "#666666"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.dpi": 300})

# (key, label, kind) in display order, top to bottom
DETECTORS = [
    ("SAME", "Count: same side twice (A, A2)", "count"),
    ("OPP", "Count: opposed sides (A, B)", "count"),
    ("SC", "Count: neutral resamples (N2, N3)", "count"),
    ("DIV", "Count: clerk + journalist (P1, P2)", "count"),
    ("xf_none", "Read, weak model: N1 alone", "read"),
    ("xf_opp", "Read, weak model: N1 + A + B", "read"),
    ("v_closed_none", "Read: N1 alone", "read"),
    ("v_closed_sc", "Read: N1 + N2 + N3", "read"),
    ("v_closed", "Read: N1 + A + B", "read"),
    ("v_closed_div", "Read: N1 + P1 + P2", "read"),
    ("v_closed_debate", "Read: N1 + instructed debate", "read"),
    ("v_file", "Reference: reads the case file", "ref"),
]


def fig_detectors(res, rd, out):
    auc = dict(rd["descriptive"]["auroc"])
    auc["SAME"] = res["auroc"]["SAME"]
    rows = [(k, lab, kind, auc[k]) for k, lab, kind in DETECTORS if k in auc]
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    for i, (k, lab, kind, a) in enumerate(reversed(rows)):
        c = {"count": COUNT, "read": READ, "ref": REF}[kind]
        ax.plot([a["ci95_low"], a["ci95_high"]], [i, i], color=c, lw=2, solid_capstyle="round")
        ax.plot(a["estimate"], i, "o", ms=6, color=c, mec="white", mew=1.5)
        ax.text(a["ci95_high"] + 0.01, i, f"{a['estimate']:.2f}", va="center", fontsize=8, color=INK)
    ax.set_yticks(range(len(rows)), [r[1] for r in reversed(rows)])
    ax.axvline(0.5, color=MUTED, lw=0.8, ls=":")
    ax.set_xlim(0.45, 1.0)
    ax.set_xlabel("AUROC for unwarranted N1 claims\n(95% dossier-cluster bootstrap CI)")
    ax.grid(axis="x", color="#e5e5e5", lw=0.6)
    fig.tight_layout()
    fig.savefig(out / "fig2_detectors.png")
    plt.close(fig)


def fig_sidetaking(drift, out):
    s = drift.sum(numeric_only=True)
    # share of side-taking claims that favour each side, by description
    vals = {"A favoured": (s.st_N1_sideA / s.st_N1_n, s.st_A_sideA / s.st_A_n),
            "B favoured": (s.st_N1_sideB / s.st_N1_n, s.st_B_sideB / s.st_B_n)}
    fig, ax = plt.subplots(figsize=(3.6, 2.6))
    x = [0, 1]
    w = 0.36
    ax.bar([i - w / 2 - 0.01 for i in x], [v[0] for v in vals.values()], w, color=REF, label="neutral (N1)")
    ax.bar([i + w / 2 + 0.01 for i in x], [v[1] for v in vals.values()], w, color=READ,
           label="requester of that side (A or B)")
    for i, v in enumerate(vals.values()):
        ax.text(i - w / 2 - 0.01, v[0] + 0.02, f"{v[0]:.2f}", ha="center", fontsize=8, color=INK)
        ax.text(i + w / 2 + 0.01, v[1] + 0.02, f"{v[1]:.2f}", ha="center", fontsize=8, color=INK)
    ax.set_xticks(x, list(vals))
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Share of side-taking claims")
    ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=2)
    fig.tight_layout()
    fig.savefig(out / "fig3_sidetaking.png")
    plt.close(fig)


def fig_mechanism(sig, out):
    # share of N1 claims asserted by both descriptions of a pair, by true label
    pairs = [("OPP", "opposed\n(A, B)"), ("SC", "resamples\n(N2, N3)"), ("DIV", "clerk, journalist\n(P1, P2)")]
    fig, ax = plt.subplots(figsize=(3.8, 2.6))
    w = 0.36
    for i, (p, lab) in enumerate(pairs):
        both = sig[f"k_{p}"] == 2
        warr, unw = both[sig.y == 0].mean(), both[sig.y == 1].mean()
        ax.bar(i - w / 2 - 0.01, warr, w, color=COUNT, label="warranted" if i == 0 else None)
        ax.bar(i + w / 2 + 0.01, unw, w, color=READ, label="unwarranted" if i == 0 else None)
        ax.text(i - w / 2 - 0.01, warr + 0.02, f"{warr:.2f}", ha="center", fontsize=8, color=INK)
        ax.text(i + w / 2 + 0.01, unw + 0.02, f"{unw:.2f}", ha="center", fontsize=8, color=INK)
    ax.set_xticks(range(len(pairs)), [p[1] for p in pairs])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Share of N1 claims repeated by both")
    ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=2)
    fig.tight_layout()
    fig.savefig(out / "fig4_mechanism.png")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    a = ap.parse_args()
    src = ROOT / "analysis" / "results" / a.split
    out = ROOT / "analysis" / "figures" / a.split
    out.mkdir(parents=True, exist_ok=True)
    res = json.loads((src / "results.json").read_text())
    rd = json.loads((src / "readers.json").read_text())
    drift = pd.read_csv(src / "per_cell_drift.csv")
    sig = pd.read_csv(src / "per_claim_signals.csv")
    assert len(sig) and len(drift), "empty inputs"
    fig_detectors(res, rd, out)
    fig_sidetaking(drift, out)
    fig_mechanism(sig, out)
    print("wrote", sorted(p.name for p in out.glob("*.png")))


if __name__ == "__main__":
    main()
