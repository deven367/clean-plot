# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_heatmaps_novels.ipynb.

# %% ../nbs/03_heatmaps_novels.ipynb 3
from __future__ import annotations

import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from fastcore.all import *
from fastcore.xtras import *
from scipy.stats import zscore
from sklearn.metrics.pairwise import cosine_similarity

from .pickle import label
from .utils import *
from .utils import check_files

# %% auto 0
__all__ = [
    "heatmap_from_pkl",
    "plot_novels",
    "plot_histograms",
    "ssms_from_pkl",
    "corr_heatmaps",
    "corr_ts",
    "lex_ts",
    "plot_standardized",
]

# %% ../nbs/03_heatmaps_novels.ipynb 6
@call_parse
def heatmap_from_pkl(
    path: str = ".",  # path to pkl files
    min_labels: bool = False,  # flag to use shorter labels
    std: bool = False,  # flag to standardize
    corr: bool = False,  # flag to save corr plot
) -> None:
    "Plot timeseries from the pkl file"
    p = Path(path).absolute()
    files = globtastic(p, recursive=False, file_glob="*.pkl").map(Path)
    print(f"Current path {p}")

    if not check_files(files):
        return

    for f in files:
        title = f.stem.split("_whole")[0].replace("_", " ").title()
        print(title)
        data = load_pickle(f)
        for i in range(len(data)):
            try:
                df = pd.DataFrame(data[i])
            except:
                print("Corrupt data in the pkl file")

            vals = df.values
            if std:
                norm = zscore(normalize(vals))
            else:
                norm = normalize(vals)

            organized_labels = [
                "DeCLUTR Base",
                "InferSent FastText",
                "DistilBERT",
                "RoBERTa",
                "USE",
                "MPNet",
                "XLM",
                "MiniLM",
            ]
            sm_labels = [
                "DC",
                "I-F",
                "DB",
                "RB",
                "USE",
                "MPNet",
                "XLM",
                "MiniLM",
            ]

            df2 = df[organized_labels]

            if min_labels:
                df2.columns = sm_labels

            if corr:
                corr_path = p.parent / "corr"
                corr_path.mkdir(exist_ok=True)

                sns.heatmap(
                    df2.corr(),
                    cmap="hot",
                    vmin=0,
                    vmax=1,
                    xticklabels=False,
                    square=True,
                    annot=True,
                    fmt=".2f",
                )
                plt.savefig(
                    corr_path / f"{title}_corr.png",
                    dpi=300,
                    bbox_inches="tight",
                )
                plt.clf()

            if std:
                vmin = np.min(df2.values) - 1
                vmax = np.max(df2.values) + 1
                ts = p.parent / "ts_std"
                ts.mkdir(exist_ok=True)
            else:
                vmin = 0
                vmax = 1
                ts = p.parent / "ts"
                ts.mkdir(exist_ok=True)

            ax = sns.heatmap(
                df2.T,
                cmap="hot",
                vmin=vmin,
                vmax=vmax,
                xticklabels=100,
                yticklabels=df2.columns,
            )
            for j in range(len(df2.columns)):
                ax.axhline(j, color="white", lw=1)
            ticks = np.linspace(0, len(df), 5, dtype=int)
            labels = np.linspace(1, len(df), 5, dtype=int)
            plt.xticks(ticks, labels, rotation=0)
            plt.yticks(rotation=0)
            plt.savefig(ts / f"{title}_ts.png", dpi=300, bbox_inches="tight")
            plt.clf()
        print("-" * 45)


