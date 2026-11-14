"""Build synthetic case-file dossiers with verified gold facts.

Stages (each asserts non-empty, schema-valid output before the next):
  0 premises: 25 incident premises per domain (glm-5.2)
  1 spec:     structured facts tagged favours A / B / N + 4 contested points with two-sided attributed testimony (glm-5.2)
  2 render:   3-5 raw documents, no fact lists (glm-5.2)
  3 verify:   per-item entailment check against the rendered text (deepseek-v4-flash, different family); unverified items dropped
Usage: python harness/dossiers.py --n-per-domain 25
"""
import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harness.llm import LLM, ROOT

OUT = ROOT / "data" / "dossiers"
AUTHOR, VERIFIER = "glm-5.2", "deepseek-v4-flash"
MIN_FACTS = 15

DOMAINS = {
    "protest": dict(
        topic="a street protest that ended in a confrontation between protesters and police",
        A=("a researcher at a human-rights NGO", "documenting possible excessive force by police against protesters"),
        B=("a public prosecutor", "preparing criminal charges against protesters for rioting and property damage")),
    "workplace": dict(
        topic="a workplace injury at an industrial site where responsibility is disputed",
        A=("a lawyer representing the injured worker", "building a negligence claim against the employer"),
        B=("a claims investigator for the employer's insurer", "assessing whether the worker's own conduct caused the injury")),
    "tenancy": dict(
        topic="a dispute between a tenant and a landlord over building conditions and an attempted eviction",
        A=("an organiser with a tenants' union", "supporting the tenant against an unfair eviction"),
        B=("counsel for the landlord", "justifying the eviction on grounds of lease violations")),
    "product": dict(
        topic="injuries reported by users of a consumer product and the manufacturer's response",
        A=("an advocate at a consumer-safety group", "pushing for a recall of the product"),
        B=("the manufacturer's head of communications", "showing the product is safe when used as directed")),
}

SPEC_INSTR = """You design realistic case files for a research study on how evidence is described. Output ONLY valid JSON, no prose, no code fences."""
SPEC_TMPL = """Domain: {topic}.
Incident premise: {premise}
Side A is {A_role}. Side B is {B_role}.

Write a JSON object with:
- "title": short case title
- "facts": exactly 20 objects {{"fact_id": "F1".."F20", "text": one concrete, atomic, checkable fact (who/what/when/where/how much), "favors": "A" | "B" | "N"}}. Exactly 7 favor A, 7 favor B, 6 neutral. A fact "favors" a side if a fair observer would see it as helping that side's case. Facts must not contradict each other.
- "contested": exactly 4 objects {{"cid": "C1".."C4", "topic": short, "witness_A": name+role, "claim_A": what that witness says (helps A), "witness_B": name+role, "claim_B": what that witness says (helps B)}}. The two claims must directly conflict, and NOTHING in the facts may settle which is true: no fact may mention the specific subject of any contested point, and every fact must be consistent with BOTH versions of every contested point.
Use invented names and places. Be specific (times, numbers, distances)."""

RENDER_INSTR = """You write raw case-file documents. Output only the documents, each starting with a header line like '=== DOCUMENT 2: Witness statement of ... ==='."""
RENDER_TMPL = """Write the case file "{title}" as 3 to 5 raw documents (for example: incident log, witness statements, an inspection or medical report, emails). Total length 1,500-2,500 words.

Rules:
- Every fact below must be stated or clearly entailed somewhere in the documents, embedded naturally (never as a list of facts).
- State each fact in a documentary record (log, official record, report, receipt, email) or by a source nobody disputes. Never state a fact ONLY inside the statement of one of the contested witnesses.
- Each contested point must appear as the two witnesses' conflicting accounts, attributed to them. Do NOT resolve any contested point, and do not add evidence that settles it.
- Neutral documentary tone. No summary, no conclusion, no opinions of the author.
- You may add incidental detail, but nothing that contradicts the facts.

FACTS:
{facts}

CONTESTED POINTS:
{contested}"""

VERIFY_INSTR = """You check whether statements are supported by a document set. Output ONLY JSON."""
VERIFY_TMPL = """DOCUMENTS:
{docs}

STATEMENTS:
{items}

For each statement id, answer true if the documents state it or clearly entail it (paraphrase is fine), else false.
Output JSON: {{"<id>": true|false, ...}} covering every id."""


SETTLER = "qwen3.5-397b"
SETTLE_TMPL = """DOCUMENTS:
{docs}

CONTESTED POINTS (two witnesses give conflicting accounts):
{points}

For each point, ignore the two witnesses' own statements and ask: does any OTHER evidence in the documents (records, logs,
reports, other people, physical evidence, timestamps) settle which account is true, or make one of them clearly false?
Output JSON: {{"<cid>": true if settled by other evidence, false if it remains genuinely unresolved}} for every cid."""


