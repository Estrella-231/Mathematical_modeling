"""
Generate Contestant Clustering Quadrant Plot
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Change to solution directory
os.chdir(Path(__file__).resolve().parents[1])

# Ensure output directory exists
os.makedirs('figures/twin_model', exist_ok=True)

# Set publication style
plt.style.use('seaborn-v0_8-paper')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'axes.linewidth': 0.8
})

# Color palette - assign specific colors to archetypes
ARCHETYPE_COLORS = {
    'Superstars': '#009E73',      # Green - positive
    'Tech Giants': '#0072B2',     # Blue - technical
    'Fan Favorites': '#E69F00',   # Orange - popular
    'Underdogs': '#CC79A7'        # Purple - struggling
}

print('=== Visualization 2: Contestant Clustering (Improved) ===')

# Load data
weekly_df = pd.read_csv('Data/processed/weekly_panel.csv')
ridge_train = pd.read_csv('Data/models/ridge_v2/ridge_fan_vote_shares_v2.csv')
ridge_test = pd.read_csv('Data/models/ridge_v2/ridge_fan_vote_shares_v2_test.csv')
ridge_all = pd.concat([ridge_train, ridge_test], ignore_index=True)

# Merge fan vote estimates
weekly_df = weekly_df.merge(
    ridge_all[['season', 'week', 'celebrity_name', 'fan_vote_share']],
    on=['season', 'week', 'celebrity_name'],
    how='left'
)

# Filter valid data
valid_df = weekly_df[weekly_df['fan_vote_share'].notna()].copy()

# Aggregate to contestant level
contestant_agg = valid_df.groupby(['season', 'celebrity_name']).agg({
    'relative_judge_score': 'mean',
    'fan_vote_share': 'mean',
    'placement': 'first',
    'week': 'max'
}).reset_index()

# Standardize features
scaler = StandardScaler()
contestant_agg['judge_score_z'] = scaler.fit_transform(contestant_agg[['relative_judge_score']])
contestant_agg['fan_vote_z'] = scaler.fit_transform(contestant_agg[['fan_vote_share']])

# Manual archetype assignment based on quadrants
def assign_archetype(row):
    judge_z = row['judge_score_z']
    fan_z = row['fan_vote_z']

    if judge_z > 0 and fan_z > 0:
        return 'Superstars'
    elif judge_z > 0 and fan_z <= 0:
        return 'Tech Giants'
    elif judge_z <= 0 and fan_z > 0:
        return 'Fan Favorites'
    else:
        return 'Underdogs'

contestant_agg['archetype'] = contestant_agg.apply(assign_archetype, axis=1)

print('\nArchetype distribution:')
print(contestant_agg['archetype'].value_counts())

# Identify famous contestants to annotate
famous_contestants = {
    'Bobby Bones': (10, 10),
    'Jerry Rice': (10, -10),
    'Bristol Palin': (-10, 10),
    'Meryl Davis': (10, 10),
    'Sabrina Bryan': (-10, -10),
    'Billy Ray Cyrus': (10, -10)
}

# Find these contestants in the data
annotate_df = contestant_agg[contestant_agg['celebrity_name'].isin(famous_contestants.keys())].copy()
print(f'\nFound {len(annotate_df)} famous contestants to annotate')

# Create figure
fig, ax = plt.subplots(figsize=(7, 6))

# Plot each archetype with specific colors
for archetype, color in ARCHETYPE_COLORS.items():
    archetype_data = contestant_agg[contestant_agg['archetype'] == archetype]
    ax.scatter(archetype_data['judge_score_z'],
               archetype_data['fan_vote_z'],
               c=color,
               label=f'{archetype} (n={len(archetype_data)})',
               s=50,
               alpha=0.6,
               edgecolors='white',
               linewidth=0.5,
               zorder=3)

# Draw quadrant lines
ax.axhline(0, color='#808080', linestyle='--', linewidth=1.5, alpha=0.7, zorder=2)
ax.axvline(0, color='#808080', linestyle='--', linewidth=1.5, alpha=0.7, zorder=2)

# Add quadrant labels
quadrant_labels = [
    (1.5, 1.5, 'High Judge\nHigh Fan'),
    (1.5, -1.5, 'High Judge\nLow Fan'),
    (-1.5, 1.5, 'Low Judge\nHigh Fan'),
    (-1.5, -1.5, 'Low Judge\nLow Fan')
]

for x, y, label in quadrant_labels:
    ax.text(x, y, label, ha='center', va='center',
            fontsize=8, color='gray', alpha=0.3, weight='bold', zorder=1)

# Annotate famous contestants
short_names = {
    'Bobby Bones': 'Bobby Bones',
    'Jerry Rice': 'Jerry Rice',
    'Bristol Palin': 'B. Palin',
    'Meryl Davis': 'M. Davis',
    'Sabrina Bryan': 'S. Bryan',
    'Billy Ray Cyrus': 'B.R. Cyrus'
}

for _, row in annotate_df.iterrows():
    name = row['celebrity_name']
    offset_x, offset_y = famous_contestants.get(name, (5, 5))
    short_name = short_names.get(name, name)

    ax.annotate(short_name,
                xy=(row['judge_score_z'], row['fan_vote_z']),
                xytext=(offset_x, offset_y),
                textcoords='offset points',
                fontsize=7,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8,
                         edgecolor='gray', linewidth=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0',
                               color='gray', lw=0.5),
                zorder=10)

# Labels and styling
ax.set_xlabel('Average Standardized Judge Score (Z-score)')
ax.set_ylabel('Average Fan Vote Share (Z-score)')
ax.set_title('Contestant Archetypes: Judge Merit vs. Fan Popularity', fontsize=11, pad=10)

# Legend
ax.legend(loc='upper left', frameon=True, fancybox=False,
          edgecolor='gray', framealpha=0.9, title='Archetype', fontsize=7)

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Grid
ax.grid(True, alpha=0.2, linewidth=0.5, zorder=0)

# Set axis limits
ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)

plt.tight_layout()

# Save
png_path = 'figures/twin_model/contestant_clustering.png'
pdf_path = 'figures/twin_model/contestant_clustering.pdf'

plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.savefig(pdf_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')

print(f'\nFigure saved:')
print(f'  PNG: {png_path}')
print(f'  PDF: {pdf_path}')

plt.close()

# Print detailed statistics
print('\n=== Archetype Statistics ===')
for archetype in ['Superstars', 'Tech Giants', 'Fan Favorites', 'Underdogs']:
    cluster_data = contestant_agg[contestant_agg['archetype'] == archetype]
    if len(cluster_data) > 0:
        print(f'\n{archetype}:')
        print(f'  Count: {len(cluster_data)} ({len(cluster_data)/len(contestant_agg)*100:.1f}%)')
        print(f'  Avg Judge Score: {cluster_data["relative_judge_score"].mean():.3f}')
        print(f'  Avg Fan Vote: {cluster_data["fan_vote_share"].mean():.3f}')
        print(f'  Avg Placement: {cluster_data["placement"].mean():.1f}')
        print(f'  Avg Survival Weeks: {cluster_data["week"].mean():.1f}')

print('\n=== Visualization 2 Complete ===')
