"""
Consistency heatmap by season and week (Rank Sum vs actual elimination).
Conforms to docs/visualization_standards.md.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


def build_consistency_matrix(results_df: pd.DataFrame) -> tuple[np.ndarray, list[int], list[int]]:
    df = results_df.copy()
    df = df.dropna(subset=["season", "week", "actual_eliminated", "rank_sum_eliminated"])
    df["match"] = (df["actual_eliminated"] == df["rank_sum_eliminated"]).astype(int)

    seasons = sorted(df["season"].unique().astype(int).tolist())
    weeks = sorted(df["week"].unique().astype(int).tolist())

    season_index = {s: i for i, s in enumerate(seasons)}
    week_index = {w: i for i, w in enumerate(weeks)}

    matrix = np.full((len(seasons), len(weeks)), np.nan)
    for _, row in df.iterrows():
        s = int(row["season"])
        w = int(row["week"])
        matrix[season_index[s], week_index[w]] = int(row["match"])

    return matrix, seasons, weeks


def plot_consistency_heatmap(results_path: Path, output_dir: Path) -> Path:
    # Styling (aligned with visualization_standards.md)
    plt.style.use("seaborn-v0_8-paper")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 9,
        "axes.labelsize": 10,
        "axes.titlesize": 11,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
    })
    COLORS = {
        "primary_blue": "#0072B2",
        "light_blue": "#56B4E9",
        "orange": "#E69F00",
        "red_orange": "#D55E00",
        "green": "#009E73",
        "yellow": "#F0E442",
        "purple": "#CC79A7",
        "black": "#000000",
        "gray": "#808080",
    }

    results_df = pd.read_csv(results_path)
    matrix, seasons, weeks = build_consistency_matrix(results_df)

    # Two-color map: 0 = incorrect, 1 = correct
    cmap = ListedColormap([COLORS["red_orange"], COLORS["light_blue"]])

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1)

    ax.set_xlabel("Week")
    ax.set_ylabel("Season")
    ax.set_title("Consistency heatmap (Rank Sum vs actual elimination)")

    # Ticks
    x_ticks = list(range(len(weeks)))
    ax.set_xticks(x_ticks[::2])
    ax.set_xticklabels([str(weeks[i]) for i in x_ticks[::2]])

    y_ticks = list(range(len(seasons)))
    ax.set_yticks(y_ticks[::2])
    ax.set_yticklabels([str(seasons[i]) for i in y_ticks[::2]])

    # Highlight controversy seasons in y-axis labels
    highlight = {2, 11, 27}
    for label in ax.get_yticklabels():
        try:
            val = int(label.get_text())
            if val in highlight:
                label.set_color(COLORS["orange"])
        except ValueError:
            continue

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_ticks([0, 1])
    cbar.set_ticklabels(["Incorrect", "Correct"])

    # Spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_png = output_dir / "heatmap_consistency_by_season_week_v1.png"
    out_pdf = output_dir / "heatmap_consistency_by_season_week_v1.pdf"
    fig.tight_layout()
    fig.savefig(out_png, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")
    fig.savefig(out_pdf, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)

    return out_png


if __name__ == "__main__":
    import sys

    src_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(src_dir))
    from config import DATA_DIR

    results_path = DATA_DIR / "simulation" / "simulation_results.csv"
    output_dir = DATA_DIR.parent / "figures" / "consistency"

    plot_consistency_heatmap(results_path, output_dir)
