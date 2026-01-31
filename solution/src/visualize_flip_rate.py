"""
High-quality flip-rate plot by season (counterfactual simulation results).
Conforms to docs/visualization_standards.md.
"""
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


def compute_flip_rate_by_season(results_df: pd.DataFrame, mode: str = "any") -> pd.DataFrame:
    """
    Compute flip rate per season.

    mode:
      - "any": 1 - all_same (any rule differs)
      - "rank_vs_percent": 1 - rank_vs_percent_same
    """
    if mode == "any":
        col = "all_same"
    elif mode == "rank_vs_percent":
        col = "rank_vs_percent_same"
    else:
        raise ValueError(f"Unknown mode: {mode}")

    season_flip = (
        results_df
        .groupby("season")[col]
        .mean()
        .reset_index()
        .rename(columns={col: "same_rate"})
    )
    season_flip["flip_rate"] = 1.0 - season_flip["same_rate"]
    return season_flip[["season", "flip_rate"]]


def plot_flip_rate_by_season(results_path: Path, output_dir: Path, mode: str = "any") -> Path:
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
        "lines.linewidth": 1.5,
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
    season_flip = compute_flip_rate_by_season(results_df, mode=mode)

    seasons = season_flip["season"].tolist()
    flip_rates = season_flip["flip_rate"].tolist()

    highlight = {2: "S2", 11: "S11", 27: "S27"}
    highlight_color = COLORS["orange"]
    line_color = COLORS["primary_blue"]

    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(
        seasons,
        flip_rates,
        color=line_color,
        linewidth=1.5,
        marker="o",
        markersize=4,
        label="Flip rate",
    )

    # Highlight controversy seasons
    for s, label in highlight.items():
        if s in seasons:
            y = season_flip.loc[season_flip["season"] == s, "flip_rate"].iloc[0]
            ax.scatter([s], [y], color=highlight_color, s=36, zorder=3)
            ax.text(s, y + 0.03, label, ha="center", va="bottom", color=highlight_color, fontsize=8)

    ax.set_xlabel("Season")
    ax.set_ylabel("Flip rate (%)")
    ax.set_title("Rule flip rate by season")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylim(0, max(0.15, max(flip_rates) + 0.1))

    ax.grid(True, axis="y", alpha=0.3, linewidth=0.5, color=COLORS["gray"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_png = output_dir / "timeseries_flip_rate_by_season_v1.png"
    out_pdf = output_dir / "timeseries_flip_rate_by_season_v1.pdf"
    fig.tight_layout()
    fig.savefig(out_png, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")
    fig.savefig(out_pdf, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)

    return out_png


if __name__ == "__main__":
    import sys
    from pathlib import Path

    src_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(src_dir))
    from config import DATA_DIR

    results_path = DATA_DIR / "simulation" / "simulation_results.csv"
    output_dir = DATA_DIR.parent / "figures" / "counterfactual"

    plot_flip_rate_by_season(results_path, output_dir, mode="any")
