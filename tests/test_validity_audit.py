"""Independent small checks for the new audit calculations, not the frozen analyses."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'analysis'))
from validity_audit import agreement, evaluate


def test_agreement_confusion_and_kappa():
    f = pd.DataFrame({'dossier_id':['a','b','c','d'], 'item':[1,2,3,4],
                      'ai_y':[0,0,1,1], 'judge':[0,1,1,1]})
    r = agreement(f, 'judge')
    assert r['agreement']['estimate'] == .75
    assert r['kappa']['estimate'] == .5
    assert r['confusion_ai_rows_judge_columns_W_U'] == [[1,1],[0,2]]
    assert r['disagreement_items'] == [2]


def test_paired_auroc_on_hand_computed_orderings():
    f = pd.DataFrame({'dossier_id':['a','a','b','b'], 'y':[0,1,0,1],
        'OPP':[0,1,0,1], 'SC':[1,1,1,1], 'DIV':[1,0,1,0],
        'v_closed_none':[0,1,0,1], 'v_closed':[0,1,0,1],
        'k_OPP':[2,1,2,1], 'k_SC':[1,1,1,1]})
    r = evaluate(f)
    assert r['auroc']['OPP']['estimate'] == 1
    assert r['auroc']['SC']['estimate'] == .5
    assert r['auroc']['DIV']['estimate'] == 0
    assert r['differences']['OPP_minus_SC']['estimate'] == .5
    assert r['differences']['opposed_context_gain']['estimate'] == 0
    assert r['warranted_repeated_by_both'] == {'OPP':1., 'SC':0.}
