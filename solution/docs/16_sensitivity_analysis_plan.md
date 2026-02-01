# Sensitivity Analysis Plan

## Document Overview

**Purpose**: Comprehensive sensitivity analysis plan for all models in the MCM/ICM Problem C project
**Date**: 2026-02-01
**Status**: Planning Phase
**Priority**: High (Required for competition submission)

---

## 1. Executive Summary

Sensitivity analysis is a critical component of mathematical modeling that evaluates how model outputs respond to variations in input parameters. This document outlines a systematic plan to:

1. Identify all tunable parameters across four core models
2. Design experiments to test parameter sensitivity
3. Quantify the impact of parameter variations on key metrics
4. Visualize results using publication-ready figures
5. Draw conclusions about model robustness and reliability

**Expected Outcomes:**
- 8-10 sensitivity analysis experiments
- 6-8 publication-quality figures
- Comprehensive sensitivity analysis section for the paper (2-3 pages)
- Evidence of model robustness and reliability

---

## 2. Model Architecture Overview

### Model Hierarchy

```
Project Models
├── Model B1: Ridge Regression Fan Vote Estimation (Primary)
│   ├── Parameters: sensitivity (α), ridge_alpha, feature_set
│   └── Metrics: Match rate, R², RMSE, MAE
│
├── Model B2: Random Forest Fan Preference Analysis (Secondary)
│   ├── Parameters: n_estimators, max_depth, min_samples_split
│   └── Metrics: R², Feature importance, Cross-validation score
│
├── Model C: Counterfactual Simulation (Comparison)
│   ├── Parameters: Voting rule type, fan_vote_source
│   └── Metrics: Flip rate, Elimination consistency
│
└── Model D: Twin Model Analysis (Impact)
    ├── Parameters: Weight w, normalization_method
    └── Metrics: Fairness score, Spearman correlation, Stability
```

---

## 3. Sensitivity Analysis Experiments

### 3.1 Model B1: Ridge Regression

#### **Experiment 1: Sensitivity Coefficient (α) Calibration** ✅ IMPLEMENTED

**Status**: Already implemented in `ridge_model_v2.py:245-291`

**Parameter**: `sensitivity` (α)
**Range**: [0.1, 2.0]
**Current Optimal**: α = 0.10
**Metric**: Elimination match rate

**Tasks**:
- [x] Implementation complete
- [ ] Generate publication figure
- [ ] Write analysis section

**Figure Requirements**:
- **Type**: Line plot with markers
- **X-axis**: Sensitivity coefficient (α)
- **Y-axis**: Elimination match rate (%)
- **Additional**: Mark optimal point, add confidence bands if possible
- **Output**: `figures/sensitivity_alpha_match_rate.png/pdf`

**Analysis Questions**:
1. Why is optimal α = 0.10 (relatively low)?
2. What does this tell us about fan vote distribution?
3. How steep is the curve around the optimum? (Robustness indicator)

---

#### **Experiment 2: Ridge Regularization Strength (alpha)** ❌ NOT IMPLEMENTED

**Parameter**: `ridge_alpha` (Ridge regularization parameter)
**Range**: [0.001, 0.01, 0.1, 1, 10, 100, 1000]
**Current Value**: 19.3070 (auto-selected by cross-validation)
**Metrics**: R², RMSE, MAE, Feature coefficient stability

**Implementation Plan**:
```python
# Pseudocode
alphas = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
results = []

for alpha in alphas:
    model = RidgeFanVoteModelV2(alpha=alpha, sensitivity=0.1)
    model.train(X_train, y_train)

    # Evaluate
    r2 = model.score(X_test, y_test)
    rmse = compute_rmse(y_test, y_pred)
    coef_variance = np.var(model.model.coef_)

    results.append({
        'alpha': alpha,
        'r2': r2,
        'rmse': rmse,
        'coef_variance': coef_variance
    })
```

**Figure Requirements**:
- **Type**: Multi-panel figure (2x2)
  - Panel A: alpha vs R² (log scale x-axis)
  - Panel B: alpha vs RMSE (log scale x-axis)
  - Panel C: alpha vs Feature coefficient variance
  - Panel D: Feature coefficients heatmap for different alphas
