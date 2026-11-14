"""Synthetic inputs in the PLAN.md v3 schema with KNOWN planted effects, for validating analyze.py.

Writes <out>/{claims,descriptions,presence,verifiers,judge2}.jsonl and <out>/dossiers/.

Generative model, per dossier x model cell. Each latent claim has an inclusion probability per framing (8 framings):
- uncontested gold facts (8 favour A, 8 favour B, 4 neutral): 0.6 everywhere; under A or A2 (B), ally-favouring
  facts +0.2*effect and opponent-favouring -0.2*effect (plants H1b: true DiD = 0.4*effect);
- 2 contested testimony facts (C1a for A, C1b for B, contested=True): 0.6 everywhere (H1b must ignore them);
- 5 SUPPORTED_OTHER and 3 NEUTRAL_INFERENCE claims: 0.6 / 0.4 everywhere (both y = 0);
- 6 SIDE_TAKING claims (3 side A, 3 side B): 0.55 in N1, N2, N3, P1, P2; 0.55 + 0.3*effect under their own side
  (A and A2 for side A, B for side B); 0.55 - 0.5*effect under the opposed side. This plants H2 and H3 (unwarranted
  claims rarely appear in both A and B, while neutral resamples and diverse requesters repeat them) and H1a;
- 2 UNSUPPORTED_FACT claims: 0.4 everywhere (no framing effect);
- Poisson(2*effect) extra SIDE_TAKING claims siding with the requester in each of A and B (plants H1a).
Presence verdict for an N1 claim in framing F: ASSERTS if the latent claim is included in F; otherwise CONTRADICTS
with probability 0.3 when F is the opposed side of a SIDE_TAKING claim, else SILENT.
Verifiers: v_closed = clip(0.35 + 0.15*y + N(0, 0.2)), v_file = clip(0.2 + 0.5*y + N(0, 0.15)).
judge2: label2 = label with probability 0.9, otherwise a random other label.
5% of SIDE_TAKING claims carry repaired="side_missing" (side and contested_id null), as the harness emits them.
With effect = 0 every framing is exchangeable, so every planted statistic is exactly 0 in expectation.

Usage: python analysis/make_synthetic.py --out analysis/synthetic/effect --effect 1.0
"""
import argparse
import json
from pathlib import Path

import numpy as np

DOMAINS = ["protest", "workplace", "tenancy", "product"]
MODELS = ["qwen3.5-397b", "gemma-4-31b-it", "deepseek-v4-flash"]
FRAMINGS = ["A", "A2", "B", "N1", "N2", "N3", "P1", "P2"]
OTHERS = [f for f in FRAMINGS if f != "N1"]
LABELLED = ["A", "B", "N1"]
SIDE = {"A": "A", "A2": "A", "B": "B"}
LABELS = ["GOLD", "SUPPORTED_OTHER", "NEUTRAL_INFERENCE", "SIDE_TAKING", "UNSUPPORTED_FACT"]


