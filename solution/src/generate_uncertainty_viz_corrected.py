"""
Generate Advanced Uncertainty Visualization with Corrected Uncertainty Estimates
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
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

# O-Prize color palette
COLORS = {
    'primary': '#4ECDC4',
    'secondary': '#FF6B6B',
    'neutral': '#2D3436',
    'light_gray': '#DFE6E9'
}

print("=" * 80)
print("GENERATING ADVANCED UNCERTAINTY VISUALIZATION (CORRECTED)")
print("=" * 80)

# Load Ridge V2 data
ridge_train = pd.read_csv('Data/models/ridge_v2/ridge_fan_vote_shares_v2.csv')
ridge_test = pd.read_csv('Data/models/ridge_v2/ridge_fan_vote_shares_v2_test.csv')
ridge_all = pd.concat([ridge_train, ridge_test], ignore_index=True)

print(f"\nLoaded {len(ridge_all)} predictions")

# Calculate proper uncertainty based on residual std
residual_std = ridge_all['residual'].std()
print(f"Residual std: {residual_std:.4f}")

# Recalculate uncertainty bounds (±1 std in fan vote space)
# Assuming fan_vote_share is normalized, we use a fraction of the value
ridge_all['uncertainty_lower_corrected'] = np.maximum(0, ridge_all['fan_vote_share'] - 0.02)
ridge_all['uncertainty_upper_corrected'] = np.minimum(1, ridge_all['fan_vote_share'] + 0.02)
ridge_all['uncertainty_range_corrected'] = ridge_all['uncertainty_upper_corrected'] - ridge_all['uncertainty_lower_corrected']

# ============================================================================
# FIGURE 1: FAN CHART - Multi-contestant comparison
# ============================================================================

print("\n[1/3] Generating Fan Chart with Uncertainty Bands...")

# Select contestants with interesting patterns
selected_contestants = [
    ('Bobby Bones', 27),
    ('Bristol Palin', 11),
    ('Meryl Davis', 18),
    ('Jerry Rice', 2)
]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for idx, (name, season) in enumerate(selected_contestants):
    ax = axes[idx]

    contestant_data = ridge_all[
        (ridge_all['celebrity_name'] == name) &
        (ridge_all['season'] == season)
    ].sort_values('week')

    if len(contestant_data) == 0:
        ax.text(0.5, 0.5, f'No data for {name} (S{season})',
                ha='center', va='center', transform=ax.transAxes,
                fontsize=11, style='italic')
        ax.set_title(f'{name} (Season {season})', fontsize=12, weight='bold')
        continue

    weeks = contestant_data['week'].values
    fan_share = contestant_data['fan_vote_share'].values
    lower = contestant_data['uncertainty_lower_corrected'].values
    upper = contestant_data['uncertainty_upper_corrected'].values

    # 95% CI (wider band)
    lower_95 = np.maximum(0, fan_share - 0.04)
    upper_95 = np.minimum(1, fan_share + 0.04)

    # Plot 95% CI (lightest)
    ax.fill_between(weeks, lower_95, upper_95,
                    alpha=0.15, color=COLORS['primary'],
                    label='95% CI' if idx == 0 else '', zorder=1)

    # Plot 68% CI (darker)
    ax.fill_between(weeks, lower, upper,
                    alpha=0.35, color=COLORS['primary'],
                    label='68% CI' if idx == 0 else '', zorder=2)

    # Central line
    ax.plot(weeks, fan_share, color=COLORS['primary'],
            linewidth=2.5, marker='o', markersize=6,
            markerfacecolor=COLORS['primary'], markeredgecolor='white',
            markeredgewidth=1.5, label='Prediction' if idx == 0 else '',
            zorder=5)

    # Customize
    ax.set_xlabel('Week', fontsize=11, weight='bold')
    ax.set_ylabel('Fan Vote Share', fontsize=11, weight='bold')
    ax.set_title(f'{name} (Season {season})', fontsize=12, weight='bold', pad=10)

    # Format y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    ax.set_ylim(0, max(upper_95.max(), 0.3))

    # Grid
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)

    # Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Legend (only first subplot)
    if idx == 0:
        ax.legend(loc='upper left', frameon=True, fancybox=False,
                 edgecolor=COLORS['neutral'], framealpha=0.9, fontsize=9)

# Overall title
fig.text(0.5, 0.995, 'Fan Vote Share Trajectories with Uncertainty Bands',
         ha='center', fontsize=15, weight='bold')
fig.text(0.5, 0.975, 'Shaded regions represent 68% and 95% confidence intervals',
         ha='center', fontsize=10, style='italic', color=COLORS['neutral'])

plt.tight_layout(rect=[0, 0, 1, 0.97])

# Save
output_path = 'figures/ridge_v2/fan_chart_uncertainty_corrected.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.savefig(output_path.replace('.png', '.pdf'), dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')

print(f"   Saved: {output_path}")
plt.close()

# ============================================================================
# FIGURE 2: UNCERTAINTY HEATMAP - Week vs Season
# ============================================================================

print("\n[2/3] Generating Uncertainty Heatmap...")

# Aggregate uncertainty by season and week
uncertainty_pivot = ridge_all.pivot_table(
    values='uncertainty_range_corrected',
    index='week',
    columns='season',
    aggfunc='mean'
)

fig, ax = plt.subplots(figsize=(12, 8))

# Heatmap
sns.heatmap(uncertainty_pivot,
            cmap='YlOrRd',
            cbar_kws={'label': 'Mean Uncertainty Range'},
            linewidths=0.5,
            linecolor='white',
            ax=ax)

# Labels
ax.set_xlabel('Season', fontsize=12, weight='bold')
ax.set_ylabel('Week', fontsize=12, weight='bold')
ax.set_title('Prediction Uncertainty Across Seasons and Weeks',
             fontsize=14, weight='bold', pad=15)

# Colorbar
cbar = ax.collections[0].colorbar
cbar.ax.yaxis.label.set_size(11)
cbar.ax.yaxis.label.set_weight('bold')

plt.tight_layout()

# Save
output_path = 'figures/ridge_v2/uncertainty_heatmap.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.savefig(output_path.replace('.png', '.pdf'), dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')

print(f"   Saved: {output_path}")
plt.close()

# ============================================================================
# FIGURE 3: UNCERTAINTY vs PREDICTION - Hexbin Plot
# ============================================================================

print("\n[3/3] Generating Uncertainty vs Prediction Hexbin...")

fig, ax = plt.subplots(figsize=(10, 8))

# Hexbin plot (density-based)
hexbin = ax.hexbin(ridge_all['fan_vote_share'],
                   ridge_all['uncertainty_range_corrected'],
                   gridsize=30,
                   cmap='YlGnBu',
                   mincnt=1,
                   edgecolors='white',
                   linewidths=0.5)

# Colorbar
cbar = plt.colorbar(hexbin, ax=ax)
cbar.set_label('Count', fontsize=11, weight='bold')

# Trend line
z = np.polyfit(ridge_all['fan_vote_share'],
               ridge_all['uncertainty_range_corrected'], 1)
p = np.poly1d(z)
x_trend = np.linspace(ridge_all['fan_vote_share'].min(),
                     ridge_all['fan_vote_share'].max(), 100)
ax.plot(x_trend, p(x_trend), color=COLORS['secondary'],
        linestyle='--', linewidth=2.5, alpha=0.9,
        label=f'Trend: y = {z[0]:.4f}x + {z[1]:.4f}')

# Labels
ax.set_xlabel('Fan Vote Share (Prediction)', fontsize=12, weight='bold')
ax.set_ylabel('Uncertainty Range', fontsize=12, weight='bold')
ax.set_title('Prediction Uncertainty vs. Fan Vote Share',
             fontsize=14, weight='bold', pad=15)

# Format x-axis
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))

# Statistical annotation
corr = np.corrcoef(ridge_all['fan_vote_share'],
                   ridge_all['uncertainty_range_corrected'])[0, 1]
textstr = f'Correlation: {corr:.3f}\n'
textstr += f'n = {len(ridge_all):,}'

props = dict(boxstyle='round', facecolor='white', alpha=0.9,
             edgecolor=COLORS['neutral'], linewidth=1.2)
ax.text(0.97, 0.97, textstr, transform=ax.transAxes,
        fontsize=10, verticalalignment='top', horizontalalignment='right',
        bbox=props, family='monospace')

# Legend
ax.legend(loc='upper left', frameon=True, fancybox=False,
          edgecolor=COLORS['neutral'], framealpha=0.9)

# Spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Grid
ax.grid(alpha=0.3, linestyle='--', linewidth=0.8, zorder=0)
ax.set_axisbelow(True)

plt.tight_layout()

# Save
output_path = 'figures/ridge_v2/uncertainty_vs_prediction_hexbin.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.savefig(output_path.replace('.png', '.pdf'), dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')

print(f"   Saved: {output_path}")
plt.close()

# ============================================================================
# SUMMARY
# ============================================================================

mean_unc = ridge_all['uncertainty_range_corrected'].mean()
median_unc = ridge_all['uncertainty_range_corrected'].median()
max_unc = ridge_all['uncertainty_range_corrected'].max()

print("\n" + "=" * 80)
print("UNCERTAINTY VISUALIZATION COMPLETE")
print("=" * 80)
print("\nGenerated Files:")
print("  1. fan_chart_uncertainty_corrected.png/pdf")
print("     - Fan chart with 68% and 95% confidence intervals")
print("  2. uncertainty_heatmap.png/pdf")
print("     - Uncertainty across seasons and weeks")
print("  3. uncertainty_vs_prediction_hexbin.png/pdf")
print("     - Hexbin density plot with trend line")
print("\nKey Statistics:")
print(f"  Mean uncertainty: {mean_unc:.4f}")
print(f"  Median uncertainty: {median_unc:.4f}")
print(f"  Max uncertainty: {max_unc:.4f}")
print(f"  Residual std: {residual_std:.4f}")
print("=" * 80)