- **Output**: `figures/sensitivity_ridge_alpha.png/pdf`

**Analysis Questions**:
1. Is the auto-selected alpha (19.3) near the optimal region?
2. How does regularization affect feature importance?
3. Trade-off between bias and variance?

---

#### **Experiment 3: Feature Set Ablation** ❌ NOT IMPLEMENTED

**Parameter**: Feature combinations
**Variants**:
1. Full feature set (baseline)
2. Judge scores only
3. Judge scores + rank
4. Judge scores + rank + cumulative average
5. All features except cumulative average

**Metrics**: R², RMSE, Match rate

**Implementation Plan**:
```python
feature_sets = {
    'full': ['relative_judge_score', 'judge_rank_in_week', 'cumulative_average'],
    'judge_only': ['relative_judge_score'],
    'judge_rank': ['relative_judge_score', 'judge_rank_in_week'],
    'no_cumulative': ['relative_judge_score', 'judge_rank_in_week']
}

for name, features in feature_sets.items():
    model = train_with_features(features)
    evaluate(model, name)
```

**Figure Requirements**:
- **Type**: Bar chart with error bars
- **X-axis**: Feature set variants
- **Y-axis**: Performance metrics (R², RMSE, Match rate)
- **Output**: `figures/sensitivity_feature_ablation.png/pdf`

**Analysis Questions**:
1. Which features are most critical?
2. Does cumulative average add predictive power?
3. Diminishing returns of adding features?

---

### 3.2 Model B2: Random Forest

#### **Experiment 4: Number of Trees (n_estimators)** ❌ NOT IMPLEMENTED

**Parameter**: `n_estimators`
**Range**: [10, 25, 50, 100, 200, 500, 1000]
**Current Value**: 100
**Metrics**: R², Training time, Feature importance stability

**Implementation Plan**:
```python
n_estimators_range = [10, 25, 50, 100, 200, 500, 1000]
results = []

for n in n_estimators_range:
    start_time = time.time()
    model = RandomForestRegressor(n_estimators=n, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    train_time = time.time() - start_time

    r2 = model.score(X_test, y_test)
    feature_importance = model.feature_importances_

    results.append({
        'n_estimators': n,
        'r2': r2,
        'train_time': train_time,
        'feature_importance': feature_importance
    })
```

**Figure Requirements**:
- **Type**: Dual-axis line plot
- **Left Y-axis**: R² score
- **Right Y-axis**: Training time (seconds)
- **X-axis**: Number of trees (log scale)
- **Output**: `figures/sensitivity_rf_n_estimators.png/pdf`

**Analysis Questions**:
1. At what point does R² plateau?
2. Trade-off between accuracy and computational cost?
3. Is n=100 sufficient or should we increase?

---

#### **Experiment 5: Maximum Depth (max_depth)** ❌ NOT IMPLEMENTED

**Parameter**: `max_depth`
**Range**: [3, 5, 7, 10, 15, 20, None]
**Current Value**: 10
**Metrics**: R², Overfitting indicator (train vs test gap)

**Implementation Plan**:
```python
max_depth_range = [3, 5, 7, 10, 15, 20, None]
results = []

for depth in max_depth_range:
    model = RandomForestRegressor(n_estimators=100, max_depth=depth, random_state=42)
    model.fit(X_train, y_train)

    train_r2 = model.score(X_train, y_train)
    test_r2 = model.score(X_test, y_test)
    overfitting_gap = train_r2 - test_r2

    results.append({
        'max_depth': depth if depth else 'None',
        'train_r2': train_r2,
        'test_r2': test_r2,
        'overfitting_gap': overfitting_gap
    })
```

**Figure Requirements**:
- **Type**: Line plot with two lines
- **Lines**: Train R² (solid), Test R² (dashed)
- **X-axis**: Maximum depth
- **Y-axis**: R² score
- **Shaded area**: Overfitting gap
- **Output**: `figures/sensitivity_rf_max_depth.png/pdf`

