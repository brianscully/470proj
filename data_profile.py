from collections import Counter
import json
from pathlib import Path
import re
import statistics

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from papertrail.corpus import load_corpus


def describe(values):
    return {'min': min(values), 'median': statistics.median(values), 'mean': round(statistics.mean(values), 2), 'max': max(values)}


def profile():
    papers, manifest = load_corpus()
    output = Path('data/figures')
    output.mkdir(parents=True, exist_ok=True)
    categories = {c: sum(c in p['categories'] for p in papers) for c in ('cs.IR', 'cs.LG', 'cs.HC')}
    years = dict(sorted(Counter(p['year'] for p in papers).items()))
    lengths = {field: [len(re.findall(r'\b\w+\b', p[field])) for p in papers] for field in ('title', 'abstract')}
    stats = {'count': len(papers), 'category_membership': categories, 'year_counts': years, 'length_words': {field: describe(values) for field, values in lengths.items()}, 'min_submitted': min(p['submitted'] for p in papers), 'max_submitted': max(p['submitted'] for p in papers), 'snapshot_sha256': manifest['snapshot_sha256']}
    Path('data/profile.json').write_text(json.dumps(stats, indent=2), encoding='utf-8')
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    for name, counts, title in [('categories', categories, 'Category membership (cross-listings count)'), ('years', years, 'Original submission year')]:
        fig, ax = plt.subplots(figsize=(5.1, 3.0), layout='constrained')
        bars = ax.bar([str(k) for k in counts], list(counts.values()), color='#246a85')
        ax.bar_label(bars, padding=3)
        ax.set_ylim(0, max(counts.values()) * 1.18)
        ax.set_ylabel('Papers')
        ax.set_title(title, fontsize=11)
        fig.savefig(output / f'{name}.png', dpi=160)
        plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.1), layout='constrained')
    for ax, (field, values) in zip(axes, lengths.items()):
        ax.hist(values, bins=30, color='#246a85', edgecolor='white')
        ax.set_title(f'{field.title()} length', fontsize=11)
        ax.set_xlabel('Unicode word tokens')
        ax.set_ylabel('Papers')
    fig.savefig(output / 'lengths.png', dpi=160)
    plt.close(fig)
    print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    profile()
