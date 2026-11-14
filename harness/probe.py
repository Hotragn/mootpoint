"""Connectivity + rate-limit probe. Prints model, latency and a 40-char reply; never prints credentials."""
import asyncio
import sys
import time

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
from harness.llm import LLM

MODELS = ["qwen3.5-397b", "gemma-4-31b-it", "deepseek-v4-flash", "glm-5.2"]


async def main():
    llm = LLM(concurrency=8)
    # 1) one call per model, sequential
    for m in MODELS:
        t = time.time()
        out = await llm.call(m, "Answer in one short sentence.", "Say hello and name the capital of France.", tag="probe")
        print(f"{m:20s} {time.time()-t:5.1f}s  {out[:40]!r}")
    # 2) parallel across models: does a 429 appear? (unique inputs so no cache hits)
    t = time.time()
    outs = await asyncio.gather(*[llm.call(m, "Reply with one word.", f"probe parallel {i}", tag="probe_par", sample=i)
                                  for i, m in enumerate(MODELS)], return_exceptions=True)
    print(f"parallel 4 models: {time.time()-t:.1f}s", [type(o).__name__ if isinstance(o, Exception) else "ok" for o in outs])
    print("credits spent so far:", round(llm.spent(), 4))


asyncio.run(main())
