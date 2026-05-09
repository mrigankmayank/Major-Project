"""Diagnostic plots: actual vs predicted, residual distribution, risk ranking."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from bihar_health_risk.config import DISTRICT_COL, FIGURES_DIR, TARGET_COL


def plot_actual_vs_predicted(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    title: str,
    out_path: Path,
) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(y_true, y_pred, alpha=0.75, edgecolors="k", linewidths=0.3)
    lims = [min(y_true.min(), y_pred.min()), max(y_true.max(), y_pred.max())]
    ax.plot(lims, lims, "r--", lw=1, label="y = x")
    ax.set_xlabel(f"Actual {TARGET_COL}")
    ax.set_ylabel("Predicted (out-of-fold)")
    ax.set_title(title)
    ax.legend(loc="upper left")
    ax.set_aspect("equal", adjustable="box")
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_top_district_risk(
    df: pd.DataFrame,
    pred_col: str,
    out_path: Path,
    top_n: int = 15,
) -> Path:
    """Horizontal bar chart of highest predicted risk districts."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sub = df[[DISTRICT_COL, pred_col]].dropna().sort_values(pred_col, ascending=False).head(top_n)
    fig, ax = plt.subplots(figsize=(8, max(4, 0.35 * len(sub))))
    ax.barh(sub[DISTRICT_COL][::-1], sub[pred_col][::-1], color="steelblue")
    ax.set_xlabel(pred_col)
    ax.set_title(f"Top {top_n} districts by predicted risk")
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_residuals(y_true: np.ndarray, y_pred: np.ndarray, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    r = y_pred - y_true
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(r, bins=15, color="gray", edgecolor="black", alpha=0.85)
    ax.axvline(0, color="r", linestyle="--")
    ax.set_title("Residuals (predicted − actual)")
    ax.set_xlabel("Percentage points")
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path
