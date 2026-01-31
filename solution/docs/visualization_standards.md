# Visualization Standards for MCM/ICM Project

## Overview

This document defines the unified visualization standards for all figures in this project. All plots must follow these specifications to ensure consistency, professionalism, and publication readiness.

## Color Palette

### Primary Colors (Okabe-Ito Colorblind-Safe Palette)

```python
COLORS = {
    'primary_blue': '#0072B2',      # Main data, lines
    'light_blue': '#56B4E9',        # Histograms, secondary data
    'orange': '#E69F00',            # Highlights, comparisons
    'red_orange': '#D55E00',        # Mean lines, important markers
    'green': '#009E73',             # Median lines, positive indicators
    'yellow': '#F0E442',            # Warnings, special cases
    'purple': '#CC79A7',            # Additional categories
    'black': '#000000',             # Text, borders
    'gray': '#808080'               # Grid lines, secondary elements
}
```

### Usage Guidelines

- **Primary data**: Use `primary_blue` (#0072B2)
- **Histograms/bars**: Use `light_blue` (#56B4E9) with 60% alpha
- **Mean lines**: Use `red_orange` (#D55E00) with dashed style `--`
- **Median lines**: Use `green` (#009E73) with dotted style `:`
- **Comparison groups**: Rotate through primary_blue, orange, green, purple
- **Background**: Always white (`#FFFFFF`)
- **Grid lines**: Light gray with 30% alpha (if needed)

## Typography

### Font Specifications

```python
FONT_CONFIG = {
    'family': 'sans-serif',
    'sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'size': 9,                    # Base font size
    'axes.labelsize': 10,         # Axis labels
    'axes.titlesize': 11,         # Subplot titles
    'xtick.labelsize': 8,         # X-axis tick labels
    'ytick.labelsize': 8,         # Y-axis tick labels
    'legend.fontsize': 8,         # Legend text
    'legend.title_fontsize': 9    # Legend title
}
```

### Text Guidelines

- **Axis labels**: Sentence case, include units in parentheses
  - Example: `"Standardized Judge Score"`, `"Time (weeks)"`
- **Statistical annotations**: Use monospace font for numbers
- **Panel labels**: Bold uppercase letters (A, B, C, D)
- **Legend**: No frame or light gray frame with 90% alpha

## Figure Dimensions

### Standard Sizes

```python
FIGURE_SIZES = {
    'single_column': (5, 3.5),      # Single column figure
    'double_column': (7, 4),        # Double column figure
    'square': (4, 4),               # Square plots (heatmaps, correlation)
    'wide': (7, 3),                 # Wide plots (time series)
    'tall': (4, 6)                  # Tall plots (vertical comparisons)
}
```

### Resolution

- **DPI**: 300 for all saved figures
- **Format**: PNG for reports, PDF for publication
- **Bbox**: Always use `bbox_inches='tight'`

## Line and Marker Styles

### Line Specifications

```python
LINE_STYLES = {
    'solid': '-',           # Primary data
    'dashed': '--',         # Mean, reference lines
    'dotted': ':',          # Median, secondary reference
    'dashdot': '-.',        # Tertiary reference
}

LINE_WIDTHS = {
    'data': 2.0,           # Main data lines
    'reference': 1.5,      # Mean/median lines
    'grid': 0.5,           # Grid lines
    'spine': 0.8           # Axis spines
}
```

### Marker Specifications

```python
MARKERS = {
    'circle': 'o',         # Primary data points
    'square': 's',         # Secondary data points
    'triangle': '^',       # Tertiary data points
    'diamond': 'D',        # Special points
}

MARKER_SIZES = {
    'small': 3,            # Dense scatter plots
    'medium': 5,           # Standard scatter plots
    'large': 8             # Emphasized points
}
```

## Plot Elements

### Spines and Borders

```python
# Remove top and right spines (Tufte style)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(0.8)
ax.spines['bottom'].set_linewidth(0.8)
```

### Grid Lines

```python
# Use sparingly, only when necessary
ax.grid(True, axis='y', alpha=0.3, linewidth=0.5, color='gray', linestyle='-')
```

### Statistical Annotation Box

```python
# Standard format for statistical summaries
props = dict(
    boxstyle='round',
    facecolor='white',
    alpha=0.8,
    edgecolor='gray',
    linewidth=0.8
)

textstr = f'n = {n:,}\nμ = {mean:.2f}\nσ = {std:.2f}'
ax.text(0.97, 0.97, textstr, transform=ax.transAxes,
        fontsize=8, verticalalignment='top',
        horizontalalignment='right', bbox=props,
        family='monospace')
```

## Standard Plot Templates

### Template 1: Distribution Plot

```python
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde, skew

def plot_distribution(data, title=None, xlabel='Value', output_path=None):
    """Create standardized distribution plot."""

    # Apply style
    plt.style.use('seaborn-v0_8-paper')
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 9,
        'axes.labelsize': 10,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'legend.fontsize': 8,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'axes.linewidth': 0.8
    })

    # Create figure
    fig, ax = plt.subplots(figsize=(5, 3.5))

    # Calculate statistics
    mean_val = np.mean(data)
    median_val = np.median(data)
    std_val = np.std(data)
    skewness = skew(data)

    # Histogram
    ax.hist(data, bins=30, density=True, alpha=0.6,
            color='#56B4E9', edgecolor='white', linewidth=0.5,
            label='Histogram')

    # Density curve
    kde = gaussian_kde(data)
    x_range = np.linspace(data.min(), data.max(), 200)
    ax.plot(x_range, kde(x_range), color='#0072B2',
            linewidth=2, label='Density curve')

    # Mean and median lines
    ax.axvline(mean_val, color='#D55E00', linestyle='--',
               linewidth=1.5, label=f'Mean = {mean_val:.2f}')
    ax.axvline(median_val, color='#009E73', linestyle=':',
               linewidth=1.5, label=f'Median = {median_val:.2f}')

    # Labels
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Density')
    if title:
        ax.set_title(title)

    # Statistical annotation
    textstr = f'n = {len(data):,}\nμ = {mean_val:.2f}\nσ = {std_val:.2f}\nSkewness = {skewness:.3f}'
    props = dict(boxstyle='round', facecolor='white', alpha=0.8,
                 edgecolor='gray', linewidth=0.8)
    ax.text(0.97, 0.97, textstr, transform=ax.transAxes,
            fontsize=8, verticalalignment='top',
            horizontalalignment='right', bbox=props,
            family='monospace')

    # Legend and styling
    ax.legend(loc='upper left', frameon=True, fancybox=False,
              edgecolor='gray', framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()

    # Save
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight',
                    facecolor='white', edgecolor='none')

    return fig, ax
```

### Template 2: Time Series Plot

```python
def plot_timeseries(x, y, xlabel='Time', ylabel='Value',
                   title=None, output_path=None, show_ci=True):
    """Create standardized time series plot."""

    fig, ax = plt.subplots(figsize=(7, 3))

    # Main line
    ax.plot(x, y, color='#0072B2', linewidth=2, marker='o',
            markersize=4, label='Data')

    # Confidence interval (if applicable)
    if show_ci and hasattr(y, 'std'):
        ci = 1.96 * y.std() / np.sqrt(len(y))
        ax.fill_between(x, y - ci, y + ci, color='#56B4E9',
                        alpha=0.3, label='95% CI')

    # Labels
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)

    # Styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='y', alpha=0.3, linewidth=0.5)
    ax.legend(frameon=False)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight',
                    facecolor='white', edgecolor='none')

    return fig, ax
```

### Template 3: Comparison Bar Plot

```python
def plot_comparison(categories, values, errors=None,
                   xlabel='Category', ylabel='Value',
                   title=None, output_path=None):
    """Create standardized comparison bar plot."""

    fig, ax = plt.subplots(figsize=(5, 3.5))

    # Bar plot
    x_pos = np.arange(len(categories))
    bars = ax.bar(x_pos, values, color='#56B4E9', alpha=0.8,
                  edgecolor='#0072B2', linewidth=1.5)

    # Error bars
    if errors is not None:
        ax.errorbar(x_pos, values, yerr=errors, fmt='none',
                   color='black', capsize=4, linewidth=1.5)

    # Labels
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    if title:
        ax.set_title(title)

    # Styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylim(bottom=0)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight',
                    facecolor='white', edgecolor='none')

    return fig, ax
```

### Template 4: Heatmap

```python
def plot_heatmap(data, xticklabels, yticklabels,
                xlabel='X', ylabel='Y', title=None,
                output_path=None, cmap='RdBu_r', center=0):
    """Create standardized heatmap."""

    import seaborn as sns

    fig, ax = plt.subplots(figsize=(6, 5))

    # Heatmap
    sns.heatmap(data, annot=True, fmt='.2f', cmap=cmap,
                center=center, square=True, linewidths=0.5,
                cbar_kws={'shrink': 0.8, 'label': 'Value'},
                xticklabels=xticklabels, yticklabels=yticklabels,
                ax=ax)

    # Labels
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight',
                    facecolor='white', edgecolor='none')

    return fig, ax
```

## Multi-Panel Figures

### Panel Layout

```python
from string import ascii_uppercase

# Create multi-panel figure
fig = plt.figure(figsize=(7, 6))
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, 0])
ax4 = fig.add_subplot(gs[1, 1])

# Add panel labels
for i, ax in enumerate([ax1, ax2, ax3, ax4]):
    ax.text(-0.15, 1.05, ascii_uppercase[i],
            transform=ax.transAxes, fontsize=12,
            fontweight='bold', va='top')
```

## File Naming Convention

```
{figure_type}_{description}_{version}.{ext}

Examples:
- distribution_judge_scores_v1.png
- timeseries_elimination_pattern_v2.pdf
- comparison_voting_schemes_final.png
- heatmap_correlation_matrix_v1.png
```

## Quality Checklist

Before finalizing any figure, verify:

- [ ] Colors match the Okabe-Ito palette
- [ ] Font sizes are readable (≥8pt for labels)
- [ ] Spines: top and right removed
- [ ] DPI = 300
- [ ] Background is white
- [ ] Axis labels include units
- [ ] Legend is clear and positioned appropriately
- [ ] Statistical annotations are present (if applicable)
- [ ] File saved in both PNG and PDF formats
- [ ] Figure works in grayscale (test for colorblind accessibility)

## Python Setup Code

Add this to the beginning of any plotting script:

```python
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats

# Standard configuration
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
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
    'lines.linewidth': 1.5
})

# Color palette
COLORS = {
    'primary_blue': '#0072B2',
    'light_blue': '#56B4E9',
    'orange': '#E69F00',
    'red_orange': '#D55E00',
    'green': '#009E73',
    'yellow': '#F0E442',
    'purple': '#CC79A7',
    'black': '#000000',
    'gray': '#808080'
}
```

## References

- Okabe-Ito colorblind-safe palette: [Color Universal Design](https://jfly.uni-koeln.de/color/)
- Tufte principles: Minimize chart junk, maximize data-ink ratio
- Nature journal figure guidelines
- Science journal figure guidelines

---

**Last Updated**: 2026-01-31
**Maintained By**: Claude Code
**Version**: 1.0
