"""
Generate Improved Rule Consistency Visualizations
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
os.makedirs('figures/simulation', exist_ok=True)

# Set publication style
plt.style.use('seaborn-v0_8-paper')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 10,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
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
print("GENERATING IMPROVED RULE CONSISTENCY VISUALIZATIONS")
print("=" * 80)

# Load simulation results
sim_df = pd.read_csv('Data/simulation/simulation_results.csv')

# Calculate consistency matrix
rules = ['rank_sum', 'percent_sum', 'judge_save']
rule_labels = ['Rank Sum', 'Percent Sum', 'Judge Save']

consistency_matrix = np.zeros((3, 3))

for i, rule1 in enumerate(rules):
    for j, rule2 in enumerate(rules):
        if i == j:
            consistency_matrix[i, j] = 1.0
        else:
            # Calculate from eliminated columns
            col1 = f'{rule1}_eliminated'
            col2 = f'{rule2}_eliminated'
            if col1 in sim_df.columns and col2 in sim_df.columns:
                consistency_matrix[i, j] = (sim_df[col1] == sim_df[col2]).mean()

# Ensure symmetry
for i in range(3):
    for j in range(i+1, 3):
        consistency_matrix[j, i] = consistency_matrix[i, j]

print("\nConsistency Matrix:")
print(consistency_matrix)

# ============================================================================
# FIGURE 1: IMPROVED CONSISTENCY MATRIX
# ============================================================================

print("\n[1/2] Generating Improved Consistency Matrix...")

fig, ax = plt.subplots(figsize=(8, 7))

# Create heatmap
sns.heatmap(consistency_matrix,
            annot=True,
            fmt='.1%',
            cmap='RdYlGn',
            center=0.85,
            vmin=0.5,
            vmax=1.0,
            square=True,
            linewidths=2,
            linecolor='white',
            cbar_kws={'label': 'Consistency Rate', 'shrink': 0.8},
            xticklabels=rule_labels,
            yticklabels=rule_labels,
            ax=ax)

# Customize colorbar
cbar = ax.collections[0].colorbar
cbar.ax.yaxis.label.set_size(11)
cbar.ax.yaxis.label.set_weight('bold')

# Add reference line on colorbar
cbar.ax.axhline(0.85, color='blue', linewidth=2, linestyle='--', alpha=0.7)
cbar.ax.text(1.5, 0.85, '85% (Ideal)', va='center', fontsize=9, color='blue', weight='bold')

# Title
ax.text(0.5, 1.12, 'Rule Consistency Matrix',
        transform=ax.transAxes, ha='center', fontsize=14, weight='bold',
        color=COLORS['neutral'])
ax.text(0.5, 1.06, 'Percentage of weeks with same elimination decision',
        transform=ax.transAxes, ha='center', fontsize=10, style='italic',
        color=COLORS['neutral'])

# Key finding annotation
max_consistency = max(consistency_matrix[0,1], consistency_matrix[0,2], consistency_matrix[1,2])
ax.text(0.5, -0.15, f'Key Finding: Maximum consistency is only {max_consistency*100:.1f}%,\nindicating significant rule instability',
        transform=ax.transAxes, ha='center', fontsize=10,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF3CD', alpha=0.8,
                  edgecolor='#FFC107', linewidth=1.5),
        color=COLORS['neutral'])

plt.tight_layout()

# Save
output_path = 'figures/simulation/rule_consistency_matrix_improved.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.savefig(output_path.replace('.png', '.pdf'), dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')

print(f"   Saved: {output_path}")
plt.close()

# ============================================================================
# FIGURE 2: FLIP RATE VISUALIZATION
# ============================================================================

print("\n[2/2] Generating Flip Rate Visualization...")

# Calculate flip rates
flip_rates = []
comparisons = [
    ('Rank Sum', 'Percent Sum', consistency_matrix[0, 1]),
    ('Rank Sum', 'Judge Save', consistency_matrix[0, 2]),
    ('Percent Sum', 'Judge Save', consistency_matrix[1, 2])
]

for rule1, rule2, consistency in comparisons:
    flip_rate = (1 - consistency) * 100
    flip_rates.append({
        'comparison': f'{rule1}\nvs\n{rule2}',
        'flip_rate': flip_rate,
        'consistency': consistency * 100
    })

flip_df = pd.DataFrame(flip_rates)

# Create figure
fig, ax = plt.subplots(figsize=(9, 6))

# Bar plot
x_pos = np.arange(len(flip_df))
bars = ax.bar(x_pos, flip_df['flip_rate'],
              color=COLORS['secondary'], alpha=0.85,
              edgecolor='white', linewidth=2, width=0.6)

# Add value labels
for idx, (bar, rate) in enumerate(zip(bars, flip_df['flip_rate'])):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{rate:.1f}%',
            ha='center', va='bottom', fontsize=12, weight='bold',
            color=COLORS['neutral'])

    # Add consistency rate below
    ax.text(bar.get_x() + bar.get_width()/2., -3,
            f'(Consistency: {flip_df.iloc[idx]["consistency"]:.1f}%)',
            ha='center', va='top', fontsize=9, style='italic',
            color=COLORS['neutral'])

# Reference line
ax.axhline(25, color='blue', linestyle='--', linewidth=2, alpha=0.7)
ax.text(len(flip_df) - 0.5, 26, '1 in 4 decisions flip',
        fontsize=9, color='blue', weight='bold', ha='right')

# Customize
ax.set_xticks(x_pos)
ax.set_xticklabels(flip_df['comparison'], fontsize=10)
ax.set_ylabel('Flip Rate (%)', fontsize=12, weight='bold')
ax.set_ylim(-5, max(flip_df['flip_rate']) * 1.2)

# Title
ax.text(0.5, 1.10, 'Voting Rule Instability: Flip Rates',
        transform=ax.transAxes, ha='center', fontsize=14, weight='bold',
        color=COLORS['neutral'])
ax.text(0.5, 1.04, 'Percentage of elimination decisions that change when switching rules',
        transform=ax.transAxes, ha='center', fontsize=10, style='italic',
        color=COLORS['neutral'])

# Insight box
insight_text = f'Up to {flip_df["flip_rate"].max():.1f}% of eliminations\nwould change under different rules'
ax.text(0.98, 0.95, insight_text,
        transform=ax.transAxes, ha='right', va='top', fontsize=11,
        bbox=dict(boxstyle='round,pad=0.6', facecolor='#FFF3CD', alpha=0.9,
                  edgecolor='#FFC107', linewidth=1.5),
        color=COLORS['neutral'], weight='bold')

# Remove spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Grid
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8, zorder=0)
ax.set_axisbelow(True)

plt.tight_layout()

# Save
output_path = 'figures/simulation/flip_rate_visualization.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.savefig(output_path.replace('.png', '.pdf'), dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')

print(f"   Saved: {output_path}")
plt.close()

# Summary
print("\n" + "=" * 80)
print("VISUALIZATION GENERATION COMPLETE")
print("=" * 80)
print("\nGenerated Files:")
print("  1. rule_consistency_matrix_improved.png/pdf")
print("  2. flip_rate_visualization.png/pdf")
print("\nKey Findings:")
print(f"  - Highest consistency: {consistency_matrix[0,1]*100:.1f}% (Rank vs Percent)")
print(f"  - Lowest consistency: {consistency_matrix[1,2]*100:.1f}% (Percent vs Judge Save)")
print(f"  - Maximum flip rate: {flip_df['flip_rate'].max():.1f}%")
print("\nRecommendation:")
print("  Use BOTH figures in the paper:")
print("  - Figure 1: Shows overall consistency pattern")
print("  - Figure 2: Emphasizes instability for stronger argument")
print("=" * 80)
