# Visualization Upgrade Plan: From Standard to Sophisticated

**Date:** 2026-02-01
**Objective:** Replace standard/low-quality charts (especially simple bar charts) with publication-ready, information-dense, and aesthetically superior visualizations.
**Design Philosophy:** "Less Ink, More Data." Use modern chart types that emphasize *relationships* and *distributions* rather than just magnitudes.

---

## 1. Visual Style Guide (The "O-Prize" Aesthetic)

*   **Color Palette:** Use a cohesive, professional palette.
    *   *Primary (Fan):* `#FF6B6B` (Muted Red/Coral)
    *   *Secondary (Judge):* `#4ECDC4` (Teal/Turquoise)
    *   *Neutral:* `#2D3436` (Charcoal) and `#DFE6E9` (Light Gray)
*   **Fonts:** `Helvetica` or `Arial` for sans-serif clarity. Large axis labels (size 12+).
*   **Background:** Clean white background (`sns.set_style("whitegrid")`), remove top/right spines (`sns.despine()`).
*   **Resolution:** All figures saved as 300 DPI PNGs or PDFs.

---

## 2. Targeted Replacements (The "Before & After")

| Current Figure (Likely Style) | **Proposed Replacement (Advanced Style)** | **Why?** |
| :--- | :--- | :--- |
| `recommendation_scores.png` <br> *(Grouped Bar Chart)* | **Radar Chart (Spider Plot)** | Shows multi-dimensional trade-offs (Fairness, Balance, Stability) for 3 rules simultaneously. Looks highly technical. |
| `feature_importance_comparison.png` <br> *(Side-by-Side Bars)* | **Dumbbell Plot (Cleveland Dot Plot)** | Connects the Fan and Judge dots for each feature with a line. Visually highlights the *gap* (Bias) directly. |
| `industry_bias.png` <br> *(Bar Chart)* | **Diverging Bar Chart** | Center the x-axis at 0. Bars go Left for Judge-Favored, Right for Fan-Favored. Sort by magnitude. |
| `ffi_comparison.png` <br> *(Overlaid Histograms)* | **Raincloud Plot (or Split Violin)** | Combines a box plot, a density plot (half-violin), and raw data points. Shows distribution shape + statistical summary + sample density. |
| `case_study_*.png` <br> *(Line Charts)* | **Bump Chart (Rank Flow)** | Specifically designed for ranking changes over time. Highlights the specific contestant's path vs. the "pack". |
| `flip_rate_by_season.png` <br> *(Bar/Line)* | **Streamgraph (Stacked Area)** | If showing flip types, a streamgraph shows the evolution of instability fluidly over time. |

---

## 3. Detailed Implementation Specs

### 3.1 Radar Chart for Problem 4 (System Evaluation)
*   **Data:** Scores for Rank Sum, Percent Sum, Judge Save, AWVS.
*   **Axes:** Fairness, Balance, Stability, Transparency, Engagement.
*   **Visual:** Semi-transparent filled polygons.
*   **Caption:** *"Figure 8.X: Multi-criteria evaluation of voting systems. AWVS (Blue) encloses the largest area, indicating superior aggregate performance."*

### 3.2 Dumbbell Plot for Problem 3 (Twin Model)
*   **Data:** Feature Importance scores for Fan RF and Judge RF.
*   **Layout:** Y-axis = Features (sorted by Gap). X-axis = Importance.
*   **Visual:**
    *   Dot 1 (Judge): Teal.
    *   Dot 2 (Fan): Coral.
    *   Line connecting them: Gray.
*   **Insight:** Long lines = High disagreement (e.g., `relative_judge_score`). Short lines = Agreement.

### 3.3 Diverging Bars for Problem 3 (Industry Bias)
*   **Data:** Net Bias % per Industry.
*   **Layout:** X-axis = Net Bias (Negative = Judge Favored, Positive = Fan Favored). Y-axis = Industry.
*   **Visual:**
    *   Positive bars: Coral.
    *   Negative bars: Teal.
    *   Vertical line at x=0.
    *   Value labels inside/at end of bars.

### 3.4 Bump Chart for Case Studies
*   **Data:** Weekly Ranks of top 5 contestants + The Controversial One.
*   **Visual:**
    *   X-axis: Week 1 to Week N.
    *   Y-axis: Rank (1 at top).
    *   Lines: Gray for background contestants. **Thick Red Line** for the subject (e.g., Bobby Bones).
    *   Nodes: Circles at each week point.

---

## 4. Execution Plan

1.  **Scripting:** Create a new Python script `src/visualize_advanced.py`.
2.  **Data Loading:** Load `weekly_panel.csv`, `simulation_results.csv`, and model artifacts.
3.  **Generation:**
    *   Generate `radar_chart.png` (Replaces `recommendation_scores.png`).
    *   Generate `dumbbell_plot.png` (Replaces `feature_importance_comparison.png`).
    *   Generate `diverging_bars.png` (Replaces `industry_bias.png`).
    *   Generate `violin_ffi.png` (Replaces `ffi_comparison.png`).
4.  **LaTeX Integration:** Update `mcmthesis-demo.tex` to point to these new files and update captions to reflect the new chart types.

## 5. Benefits
*   **Space Efficiency:** Radar charts combine 3-4 bar charts into one.
*   **Readability:** Dumbbell plots make comparing two groups (Fan vs Judge) instant, whereas side-by-side bars require cognitive effort to compare heights.
*   **Aesthetics:** "O-Prize" papers are defined by non-standard, high-information-density graphics.
