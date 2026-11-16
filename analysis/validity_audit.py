"""Exploratory source/extraction sensitivity and frozen AI annotation agreement.

See VALIDITY-AUDIT-PROTOCOL.md. Never modifies original results or annotations.
"""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from analyze import Boot, N_BOOT, SEED, describe, h1a_arr
from robustness_extra import load

ROOT = Path(__file__).resolve().parents[1]
LABELS = ROOT / 'analysis/human_labels'
BAD_DOSSIERS = {'product-19', 'protest-30', 'workplace-14', 'product-17', 'tenancy-21'}
META = {('product-17', 'gemma-4-31b-it', 'N1:15'),
        ('workplace-07', 'glm-53-flash', 'N1:15')}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def agreement(frame, column):
    d = frame.dossier_id.to_numpy()
    a = frame.ai_y.to_numpy(int)
    b = frame[column].to_numpy(int)
    boot = Boot(sorted(set(d)), N_BOOT, SEED)
    n = boot.dsum(d, np.ones(len(d)))
    observed = boot.dsum(d, a == b) / n
    pa, pb = boot.dsum(d, a) / n, boot.dsum(d, b) / n
    chance = pa * pb + (1-pa) * (1-pb)
    with np.errstate(invalid='ignore', divide='ignore'):
        kappa = (observed - chance) / (1-chance)
    return {'agreement': describe(observed), 'kappa': describe(kappa),
            'n': len(a), 'n_dossiers': len(set(d)),
            'confusion_ai_rows_judge_columns_W_U': [
                [int(((a == i) & (b == j)).sum()) for j in (0, 1)] for i in (0, 1)],
            'disagreement_items': frame.loc[a != b, 'item'].astype(int).tolist()}


def evaluate(frame):
    d, y = frame.dossier_id.to_numpy(), frame.y.to_numpy(int)
    boot = Boot(sorted(set(d)), N_BOOT, SEED)
    detectors = ['OPP', 'SC', 'DIV', 'v_closed_none', 'v_closed']
    if 'xs_none' in frame:
        detectors.append('xs_none')
    arrays = {name: boot.auroc(d, y, frame[name].to_numpy(float)) for name in detectors}
    out = {'n_claims': len(frame), 'n_unwarranted': int(y.sum()), 'n_dossiers': len(set(d)),
           'auroc': {name: describe(values) for name, values in arrays.items()},
           'differences': {name: describe(arrays[a]-arrays[b]) for name, a, b in [
               ('OPP_minus_SC', 'OPP', 'SC'), ('OPP_minus_DIV', 'OPP', 'DIV'),
               ('reader_minus_SC', 'v_closed_none', 'SC'),
               ('opposed_context_gain', 'v_closed', 'v_closed_none')]}}
    warranted = frame[frame.y == 0]
    out['warranted_repeated_by_both'] = {
        pair: float((warranted[f'k_{pair}'] == 2).mean()) for pair in ('OPP', 'SC')}
    return out


