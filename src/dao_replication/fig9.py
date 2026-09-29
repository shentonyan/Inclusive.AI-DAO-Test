"""Fig. 9: t-SNE of user messages from the human-AI chat, k = 4 clusters.

NOT the article's analysis: it embedded messages with OpenAI's Ada-2 model, which
is not available offline here. This module uses averaged spaCy `en_core_web_md`
word vectors instead (optional dependency, see README) and reports how stable the
result is. Cluster letters carry no correspondence to the article's cluster numbers.
No message text is written to any output.
"""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from .config import SEED  # noqa: E402
from .data import load_text  # noqa: E402
from .figures import INK, INK2, SURFACE, _base  # noqa: E402

STYLE = [("#f4778a", "o"), ("#a5a936", "s"), ("#2a9d92", "D"), ("#b8a6f2", "^")]  # as in the article: pink, olive, teal, lavender
KEYWORDS = {  # aggregate keyword shares only; used to compare with the themes named in the article's caption
    "nurse / CEO mentioned": r"\b(?:nurse|ceo)\b",
    "stereotype / bias / harm": r"stereotyp|\bbias|\bharm|hurt|offens|discriminat",
    "change / different / regenerate": r"\b(?:change|different|differently|regenerate|another|instead|redo|show|make)\b",
    "acknowledgement (yes/no/ok/thanks/hi)": r"^\s*(?:yes|no|ok|okay|sure|thanks|thank you|hello|hi|hey|nope|yeah)\b",
}


def spacy_available() -> bool:
    """True when scikit-learn, spaCy and the en_core_web_md model are all installed."""
    try:
        import sklearn  # noqa: F401
        import spacy

        spacy.load("en_core_web_md")
        return True
    except Exception:  # noqa: BLE001
        return False


def load_messages() -> pd.DataFrame:
    t = load_text("human_ai_chat")["text"].dropna().astype(str).str.strip()
    t = t[t != ""]
    vc = t.value_counts()
    return pd.DataFrame({"text": vc.index, "count": vc.to_numpy()})


def embed_spacy(texts) -> np.ndarray:
    import spacy
    from sklearn.preprocessing import normalize

    nlp = spacy.load("en_core_web_md", disable=["parser", "ner", "tagger", "lemmatizer", "attribute_ruler"])
    return normalize(np.array([nlp(x).vector for x in texts]))


def embed_tfidf(texts) -> np.ndarray:
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import normalize

    x = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True).fit_transform(texts)
    return normalize(TruncatedSVD(100, random_state=SEED).fit_transform(x))


def analyse(k: int = 4):
    from sklearn.cluster import KMeans
    from sklearn.manifold import TSNE
    from sklearn.metrics import adjusted_rand_score

    m = load_messages()
    emb = embed_spacy(m["text"])
    elbow = pd.DataFrame({"k": range(1, 11), "wcss": [KMeans(i, n_init=10, random_state=SEED).fit(emb).inertia_ for i in range(1, 11)]})
    km = KMeans(k, n_init=20, random_state=SEED).fit(emb)
    w = m["count"].to_numpy()
    lab = km.labels_
    order = np.argsort(-np.bincount(lab, weights=w))  # letter A = the largest cluster by messages
    remap = {old: new for new, old in enumerate(order)}
    m["cluster"] = [remap[i] for i in lab]
    xy = TSNE(2, perplexity=30, init="pca", random_state=SEED).fit_transform(emb)
    m["x"], m["y"] = xy[:, 0], xy[:, 1]
    # stability
    base = m["cluster"].to_numpy()
    ari_seed = [adjusted_rand_score(base, KMeans(k, n_init=10, random_state=s).fit_predict(emb)) for s in range(1, 9)]
    tf = KMeans(k, n_init=10, random_state=SEED).fit_predict(embed_tfidf(m["text"]))
    stab = pd.DataFrame([
        ("k-means seeds 1-8 vs. base run (ARI, min / median)", f"{min(ari_seed):.2f} / {np.median(ari_seed):.2f}"),
        ("TF-IDF+SVD embedding vs. word-vector embedding (ARI)", f"{adjusted_rand_score(base, tf):.2f}"),
        ("distinct messages / all messages", f"{len(m)} / {int(w.sum())}"),
    ], columns=["check", "value"])
    # cluster summary (aggregate only)
    rows = []
    words = m["text"].str.split().str.len()
    for c in range(k):
        s = m[m["cluster"] == c]
        ww = s["count"].to_numpy()
        row = {"cluster": "ABCD"[c], "messages": int(ww.sum()), "distinct": len(s),
               "median_words": float(np.repeat(words[s.index].to_numpy(), ww).size and np.median(np.repeat(words[s.index].to_numpy(), ww))),
               "pct_le3_words": 100 * float((ww * (words[s.index].to_numpy() <= 3)).sum() / ww.sum())}
        for name, pat in KEYWORDS.items():
            hit = s["text"].str.lower().str.contains(pat, flags=re.I, regex=True).to_numpy()
            row[name + " (%)"] = 100 * float((ww * hit).sum() / ww.sum())
        rows.append(row)
    return m, elbow, stab, pd.DataFrame(rows)