**Analysis Questions**:
1. Is max_depth=10 preventing overfitting?
2. What is the optimal depth for generalization?
3. How much does depth affect feature importance?

---

### 3.3 Model C: Counterfactual Simulation

#### **Experiment 6: Voting Rule Sensitivity** ✅ PARTIALLY IMPLEMENTED

**Status**: Flip rates calculated, but not visualized systematically

**Parameter**: Voting rule type
**Variants**: Rank Sum, Percent Sum, Judge Save
**Metrics**: Flip rate, Elimination consistency, FFI distribution

**Current Results**:
- Rank vs Percent: 23.57% flip rate
- Rank vs Judge Save: 27.39% flip rate
- Percent vs Judge Save: 38.22% flip rate

**Tasks**:
- [x] Calculate flip rates
- [ ] Generate comprehensive visualization
- [ ] Analyze season-by-season variation

**Figure Requirements**:
- **Type**: Multi-panel figure (2x2)
  - Panel A: Flip rate matrix (heatmap)
  - Panel B: FFI distribution by voting rule (violin plot)
  - Panel C: Season-by-season flip rate (line plot)
  - Panel D: Controversial cases impact (bar chart)
- **Output**: `figures/sensitivity_voting_rules.png/pdf`

**Analysis Questions**:
1. Which rule is most "stable" (least flips)?
2. Do certain seasons show higher sensitivity?
3. How do controversial cases behave under different rules?

---

#### **Experiment 7: Fan Vote Source Sensitivity** ❌ NOT IMPLEMENTED

**Parameter**: Source of fan vote estimates
**Variants**:
1. Ridge V2 predictions (current)
2. Random Forest predictions
3. Uniform distribution (baseline)
4. Judge-score-proportional (naive baseline)

**Metrics**: Flip rate consistency, Match rate

**Implementation Plan**:
```python
fan_vote_sources = {
    'ridge_v2': load_ridge_predictions(),
    'random_forest': load_rf_predictions(),
    'uniform': generate_uniform_votes(),
    'judge_proportional': generate_judge_proportional_votes()
}

for source_name, fan_votes in fan_vote_sources.items():
    simulator = VotingSimulator()
    results = simulator.simulate_all_rules(fan_votes)
    analyze_flip_rates(results, source_name)
```

**Figure Requirements**:
- **Type**: Grouped bar chart
- **X-axis**: Fan vote source
- **Y-axis**: Flip rate (%)
- **Groups**: Three pairwise comparisons (Rank vs Percent, etc.)
- **Output**: `figures/sensitivity_fan_vote_source.png/pdf`

**Analysis Questions**:
1. How sensitive are flip rates to fan vote estimation method?
2. Do all methods agree on controversial cases?
3. Which baseline (uniform vs judge-proportional) is more realistic?

---

### 3.4 Model D: Twin Model & New Voting System

#### **Experiment 8: Weight Parameter (w) Optimization** ❌ NOT IMPLEMENTED

**Parameter**: Judge weight `w` in new voting system
**Formula**: `S_total = w × f(Judge) + (1-w) × g(Fan)`
**Range**: [0, 0.1, 0.2, ..., 1.0]
**Metrics**: Fairness score, Spearman correlation, Stability index

**Implementation Plan**:
```python
weights = np.linspace(0, 1, 11)
results = []

for w in weights:
    # Simulate new voting system
    fairness = compute_fairness_score(w)
    correlation = compute_spearman_correlation(w)
    stability = compute_stability_index(w)

    results.append({
        'weight': w,
        'fairness': fairness,
        'correlation': correlation,
        'stability': stability
    })
```

**Figure Requirements**:
- **Type**: Multi-objective optimization plot (Pareto frontier)
- **X-axis**: Fairness score
- **Y-axis**: Stability score
- **Color**: Weight w (colorbar)
- **Markers**: Different normalization methods
- **Output**: `figures/sensitivity_weight_optimization.png/pdf`

**Analysis Questions**:
1. What is the optimal weight for balancing fairness and excitement?
2. Is there a Pareto-optimal solution?
3. How does normalization method affect the trade-off?

