"""
Uncertainty Heatmap Visualization
Creates a high-quality scientific heatmap showing uncertainty across seasons and weeks
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configure matplotlib for publication-quality figures
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.linewidth'] = 0.8
plt.rcParams['lines.linewidth'] = 1.5

def load_uncertainty_data():
    """Load V2 model output with uncertainty estimates"""
    data_path = Path(__file__).parent.parent / 'Data' / 'models' / 'ridge_v2' / 'ridge_fan_vote_shares_v2.csv'
    df = pd.read_csv(data_path)
    return df

def prepare_heatmap_data(df):
    """
    Aggregate uncertainty by season and week
    Returns a pivot table suitable for heatmap visualization
    """
    # Use uncertainty_upper as the uncertainty metric
    # (uncertainty_range is zero because lower=upper in the V2 model)
    heatmap_data = df.groupby(['season', 'week'])['uncertainty_upper'].mean().reset_index()

    # Pivot to create matrix format
    pivot_data = heatmap_data.pivot(index='week', columns='season', values='uncertainty_upper')

    return pivot_data

def create_uncertainty_heatmap(pivot_data, output_dir):
    """
    Create publication-quality heatmap
    """
    # Create figure with appropriate size
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)

    # Reversed colormap: deep blue -> yellow -> deep red (blue=low, red=high)
    from matplotlib.colors import LinearSegmentedColormap
    colors_list = [
        '#1E40AF', '#3B82F6', '#60A5FA', '#A7F3D0', '#FEF3C7',
        '#FBBF24', '#F97316', '#DC2626', '#B91C1C'
    ]
    cmap_custom = LinearSegmentedColormap.from_list('scientific_byr', colors_list, N=256)
    
    sns.heatmap(
        pivot_data,
        cmap=cmap_custom,
        cbar_kws={
            'label': 'Uncertainty (Standard Error of Fan Vote Share)',
            'shrink': 0.8,
            'aspect': 30,
            'pad': 0.02
        },
        linewidths=0.5,
        linecolor='white',
        square=False,
        ax=ax,
        vmin=0,  # Set minimum to 0 for consistent scale
        fmt='.3f',
        annot=False,  # Don't annotate cells (too many values)
        robust=True  # Use robust quantiles for color scaling
    )

    # Customize axes
    ax.set_xlabel('Season', fontsize=13, fontweight='bold')
    ax.set_ylabel('Week', fontsize=13, fontweight='bold')
    ax.set_title('Fan Vote Uncertainty Across Seasons and Weeks\n(Ridge Regression Model V2)',
                 fontsize=14, fontweight='bold', pad=15)

    # Improve tick labels
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, ha='center')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    # Invert y-axis so week 1 is at top
    ax.invert_yaxis()

    # Add grid for better readability
    ax.set_xticks(np.arange(pivot_data.shape[1]) + 0.5, minor=False)
    ax.set_yticks(np.arange(pivot_data.shape[0]) + 0.5, minor=False)

    # Tight layout
    plt.tight_layout()

    # Save figure
    output_path_png = output_dir / 'uncertainty_heatmap.png'
    output_path_pdf = output_dir / 'uncertainty_heatmap.pdf'

    plt.savefig(output_path_png, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path_pdf, bbox_inches='tight', facecolor='white')

    print(f"[OK] Heatmap saved to:")
    print(f"  - {output_path_png}")
    print(f"  - {output_path_pdf}")

    plt.close()

    return output_path_png, output_path_pdf

def create_summary_statistics(df):
    """Generate summary statistics for uncertainty"""
    stats = {
        'Overall Mean': df['uncertainty_upper'].mean(),
        'Overall Std': df['uncertainty_upper'].std(),
        'Overall Min': df['uncertainty_upper'].min(),
        'Overall Max': df['uncertainty_upper'].max(),
        'Overall Median': df['uncertainty_upper'].median()
    }

    # By season
    season_stats = df.groupby('season')['uncertainty_upper'].agg(['mean', 'std', 'min', 'max'])

    # By week
    week_stats = df.groupby('week')['uncertainty_upper'].agg(['mean', 'std', 'min', 'max'])

    return stats, season_stats, week_stats

def main():
    """Main execution"""
    print("=" * 60)
    print("Uncertainty Heatmap Visualization")
    print("=" * 60)

    # Load data
    print("\n[1/4] Loading uncertainty data...")
    df = load_uncertainty_data()
    print(f"  Loaded {len(df)} contestant-week observations")
    print(f"  Seasons: {df['season'].min()} to {df['season'].max()}")
    print(f"  Weeks: {df['week'].min()} to {df['week'].max()}")

    # Prepare heatmap data
    print("\n[2/4] Preparing heatmap data...")
    pivot_data = prepare_heatmap_data(df)
    print(f"  Heatmap dimensions: {pivot_data.shape[0]} weeks × {pivot_data.shape[1]} seasons")
    print(f"  Missing cells: {pivot_data.isna().sum().sum()} / {pivot_data.size}")

    # Create output directory
    output_dir = Path(__file__).parent.parent / 'figures' / 'uncertainty'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create heatmap
    print("\n[3/4] Creating heatmap...")
    create_uncertainty_heatmap(pivot_data, output_dir)

    # Generate statistics
    print("\n[4/4] Computing summary statistics...")
    stats, season_stats, week_stats = create_summary_statistics(df)

    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    print("\nOverall Uncertainty:")
    for key, value in stats.items():
        print(f"  {key:20s}: {value:.6f}")

    print("\nTop 5 Seasons by Mean Uncertainty:")
    print(season_stats.nlargest(5, 'mean')[['mean', 'std']])

    print("\nTop 5 Weeks by Mean Uncertainty:")
    print(week_stats.nlargest(5, 'mean')[['mean', 'std']])

    print("\n" + "=" * 60)
    print("[OK] Visualization complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