def parse_json(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON object in output")
    return json.loads(m.group(0))


def ok(r):
    """Keep rule: >=15 verified items, >=12 uncontested facts, >=2 unsettled contested pairs (4 items)."""
    n_c = sum(f["contested"] for f in r["facts"])
    return len(r["facts"]) >= MIN_FACTS and len(r["facts"]) - n_c >= 12 and n_c >= 4


def gold_items(spec):
    items = [dict(fact_id=f["fact_id"], text=f["text"], favors=f["favors"], contested=False) for f in spec["facts"]]
    for c in spec["contested"]:
        items.append(dict(fact_id=c["cid"] + "a", text=f'{c["witness_A"]} stated that {c["claim_A"]}', favors="A", contested=True))
        items.append(dict(fact_id=c["cid"] + "b", text=f'{c["witness_B"]} stated that {c["claim_B"]}', favors="B", contested=True))
    return items


def check_spec(spec):
    assert len(spec["facts"]) == 20, "need 20 facts"
    assert {f["favors"] for f in spec["facts"]} <= {"A", "B", "N"}
    assert len(spec["contested"]) == 4, "need 4 contested"
    for f in spec["facts"]:
        assert f["text"].strip()


async def premises(llm, domain, n):
    d = DOMAINS[domain]
    out = await llm.call(AUTHOR, "Output ONLY a JSON object.",
                         f'List {n} distinct, specific incident premises for case files about {d["topic"]}. '
                         f'Vary setting, scale, people and circumstances. One sentence each. '
                         f'Output {{"premises": [..{n} strings..]}}', temperature=0.9, max_tokens=3000, tag="premises")
    ps = parse_json(out)["premises"]
    assert len(ps) >= n and all(p.strip() for p in ps), f"premises short for {domain}"
    return ps[:n]


async def build_one(llm, domain, idx, premise, did):
    path = OUT / f"{did}.json"
    if path.exists():
        return json.loads(path.read_text())
    d = DOMAINS[domain]
    for attempt in range(3):
        try:
            spec = parse_json(await llm.call(AUTHOR, SPEC_INSTR, SPEC_TMPL.format(
                topic=d["topic"], premise=premise, A_role=d["A"][0], B_role=d["B"][0]),
                temperature=0.8, max_tokens=4000, sample=attempt, tag="spec"))
            check_spec(spec)
            break
        except (ValueError, AssertionError, KeyError, json.JSONDecodeError):
            if attempt == 2:
                raise
    facts_txt = "\n".join(f'- {f["text"]}' for f in spec["facts"])
    cont_txt = "\n".join(f'- {c["topic"]}: {c["witness_A"]} says "{c["claim_A"]}"; {c["witness_B"]} says "{c["claim_B"]}"'
                         for c in spec["contested"])
    docs = await llm.call(AUTHOR, RENDER_INSTR, RENDER_TMPL.format(title=spec["title"], facts=facts_txt, contested=cont_txt),
                          temperature=0.7, max_tokens=6000, tag="render")
    nwords = len(docs.split())
    assert nwords >= 900, f"{did}: rendered dossier too short ({nwords} words)"
    items = gold_items(spec)
    ver = parse_json(await llm.call(VERIFIER, VERIFY_INSTR, VERIFY_TMPL.format(
        docs=docs, items="\n".join(f'{i["fact_id"]}: {i["text"]}' for i in items)), temperature=0.0, max_tokens=1500, tag="verify"))
    kept = [i for i in items if ver.get(i["fact_id"]) is True]
    # settle check (different family from the author): a contested point the file resolves is not contested; drop its pair
    settle = parse_json(await llm.call(SETTLER, VERIFY_INSTR, SETTLE_TMPL.format(docs=docs, points="\n".join(
        f'{c["cid"]}: {c["witness_A"]} says "{c["claim_A"]}" / {c["witness_B"]} says "{c["claim_B"]}"' for c in spec["contested"])),
        temperature=0.0, max_tokens=800, tag="settle"))
    settled = {c["cid"] for c in spec["contested"] if settle.get(c["cid"]) is True}
    kept = [i for i in kept if not (i["contested"] and i["fact_id"][:-1] in settled)]
    rec = dict(dossier_id=did, split=None, domain=domain, title=spec["title"], premise=premise,
               side_A=dict(role=d["A"][0], goal=d["A"][1]), side_B=dict(role=d["B"][0], goal=d["B"][1]),
               documents=docs, n_words=nwords, facts=kept, n_items_spec=len(items), n_items_verified=len(kept),
               settled=sorted(settled))
    return rec


async def main(n_per_domain):
    llm = LLM(concurrency=12)
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for domain in DOMAINS:
        ps = await premises(llm, domain, n_per_domain + 5)  # 5 spares for replacements
        jobs.append((domain, ps))
    recs = []

    # domains in parallel, dossiers within a domain in batches
    async def batched(domain, ps):
        sem = asyncio.Semaphore(6)
        async def one(k):
            async with sem:
                did = f"{domain}-{k:02d}"
                try:
                    return await build_one(llm, domain, k, ps[k], did)
                except Exception as e:
                    print(f"FAIL {did}: {type(e).__name__}: {str(e)[:120]}")
                    return None
        res = await asyncio.gather(*[one(k) for k in range(len(ps))])
        good = [r for r in res if r and ok(r)]
        for r in res:
            if r and r not in good:
                print(f"DROP {r['dossier_id']}: {r['n_items_verified']}/{r['n_items_spec']} verified")
        return good[:n_per_domain]

    results = await asyncio.gather(*[batched(d, ps) for d, ps in jobs])
    for good in results:
        assert len(good) == n_per_domain, f"only {len(good)} good dossiers in a domain"
        for j, rec in enumerate(good):  # split fixed by position: first half dev, second half test
            rec["split"] = "dev" if j < n_per_domain // 2 else "test"
            (OUT / f"{rec['dossier_id']}.json").write_text(json.dumps(rec, indent=1))
            recs.append(rec)
    print(f"wrote {len(recs)} dossiers; credits spent {llm.spent():.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-per-domain", type=int, default=25)
    asyncio.run(main(ap.parse_args().n_per_domain))
