"""Measure bar heights from the raster figures embedded in the article PDF.

Optional tooling (needs Pillow; PyMuPDF only to extract the images). The article's
Figures are not redistributed here; the measured values are in data/paper_figures/.

The article's Figs 5-7 are matplotlib grouped bar charts saved as PNG. Bars have
a black outline, the axes have a full frame, and the y-axis runs 1.0 (bottom
spine) to 5.0 (top spine). Heights are read from pixels:

  1. find the top and bottom spines (rows that are mostly dark) -> y calibration;
  2. classify every pixel column near the baseline by its dominant non-dark
     colour; runs of one colour are bars, dark runs are outlines / gaps;
  3. for each bar walk up from the baseline to the first white pixel; the last
     non-white row is the top of the outline.

Accuracy is about one pixel, i.e. 0.005-0.01 rating points at these resolutions.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from PIL import Image  # optional dependency: pip install pillow


@dataclass
class Bars:
    values: pd.DataFrame  # group, item, value, x0, x1
    y_top_px: float
    y_bottom_px: float
    geometry: dict | None = None


def _spines(rgb: np.ndarray) -> tuple[int, int, int, int]:
    """(left_x, right_x, top_y, bottom_y) of the dark frame."""
    dark = rgb.max(axis=2) < 90
    h, w = dark.shape
    row_frac = dark.mean(axis=1)
    col_frac = dark.mean(axis=0)
    rows = np.where(row_frac > 0.6)[0]
    cols = np.where(col_frac > 0.5)[0]
    if len(rows) < 2 or len(cols) < 1:
        raise ValueError("could not find the axes frame")
    # group consecutive rows -> spine centres
    def centres(idx):
        groups = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
        return [g.mean() for g in groups]
    rc = centres(rows)
    cc = centres(cols)
    return int(round(cc[0])), int(round(cc[-1])) if len(cc) > 1 else w - 1, rc[0], rc[-1]


def _colour_key(px: np.ndarray) -> np.ndarray:
    return (px // 24).astype(int)


def digitize(path: str, n_items: int, n_groups: int = 4, y_range=(1.0, 5.0), min_bar_px: int = 5,
             baseline_window: tuple[int, int] = (6, 140)) -> Bars:
    rgb = np.asarray(Image.open(path).convert("RGB")).astype(int)
    left, right, y_top, y_bot = _spines(rgb)
    H = rgb.shape[0]
    y_bot_i = int(round(y_bot))

    # per-column dominant non-dark, non-white colour in a strip above the baseline
    lo, hi = baseline_window
    strip = rgb[y_bot_i - hi : y_bot_i - lo, :, :]
    labels: list[tuple | None] = []
    for x in range(left + 2, right - 1):
        col = strip[:, x, :]
        bright = col.max(axis=1)
        keep = (bright > 110) & (col.min(axis=1) < 235)
        if keep.sum() < 0.3 * len(col):
            labels.append(None)
            continue
        keys = [tuple(k) for k in _colour_key(col[keep])]
        vals, counts = np.unique(np.array(keys), axis=0, return_counts=True)
        labels.append(tuple(vals[counts.argmax()]))

    # runs of the same colour
    runs = []
    start = None
    cur = None
    for i, lab in enumerate(labels + [None]):
        if lab != cur:
            if cur is not None and start is not None and i - start >= min_bar_px:
                runs.append((start + left + 2, i - 1 + left + 2, cur))
            start, cur = i, lab
    # merge neighbouring runs of the same colour separated by a hatch line (<=3 px)
    merged = []
    for r in runs:
        if merged and merged[-1][2] == r[2] and r[0] - merged[-1][1] <= 3:
            merged[-1] = (merged[-1][0], r[1], r[2])
        else:
            merged.append(r)
    runs = merged

    if len(runs) != n_items * n_groups:
        raise ValueError(f"found {len(runs)} bars, expected {n_items * n_groups}: {[(a, b) for a, b, _ in runs]}")

    rows = []
    for k, (x0, x1, _) in enumerate(runs):
        g, i = divmod(k, n_items)
        w = x1 - x0
        xs = range(x0 + int(0.25 * w), x1 - int(0.25 * w) + 1)
        tops = []
        for x in xs:
            y = y_bot_i - 3
            while y > 0 and rgb[y, x].min() < 235:
                y -= 1
            tops.append(y + 1)  # first row of the non-white run = top of the outline
        top = float(np.median(tops)) + 1.0  # centre of the ~2 px outline
        val = y_range[0] + (y_bot - top) / (y_bot - y_top) * (y_range[1] - y_range[0])
        rows.append({"group": g, "item": i, "value": val, "x0": x0, "x1": x1, "top_px": top})
    return Bars(pd.DataFrame(rows), y_top, y_bot)


def digitize_geometry(path: str, n_items: int, n_groups: int = 4, y_range=(1.0, 5.0), min_bar_px: int = 5,
                      baseline_window=(6, 140)) -> Bars:
    """Same measurement, but bar positions come from group geometry (equal-width
    bars, equal group spacing) instead of colour runs, which patterned fills break."""
    rgb = np.asarray(Image.open(path).convert("RGB")).astype(int)
    left, right, y_top, y_bot = _spines(rgb)
    y_bot_i = int(round(y_bot))
    # find the leftmost/rightmost bar pixels near the baseline to get group extents
    strip = rgb[y_bot_i - baseline_window[1] : y_bot_i - baseline_window[0], left + 3 : right - 2, :]
    nonwhite = (strip.min(axis=2) < 235).mean(axis=0) > 0.5
    xs = np.where(nonwhite)[0] + left + 3
    clusters = np.split(xs, np.where(np.diff(xs) > 60)[0] + 1)
    clusters = [c for c in clusters if len(c) > 20]
    starts = [c[0] for c in clusters]
    ends = [c[-1] for c in clusters]
    if len(clusters) < 2:
        raise ValueError("could not find group clusters")
    widths = [e - s for s, e in zip(starts, ends)]
    gw = float(np.median(widths))
    spacing = float(np.median(np.diff(starts)))
    # extrapolate missing groups
    while len(starts) < n_groups:
        starts.append(starts[-1] + spacing)
    starts = starts[:n_groups]
    pitch = gw / n_items
    rows = []
    for g, s in enumerate(starts):
        for i in range(n_items):
            x0 = s + i * pitch
            x1 = x0 + pitch
            xs_c = range(int(x0 + 0.3 * pitch), int(x1 - 0.3 * pitch) + 1)
            tops = []
            for x in xs_c:
                y = y_bot_i - 3
                while y > 0 and rgb[y, x].min() < 235:
                    y -= 1
                tops.append(y + 1)
            top = float(np.median(tops)) + 1.0
            val = y_range[0] + (y_bot - top) / (y_bot - y_top) * (y_range[1] - y_range[0])
            rows.append({"group": g, "item": i, "value": val, "x0": x0, "x1": x1, "top_px": top})
    b = Bars(pd.DataFrame(rows), y_top, y_bot)
    b.geometry = {"starts": starts, "group_width": gw, "spacing": spacing, "pitch": pitch}
    return b
