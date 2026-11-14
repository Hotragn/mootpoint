"""Single LLM call path: Adaption Responses API, with a SQLite cache and a call log.

New code written during the sprint. The endpoint and payload fields follow what I learned in my
earlier project (approve-what-you-see); disclosed as preexisting knowledge in README.
- Cache key = sha256 of (model, instructions, input, temperature, max_tokens, sample index), so reruns replay
  for free and the `sample` index gives independent draws at temperature > 0 (the API documents no seed).
- Every call is logged: tag, model, tokens, credits, latency, cache hit.
"""
import asyncio
import hashlib
import json
import os
import random
import sqlite3
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
URL = "https://api.prod.adaptionlabs.ai/api/v1/responses"
# credits (= USD) per 1M tokens (input, output). Source: docs.adaptionlabs.ai/inference-stacks/models, read 2026-11-14
PRICES = {"gemma-4-31b-it": (0.09, 0.34), "glm-5.2": (1.40, 4.40), "qwen3.5-397b": (0.55, 3.50),
          "gemma-4-26b-a4b-it": (0.077, 0.26), "qwen3.8-27b": (0.039, 1.25),
          "deepseek-v4-flash": (0.045, 0.14), "glm-53-flash": (0.15, 0.50)}
SPEND_CAP = 300.0  # credits; hard stop well under the 1,250 grant


def load_env():
    for p in (ROOT / ".env", ROOT.parent / ".env"):
        if p.exists():
            for line in p.read_text().splitlines():
                if "=" in line and not line.lstrip().startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class LLM:
    def __init__(self, db_path=ROOT / "runs" / "cache.sqlite", concurrency=1):
        load_env()
        if not os.environ.get("ADAPTION_API_KEY"):
            raise RuntimeError("ADAPTION_API_KEY missing from .env")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(db_path)
        self.db.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, text TEXT, usage TEXT)")
        self.db.execute("CREATE TABLE IF NOT EXISTS calls (ts REAL, tag TEXT, model TEXT, key TEXT, "
                        "in_tok INT, out_tok INT, credits REAL, latency REAL, cached INT, status TEXT)")
        self.sem = asyncio.Semaphore(concurrency)

    def spent(self) -> float:
        return self.db.execute("SELECT COALESCE(SUM(credits),0) FROM calls WHERE cached=0").fetchone()[0]

    async def call(self, model, instructions, input, temperature=0.0, max_tokens=1500, sample=0, tag=""):
        key = hashlib.sha256(json.dumps([model, instructions, input, temperature, max_tokens, sample]).encode()).hexdigest()
        row = self.db.execute("SELECT text FROM cache WHERE key=?", (key,)).fetchone()
        if row:
            self._log(tag, model, key, {}, 0.0, 0.0, 1, "cached")
            return row[0]
        if self.spent() >= SPEND_CAP:
            raise RuntimeError(f"spend cap {SPEND_CAP} reached")
        payload = dict(model=model, instructions=instructions, input=input, temperature=temperature,
                       max_output_tokens=max_tokens, store=False, agentic_memory=False,
                       reasoning={"effort": "none"})
        async with self.sem:
            t0 = time.time()
            data = await self._post(payload)
            lat = time.time() - t0
        text = data.get("output_text") or "".join(
            p.get("text", "") for o in data.get("output", []) if o.get("type") == "message" for p in o.get("content", []))
        usage = data.get("usage") or {}
        pin, pout = PRICES[model]
        cost = (usage.get("input_tokens", 0) * pin + usage.get("output_tokens", 0) * pout) / 1e6
        status = data.get("status") or "?"
        if not text.strip():
            self._log(tag, model, key, usage, cost, lat, 0, "EMPTY")
            raise RuntimeError(f"empty output from {model} (status={status})")  # never pass empty text downstream
        self.db.execute("INSERT OR REPLACE INTO cache VALUES (?,?,?)", (key, text, json.dumps(usage)))
        self._log(tag, model, key, usage, cost, lat, 0, status)
        return text

    def _log(self, tag, model, key, usage, cost, lat, cached, status):
        self.db.execute("INSERT INTO calls VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (time.time(), tag, model, key, usage.get("input_tokens", 0), usage.get("output_tokens", 0),
                         cost, lat, cached, status))
        self.db.commit()

    async def _post(self, payload) -> dict:
        headers = {"Authorization": f"Bearer {os.environ['ADAPTION_API_KEY']}"}
        for attempt in range(40):
            try:
                async with httpx.AsyncClient(timeout=300) as c:
                    r = await c.post(URL, json=payload, headers=headers)
                if r.status_code == 429:
                    await asyncio.sleep(15 + random.random() * 10)
                    continue
                if r.status_code >= 500:
                    await asyncio.sleep(min(60, 2 ** attempt))
                    continue
                if r.status_code >= 400:  # body may echo the request, never the key; truncate anyway
                    raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
                return r.json()
            except httpx.TransportError:
                await asyncio.sleep(min(60, 2 ** attempt))
        raise RuntimeError("gave up after 40 attempts")
