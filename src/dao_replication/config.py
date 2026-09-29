"""Paths, file names and label conventions shared by all modules."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SEED = 20260930

FILES = {
    "vote_round1": "anonymous_round1_vote.csv",
    "vote_round2": "anonymous_round3_vote.csv",  # the file name says "round3"; see docs/REPRODUCIBILITY.md
    "gov_survey": "anonymized_gov-survey_two_rounds.csv",
    "value_survey": "anonymized_value-survey_two_rounds.csv",
    "human_ai_chat": "Human-AI-chat.csv",
    "group_discussion": "Group-Discussion.csv",
}

CHOICES = ["choice_1", "choice_2", "choice_3", "choice_4"]
RATIOS = ["r1", "r2", "r3", "r4"]

CHOICE_LABELS = {
    "choice_1": "Use the current model",
    "choice_2": "Use additional user information",
    "choice_3": "Track and apply user preferences",
    "choice_4": "Add specific flags/tags",
}

# Order used in the paper's Table 1: quadratic first, equal power first.
CONDITIONS = ["quadratic-equal", "quadratic-early", "ranked-equal", "ranked-early"]

# "early" in the data files corresponds to the paper's "20/80" condition.
CONDITION_LABELS = {
    "quadratic-equal": "Quadratic, equal",
    "quadratic-early": "Quadratic, 20/80",
    "ranked-equal": "Ranked, equal",
    "ranked-early": "Ranked, 20/80",
}


def data_dir() -> Path:
    """Folder holding the OSF CSV files (env var DAO_DATA_DIR, default data/raw)."""
    env = os.environ.get("DAO_DATA_DIR")
    return Path(env) if env else REPO_ROOT / "data" / "raw"


def results_dir() -> Path:
    """Output folder (env var DAO_RESULTS_DIR, default results/)."""
    p = Path(os.environ.get("DAO_RESULTS_DIR", REPO_ROOT / "results"))
    p.mkdir(parents=True, exist_ok=True)
    return p


def data_path(key: str) -> Path:
    path = data_dir() / FILES[key]
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Download the OSF archive and unzip it into "
            f"{data_dir()} (see data/README.md), or set DAO_DATA_DIR."
        )
    return path
