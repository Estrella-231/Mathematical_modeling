"""
Generate Improved Elimination Match Rate by Season Chart
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
os.makedirs('figures/elimination_match_rate', exist_ok=True)

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

# Enhanced scientific color palette (blue=high, red=low)
COLORS = {
    'excellent': '#1E40AF',   # Deep blue - high match rate
    'good': '#60A5FA',        # Light blue - good match rate
    'poor': '#FBBF24',        # Yellow - fair match rate
    'bad': '#DC2626',         # Deep red - low match rate
    'neutral': '#2D3436',     # Charcoal
    'light_gray': '#DFE6E9'   # Light gray
}

print("Generating Improved Elimination Match Rate by Season Chart...")

# Load simulation results
sim_df = pd.read_csv('Data/simulation/simulation_results.csv')

# Calculate match rate for each season
season_match_rates = []

for season in range(1, 35):
    season_data = sim_df[sim_df['season'] == season].copy()

    if len(season_data) == 0:
        continue

    # Determine which prediction to use based on season
    if season <= 2:
        predicted_col = 'rank_sum_eliminated'
    elif season <= 27:
        predicted_col = 'percent_sum_eliminated'
    else:
        predicted_col = 'judge_save_eliminated'

    # Calculate match rate
    matches = (season_data['actual_eliminated'] == season_data[predicted_col]).sum()
    total = len(season_data)
    match_rate = (matches / total) if total > 0 else 0

    season_match_rates.append({
        'season': season,
        'match_rate': match_rate,
        'matches': matches,
        'total': total
    })

# Convert to DataFrame
match_df = pd.DataFrame(season_match_rates)

# Calculate overall average
overall_avg = match_df['match_rate'].mean()

print(f"Loaded {len(match_df)} seasons")
print(f"Overall match rate: {overall_avg:.1%}")

# Assign colors based on match rate thresholds
def get_color(rate):
    if rate >= 0.90:
        return COLORS['excellent']
    elif rate >= 0.80:
        return COLORS['good']
    elif rate >= 0.60:
        return COLORS['poor']
    else:
        return COLORS['bad']

colors = [get_color(rate) for rate in match_df['match_rate']]

# Create figure
fig, ax = plt.subplots(figsize=(14, 6))

# Bar plot
bars = ax.bar(match_df['season'], match_df['match_rate'],
              color=colors, alpha=0.85, edgecolor='white', linewidth=1.5,
              width=0.8)

# Add value labels on top of bars
for idx, (season, rate) in enumerate(zip(match_df['season'], match_df['match_rate'])):
    if rate >= 0.85:  # Only show label if above overall average
        label_y = rate + 0.02
    else:
        label_y = rate + 0.02

    ax.text(season, label_y, f'{rate:.0%}',
            ha='center', va='bottom', fontsize=8, weight='bold',
            color=COLORS['neutral'])

# Overall average line
ax.axhline(overall_avg, color=COLORS['neutral'], linestyle='--',
           linewidth=2, alpha=0.8, zorder=5,
           label=f'Overall: {overall_avg:.1%}')

# Add shaded regions for different voting rules
ax.axvspan(0.5, 2.5, alpha=0.10, color='#FBBF24', zorder=0)
ax.axvspan(2.5, 27.5, alpha=0.10, color='#A7F3D0', zorder=0)
ax.axvspan(27.5, 34.5, alpha=0.10, color='#60A5FA', zorder=0)

# Add rule period labels
ax.text(1.5, 1.05, 'Rank\n(S1-2)', ha='center', va='bottom', fontsize=9,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8,
                  edgecolor='gray', linewidth=0.8),
        transform=ax.get_xaxis_transform())

ax.text(15, 1.05, 'Percent\n(S3-27)', ha='center', va='bottom', fontsize=9,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8,
                  edgecolor='gray', linewidth=0.8),
        transform=ax.get_xaxis_transform())

ax.text(31, 1.05, 'Judge Save\n(S28-34)', ha='center', va='bottom', fontsize=9,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8,
                  edgecolor='gray', linewidth=0.8),
        transform=ax.get_xaxis_transform())

# Labels and title
ax.set_xlabel('Season', fontsize=12, weight='bold')
ax.set_ylabel('Elimination Match Rate', fontsize=12, weight='bold')

# Title with subtitle
ax.text(0.5, 1.12, 'Elimination Match Rate by Season',
        transform=ax.transAxes, ha='center', fontsize=14, weight='bold',
        color=COLORS['neutral'])
ax.text(0.5, 1.06, 'Model prediction accuracy across 34 seasons and three voting rules',
        transform=ax.transAxes, ha='center', fontsize=10, style='italic',
        color=COLORS['neutral'])

# Y-axis formatting
ax.set_ylim(0, 1.15)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))

# X-axis
ax.set_xlim(0, 35)
ax.set_xticks(range(0, 35, 2))

# Legend with color coding explanation
from matplotlib.patches import Patch
legend_elements = [
    ax.get_legend_handles_labels()[0][0],  # Overall line
    Patch(facecolor=COLORS['excellent'], label='Excellent (≥90%)', alpha=0.85),
    Patch(facecolor=COLORS['good'], label='Good (80-89%)', alpha=0.85),
    Patch(facecolor=COLORS['poor'], label='Fair (60-79%)', alpha=0.85),
    Patch(facecolor=COLORS['bad'], label='Poor (<60%)', alpha=0.85)
]
ax.legend(handles=legend_elements, loc='lower left', frameon=True,
          fancybox=False, edgecolor=COLORS['neutral'], framealpha=0.95,
          fontsize=9, ncol=5)

# Statistical annotation
period1_avg = match_df[match_df['season'] <= 2]['match_rate'].mean()
period2_avg = match_df[(match_df['season'] >= 3) & (match_df['season'] <= 27)]['match_rate'].mean()
period3_avg = match_df[match_df['season'] >= 28]['match_rate'].mean()

textstr = f'Period Averages:\n'
textstr += f'S1-2: {period1_avg:.1%}\n'
textstr += f'S3-27: {period2_avg:.1%}\n'
textstr += f'S28-34: {period3_avg:.1%}'

props = dict(boxstyle='round', facecolor='white', alpha=0.9,
             edgecolor=COLORS['neutral'], linewidth=1.2)
ax.text(0.98, 0.98, textstr, transform=ax.transAxes,
        fontsize=9, verticalalignment='top', horizontalalignment='right',
        bbox=props, family='monospace')

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Grid
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8, zorder=0)
ax.set_axisbelow(True)

plt.tight_layout()

# Save
output_path = 'figures/elimination_match_rate/match_rate_by_season_improved.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.savefig(output_path.replace('.png', '.pdf'), dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')

print(f"\nSaved: {output_path}")
print(f"Saved: {output_path.replace('.png', '.pdf')}")

plt.close()

# Print statistics
print("\n=== Season Statistics ===")
print(f"Best season: S{match_df.loc[match_df['match_rate'].idxmax(), 'season']:.0f} ({match_df['match_rate'].max():.1%})")
print(f"Worst season: S{match_df.loc[match_df['match_rate'].idxmin(), 'season']:.0f} ({match_df['match_rate'].min():.1%})")
print(f"\nPeriod 1 (S1-2, Rank): {period1_avg:.1%}")
print(f"Period 2 (S3-27, Percent): {period2_avg:.1%}")
print(f"Period 3 (S28-34, Judge Save): {period3_avg:.1%}")
print(f"Overall: {overall_avg:.1%}")

print("\n=== Chart Generation Complete ===")