def fig9_paper_layout(m: pd.DataFrame, summary: pd.DataFrame, path: Path):
    fig, (ax, box) = plt.subplots(1, 2, figsize=(12.5, 5.4), gridspec_kw={"width_ratios": [1.6, 1]})
    fig.patch.set_facecolor(SURFACE)
    _base(ax)
    ax.grid(False)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(True)
    for c in range(4):
        s = m[m["cluster"] == c]
        col, mk = STYLE[c]
        ax.scatter(s["x"], s["y"], s=14 + 8 * np.log1p(s["count"]), c=col, marker=mk, alpha=0.6, linewidths=0, label=f"Cluster {'ABCD'[c]}")
    ax.legend(title="Cluster", frameon=True, fontsize=8, title_fontsize=8, loc="upper left", framealpha=0.9)
    ax.set_title("Replication attempt (spaCy word vectors, not Ada-2); marker size grows with message repeats", color=INK, fontsize=9.5, loc="left")
    box.axis("off")
    hdr = f"{'':<3}{'msgs':>6}{'median':>8}{'<=3 w':>7}"
    lines = [hdr + "   what the four keyword families hit (% of messages)"]
    box.text(0, 1.0, "Cluster summary (aggregate statistics only)", fontsize=10, color=INK, va="top", fontweight="bold")
    y = 0.9
    keys = list(KEYWORDS)
    for _, r in summary.iterrows():
        txt = (f"Cluster {r['cluster']}: {r['messages']} messages ({r['distinct']} distinct), median {r['median_words']:.0f} words, "
               f"{r['pct_le3_words']:.0f}% have <= 3 words")
        box.text(0, y, txt, fontsize=8.3, color=INK, va="top")
        detail = "; ".join(f"{k.split(' (')[0]} {r[k + ' (%)']:.0f}%" for k in keys)
        box.text(0.02, y - 0.055, detail, fontsize=7.4, color=INK2, va="top", wrap=True)
        y -= 0.19
    fig.tight_layout()
    fig.savefig(path, dpi=200, facecolor=SURFACE)
    plt.close(fig)


def fig_elbow(elbow: pd.DataFrame, path: Path):
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    fig.patch.set_facecolor(SURFACE)
    _base(ax)
    ax.plot(elbow["k"], elbow["wcss"], color="#2a78d6", marker="o", lw=2, ms=6, markeredgecolor=SURFACE)
    ax.axvline(4, color=INK2, ls=":", lw=1)
    ax.set_xlabel("k", color=INK2, fontsize=9)
    ax.set_ylabel("Within-cluster sum of squares", color=INK2, fontsize=9)
    ax.set_xticks(elbow["k"])
    ax.set_title("Elbow curve for the substitute embedding (dotted: the article's k = 4)", color=INK, fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(path, dpi=200, facecolor=SURFACE)
    plt.close(fig)
