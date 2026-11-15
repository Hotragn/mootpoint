"""Exploratory (final audit, after test was analysed): the with-file reference reader using glm-5.2, the same model as
the cross-family closed-book reader (harness/xf_strong.py). This gives a same-model ceiling: how much closed-book
reading loses against reading the case file. Same prompt as the frozen v_file stage; only the model changes.
Writes runs/<split>/vfile_strong.jsonl. Usage: .venv/bin/python harness/vfile_strong.py --split test
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harness.judge import MAP_INSTR, ROOT, VFILE_TMPL, load, n1_claims, retry_json, valid_probs, write
from harness.llm import LLM

READER = "glm-5.2"


async def main(split):
    llm = LLM(concurrency=8)
    dossiers, cells = load(split)
    rows = [json.loads(l) for l in open(ROOT / "runs" / split / "claims.jsonl")]

    async def one(key, claims):
        d = dossiers[key[0]]
        ids = [c["claim_id"] for c in claims]
        ctext = "\n".join(f'{c["claim_id"]}: {c["text"]}' for c in claims)
        r = await retry_json(llm, READER, MAP_INSTR, VFILE_TMPL.format(docs=d["documents"], claims=ctext),
                             lambda o: valid_probs(o, ids), 3000, "vfile_strong")
        return [] if r is None else [dict(dossier_id=key[0], model=key[1], claim_id=cid, vs_file=r[cid]) for cid in ids]

    by = n1_claims(rows)
    out = await asyncio.gather(*[one(k, v) for k, v in by.items()])
    flat = [r for o in out for r in o]
    assert flat, "no rows"
    write(split, "vfile_strong.jsonl", flat)
    print(f"vfile_strong: {sum(1 for o in out if o)}/{len(by)} cells, {len(flat)} rows; credits {llm.spent():.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    asyncio.run(main(ap.parse_args().split))