def main():
    manifest = json.loads((LABELS/'ai_labels_manifest.json').read_text())
    for name, expected in manifest['sha256'].items():
        assert digest(ROOT/name) == expected, f'Frozen input changed: {name}'
    audit = pd.read_csv(LABELS/'ai_labels_audit.csv', keep_default_na=False)
    assert set(audit.loc[audit.review_flag == 'inconsistent_source', 'dossier_id']) == BAD_DOSSIERS
    key = pd.read_csv(LABELS/'key_DO_NOT_OPEN_BEFORE_LABELLING.csv')
    joined = audit.merge(key, on=['item', 'dossier_id'], validate='one_to_one')
    assert len(joined) == 100
    labelled = joined[joined.ai_label.isin(['W', 'U'])].copy()
    labelled['ai_y'] = (labelled.ai_label == 'U').astype(int)
    labelled['y2'] = labelled.label2.isin(['SIDE_TAKING', 'UNSUPPORTED_FACT']).astype(int)
    out = {'note': 'Exploratory post-test sensitivity, not a corrected gold benchmark or human validation.',
           'protocol_sha256': digest(ROOT/'analysis/VALIDITY-AUDIT-PROTOCOL.md'),
           'script_sha256': digest(Path(__file__)), 'seed': SEED, 'bootstrap_resamples': N_BOOT,
           'ai_labels_sha256': digest(LABELS/'ai_labels.csv'),
           'key_sha256': digest(LABELS/'key_DO_NOT_OPEN_BEFORE_LABELLING.csv'),
           'coverage': {'labelled': len(labelled), 'sampled': len(joined), 'abstained_items': [82]},
           'excluded_dossiers': sorted(BAD_DOSSIERS),
           'agreement': {'judge1': agreement(labelled, 'y'), 'judge2': agreement(labelled, 'y2')},
           'runs': {}}
    labelled[['item', 'dossier_id', 'model', 'claim_id', 'ai_label', 'label', 'label2',
              'evidence', 'review_flag', 'rationale']].to_csv(
                  LABELS/'ai_judge_comparison.csv', index=False)
    excerpts = []
    for run in ('test', 'test_r1'):
        frame, result_dir = load(run)
        subsets = {'original': frame, 'exclude_flagged_dossiers': frame[~frame.dossier_id.isin(BAD_DOSSIERS)]}
        descriptions = pd.read_json(ROOT/'runs'/run/'descriptions.jsonl', lines=True)
        neutral = descriptions[(descriptions.framing == 'N1') & ~descriptions.excluded].copy()
        neutral['actual_words'] = neutral.text.str.split().str.len()
        neutral['length_compliant'] = neutral.actual_words.between(200, 300)
        compliant = set(map(tuple, neutral.loc[neutral.length_compliant, ['dossier_id', 'model']].to_numpy()))
        keep_length = np.array([tuple(row) in compliant for row in frame[['dossier_id', 'model']].to_numpy()])
        subsets['exclude_glm_generator'] = frame[frame.model != 'glm-53-flash']
        subsets['N1_length_compliant'] = frame[keep_length]
        out.setdefault('output_compliance', {})[run] = {
            model: {'n_nonempty_N1': len(group), 'n_length_compliant': int(group.length_compliant.sum()),
                    'min_words': int(group.actual_words.min()), 'median_words': float(group.actual_words.median()),
                    'max_words': int(group.actual_words.max())} for model, group in neutral.groupby('model')}
        if run == 'test':
            meta_mask = np.array([tuple(row) in META for row in frame[['dossier_id', 'model', 'claim_id']].to_numpy()])
            assert int(meta_mask.sum()) == 2
            subsets['exclude_meta_claims'] = frame[~meta_mask]
            subsets['exclude_dossiers_and_meta_claims'] = frame[~meta_mask & ~frame.dossier_id.isin(BAD_DOSSIERS)]
            for did, model, claim_id in sorted(META):
                claim = frame[(frame.dossier_id == did) & (frame.model == model) & (frame.claim_id == claim_id)].iloc[0]
                desc = descriptions[(descriptions.dossier_id == did) & (descriptions.model == model) & (descriptions.framing == 'N1')]
                assert len(desc) == 1
                excerpts.append({'dossier_id': did, 'model': model, 'claim_id': claim_id,
                                 'extracted_claim': claim['text'], 'original_description': desc.iloc[0]['text']})
        out['runs'][run] = {}
        drift = pd.read_csv(result_dir/'per_cell_drift.csv')
        for name, subset in subsets.items():
            out['runs'][run][name] = evaluate(subset)
            if name in ('original', 'exclude_flagged_dossiers'):
                dd = drift if name == 'original' else drift[~drift.dossier_id.isin(BAD_DOSSIERS)]
                out['runs'][run][name]['H1a'] = describe(h1a_arr(Boot(sorted(dd.dossier_id.unique()), N_BOOT, SEED), dd))
            print(run, name, out['runs'][run][name]['differences']['OPP_minus_SC'], flush=True)
    target = ROOT/'analysis/results/validity_audit'
    target.mkdir(parents=True, exist_ok=True)
    (target/'results.json').write_text(json.dumps(out, indent=2)+'\n')
    (target/'extraction_examples.json').write_text(json.dumps(excerpts, indent=2)+'\n')
    print(json.dumps(out['agreement'], indent=2))


if __name__ == '__main__':
    main()
