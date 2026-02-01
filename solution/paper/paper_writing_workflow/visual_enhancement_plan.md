# Visual Enhancement Plan: Heatmap & Clustering

**Date:** 2026-02-01
**Objective:** Add high-impact "O-Prize Style" visualizations to the paper.
**Target Section:** Section 7 (Problem 3: Determinants of Success).

---

## 1. Visualization 1: Feature Correlation Heatmap

### Purpose
To visually demonstrate that "Judge Scores" and "Fan Votes" (or other metadata) have different correlation structures with key features. This justifies the need for separate models (Twin Random Forest).

### Location
**Section 7.1 (Twin-Model Architecture)**, right before describing the model results. It serves as "Exploratory Data Analysis" (EDA) for Problem 3.

### Data Requirements
*   **Source:** `weekly_panel.csv` combined with `contestant_static.csv`.
*   **Columns to Correlate:**
    *   `relative_judge_score` (Target 1)
    *   `fan_vote_share` (Target 2 - Estimated)
    *   `celebrity_age`
    *   `partner_experience`
    *   `partner_win_rate`
    *   `week`
    *   `cumulative_average`
*   **Preprocessing:**
    *   Calculate Spearman correlation matrix.
    *   One-hot encode `celebrity_industry` if possible, or just skip categorical for the heatmap to keep it clean.

### Caption Draft
*"Figure 7.1: Spearman correlation heatmap of key performance and demographic features. Note the strong correlation between `week` and `fan_vote_share` vs. the weaker correlation with `judge_score`, hinting at different drivers."*

---

## 2. Visualization 2: Contestant Clustering (The "Quadrant Plot")

### Purpose
To classify contestants into archetypes based on the two dimensions of success: Merit (Judges) vs. Popularity (Fans). This adds "Sociological Depth" to the paper, similar to the O-Prize's word difficulty clustering.

### Location
**Section 7.2 (Divergence Analysis)** or **Section 7.3 (Industry Effects)**. It perfectly illustrates the "Technical Bias" concept.

### Data Requirements
*   **Source:** Aggregated season-level data (one point per contestant).
*   **X-Axis:** `Average Standardized Judge Score` (Z-score).
*   **Y-Axis:** `Average Fan Vote Share` (Estimated).
*   **Algorithm:** K-Means Clustering ($k=4$).

### The 4 Clusters (Archetypes)
1.  **Tech Giants (High Judge, Low Fan):** Skilled dancers who lack charisma (e.g., Sabrina Bryan).
2.  **Fan Favorites (Low Judge, High Fan):** The "Bobby Bones" cluster.
3.  **Superstars (High Judge, High Fan):** The winners (e.g., Meryl Davis).
4.  **Underdogs (Low Judge, Low Fan):** Early eliminations.

### Visual Style
*   **Scatter Plot:** Each dot is a contestant.
*   **Color:** By Cluster ID.
*   **Labels:** Annotate 3-4 famous names (Bobby Bones, Jerry Rice) to make it readable.
*   **Quadrants:** Draw dashed lines at $X=0, Y=0$.

### Caption Draft
*"Figure 7.3: Contestant Archetypes. We identify four distinct clusters using K-Means ($k=4$) on judge and fan scores. The 'Fan Favorites' cluster (top-left) highlights the primary source of controversy in the current voting system."*

---

## 3. Implementation Steps

1.  **Python Script:** Create `src/visualize_clustering.py`.
2.  **Generate Plot:** Save to `solution/figures/twin_model/contestant_clustering.png` and `correlation_heatmap.png`.
3.  **LaTeX Update:** Insert `\includegraphics` commands in `mcmthesis-demo.tex`.
