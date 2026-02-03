"""
3D Consistency Visualization: Season-Week Elimination Match Analysis
Advanced scientific visualization with publication-ready styling.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LinearSegmentedColormap, Normalize


def build_consistency_matrix(results_df: pd.DataFrame) -> tuple[np.ndarray, list[int], list[int]]:
    """Build consistency matrix from simulation results."""
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


def create_3d_bar_chart(results_path: Path, output_dir: Path, view_angle: tuple = (30, 45)) -> Path:
    """
    Create 3D bar chart visualization of consistency data.

    Args:
        results_path: Path to simulation results CSV
        output_dir: Output directory for figures
        view_angle: Tuple of (elevation, azimuth) for 3D view

    Returns:
        Path to saved PNG file
    """
    # Professional styling
    plt.style.use("seaborn-v0_8-paper")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.dpi": 300,
        "savefig.dpi": 300,
    })

    # Enhanced color scheme with deeper colors for better contrast
    COLORS = {
        "correct": "#1E40AF",      # Deep blue for correct predictions
        "incorrect": "#DC2626",    # Deep red for incorrect
        "neutral": "#FEF3C7",      # Light yellow for missing data
    }

    # Load and process data
    results_df = pd.read_csv(results_path)
    matrix, seasons, weeks = build_consistency_matrix(results_df)

    # Create figure with 3D axis
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Prepare data for 3D bars
    xpos, ypos = np.meshgrid(np.arange(len(weeks)), np.arange(len(seasons)))
    xpos = xpos.flatten()
    ypos = ypos.flatten()
    zpos = np.zeros_like(xpos)

    # Bar dimensions
    dx = dy = 0.8  # Bar width (leave gaps for visibility)
    dz = matrix.T.flatten()  # Heights (transposed to match x-y orientation)

    # Color mapping: blue for correct (1), orange for incorrect (0), gray for NaN
    colors = []
    for val in dz:
        if np.isnan(val):
            colors.append(COLORS["neutral"])
        elif val == 1:
            colors.append(COLORS["correct"])
        else:
            colors.append(COLORS["incorrect"])

    # Create 3D bars
    ax.bar3d(xpos, ypos, zpos, dx, dy, dz,
             color=colors,
             shade=True,
             alpha=0.9,
             edgecolor='white',
             linewidth=0.5)

    # Axis labels and title
    ax.set_xlabel('Week', fontsize=11, labelpad=10)
    ax.set_ylabel('Season', fontsize=11, labelpad=10)
    ax.set_zlabel('Match Rate', fontsize=11, labelpad=10)
    ax.set_title('Elimination Prediction Consistency: Rank Sum vs Actual\n3D Season-Week Analysis',
                 fontsize=13, fontweight='bold', pad=20)

    # Set ticks
    ax.set_xticks(np.arange(0, len(weeks), 2) + 0.4)
    ax.set_xticklabels([str(weeks[i]) for i in range(0, len(weeks), 2)])

    ax.set_yticks(np.arange(0, len(seasons), 2) + 0.4)
    ax.set_yticklabels([str(seasons[i]) for i in range(0, len(seasons), 2)])

    ax.set_zticks([0, 0.5, 1])
    ax.set_zticklabels(['0\n(Incorrect)', '0.5', '1\n(Correct)'])

    # Reverse week axis (X-axis in bar3d plot)
    ax.invert_xaxis()

    # Set view angle
    ax.view_init(elev=view_angle[0], azim=view_angle[1])

    # Grid styling
    ax.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('gray')
    ax.yaxis.pane.set_edgecolor('gray')
    ax.zaxis.pane.set_edgecolor('gray')
    ax.xaxis.pane.set_alpha(0.1)
    ax.yaxis.pane.set_alpha(0.1)
    ax.zaxis.pane.set_alpha(0.1)

    # Add custom legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS["correct"], edgecolor='white', label='Correct Prediction'),
        Patch(facecolor=COLORS["incorrect"], edgecolor='white', label='Incorrect Prediction'),
        Patch(facecolor=COLORS["neutral"], edgecolor='white', label='No Data')
    ]
    ax.legend(handles=legend_elements, loc='upper left', frameon=True,
              fancybox=True, shadow=True, framealpha=0.9)

    # Save figure
    output_dir.mkdir(parents=True, exist_ok=True)
    angle_suffix = f"_elev{view_angle[0]}_azim{view_angle[1]}"
    out_png = output_dir / f"heatmap_consistency_3d{angle_suffix}.png"
    out_pdf = output_dir / f"heatmap_consistency_3d{angle_suffix}.pdf"

    plt.tight_layout()
    fig.savefig(out_png, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")
    fig.savefig(out_pdf, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)

    return out_png


def create_3d_surface_plot(results_path: Path, output_dir: Path, view_angle: tuple = (30, 45)) -> Path:
    """
    Create 3D surface plot visualization with smooth interpolation.

    Args:
        results_path: Path to simulation results CSV
        output_dir: Output directory for figures
        view_angle: Tuple of (elevation, azimuth) for 3D view

    Returns:
        Path to saved PNG file
    """
    # Professional styling
    plt.style.use("seaborn-v0_8-paper")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "figure.dpi": 300,
        "savefig.dpi": 300,
    })

    # Load and process data
    results_df = pd.read_csv(results_path)
    matrix, seasons, weeks = build_consistency_matrix(results_df)

    # Create meshgrid
    X, Y = np.meshgrid(np.arange(len(weeks)), np.arange(len(seasons)))
    Z = matrix.copy()

    # Replace NaN with 0.5 for visualization (neutral)
    Z_filled = np.where(np.isnan(Z), 0.5, Z)

    # Create figure
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Reversed colormap: deep blue -> yellow -> deep red (blue=low/correct, red=high/incorrect)
    colors_list = [
        '#1E40AF', '#3B82F6', '#60A5FA', '#A7F3D0', '#FEF3C7',
        '#FBBF24', '#F97316', '#DC2626', '#B91C1C'
    ]
    n_bins = 256
    cmap = LinearSegmentedColormap.from_list('scientific_byr', colors_list, N=n_bins)

    # Surface with visible grid structure (reference style)
    surf = ax.plot_surface(X, Y, Z_filled,
                          cmap=cmap,
                          vmin=0, vmax=1,
                          alpha=0.80,
                          edgecolor='white',      # Grid lines
                          antialiased=True,
                          shade=True,
                          linewidth=0.3,          # Visible grid
                          rcount=40,              # Moderate for clear grid
                          ccount=40)

    # Three-wall projection system
    contour_levels = np.linspace(0, 1, 12)
    
    # Bottom wall (Z=0)
    ax.contourf(X, Y, Z_filled, zdir='z', offset=0,
                cmap=cmap, alpha=0.90, levels=contour_levels)
    
    # Back wall (Y=max)
    ax.contourf(X, Y, Z_filled, zdir='y', offset=Y.max(),
                cmap=cmap, alpha=0.75, levels=contour_levels)
    
    # Left wall (X=min)
    ax.contourf(X, Y, Z_filled, zdir='x', offset=X.min(),
                cmap=cmap, alpha=0.75, levels=contour_levels)

    # Axis labels and title
    ax.set_xlabel('Week', fontsize=11, labelpad=10)
    ax.set_ylabel('Season', fontsize=11, labelpad=10)
    ax.set_zlabel('Match Rate', fontsize=11, labelpad=10)
    ax.set_title('Elimination Prediction Consistency: Surface Analysis\nRank Sum Method vs Actual Eliminations',
                 fontsize=13, fontweight='bold', pad=20)

    # Set ticks
    ax.set_xticks(np.arange(0, len(weeks), 2))
    ax.set_xticklabels([str(weeks[i]) for i in range(0, len(weeks), 2)])

    ax.set_yticks(np.arange(0, len(seasons), 2))
    ax.set_yticklabels([str(seasons[i]) for i in range(0, len(seasons), 2)])

    ax.set_zticks([0, 0.5, 1])
    ax.set_zticklabels(['0\n(Incorrect)', '0.5', '1\n(Correct)'])

    # Reverse week axis (X-axis in surface plot)
    ax.invert_xaxis()

    # Set view angle
    ax.view_init(elev=view_angle[0], azim=view_angle[1])

    # Grid and pane styling (reference style)
    ax.grid(True, linestyle='-', alpha=0.4, linewidth=0.5, color='gray')
    ax.xaxis.pane.fill = True
    ax.yaxis.pane.fill = True
    ax.zaxis.pane.fill = True
    ax.xaxis.pane.set_alpha(0.1)
    ax.yaxis.pane.set_alpha(0.1)
    ax.zaxis.pane.set_alpha(0.1)
    ax.xaxis.pane.set_edgecolor('gray')
    ax.yaxis.pane.set_edgecolor('gray')
    ax.zaxis.pane.set_edgecolor('gray')
    ax.xaxis.pane.set_linewidth(1)
    ax.yaxis.pane.set_linewidth(1)
    ax.zaxis.pane.set_linewidth(1)
    ax.xaxis.pane.set_edgecolor('gray')
    ax.yaxis.pane.set_edgecolor('gray')
    ax.zaxis.pane.set_edgecolor('gray')
    ax.xaxis.pane.set_alpha(0.1)
    ax.yaxis.pane.set_alpha(0.1)
    ax.zaxis.pane.set_alpha(0.1)

    # Add colorbar
    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, pad=0.1)
    cbar.set_label('Match Rate', rotation=270, labelpad=20, fontsize=10)
    cbar.set_ticks([0, 0.5, 1])
    cbar.set_ticklabels(['Incorrect\n(0)', 'Neutral\n(0.5)', 'Correct\n(1)'])

    # Save figure
    output_dir.mkdir(parents=True, exist_ok=True)
    angle_suffix = f"_elev{view_angle[0]}_azim{view_angle[1]}"
    out_png = output_dir / f"surface_consistency_3d{angle_suffix}.png"
    out_pdf = output_dir / f"surface_consistency_3d{angle_suffix}.pdf"

    plt.tight_layout()
    fig.savefig(out_png, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")
    fig.savefig(out_pdf, bbox_inches="tight", facecolor="none")
    plt.close(fig)

    return out_png


def generate_multiple_views(results_path: Path, output_dir: Path) -> list[Path]:
    """
    Generate 3D visualizations from multiple viewing angles.

    Returns:
        List of paths to generated files
    """
    output_files = []

    # Define viewing angles: (elevation, azimuth)
    views = [
        (30, 45, "standard"),      # Standard 3D view
        (20, 135, "side"),         # Side view
        (60, 45, "top"),           # Top-down view
        (15, 225, "corner"),       # Corner view
    ]

    print("Generating 3D surface plots from multiple angles...")
    for elev, azim, name in views:
        print(f"  - {name} view (elev={elev}°, azim={azim}°)")
        out_file = create_3d_surface_plot(results_path, output_dir, view_angle=(elev, azim))
        output_files.append(out_file)

    return output_files


if __name__ == "__main__":
    import sys

    src_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(src_dir))
    from config import DATA_DIR

    results_path = DATA_DIR / "simulation" / "simulation_results.csv"
    output_dir = DATA_DIR.parent / "figures" / "consistency"

    print("=" * 60)
    print("3D Consistency Visualization Generator")
    print("=" * 60)
    print(f"Input: {results_path}")
    print(f"Output: {output_dir}")
    print()

    output_files = generate_multiple_views(results_path, output_dir)

    print("\n" + "=" * 60)
    print(f"Generated {len(output_files)} visualization files")
    print("=" * 60)
    print("\nOutput files:")
    for f in output_files:
        print(f"  - {f.name}")
