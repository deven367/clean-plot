# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04_heatmaps_novels.ipynb (unless otherwise specified).

__all__ = ['plot_novels']

# Cell
from .core import loader
from .pickle import label
from .functions import normalize
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
from fastcore.all import *
from pathlib import Path

# Cell
@call_parse
def plot_novels(path: Param("path for embeddings"),
                start: Param("start for section", default=0, type=int),
                end: Param("end for section", default=-1, type=int),
                x: Param("x-ticks", default=50, type=int),
                y: Param("y-ticks", default=50, type=int)):
    "Generates plots for embeddings in the folder"

    assert start < end, 'Incorrect bounds'

    # Marker for xticks and yticks
    if x == -1:
        x = False
    if y == -1:
        y = False

    files = loader(path, '.npy')
    curr = Path.cwd()
    if start > 0:
        new_path = curr/f'sections_{start} {end}'
        new_path.mkdir(exist_ok=True)
    else:
        new_path = curr/'full_plots'
        new_path.mkdir(exist_ok=True)

    for f in files:
        fname = f.stem.split('_cleaned_')
        book, method = fname[0], label(fname[1])

        title = f'{book.title()} {method}'

        em = np.load(f)

        if end == -1:
            end = len(em)


        ticks = np.linspace(1, end - start, 5, dtype=int)

        if start == 0:
            labels = np.linspace(start + 1, end, 5, dtype=int)
        else:
            labels = np.linspace(start, end, 5, dtype=int)

        if fname[1] == 'lexical_wt_ssm':
            sim = em
            print(em.shape)
            n = normalize(sim)
            np.fill_diagonal(sim, 1)
        else:
            sim = cosine_similarity(em, em)
            n = normalize(sim)



        sns.heatmap(n[start:end, start:end], cmap='hot',
                    vmin=0, vmax=1, square=True,
                    xticklabels=False)


        plt.yticks(ticks, labels, rotation = 0)
#         plt.title(title)
        plt.ylabel('sentence number')
        plt.savefig(new_path/f'{title}.png', dpi = 300, bbox_inches='tight')
        print(f'Done plotting {title}.png')
        plt.clf()
        del em, sim, n