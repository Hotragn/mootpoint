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


def test_valid_map_rejects_unknown_labels_and_repairs_bad_gold_ids():
    ok = {"claims": [{"text": "x", "label": "GOLD", "gold_id": "F1"}, {"text": "y", "label": "UNSUPPORTED_FACT", "gold_id": None}]}
    assert len(judge.valid_map(ok, {"F1"})) == 2
    with pytest.raises(AssertionError):
        judge.valid_map({"claims": [{"text": "x", "label": "MAYBE"}]}, {"F1"})
    rep = judge.valid_map({"claims": [{"text": "x", "label": "GOLD", "gold_id": "F9"}]}, {"F1"})
    assert rep[0]["label"] == "SUPPORTED_OTHER" and rep[0]["repaired"] == "gold_id_missing"
    with pytest.raises(AssertionError):
        judge.valid_map({"claims": []}, {"F1"})


def test_side_taking_with_bad_side_is_kept_unwarranted_but_side_nulled():
    ok = judge.valid_map({"claims": [{"text": "x", "label": "SIDE_TAKING", "contested_id": "C1", "side": "A"}]}, {"F1"}, frozenset({"C1"}))
    assert ok[0]["side"] == "A" and ok[0]["repaired"] is None
    for bad in [{"contested_id": "C9", "side": "A"}, {"contested_id": "C1", "side": None}]:
        r = judge.valid_map({"claims": [{"text": "x", "label": "SIDE_TAKING", **bad}]}, {"F1"}, frozenset({"C1"}))
        assert r[0]["label"] == "SIDE_TAKING" and r[0]["side"] is None and r[0]["repaired"] == "side_missing"


def test_presence_and_prob_validators():
    assert judge.valid_presence({"N1:0": {"D1": "ASSERTS", "D2": "SILENT"}}, ["N1:0"], 2)
    with pytest.raises(AssertionError):
        judge.valid_presence({"N1:0": {"D1": "MAYBE", "D2": "SILENT"}}, ["N1:0"], 2)
    with pytest.raises(KeyError):
        judge.valid_presence({"N1:0": {"D1": "ASSERTS"}}, ["N1:0"], 2)
    assert judge.valid_probs({"N1:0": "0.3"}, ["N1:0"]) == {"N1:0": 0.3}
    with pytest.raises(AssertionError):
        judge.valid_probs({"N1:0": 1.5}, ["N1:0"])


def test_diverse_framings_are_non_stakeholders():
    d = dict(side_A=dict(role="RA", goal="GA"), side_B=dict(role="RB", goal="GB"), documents="DOCS")
    for f in ["P1", "P2"]:
        p = describe.prompt(d, f)
        assert "RA" not in p and "RB" not in p and describe.DIVERSE[f][0] in p


def test_contested_points_only_lists_complete_unsettled_pairs():
    d = dict(facts=[dict(fact_id="F1", contested=False, text="f"), dict(fact_id="C1a", contested=True, text="wa says x"),
                    dict(fact_id="C1b", contested=True, text="wb says y"), dict(fact_id="C2a", contested=True, text="orphan")])
    cids, txt = judge.contested_points(d)
    assert cids == {"C1"} and "wa says x" in txt and "orphan" not in txt


def test_debate_arm_argues_and_presence_excludes_it():
    d = dict(side_A=dict(role="RA", goal="GA"), side_B=dict(role="RB", goal="GB"), documents="DOCS")
    assert "strongest case" in describe.prompt(d, "DA") and "RA" in describe.prompt(d, "DA")
    assert "RB" in describe.prompt(d, "DB") and "strongest case" not in describe.prompt(d, "A")
    assert "DA" not in judge.OTHERS and "DB" not in judge.OTHERS  # frozen analysis expects exactly 7 presence framings
    assert judge.VCONTEXTS["v_closed_debate"] == ("DA", "DB") and judge.VCONTEXTS["v_closed"] == ("A", "B")