# %% ../nbs/03_heatmaps_novels.ipynb 9
@call_parse
def plot_novels(
    path: str = None,  # path for embeddings
    start: int = 0,  # start for section
    end: int = -1,  # end for section
    x: bool = False,  # x-ticks
    y: int = 5,  # y-ticks,
    std: bool = False,  # flag to standardize
):
    "Generates plots for embeddings in the folder"

    #     d = {}

    if start == 0 and end == -1:
        pass
    elif start >= 0 and end == -1:
        pass
    else:
        assert start < end, "Incorrect bounds"

    # Marker for xticks and yticks
    if x == -1:
        x = False
    if y == -1:
        y = False

    files = globtastic(path, recursive=False, file_glob="*.npy").map(Path)
    if not check_files(files):
        return

    curr = Path.cwd()
    if std:
        if start > 0:
            new_path = curr / f"sections_{start} {end}_std"
            new_path.mkdir(exist_ok=True)
        else:
            new_path = curr / "full_plots_std"
            new_path.mkdir(exist_ok=True)
    else:
        if start > 0:
            new_path = curr / f"sections_{start} {end}"
            new_path.mkdir(exist_ok=True)
        else:
            new_path = curr / "full_plots"
            new_path.mkdir(exist_ok=True)

    for f in files:
        arr = np.load(f)
        if "use" in f.stem:
            b = arr.shape[0]
            assert (
                b > end
            ), f"Incorrect bounds, book only contains {b} sentences"
        elif "xlm" in f.stem:
            b = arr.shape[0]
            assert (
                b > end
            ), f"Incorrect bounds, book only contains {b} sentences"

    for f in files:
        fname = f.stem.split("_cleaned_")
        book, method = fname[0], label(fname[1])
        book = book.replace("_", " ")

        title = f"{book.title()} {method}"

        em = np.load(f)

        if end == -1:
            end = len(em)

        ticks = np.linspace(1, end - start, y, dtype=int)

        if start == 0:
            labels = np.linspace(start + 1, end, y, dtype=int)
        else:
            labels = np.linspace(start, end, y, dtype=int)

        if fname[1] == "lexical_wt_ssm":
            sim = em
            print(em.shape)
            n = normalize(sim)
            np.fill_diagonal(sim, 1)
        else:
            sim = cosine_similarity(em, em)
            n = normalize(sim)

        if std:
            numerator = n - np.mean(n)
            denominator = np.sqrt(np.sum(numerator**2) / (numerator.size - 1))

            ab1 = numerator / denominator
            n = ab1

            if np.min(n) < 0:
                vmin = int(np.min(n)) - 1
            vmax = int(np.max(n)) + 1

            if end == -1:
                sns.heatmap(
                    n[start:, start:],
                    cmap="hot",
                    vmin=vmin,
                    vmax=vmax,
                    square=True,
                    xticklabels=False,
                )
            else:
                sns.heatmap(
                    n[start:end, start:end],
                    cmap="hot",
                    vmin=vmin,
                    vmax=vmax,
                    square=True,
                    xticklabels=False,
                )
        else:
            if end == -1:
                sns.heatmap(
                    n[start:, start:],
                    cmap="hot",
                    vmin=0,
                    vmax=1,
                    square=True,
                    xticklabels=False,
                )
            else:
                sns.heatmap(
                    n[start:end, start:end],
                    cmap="hot",
                    vmin=0,
                    vmax=1,
                    square=True,
                    xticklabels=False,
                )
        #         d[method] = n
        plt.yticks(ticks, labels, rotation=0)
        #         plt.title(title)
        plt.ylabel("sentence number")
        plt.savefig(new_path / f"{title}.png", dpi=300, bbox_inches="tight")
        print(f"Done plotting {title}.png")
        plt.clf()
        del em, sim, n


# %% ../nbs/03_heatmaps_novels.ipynb 11
from scipy.stats import zscore


