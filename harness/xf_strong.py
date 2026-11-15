"""Exploratory (audit, after test was analysed): a STRONG closed-book reader from a different family than the
labelling judge (qwen3.5-397b), to test whether reader AUROC is judge self-agreement. Same prompts as the frozen
verifier stage; only the model changes. Writes runs/<split>/xf_strong.jsonl.
Usage: .venv/bin/python harness/xf_strong.py --split test
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harness.judge import MAP_INSTR, ROOT, load, n1_claims, retry_json, valid_probs, vclosed_prompt, write
from harness.llm import LLM

READER = "glm-5.2"  # GLM family; the judge is qwen. glm-53-flash (a generator) shares the family: disclosed
CONTEXTS = {"xs_none": (), "xs_opp": ("A", "B")}


async def main(split):
    llm = LLM(concurrency=8)
    dossiers, cells = load(split)
    rows = [json.loads(l) for l in open(ROOT / "runs" / split / "claims.jsonl")]

    async def one(key, claims):
        d, fr = dossiers[key[0]], cells[key]
        if not {"N1", "A", "B"} <= set(fr):
            return []
        ids = [c["claim_id"] for c in claims]
        ctext = "\n".join(f'{c["claim_id"]}: {c["text"]}' for c in claims)
        res = await asyncio.gather(*[retry_json(llm, READER, MAP_INSTR, vclosed_prompt(d, fr, ctx, ctext),
                                                (lambda o: valid_probs(o, ids)), 3000, "xs_reader")
                                     for ctx in CONTEXTS.values()])
        if any(r is None for r in res):
            return []
        return [dict(dossier_id=key[0], model=key[1], claim_id=cid, **{n: r[cid] for n, r in zip(CONTEXTS, res)})
                for cid in ids]

    by = n1_claims(rows)
    out = await asyncio.gather(*[one(k, v) for k, v in by.items()])
    flat = [r for o in out for r in o]
    write(split, "xf_strong.jsonl", flat)
    print(f"xf_strong: {sum(1 for o in out if o)}/{len(by)} cells, {len(flat)} rows; credits {llm.spent():.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    asyncio.run(main(ap.parse_args().split))
