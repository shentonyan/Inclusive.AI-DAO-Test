"""Make `dao_replication` importable when running pytest from a fresh checkout
(without `pip install -e .`)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
