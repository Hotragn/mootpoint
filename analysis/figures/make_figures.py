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
import matplotlib.patches
import matplotlib.pyplot as plt
import matplotlib.ticker
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
COUNT, READ, REF = "#0072B2", "#D55E00", "#7F7F7F"
INK, MUTED = "#222222", "#666666"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.dpi": 300})

# groups of (key, label, kind), top to bottom; kind sets colour (gray = baseline or reference, not a detector)
GROUPS = [
    ("Trivial baselines", [("random", "Random score", "ref"), ("evaluative_words", "Count of evaluative words", "ref")]),
    ("Counting (two extra descriptions)", [
        ("SAME", "Same side twice (A, A2)", "count"), ("OPP", "Opposed sides (A, B)", "count"),
        ("SC", "Neutral resamples (N2, N3)", "count"), ("DIV", "Clerk + journalist (P1, P2)", "count"),
        ("contra_OPP", "Opposed sides, counting contradictions", "count")]),
    ("Reading, qwen3.5-397b (also the labelling judge)", [
        ("v_closed_none", "N1 alone", "read"), ("v_closed_sc", "N1 + N2 + N3", "read"),
        ("v_closed", "N1 + A + B", "read"), ("v_closed_div", "N1 + P1 + P2", "read"),
        ("v_closed_debate", "N1 + instructed debate (DA, DB)", "read")]),
    ("Reading, glm-5.2 (another family)", [("xs_none", "N1 alone", "read"), ("xs_opp", "N1 + A + B", "read")]),
    ("Reading, deepseek-v4-flash (weaker)", [("xf_none", "N1 alone", "read"), ("xf_opp", "N1 + A + B", "read")]),
    ("Reference: reads the case file", [("v_file", "qwen3.8-27b", "ref"), ("vs_file", "glm-5.2", "ref")]),
]


def fig_detectors(res, rd, extra, out):
    auc = dict(rd["descriptive"]["auroc"])
    auc["SAME"] = res["auroc"]["SAME"]
    if extra:
        a2, ex = extra
        auc.update({k: a2["judge_labels"][k] for k in ("random", "evaluative_words", "xs_none", "xs_opp")})
        auc["contra_OPP"] = ex["contradiction_counting"]["OPP"]
        auc["vs_file"] = ex["glm52"]["vs_file"]
    ys, labels, y = [], [], 0.0
    fig, ax = plt.subplots(figsize=(6.0, 5.6))
    for gname, items in GROUPS:
        items = [it for it in items if it[0] in auc]
        if not items:
            continue
        ax.text(0.452, y - 0.05, gname, fontsize=8, fontweight="bold", color=INK, va="bottom")
        y -= 0.85
        for k, lab, kind in items:
            a, c = auc[k], {"count": COUNT, "read": READ, "ref": REF}[kind]
            ax.plot([a["ci95_low"], a["ci95_high"]], [y, y], color=c, lw=2, solid_capstyle="round")
            ax.plot(a["estimate"], y, "o", ms=6, color=c, mec="white", mew=1.5)
            ax.text(a["ci95_high"] + 0.008, y, f"{a['estimate']:.2f}", va="center", fontsize=7.5, color=INK)
            ys.append(y)
            labels.append(lab)
            y -= 0.8
        y -= 0.35
    ax.set_yticks(ys, labels, fontsize=8)
    ax.set_ylim(y + 0.3, 0.6)
    ax.axvline(0.5, color=MUTED, lw=0.8, ls=":")
    ax.set_xlim(0.45, 1.0)
    ax.set_xlabel(f"AUROC for unwarranted N1 claims (95% CI)\n{rd['n']['N1_claims']:,} claims, {rd['n']['N1_unwarranted']} unwarranted")
    ax.grid(axis="x", color="#e5e5e5", lw=0.6)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
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
    """Opposed descriptions disagree by silence: for each pair and true label, how N1 claims fare in the pair."""
    pairs = [("OPP", "Opposed (A, B)"), ("SC", "Resamples (N2, N3)"), ("DIV", "Clerk, journalist (P1, P2)")]
    segs = [("both repeat it", COUNT), ("one or both silent", "#C8C8C8"), ("contradicted", READ)]
    rows = []
    for p, lab in pairs:
        for yv, ylab in ((0, "warranted"), (1, "unwarranted")):
            s = sig[sig.y == yv]
            both = (s[f"k_{p}"] == 2).mean()
            contra = (s[f"contra_{p}"] > 0).mean()
            rows.append((f"{lab}, {ylab}", [both, 1 - both - contra, contra]))
    fig, ax = plt.subplots(figsize=(5.6, 2.9))
    ypos = [0, 1, 2.6, 3.6, 5.2, 6.2]
    for yp, (lab, vals) in zip(ypos, rows):
        left = 0
        for (name, c), v in zip(segs, vals):
            ax.barh(yp, v, left=left, height=0.8, color=c, edgecolor="white", linewidth=1.5)
            if v >= 0.06:
                ax.text(left + v / 2, yp, f"{v:.0%}", ha="center", va="center", fontsize=7.5,
                        color="white" if c != "#C8C8C8" else INK)
            left += v
    ax.set_yticks(ypos, [r[0] for r in rows])
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_xlabel("Share of N1 claims")
    handles = [matplotlib.patches.Patch(color=c, label=n) for n, c in segs]
    ax.legend(handles=handles, frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.4, 1.17), ncol=3)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
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
    a2, ex = src / "audit_extras.json", src / "exploratory_final.json"  # exploratory, optional
    extra = (json.loads(a2.read_text()), json.loads(ex.read_text())) if a2.exists() and ex.exists() else None
    fig_detectors(res, rd, extra, out)
    fig_sidetaking(drift, out)
    fig_mechanism(sig, out)
    print("wrote", sorted(p.name for p in out.glob("*.png")))


if __name__ == "__main__":
    main()