# %% ../nbs/03_heatmaps_novels.ipynb 12
@call_parse
def plot_histograms(
    path: str, std: bool = False  # path for embeddings  # flag to standardize
):
    "Generates histograms for embeddings in the folder"

    d = {}

    files = loader(path, ".npy")
    curr = Path.cwd()
    if std:
        new_path = curr / f"histogram_std"
        new_path.mkdir(exist_ok=True)
    else:
        new_path = curr / f"histogram"
        new_path.mkdir(exist_ok=True)

    for f in files:
        fname = f.stem.split("_cleaned_")
        book, method = fname[0], label(fname[1])

        title = f"{book.replace('_', ' ').title()}"

        em = np.load(f)

        if fname[1] == "lexical_wt_ssm":
            sim = em
            print(em.shape)
            n = normalize(sim)
            np.fill_diagonal(sim, 1)
        else:
            sim = cosine_similarity(em, em)
            n = normalize(sim)

        if std:
            numerator = n - np.mean(n)
            denominator = np.sqrt(np.sum(numerator**2) / (numerator.size - 1))

            ab1 = numerator / denominator
            n = ab1

        n = n.astype("float32")
        print(f"Processed {method}")
        d[method] = n.flatten()
        del em, sim, n

    organized_labels = [
        "DeCLUTR Base",
        "InferSent FastText",
        "DistilBERT",
        "RoBERTa",
        "USE",
        "MPNet",
        "XLM",
        "MiniLM",
    ]

    label2 = ["DC", "I-F", "DB", "RB", "USE", "MPNet", "XLM", "MiniLM"]
    fig, ax = plt.subplots(4, 2, figsize=(4, 6), sharex=True, sharey=True)
    ssm_df = pd.DataFrame(d)
    k = 0
    for row in range(4):
        for col in range(2):
            x = ssm_df[organized_labels[k]]
            sns.histplot(zscore(x), ax=ax[row][col], binwidth=1)  # , bins=7
            ax[row][col].set_title(label2[k])
            #             ax[row][col].set_xlim(-5, 5)
            if row == 3:
                ax[row][col].set_xlabel("")
            k += 1
    plt.tight_layout()
    plt.savefig(new_path / f"{title}_hist.png", dpi=300, bbox_inches="tight")
    print(f"Done plotting {title}.png")


# %% ../nbs/03_heatmaps_novels.ipynb 13
import pandas as pd


# %% ../nbs/03_heatmaps_novels.ipynb 14
@call_parse
def ssms_from_pkl(
    path: str,  # path for pkl file
    start: int = 0,  # start for section
    end: int = -1,  # end for section
    x: bool = False,  # x-ticks
    y: int = 5,  # y-ticks
):
    "Generates SSMs from pkl files"
    if start == 0 and end == -1:
        pass
    else:
        assert start < end, "Incorrect bounds"

    curr = Path.cwd()
    if start > 0:
        new_path = curr / f"sections_{start} {end}"
        new_path.mkdir(exist_ok=True)
    else:
        new_path = curr / "full_plots"
        new_path.mkdir(exist_ok=True)

    files = loader(path, ".pkl")
    for f in files:
        d = load_dictionary(f)
        fname = f.stem.split("_ssms")
        for k, v in d.items():
            book = fname[0]
            title = f"{book.title()} {k}"
            sns.heatmap(
                v, cmap="hot", vmin=0, vmax=1, square=True, xticklabels=False
            )
            ticks = np.linspace(1, end - start, y, dtype=int)

            if start == 0:
                labels = np.linspace(start + 1, end, y, dtype=int)
            else:
                labels = np.linspace(start, end, y, dtype=int)

            plt.yticks(ticks, labels, rotation=0)
            plt.ylabel("sentence number")
            plt.savefig(
                new_path / f"{title}.pdf",
                format="pdf",
                dpi=300,
                bbox_inches="tight",
            )
            print(f"Done plotting {title}")
            plt.clf()


# %% ../nbs/03_heatmaps_novels.ipynb 15
@call_parse
def corr_heatmaps(
    path: str, std: bool = False  # path for embeddings  # standardize or not
):
    "Generates correlation plots from normalized SSMs"

    files = loader(path, ".npy")
    curr = Path.cwd()

    new_path = curr / f"corr_ssm"
    new_path.mkdir(exist_ok=True)

    d = {}
    for f in files:
        fname = f.stem.split("_cleaned_")
        book, method = fname[0], label(fname[1])

        em = np.load(f)

        if fname[1] == "lexical_wt_ssm":
            #             print(em.shape)
            sim = em
        else:
            sim = cosine_similarity(em, em)

        n = normalize(sim)

        # condition to standardize the
        if std:
            numerator = n - np.mean(n)
            denominator = np.sqrt(np.sum(numerator**2) / (numerator.size - 1))

            ab1 = numerator / denominator
            d[method] = ab1.flatten()
        else:
            d[method] = n.flatten()

        print(f"{method}: {n.shape}")
        del em, sim, n

    organized_labels = [
        "DeCLUTR Base",
        "DeCLUTR Small",
        "InferSent FastText",
        "InferSent GloVe",
        "DistilBERT",
        "RoBERTa",
        "USE",
        "Lexical Weights",
    ]
    df = pd.DataFrame(d)

    df = df[organized_labels]

    corr = df.corr()

    sns.heatmap(
        corr,
        cmap="hot",
        vmin=0,
        vmax=1,
        square=True,
        annot=True,
        xticklabels=False,
        yticklabels=df.columns,
        fmt=".2f",
    )

    title = f"{book.title()}"

    if std:
        np.save(new_path / f"{title}_corr_std_ssm.npy", corr)
        plt.savefig(
            new_path / f"{title}_corr_std_ssm.png", dpi=300, bbox_inches="tight"
        )
    else:
        np.save(new_path / f"{title}_corr_ssm.npy", corr)
    #     plt.title(title)
    #     plt.savefig(new_path/f'{title}_corr_ssm.png', dpi = 300, bbox_inches='tight')
    print(f"Done plotting {title}_corr_ssm.png")


