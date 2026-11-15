"""Exploratory (Sun Nov 15, after test): rerun the presence matrix with a second matcher from a different family
(glm-5.2; the main matcher is qwen3.5-397b). Same blinded prompt, same seeded shuffle and D1..D7 names; only the
model changes. Tests whether the OPP < SC gap and the omission pattern depend on one matcher's habits.
Writes runs/<split>/presence_glm52.jsonl (same schema as presence.jsonl).
Usage: .venv/bin/python harness/presence2.py --split test
"""
import argparse
import asyncio
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harness.judge import OTHERS, PRES_INSTR, PRES_TMPL, ROOT, load, n1_claims, retry_json, valid_presence, write
from harness.llm import LLM

MATCHER = "glm-5.2"  # GLM family; shares a family with generator glm-53-flash (disclosed)


async def main(split):
    llm = LLM(concurrency=8)
    _, cells = load(split)
    rows = [json.loads(l) for l in open(ROOT / "runs" / split / "claims.jsonl")]

    async def one(key, claims):
        fr = cells[key]
        if not set(OTHERS) <= set(fr):
            return []
        order = OTHERS[:]
        random.Random(f"{key[0]}|{key[1]}").shuffle(order)  # identical order and names to the main matcher
        texts = "\n\n".join(f"[D{j+1}]\n{fr[f]['text']}" for j, f in enumerate(order))
        ctext = "\n".join(f'{c["claim_id"]}: {c["text"]}' for c in claims)
        ids = [c["claim_id"] for c in claims]
        res = await retry_json(llm, MATCHER, PRES_INSTR, PRES_TMPL.format(claims=ctext, texts=texts, k=len(order)),
                               lambda o: valid_presence(o, ids, len(order)), 8000, "presence2")
        if res is None:
            return []
        return [dict(dossier_id=key[0], model=key[1], claim_id=cid, framing=f, verdict=res[cid][f"D{j+1}"])
                for cid in ids for j, f in enumerate(order)]

    by = n1_claims(rows)
    out = await asyncio.gather(*[one(k, v) for k, v in by.items()])
    flat = [r for o in out for r in o]
    write(split, "presence_glm52.jsonl", flat)
    print(f"presence2: {sum(1 for o in out if o)}/{len(by)} cells, {len(flat)} rows; credits {llm.spent():.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    asyncio.run(main(ap.parse_args().split))