def make(out, effect=1.0, n_dossiers=48, seed=0, split="test", drop_cells=0):
    rng = np.random.default_rng(seed)
    out = Path(out)
    (out / "dossiers").mkdir(parents=True, exist_ok=True)
    claims, desc, pres, ver, j2 = [], [], [], [], []
    dropped = []
    for d in range(n_dossiers):
        did = f"syn{d:03d}"
        domain = DOMAINS[d % len(DOMAINS)]
        facts = [{"fact_id": f"F{i}", "text": f"fact {i}", "favors": fv, "contested": False}
                 for i, fv in enumerate(["A"] * 8 + ["B"] * 8 + ["N"] * 4)]
        facts += [{"fact_id": "C1a", "text": "witness a", "favors": "A", "contested": True},
                  {"fact_id": "C1b", "text": "witness b", "favors": "B", "contested": True}]
        (out / "dossiers" / f"{did}.json").write_text(json.dumps(
            {"dossier_id": did, "split": split, "domain": domain, "side_A": {"role": "a"}, "side_B": {"role": "b"},
             "documents": "synthetic documents", "facts": facts, "settled": []}))
        for mi, m in enumerate(MODELS):
            latent = []  # (lid, label, gold_id, contested_id, side, prob per framing)
            for f in facts:
                p = {}
                for fr in FRAMINGS:
                    s = SIDE.get(fr)
                    bias = 0 if s is None or f["favors"] == "N" or f["contested"] else (0.2 if f["favors"] == s else -0.2)
                    p[fr] = 0.6 + effect * bias
                latent.append((f"g{f['fact_id']}", "GOLD", f["fact_id"], None, None, p))
            latent += [(f"so{k}", "SUPPORTED_OTHER", None, None, None, dict.fromkeys(FRAMINGS, 0.6)) for k in range(5)]
            latent += [(f"ni{k}", "NEUTRAL_INFERENCE", None, None, None, dict.fromkeys(FRAMINGS, 0.4)) for k in range(3)]
            for k in range(6):
                lean = "A" if k < 3 else "B"
                p = {fr: 0.55 if fr not in SIDE else (0.55 + 0.3 * effect if SIDE[fr] == lean else 0.55 - 0.5 * effect)
                     for fr in FRAMINGS}
                latent.append((f"st{k}", "SIDE_TAKING", None, "C1" if lean == "A" else "C2", lean, p))
            latent += [(f"uf{k}", "UNSUPPORTED_FACT", None, None, None, dict.fromkeys(FRAMINGS, 0.4)) for k in range(2)]
            inc = {fr: [lt for lt in latent if rng.random() < lt[5][fr]] for fr in FRAMINGS}
            # first `drop_cells` cells of the first model: P1 excluded (exercises incomplete-cell exclusion)
            drop = mi == 0 and d < drop_cells
            if drop:
                dropped.append((did, m))
            for fr in FRAMINGS:
                desc.append(dict(dossier_id=did, model=m, framing=fr, text=f"description {fr}", n_words=250,
                                 excluded=drop and fr == "P1"))
            for fr in LABELLED:
                rows = [(lid, lab, gid, con, side) for lid, lab, gid, con, side, _ in inc[fr]]
                if fr in SIDE:
                    rows += [(f"xs{j}", "SIDE_TAKING", None, "C3", SIDE[fr]) for j in range(rng.poisson(2 * effect))]
                for lid, lab, gid, con, side in rows:
                    cid = f"{fr}:{lid}"
                    rp = None
                    if lab == "SIDE_TAKING" and rng.random() < 0.05:  # harness repair: judge omitted the side
                        con, side, rp = None, None, "side_missing"
                    claims.append(dict(dossier_id=did, split=split, domain=domain, model=m, framing=fr, claim_id=cid,
                                       text=f"claim {lid}", label=lab, gold_id=gid, contested_id=con, side=side,
                                       evidence=None, repaired=rp))
                    if fr != "N1":
                        continue
                    present = {f2: {x[0] for x in inc[f2]} for f2 in OTHERS}
                    for f2 in OTHERS:
                        if drop and f2 == "P1":
                            continue
                        if lid in present[f2]:
                            v = "ASSERTS"
                        elif lab == "SIDE_TAKING" and f2 in SIDE and SIDE[f2] != side and rng.random() < 0.3:
                            v = "CONTRADICTS"
                        else:
                            v = "SILENT"
                        pres.append(dict(dossier_id=did, model=m, claim_id=cid, framing=f2, verdict=v))
                    y = lab in ("SIDE_TAKING", "UNSUPPORTED_FACT")
                    ver.append(dict(dossier_id=did, model=m, claim_id=cid,
                                    v_closed=float(np.clip(0.35 + 0.15 * y + rng.normal(0, 0.2), 0, 1)),
                                    v_file=float(np.clip(0.2 + 0.5 * y + rng.normal(0, 0.15), 0, 1))))
                    lab2 = lab if rng.random() < 0.9 else str(rng.choice([x for x in LABELS if x != lab]))
                    j2.append(dict(dossier_id=did, model=m, claim_id=cid, label2=lab2))
    for name, rows in [("claims", claims), ("descriptions", desc), ("presence", pres), ("verifiers", ver),
                       ("judge2", j2)]:
        with open(out / f"{name}.jsonl", "w") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
    return out / "claims.jsonl", out / "dossiers", dropped


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--effect", type=float, default=1.0)
    ap.add_argument("--n-dossiers", type=int, default=48)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--drop-cells", type=int, default=0)
    a = ap.parse_args()
    print(make(a.out, a.effect, a.n_dossiers, a.seed, drop_cells=a.drop_cells)[:2])
