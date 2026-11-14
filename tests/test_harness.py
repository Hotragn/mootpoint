"""Invariant tests for the harness (no network: a fake LLM stands in)."""
import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harness import describe, dossiers, judge


class FakeLLM:
    def __init__(self, replies):
        self.replies = list(replies)

    async def call(self, *a, **k):
        return self.replies.pop(0)


def spec(n_facts=20, n_cont=4):
    return dict(title="t", facts=[dict(fact_id=f"F{i}", text=f"fact {i}", favors="ABN"[i % 3]) for i in range(1, n_facts + 1)],
                contested=[dict(cid=f"C{i}", topic="x", witness_A="wa", claim_A="ca", witness_B="wb", claim_B="cb") for i in range(1, n_cont + 1)])


def test_parse_json_strips_fences_and_rejects_prose():
    assert dossiers.parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    with pytest.raises(ValueError):
        dossiers.parse_json("no json here")


def test_gold_items_attributes_contested_testimony_to_each_side():
    items = dossiers.gold_items(spec())
    assert len(items) == 28
    c = [i for i in items if i["contested"]]
    assert {i["favors"] for i in c if i["fact_id"].endswith("a")} == {"A"}
    assert {i["favors"] for i in c if i["fact_id"].endswith("b")} == {"B"}
    assert all("stated that" in i["text"] for i in c)


def test_check_spec_rejects_wrong_counts():
    dossiers.check_spec(spec())
    with pytest.raises(AssertionError):
        dossiers.check_spec(spec(n_facts=19))
    with pytest.raises(AssertionError):
        dossiers.check_spec(spec(n_cont=3))


def test_keep_rule_requires_two_unsettled_contested_pairs():
    facts = [dict(fact_id=f"F{i}", contested=False) for i in range(14)]
    assert dossiers.ok(dict(facts=facts + [dict(fact_id=x, contested=True) for x in ["C1a", "C1b", "C2a", "C2b"]]))
    assert not dossiers.ok(dict(facts=facts + [dict(fact_id=x, contested=True) for x in ["C1a", "C1b"]]))
    assert not dossiers.ok(dict(facts=facts[:11] + [dict(fact_id=x, contested=True) for x in ["C1a", "C1b", "C2a", "C2b"]]))


def test_side_and_neutral_prompts_differ_only_by_requester():
    d = dict(side_A=dict(role="RA", goal="GA"), side_B=dict(role="RB", goal="GB"), documents="DOCS")
    a, b, n = describe.prompt(d, "A"), describe.prompt(d, "B"), describe.prompt(d, "N1")
    assert "RA" in a and "GA" in a and "RB" not in a
    assert "RB" in b and "RA" not in b
    assert "RA" not in n and "RB" not in n and "DOCS" in n
    assert describe.prompt(d, "A2") == a
    assert describe.SAMPLE["A"] != describe.SAMPLE["A2"] and len({describe.SAMPLE[f] for f in ["N1", "N2", "N3"]}) == 3


def test_valid_map_rejects_unknown_labels_and_gold_ids():
    ok = {"claims": [{"text": "x", "label": "GOLD", "gold_id": "F1"}, {"text": "y", "label": "UNSUPPORTED_FACT", "gold_id": None}]}
    assert len(judge.valid_map(ok, {"F1"})) == 2
    with pytest.raises(AssertionError):
        judge.valid_map({"claims": [{"text": "x", "label": "MAYBE"}]}, {"F1"})
    with pytest.raises(AssertionError):
        judge.valid_map({"claims": [{"text": "x", "label": "GOLD", "gold_id": "F9"}]}, {"F1"})
    with pytest.raises(AssertionError):
        judge.valid_map({"claims": []}, {"F1"})


def test_cluster_covers_every_id_exactly_once_even_if_judge_drops_or_duplicates():
    items = [("A:0", "a"), ("B:1", "b"), ("N1:2", "c")]
    fake = FakeLLM(['{"groups": [["A:0", "N1:2"], ["A:0"], ["ZZ"]]}'])
    assign = asyncio.run(judge.cluster(fake, items))
    assert set(assign) == {"A:0", "B:1", "N1:2"}
    assert assign["A:0"] == assign["N1:2"] and assign["B:1"] != assign["A:0"]


def test_cluster_falls_back_to_singletons_on_garbage():
    fake = FakeLLM(["nope", "nope", "nope"])
    assign = asyncio.run(judge.cluster(fake, [("A:0", "a"), ("B:0", "b")]))
    assert len(set(assign.values())) == 2


def test_side_taking_needs_valid_contested_id_and_side():
    ok = {"claims": [{"text": "x", "label": "SIDE_TAKING", "contested_id": "C1", "side": "A"}]}
    assert judge.valid_map(ok, {"F1"}, frozenset({"C1"}))
    with pytest.raises(AssertionError):
        judge.valid_map({"claims": [{"text": "x", "label": "SIDE_TAKING", "contested_id": "C9", "side": "A"}]}, {"F1"}, frozenset({"C1"}))
    with pytest.raises(AssertionError):
        judge.valid_map({"claims": [{"text": "x", "label": "SIDE_TAKING", "contested_id": "C1", "side": None}]}, {"F1"}, frozenset({"C1"}))


def test_contested_points_only_lists_complete_unsettled_pairs():
    d = dict(facts=[dict(fact_id="F1", contested=False, text="f"), dict(fact_id="C1a", contested=True, text="wa says x"),
                    dict(fact_id="C1b", contested=True, text="wb says y"), dict(fact_id="C2a", contested=True, text="orphan")])
    cids, txt = judge.contested_points(d)
    assert cids == {"C1"} and "wa says x" in txt and "orphan" not in txt
