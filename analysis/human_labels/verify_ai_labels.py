"""Validate saved AI annotation artifacts. Does not judge semantic correctness."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


def main():
    folder = Path(__file__).resolve().parent
    project = folder.parent.parent
    manifest = json.loads((folder / 'ai_labels_manifest.json').read_text())
    for name, expected in manifest['sha256'].items():
        actual = hashlib.sha256((project / name).read_bytes()).hexdigest()
        assert actual == expected, f'Changed since annotation freeze: {name}'
    source = json.loads(re.search(r'const ROWS=(.*?);const KEY=',
                                 (folder / 'label.html').read_text()).group(1))
    with (folder / 'ai_labels.csv').open(newline='') as stream:
        labels = list(csv.DictReader(stream))
    with (folder / 'ai_labels_audit.csv').open(newline='') as stream:
        audit = list(csv.DictReader(stream))
    assert len(labels) == len(audit) == len(source) == 100
    assert [int(row['item']) for row in labels] == list(range(1, 101))
    for original, label, detail in zip(source, labels, audit):
        assert str(original['item']) == label['item'] == detail['item']
        assert original['dossier_id'] == detail['dossier_id']
        assert original['text'] == detail['text']
        assert label['your_label'] == detail['ai_label']
        assert label['your_label'] in ('W', 'U', '')
        assert label['note'].startswith('AI-generated')
        assert detail['evidence'] and detail['rationale']
        if not label['your_label']:
            assert detail['review_flag'] == 'missing_context'
    assert (folder / 'ai_labels.csv').read_bytes() == (folder / 'my_labels.csv').read_bytes()
    counts = dict(Counter(row['your_label'] or 'abstain' for row in labels))
    assert counts == manifest['counts']
    print(f'PASS: 100 unique items; labels {counts}; provenance and hashes intact.')
    print('Semantic correctness and superiority to human labeling are not established by this check.')


if __name__ == '__main__':
    main()