---

#### **Experiment 9: Normalization Method Comparison** ❌ NOT IMPLEMENTED

**Parameter**: Normalization function for judge scores and fan votes
**Variants**:
1. Rank-based (current)
2. Percent-based (current)
3. Z-score normalization
4. Min-Max scaling
5. Softmax transformation

**Metrics**: Flip rate, Correlation with original rankings

**Implementation Plan**:
```python
normalization_methods = {
    'rank': normalize_by_rank,
    'percent': normalize_by_percent,
    'zscore': normalize_by_zscore,
    'minmax': normalize_by_minmax,
    'softmax': normalize_by_softmax
}

for method_name, normalize_fn in normalization_methods.items():
    judge_norm = normalize_fn(judge_scores)
    fan_norm = normalize_fn(fan_votes)
    combined = 0.5 * judge_norm + 0.5 * fan_norm

    flip_rate = compute_flip_rate(combined, original_eliminations)
    correlation = compute_correlation(combined, original_rankings)

    results.append({
        'method': method_name,
        'flip_rate': flip_rate,
        'correlation': correlation
    })
```

**Figure Requirements**:
- **Type**: Scatter plot with annotations
- **X-axis**: Flip rate (%)
- **Y-axis**: Spearman correlation
- **Points**: Different normalization methods
- **Annotations**: Method names
- **Output**: `figures/sensitivity_normalization_methods.png/pdf`

**Analysis Questions**:
1. Which normalization preserves ranking order best?
2. Which method introduces most variability (excitement)?
3. Is there a "best" normalization for fairness?

---

## 4. Implementation Priority

### Phase 1: High Priority (Week 1)
1. ✅ **Experiment 1**: Sensitivity coefficient (α) - Generate figure
2. ❌ **Experiment 2**: Ridge alpha - Implement and analyze
3. ❌ **Experiment 6**: Voting rule sensitivity - Complete visualization

**Rationale**: These are core parameters with direct impact on main results.

### Phase 2: Medium Priority (Week 2)
4. ❌ **Experiment 4**: RF n_estimators
5. ❌ **Experiment 5**: RF max_depth
6. ❌ **Experiment 8**: Weight optimization

**Rationale**: Important for model validation and new system design.

### Phase 3: Low Priority (Week 3, if time permits)
7. ❌ **Experiment 3**: Feature ablation
8. ❌ **Experiment 7**: Fan vote source
9. ❌ **Experiment 9**: Normalization methods

**Rationale**: Supplementary analyses that strengthen the paper but not critical.

---

## 5. Visualization Standards

All sensitivity analysis figures must follow `docs/visualization_standards.md`:

### Common Requirements
- **Resolution**: 300 DPI
- **Format**: PNG + PDF
- **Color palette**: Okabe-Ito (colorblind-safe)
- **Font**: Arial/Helvetica, 8-10pt
- **Spines**: Remove top and right
- **Grid**: Horizontal only, alpha=0.3

### Specific Plot Types

#### Line Plots (Experiments 1, 2, 4, 5, 6)
- Line width: 2.0
- Markers: Circle, size 5
- Confidence bands: 95% CI if available
- Reference lines: Dashed, width 1.5