#     plt.clf()


# %% ../nbs/03_heatmaps_novels.ipynb 16
@call_parse
def corr_ts(path: str):  # path for embeddings
    "Generates correlation plots from time series"
    files = loader(path, ".pkl")
    curr = Path.cwd()

    new_path = curr / f"corr_ts"
    new_path.mkdir(exist_ok=True)

    d = {}
    for f in files:
        fname = f.stem.split("_cleaned_")
        fname = open(f, "rb")
        data = pickle.load(fname)
        _plot(embedding_path, data, name)


# %% ../nbs/03_heatmaps_novels.ipynb 17
@call_parse
def lex_ts(path: str):  # path for embeddings
    "Generate lexical TS from Lexical SSM"

    files = loader(path, "wt_ssm.npy")
    curr = Path.cwd()

    for f in files:
        em = np.load(f)
        x = normalize(em)
        np.fill_diagonal(x, 1)

        z = []
        for i in range(len(x) - 1):
            z.append(x[i][i + 1])

        print(len(x))
        np.save(f"{f.stem[:-3]}ts", z)
        print(len(z))


# %% ../nbs/03_heatmaps_novels.ipynb 18
@call_parse
def plot_standardized(
    path: str,  # path for embeddings
    start: int = 0,  # start for section
    end: int = -1,  # end for section
    x: bool = False,  # x-ticks
    y: int = 5,  # y-ticks
):
    "Generates plots for embeddings in the folder"

    if start > end:
        assert "Incorrect bounds"

    # Marker for xticks and yticks
    if x == -1:
        x = False
    if y == -1:
        y = False

    files = loader(path, ".npy")
    curr = Path.cwd()
    if start > 0:
        new_path = curr / f"sections_{start} {end}"
        new_path.mkdir(exist_ok=True)
    else:
        new_path = curr / "full_plots"
        new_path.mkdir(exist_ok=True)

    for f in files:
        fname = f.stem.split("_cleaned_")
        book, method = fname[0], label(fname[1])

        title = f"{book.title()} {method}"

        em = np.load(f)

        if start == 0:
            start = 1

        if end == -1:
            end = len(em)

        ticks = np.linspace(1, end - start, 5, dtype=int)
        labels = np.linspace(start, end, 5, dtype=int)

        if fname[1] == "lexical_wt_ssm":
            sim = em
            print(em.shape)
            n = normalize(sim)
            np.fill_diagonal(sim, 1)
        else:
            sim = cosine_similarity(em, em)
            n = normalize(sim)

        numerator = n - np.mean(n)
        denominator = np.sqrt(np.sum(numerator**2) / (numerator.size - 1))

        ab1 = numerator / denominator

        sns.heatmap(
            ab1[start:end, start:end],
            cmap="hot",
            vmin=0,
            vmax=1,
            square=True,
            xticklabels=False,
        )

        plt.yticks(ticks, labels, rotation=0)
        #         plt.title(title)
        plt.ylabel("sentence number")
        plt.savefig(new_path / f"{title}.png", dpi=300, bbox_inches="tight")
        plt.savefig(new_path / f"{title}.pdf", dpi=300, bbox_inches="tight")
        print(f"Done plotting {title}")
        plt.clf()
        del em, sim, n, numerator, denominator, ab1
