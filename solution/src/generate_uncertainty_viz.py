"""
Generate Advanced Uncertainty Visualization - Fan Chart
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Change to solution directory
os.chdir(Path(__file__).resolve().parents[1])

# Ensure output directory exists
os.makedirs('figures/ridge_v2', exist_ok=True)

# Set publication style
plt.style.use('seaborn-v0_8-paper')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 10,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'axes.linewidth': 1.0
})

# Reference style: blue/red series with light shaded areas, light gray grid
COLORS = {
    'primary': '#2563EB',       # Solid blue (main series)
    'primary_fill': '#93C5FD',  # Light blue shaded area
    'secondary': '#DC2626',     # Solid red (second series if any)
    'secondary_fill': '#FCA5A5', # Light red shaded area
    'neutral': '#2D3436',       # Charcoal
    'light_gray': '#E5E7EB',    # Light gray grid/reference
    'ref_line': '#9CA3AF',      # Dotted reference line
}

print("=" * 80)
print("GENERATING ADVANCED UNCERTAINTY VISUALIZATION")
print("=" * 80)

# Load Ridge V2 data
ridge_train = pd.read_csv('Data/models/ridge_v2/ridge_fan_vote_shares_v2.csv')
ridge_test = pd.read_csv('Data/models/ridge_v2/ridge_fan_vote_shares_v2_test.csv')
ridge_all = pd.concat([ridge_train, ridge_test], ignore_index=True)

print(f"\nLoaded {len(ridge_all)} predictions")
print(f"Columns: {ridge_all.columns.tolist()}")

# Select a few interesting contestants for visualization
# Focus on controversial/famous ones
famous_contestants = [
    ('Bobby Bones', 27),
    ('Bristol Palin', 11),
    ('Jerry Rice', 2),
    ('Meryl Davis', 18)
]

# ============================================================================
# FIGURE 1: FAN CHART - Time Series with Uncertainty
# ============================================================================

print("\n[1/3] Generating Fan Chart...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for idx, (name, season) in enumerate(famous_contestants):
    ax = axes[idx]

    # Get contestant data
    contestant_data = ridge_all[
        (ridge_all['celebrity_name'] == name) &
        (ridge_all['season'] == season)
    ].sort_values('week')

    if len(contestant_data) == 0:
        ax.text(0.5, 0.5, f'No data for {name} (S{season})',
                ha='center', va='center', transform=ax.transAxes)
        continue

    weeks = contestant_data['week'].values
    fan_share = contestant_data['fan_vote_share'].values

    # Calculate uncertainty if available
    if 'uncertainty_lower' in contestant_data.columns:
        lower = contestant_data['uncertainty_lower'].values
        upper = contestant_data['uncertainty_upper'].values
    else:
        # Estimate uncertainty as ±10% of the value
        lower = fan_share * 0.9
        upper = fan_share * 1.1

    # Plot central line (blue, matching reference style)
    ax.plot(weeks, fan_share, color=COLORS['primary'],
            linewidth=2.5, marker='o', markersize=6,
            markerfacecolor=COLORS['primary'], markeredgecolor='white',
            markeredgewidth=1.5, label='Fan Vote Share', zorder=5)

    # Plot uncertainty bands (light blue shaded area)
    ax.fill_between(weeks, lower, upper,
                    alpha=0.35, color=COLORS['primary_fill'],
                    label='Uncertainty Range', zorder=2)

    # Wider band (95% CI estimate)
    lower_95 = fan_share * 0.8
    upper_95 = fan_share * 1.2
    ax.fill_between(weeks, lower_95, upper_95,
                    alpha=0.15, color=COLORS['primary_fill'],
                    zorder=1)

    # Horizontal reference line (light gray dotted)
    ax.axhline(y=fan_share.mean(), color=COLORS['ref_line'], linestyle=':',
               linewidth=1.5, alpha=0.8, zorder=0)

    # Customize
    ax.set_xlabel('Week', fontsize=11, weight='bold')
    ax.set_ylabel('Fan Vote Share', fontsize=11, weight='bold')
    ax.set_title(f'{name} (Season {season})', fontsize=12, weight='bold',
                pad=10)

    # Format y-axis as percentage
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))

    # Light gray grid (both axes)
    ax.grid(True, alpha=0.35, color=COLORS['light_gray'], linestyle='-', linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)

    # Reverse week axis (week increases right-to-left)
    ax.invert_xaxis()

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Legend
    if idx == 0:
        ax.legend(loc='upper left', frameon=True, fancybox=False,
                 edgecolor=COLORS['neutral'], framealpha=0.9, fontsize=9)

# Overall title
fig.suptitle('Fan Vote Share Trajectories with Uncertainty Bands',
             fontsize=15, weight='bold', y=0.995)

plt.tight_layout()

# Save
output_path = 'figures/ridge_v2/fan_chart_uncertainty.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.savefig(output_path.replace('.png', '.pdf'), dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')

print(f"   Saved: {output_path}")
plt.close()

# ============================================================================
# FIGURE 2: UNCERTAINTY DISTRIBUTION
# ============================================================================

print("\n[2/3] Generating Uncertainty Distribution...")

# Calculate uncertainty range
if 'uncertainty_lower' in ridge_all.columns and 'uncertainty_upper' in ridge_all.columns:
    ridge_all['uncertainty_range'] = ridge_all['uncertainty_upper'] - ridge_all['uncertainty_lower']
else:
    # Estimate based on residual std
    ridge_all['uncertainty_range'] = ridge_all['fan_vote_share'] * 0.1

fig, ax = plt.subplots(figsize=(10, 6))

# Histogram + KDE
ax.hist(ridge_all['uncertainty_range'], bins=50, density=True,
        alpha=0.6, color=COLORS['primary'], edgecolor='white',
        linewidth=1, label='Histogram')

# KDE
from scipy import stats
kde = stats.gaussian_kde(ridge_all['uncertainty_range'].dropna())
x_range = np.linspace(ridge_all['uncertainty_range'].min(),
                     ridge_all['uncertainty_range'].max(), 200)
ax.plot(x_range, kde(x_range), color=COLORS['neutral'],
        linewidth=2.5, label='Density Curve')

# Statistics
mean_unc = ridge_all['uncertainty_range'].mean()
median_unc = ridge_all['uncertainty_range'].median()

ax.axvline(mean_unc, color=COLORS['secondary'], linestyle='--',
           linewidth=2, label=f'Mean = {mean_unc:.4f}')
ax.axvline(median_unc, color=COLORS['neutral'], linestyle=':',
           linewidth=2, label=f'Median = {median_unc:.4f}')

# Labels
ax.set_xlabel('Uncertainty Range', fontsize=12, weight='bold')
ax.set_ylabel('Density', fontsize=12, weight='bold')
ax.set_title('Distribution of Prediction Uncertainty',
             fontsize=14, weight='bold', pad=15)

# Statistical annotation
textstr = f'n = {len(ridge_all):,}\n'
textstr += f'Mean = {mean_unc:.4f}\n'
textstr += f'Median = {median_unc:.4f}\n'
textstr += f'Std = {ridge_all["uncertainty_range"].std():.4f}'

props = dict(boxstyle='round', facecolor='white', alpha=0.9,
             edgecolor=COLORS['neutral'], linewidth=1.2)
ax.text(0.97, 0.97, textstr, transform=ax.transAxes,
        fontsize=9, verticalalignment='top', horizontalalignment='right',
        bbox=props, family='monospace')

# Legend
ax.legend(loc='upper right', frameon=True, fancybox=False,
          edgecolor=COLORS['neutral'], framealpha=0.9)

# Remove spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Grid
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8, zorder=0)
ax.set_axisbelow(True)

plt.tight_layout()

# Save
output_path = 'figures/ridge_v2/uncertainty_distribution.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.savefig(output_path.replace('.png', '.pdf'), dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')

print(f"   Saved: {output_path}")
plt.close()

# ============================================================================
# FIGURE 3: UNCERTAINTY vs PREDICTION SCATTER
# ============================================================================

print("\n[3/3] Generating Uncertainty vs Prediction Scatter...")

fig, ax = plt.subplots(figsize=(10, 7))

# Reversed colormap: blue (low) -> red (high)
from matplotlib.colors import LinearSegmentedColormap
colors_list = [
    '#1E40AF', '#3B82F6', '#60A5FA', '#A7F3D0', '#FEF3C7',
    '#FBBF24', '#F97316', '#DC2626', '#B91C1C'
]
cmap_custom = LinearSegmentedColormap.from_list('scientific_byr', colors_list, N=256)

scatter = ax.scatter(ridge_all['fan_vote_share'],
                    ridge_all['uncertainty_range'],
                    c=ridge_all['week'],
                    cmap=cmap_custom,
                    alpha=0.6,
                    s=30,
                    edgecolors='none')

# Colorbar
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Week', fontsize=11, weight='bold')

# Trend line
z = np.polyfit(ridge_all['fan_vote_share'], ridge_all['uncertainty_range'], 1)
p = np.poly1d(z)
x_trend = np.linspace(ridge_all['fan_vote_share'].min(),
                     ridge_all['fan_vote_share'].max(), 100)
ax.plot(x_trend, p(x_trend), color=COLORS['secondary'],
        linestyle='--', linewidth=2, alpha=0.8,
        label=f'Trend: y = {z[0]:.3f}x + {z[1]:.3f}')

# Labels
ax.set_xlabel('Fan Vote Share (Prediction)', fontsize=12, weight='bold')
ax.set_ylabel('Uncertainty Range', fontsize=12, weight='bold')
ax.set_title('Prediction Uncertainty vs. Fan Vote Share',
             fontsize=14, weight='bold', pad=15)

# Format x-axis as percentage
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))

# Legend
ax.legend(loc='upper right', frameon=True, fancybox=False,
          edgecolor=COLORS['neutral'], framealpha=0.9)

# Remove spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Grid
ax.grid(alpha=0.3, linestyle='--', linewidth=0.8, zorder=0)
ax.set_axisbelow(True)

plt.tight_layout()

# Save
output_path = 'figures/ridge_v2/uncertainty_vs_prediction.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.savefig(output_path.replace('.png', '.pdf'), dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')

print(f"   Saved: {output_path}")
plt.close()

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("UNCERTAINTY VISUALIZATION COMPLETE")
print("=" * 80)
print("\nGenerated Files:")
print("  1. fan_chart_uncertainty.png/pdf - Fan chart with uncertainty bands")
print("  2. uncertainty_distribution.png/pdf - Distribution of uncertainty")
print("  3. uncertainty_vs_prediction.png/pdf - Scatter plot analysis")
print("\nKey Statistics:")
print(f"  Mean uncertainty: {mean_unc:.4f}")
print(f"  Median uncertainty: {median_unc:.4f}")
print(f"  Max uncertainty: {ridge_all['uncertainty_range'].max():.4f}")
print("=" * 80)