#### Bar Charts (Experiments 3, 7)
- Bar color: Light blue (#56B4E9)
- Edge color: Primary blue (#0072B2)
- Error bars: Black, capsize 4

#### Heatmaps (Experiment 6)
- Colormap: RdBu_r (diverging) or viridis (sequential)
- Annotations: Show values, format `.2f`
- Colorbar: Labeled, shrink 0.8

#### Scatter Plots (Experiments 8, 9)
- Marker size: 50-100
- Alpha: 0.7 for overlapping points
- Annotations: Avoid overlap, use adjustText if needed

---

## 6. Analysis Framework

For each experiment, follow this structure:

### 6.1 Quantitative Analysis
- **Parameter range tested**: [min, max, step]
- **Optimal value**: X (if applicable)
- **Sensitivity metric**: ΔOutput / ΔParameter
- **Robustness indicator**: Width of near-optimal region

### 6.2 Qualitative Analysis
- **Physical interpretation**: What does this parameter represent?
- **Expected behavior**: Does the result match intuition?
- **Practical implications**: How should users set this parameter?

### 6.3 Robustness Assessment
- **Low sensitivity**: Output changes < 5% for ±20% parameter change → Robust
- **Medium sensitivity**: Output changes 5-15% → Moderately robust
- **High sensitivity**: Output changes > 15% → Requires careful tuning

---

## 7. Paper Integration

### Section Structure (Recommended)

```markdown
## 5. Sensitivity Analysis

### 5.1 Overview
Brief introduction to sensitivity analysis purpose and scope.

### 5.2 Model B1: Ridge Regression Sensitivity
#### 5.2.1 Sensitivity Coefficient Calibration
[Figure 1: α vs Match Rate]
Analysis and interpretation...

#### 5.2.2 Regularization Strength
[Figure 2: Ridge alpha multi-panel]
Analysis and interpretation...

### 5.3 Model B2: Random Forest Hyperparameters
#### 5.3.1 Number of Trees
[Figure 3: n_estimators vs R²]
Analysis and interpretation...

#### 5.3.2 Maximum Depth
[Figure 4: max_depth vs overfitting]
Analysis and interpretation...

### 5.4 Model C: Voting Rule Robustness
[Figure 5: Voting rule sensitivity multi-panel]
Analysis and interpretation...

### 5.5 Model D: New System Parameter Optimization
[Figure 6: Weight optimization Pareto frontier]
Analysis and interpretation...

### 5.6 Summary and Conclusions
- Key findings from sensitivity analysis
- Model robustness assessment
- Recommendations for parameter selection
```

### Expected Length
- Total: 2-3 pages
- Figures: 6-8 (each with caption)
- Text: ~1500-2000 words

---

## 8. Code Organization

### Directory Structure
```
solution/
├── src/
│   ├── sensitivity_analysis/
│   │   ├── __init__.py
│   │   ├── ridge_sensitivity.py          # Experiments 1-3
│   │   ├── rf_sensitivity.py             # Experiments 4-5
│   │   ├── voting_rule_sensitivity.py    # Experiments 6-7
│   │   └── new_system_sensitivity.py     # Experiments 8-9
│   └── visualize_sensitivity.py          # Unified plotting script
├── figures/
│   └── sensitivity/                      # All sensitivity figures
└── docs/
    └── 16_sensitivity_analysis_plan.md   # This document
```

### Script Template

```python
"""
Sensitivity Analysis: [Experiment Name]
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config import DATA_DIR, FIGURES_DIR
from docs.visualization_standards import apply_publication_style

def run_experiment():
    """
    Main experiment function
    """
    # 1. Load data
    # 2. Define parameter range
    # 3. Run sensitivity sweep
    # 4. Collect results
    # 5. Generate figure
    # 6. Save results
    pass

def plot_results(results, output_path):
    """
    Generate publication-quality figure
    """
    apply_publication_style()
    fig, ax = plt.subplots(figsize=(5, 3.5))

    # Plotting code...

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    results = run_experiment()
    plot_results(results, FIGURES_DIR / "sensitivity" / "experiment_name.png")
```

---

## 9. Success Criteria

### Minimum Requirements (Must Have)
- [ ] At least 5 experiments completed
- [ ] At least 4 publication-quality figures
- [ ] Quantitative sensitivity metrics for all key parameters
- [ ] Robustness assessment for primary model (Ridge V2)
- [ ] Paper section draft (1.5+ pages)

### Target Goals (Should Have)
- [ ] All 9 experiments completed
- [ ] 6-8 publication-quality figures
- [ ] Comprehensive sensitivity analysis section (2-3 pages)
- [ ] Interactive sensitivity dashboard (optional, for presentation)

### Stretch Goals (Nice to Have)
- [ ] Monte Carlo sensitivity analysis (global sensitivity)
- [ ] Sobol indices for feature importance
- [ ] Automated sensitivity report generation
- [ ] Sensitivity analysis appendix with detailed tables

---

## 10. Timeline

### Week 1 (Days 1-3)
- Day 1: Implement Experiments 1-2 (Ridge sensitivity)
- Day 2: Implement Experiment 6 (Voting rule sensitivity)
- Day 3: Generate figures and draft analysis

### Week 2 (Days 4-6)
- Day 4: Implement Experiments 4-5 (RF sensitivity)
- Day 5: Implement Experiment 8 (Weight optimization)
- Day 6: Generate figures and integrate into paper

### Week 3 (Days 7-9, if needed)
- Day 7: Implement remaining experiments (3, 7, 9)
- Day 8: Finalize all figures and analysis
- Day 9: Review, polish, and integrate into final paper

---

## 11. References

### Sensitivity Analysis Methods
1. Saltelli, A., et al. (2008). *Global Sensitivity Analysis: The Primer*. Wiley.
2. Iooss, B., & Lemaître, P. (2015). A review on global sensitivity analysis methods. *Uncertainty Management in Simulation-Optimization of Complex Systems*.

### MCM/ICM Guidelines
3. COMAP (2026). *MCM/ICM Contest Instructions*.
4. Previous winning papers with strong sensitivity analysis sections.

### Visualization
5. Tufte, E. R. (2001). *The Visual Display of Quantitative Information*. Graphics Press.
6. Okabe-Ito colorblind-safe palette: https://jfly.uni-koeln.de/color/

---

## 12. Notes and Considerations

### Computational Cost
- Experiment 4 (n_estimators=1000) may take 10-20 minutes
- Experiment 7 (multiple fan vote sources) requires re-running full simulation
- Consider parallelization for parameter sweeps

### Data Requirements
- All experiments use existing processed data
- No new data collection needed
- Ensure reproducibility with fixed random seeds

### Potential Issues
1. **Overfitting in RF**: May need to adjust cross-validation strategy
2. **Computational time**: Large parameter sweeps may be slow
3. **Figure complexity**: Multi-panel figures need careful layout

### Mitigation Strategies
1. Use stratified k-fold cross-validation
2. Implement parallel processing with `joblib`
3. Follow visualization standards strictly, use GridSpec for layouts

---

## Appendix A: Sensitivity Metrics Definitions

### A.1 Local Sensitivity
$$
S_i = \frac{\partial Y}{\partial X_i} \bigg|_{X=X_0}
$$

### A.2 Normalized Sensitivity
$$
S_i^{norm} = \frac{\partial Y}{\partial X_i} \cdot \frac{X_i}{Y} \bigg|_{X=X_0}
$$

### A.3 Robustness Index
$$
R = 1 - \frac{\text{Var}(Y | X \in [X_{min}, X_{max}])}{\text{Var}(Y_{all})}
$$

### A.4 Flip Rate (for discrete outcomes)
$$
\text{Flip Rate} = \frac{\text{Number of changed outcomes}}{\text{Total outcomes}}
$$

---

## Appendix B: Quick Reference Table

| Experiment | Parameter | Range | Current | Priority | Status |
|------------|-----------|-------|---------|----------|--------|
| 1 | sensitivity (α) | [0.1, 2.0] | 0.10 | High | ✅ Implemented |
| 2 | ridge_alpha | [0.001, 1000] | 19.31 | High | ❌ Not started |
| 3 | feature_set | 5 variants | Full | Low | ❌ Not started |
| 4 | n_estimators | [10, 1000] | 100 | Medium | ❌ Not started |
| 5 | max_depth | [3, None] | 10 | Medium | ❌ Not started |
| 6 | voting_rule | 3 types | - | High | 🟡 Partial |
| 7 | fan_vote_source | 4 sources | Ridge V2 | Low | ❌ Not started |
| 8 | weight (w) | [0, 1] | - | Medium | ❌ Not started |
| 9 | normalization | 5 methods | Rank/Percent | Low | ❌ Not started |

---

**Document Version**: 1.0
**Last Updated**: 2026-02-01
**Next Review**: After Phase 1 completion
**Owner**: Claude Code Team
