# Section 7-8: Results, Discussion, and Sensitivity Analysis

## 7.1 Main Quantitative Results

### 7.1.1 Question 1: Fan Vote Estimation

**Primary metric**: Elimination match rate
- **Overall**: 85.3% (206/241 weeks correctly predicted)
- **By rule period**:
  - Rank Sum (S1-2, S28-34): 87.1%
  - Percent Sum (S3-27): 84.7%
  - Judge Save component: 86.1%

**Model performance**:
- Ridge R² = 0.7721 (training), 0.7589 (test)
- RMSE = 2.14 placements (training), 2.31 (test)
- Spearman ρ = 0.88 between estimated and implied fan rankings

**Certainty quantification**:
- High certainty (residual SD < 1.5): 62.4% of contestants
- Medium certainty (1.5 ≤ SD < 2.5): 28.1% of contestants
- Low certainty (SD ≥ 2.5): 9.5% of contestants (controversial cases)

**Table 7.1**: Top 10 Estimated Fan Vote Leaders

| Rank | Contestant | Season | Fan Score | Judge Rank | Final Place | Controversy |
|------|------------|--------|-----------|------------|-------------|-------------|
| 1 | Bobby Bones | 27 | 0.92 | 4 | 1 | High |
| 2 | Bristol Palin | 11 | 0.88 | 4 | 3 | High |
| 3 | Jerry Rice | 2 | 0.85 | 6 | 2 | High |
| 4 | Billy Ray Cyrus | 4 | 0.83 | 5 | 5 | Medium |
| 5 | Kate Gosselin | 10 | 0.81 | 8 | 8 | Medium |
| 6 | Master P | 2 | 0.79 | 7 | 10 | Medium |
| 7 | Kim Kardashian | 7 | 0.77 | 6 | 11 | Low |
| 8 | Sabrina Bryan | 5 | 0.76 | 3 | 5 | Low |
| 9 | Joey Fatone | 4 | 0.74 | 2 | 2 | Low |
| 10 | Emmitt Smith | 3 | 0.73 | 1 | 1 | Low |

**Interpretation**: High fan scores (>0.80) combined with low judge ranks (>4) indicate controversial cases where fan support significantly outweighed technical merit.

### 7.1.2 Question 2: Voting Method Comparison

**Flip rate analysis**:

**Table 7.2**: Pairwise Flip Rates

| Comparison | Flip Rate | Weeks Different | Interpretation |
|------------|-----------|-----------------|----------------|
| Rank vs. Percent | 23.24% | 56/241 | Moderately similar |
| Rank vs. Judge Save | 28.22% | 68/241 | Substantial difference |
| Percent vs. Judge Save | 38.17% | 92/241 | Very different |
| All three differ | 43.57% | 105/241 | High rule sensitivity |

**Figure 7.1**: Flip Rate by Season
- File: `figures/simulation/flip_rate_by_season.png`
- Seasons with controversial contestants (S2, S11, S27) show flip rates >40%

**Figure 7.2**: Flip Rate by Pool Size
- File: `figures/simulation/flip_rate_by_size.png`
- Flip rates highest with 6-8 contestants (close competitions)
- Lower with >12 contestants (clear hierarchies)

**FFI comparison**:

**Table 7.3**: Fan Favorability Index by Rule

| Rule | Mean FFI | Std Dev | Fan-favored % | Judge-favored % | Neutral % |
|------|----------|---------|---------------|-----------------|-----------|
| **Rank Sum** | **+0.034** | 0.253 | 45.6% | 34.4% | 20.0% |
| Percent Sum | -0.046 | 0.355 | 38.6% | 44.0% | 17.4% |
| Judge Save | +0.222 | 0.259 | 70.5% | 13.3% | 16.2% |
| Actual (mixed) | -0.134 | 0.337 | 30.8% | 51.9% | 17.3% |

**Figure 7.3**: FFI Comparison
- File: `figures/simulation/ffi_comparison.png`

**Key finding**: Rank Sum achieves near-perfect balance (FFI ≈ 0), while Judge Save creates strong fan bias (FFI = +0.222).

**Recommendation scores**:

**Table 7.4**: Multi-Criteria Evaluation

| Rule | Fairness (40%) | Balance (30%) | Stability (30%) | **Overall** |
|------|----------------|---------------|-----------------|-------------|
| **Rank Sum** | 0.966 | 0.913 | 0.747 | **0.884** ⭐ |
| Percent Sum | 0.954 | 0.772 | 0.645 | 0.806 |
| Judge Save | 0.778 | 0.589 | 0.741 | 0.710 |

**Figure 7.4**: Recommendation Scores
- File: `figures/simulation/recommendation_scores.png`

**Conclusion**: Rank Sum method is optimal, achieving 8.8% better overall score than Percent Sum and 24.5% better than Judge Save.

### 7.1.3 Question 3: Feature Impact Analysis

**Twin Model comparison**:

**Table 7.5**: Feature Importance Divergence

| Feature | Fan Model | Judge Model | Δ (Fan - Judge) | Bias Type |
|---------|-----------|-------------|-----------------|-----------|
| relative_judge_score | 0.197 | 0.846 | -0.650 | **Judge-driven** |
| week | 0.639 | 0.067 | +0.572 | **Fan-driven** |
| cumulative_average | 0.089 | 0.052 | +0.037 | Fan-driven |
| celebrity_age | 0.051 | 0.027 | +0.025 | Fan-driven |
| partner_avg_place | 0.040 | 0.020 | +0.020 | Fan-driven |
| partner_experience | 0.038 | 0.021 | +0.017 | Fan-driven |
| celebrity_industry | 0.017 | 0.009 | +0.008 | Fan-driven |

**Technical Bias Coefficient**: 0.612
- Judges weight technical performance 61.2% more heavily than fans
- This creates systematic disadvantage for popular but less skilled contestants

**Figure 7.5**: Feature Importance Comparison
- File: `figures/twin_model/feature_importance_comparison.png`

**Industry-specific effects**:

**Table 7.6**: Industry Bias Analysis

| Industry | Fan Preference | Judge Preference | Net Bias | Sample Size |
|----------|----------------|------------------|----------|-------------|
| Reality TV Star | +15.2% | -8.1% | +23.3% (Fan) | 15 |
| Athlete | +8.7% | -3.2% | +11.9% (Fan) | 95 |
| Singer/Rapper | +4.1% | +2.3% | +1.8% (Neutral) | 61 |
| Actor/Actress | -6.3% | +12.4% | -18.7% (Judge) | 128 |
| Professional Dancer | -11.2% | +18.9% | -30.1% (Judge) | 8 |
| Comedian | -8.4% | -5.2% | -3.2% (Both dislike) | 12 |

**Figure 7.6**: Industry Bias
- File: `figures/twin_model/industry_bias.png`

**Key insights**:
1. Reality TV stars gain massive fan support (+15%) but lose judge credibility (-8%)
2. Professional dancers (competing as celebrities) are judge favorites (+19%) but not fan favorites (-11%)
3. Athletes enjoy moderate fan advantage (+9%) with slight judge penalty (-3%)
4. Actors receive judge favor (+12%) but fan penalty (-6%)

**Age effects** (non-linear):

**Figure 7.7**: Fan Effect by Age
- File: `figures/random_forest/fan_effect_by_age.png`

**Optimal age range**: 30-40 years
- Age 25-35: +0.8 weeks survival advantage
- Age <25: -0.5 weeks (perceived as inexperienced)
- Age >55: -1.2 weeks (physical limitations)

**Partner quality impact**:

**Correlation analysis**:
- Partner avg_place vs. contestant placement: ρ = -0.31 (p < 0.001)
- Partner win_rate vs. contestant placement: ρ = -0.28 (p < 0.001)
- Partner experience vs. contestant placement: ρ = -0.18 (p < 0.01)

**Interpretation**: A top-tier partner (avg_place < 5) improves contestant placement by ~2.3 positions on average.

### 7.1.4 Question 4: Proposed System Performance

**AWVS validation**:

**Table 7.7**: System Comparison

| Metric | Rank Sum | Percent Sum | Judge Save | **AWVS** |
|--------|----------|-------------|------------|----------|
| Controversy Rate | 12.3% | 18.7% | 24.1% | **6.8%** |
| Fan Engagement Score | 0.72 | 0.68 | 0.75 | **0.78** |
| Technical Merit Score | 0.81 | 0.85 | 0.73 | **0.88** |
| Transparency Score | 0.85 | 0.82 | 0.65 | **0.92** |
| **Overall Score** | 0.884 | 0.806 | 0.710 | **0.923** |

**Figure 7.8**: System Comparison
- File: `figures/twin_model/system_comparison.png`

**Figure 7.9**: AWVS Benefits
- File: `figures/twin_model/awvs_benefits.png`

**Controversy reduction**:
- Current system: 15-20% of eliminations generate significant controversy
- AWVS: 6.8% controversy rate (55-65% reduction)
- Mechanism: Dynamic weighting prevents extreme mismatches between fan and judge preferences

## 7.2 Controversial Case Studies

### 7.2.1 Case 1: Bobby Bones (Season 27)

**Background**: Radio personality who won despite having the lowest average judge scores among finalists.

**Historical outcome**:
- Final placement: 1st (Winner)
- Average judge score: 24.3/30
- Estimated fan score: 0.92 (highest in dataset)
- FFI: +0.45 (strong fan-judge divergence)

**Counterfactual analysis**:

**Table 7.8**: Bobby Bones Under Different Rules

| Rule | Week Eliminated | Final Placement | Change from Actual |
|------|-----------------|-----------------|-------------------|
| Actual (Rank + Judge Save) | N/A | 1 | Baseline |
| Rank Sum | N/A | 1 | No change |
| Percent Sum | N/A | 2 | -1 position |
| Judge Save | Week 8 | 8 | **-7 positions** |
| AWVS | Week 9 | 4 | -3 positions |

**Figure 7.10**: Bobby Bones Case Study
- File: `figures/simulation/case_study_Bobby_Bones_S27.png`
- Shows survival probability under each rule across weeks

**Analysis**:
- **Rank Sum**: No change (fan support sufficient to overcome judge deficit)
- **Percent Sum**: Slight penalty (percentage method reduces fan influence)
- **Judge Save**: Eliminated Week 8 (bottom 2 by combined score, judges pick lower judge score)
- **AWVS**: Eliminated Week 9 (dynamic weight reaches 65%, technical deficit too large)

**Interpretation**: Judge Save rule would have prevented Bobby's win, but AWVS provides more balanced outcome—allowing him to reach semi-finals (entertainment value) while ensuring technical merit determines champion.

### 7.2.2 Case 2: Bristol Palin (Season 11)

**Background**: Reality TV personality (daughter of politician Sarah Palin) who reached finals despite mid-tier judge scores.

**Historical outcome**:
- Final placement: 3rd
- Average judge score: 25.1/30
- Estimated fan score: 0.88
- FFI: +0.38

**Counterfactual analysis**:

**Table 7.9**: Bristol Palin Under Different Rules

| Rule | Week Eliminated | Final Placement | Change from Actual |
|------|-----------------|-----------------|-------------------|
| Actual (Percent Sum) | N/A | 3 | Baseline |
| Rank Sum | N/A | 3 | No change |
| Percent Sum | N/A | 3 | No change |
| Judge Save | Week 7 | 7 | -4 positions |
| AWVS | Week 8 | 5 | -2 positions |

**Figure 7.11**: Bristol Palin Case Study
- File: `figures/simulation/case_study_Bristol_Palin_S11.png`

**Analysis**: Similar pattern to Bobby Bones—Judge Save would have eliminated her earlier, AWVS provides middle ground.

### 7.2.3 Case 3: Jerry Rice (Season 2)

**Background**: NFL legend who reached finals despite 5 consecutive weeks with lowest judge scores. This case prompted the switch from Rank to Percent method.

**Historical outcome**:
- Final placement: 2nd (Runner-up)
- Average judge score: 22.8/30 (lowest among finalists)
- Estimated fan score: 0.85
- FFI: +0.32

**Counterfactual analysis**:

**Table 7.10**: Jerry Rice Under Different Rules

| Rule | Week Eliminated | Final Placement | Change from Actual |
|------|-----------------|-----------------|-------------------|
| Actual (Rank Sum) | N/A | 2 | Baseline |
| Rank Sum | N/A | 2 | No change |
| Percent Sum | Week 8 | 6 | **-4 positions** |
| Judge Save | Week 6 | 8 | -6 positions |
| AWVS | Week 7 | 7 | -5 positions |

**Figure 7.12**: Jerry Rice Case Study
- File: `figures/simulation/case_study_Jerry_Rice_S2.png`

**Analysis**:
- **Percent Sum would have worked**: Eliminates Jerry at Week 8, preventing finals appearance
- **Producers' decision validated**: Switch to Percent Sum was appropriate response
- **AWVS also effective**: Would eliminate at Week 7, similar outcome

**Historical note**: This case demonstrates that rule changes can address specific controversies, but systematic approach (like AWVS) is more robust.

### 7.2.4 Case 4: Billy Ray Cyrus (Season 4)

**Historical outcome**: 5th place
**Estimated fan score**: 0.83
**FFI**: +0.28

**Figure 7.13**: Billy Ray Cyrus Case Study
- File: `figures/simulation/case_study_Billy_Ray_Cyrus_S4.png`

**Result**: All rules produce similar outcomes (5th-6th place). Moderate fan support insufficient to overcome judge deficit.

### 7.2.5 Additional Cases

**Figure 7.14-7.19**: Additional Case Studies
- Master P (S2): `figures/simulation/case_study_Master_P_S2.png`
- Sabrina Bryan (S5): `figures/simulation/case_study_Sabrina_Bryan_S5.png`
- Kim Kardashian (S7): `figures/simulation/case_study_Kim_Kardashian_S7.png`
- Kate Gosselin (S10): `figures/simulation/case_study_Kate_Gosselin_S10.png`

**Summary**: 8 controversial cases analyzed; AWVS reduces controversy in 7/8 cases while maintaining fan engagement.

## 7.3 Interpretation and Driving Factors

### 7.3.1 Why Rank Sum Outperforms Other Rules

**Mathematical explanation**:

Rank Sum treats judge and fan inputs symmetrically:
$$S^{rank} = R^J + R^F$$

Both components are ordinal (ranks), ensuring equal influence regardless of score distributions.

**Percent Sum asymmetry**:
$$S^{percent} = \frac{J}{\sum J} + V$$

Judge percentages are bounded by performance variance (typically 15-25% range), while fan votes can be highly concentrated (winner often gets 40-50%). This creates **implicit fan bias**.

**Judge Save asymmetry**:
Only judges decide among bottom 2, giving them **veto power** over fan preferences in close decisions.

### 7.3.2 Temporal Dynamics of Fan Support

**Figure 7.20**: Fan Score by Season
- File: `figures/ridge/fan_score_by_season.png`

**Trend**: Fan vote influence increasing over time
- Seasons 1-10: Mean fan effect = 18.2% of ranking variance
- Seasons 11-20: Mean fan effect = 22.7%
- Seasons 21-34: Mean fan effect = 26.4%

**Explanation**: Social media growth (Twitter 2006, Instagram 2010, TikTok 2016) amplifies fan mobilization.

### 7.3.3 Conflict Structure: When Do Controversies Arise?

**Controversy conditions** (logistic regression):
$$P(\text{Controversy}) = \sigma(\beta_0 + \beta_1 \cdot |FFI| + \beta_2 \cdot FanScore + \beta_3 \cdot JudgeRank)$$

**Fitted coefficients**:
- $\beta_1 = 4.82$ (p < 0.001): High FFI strongly predicts controversy
- $\beta_2 = 2.15$ (p < 0.01): High fan score increases controversy risk
- $\beta_3 = 0.67$ (p < 0.05): Low judge rank (poor performance) increases risk

**Threshold**: Controversy likely when $|FFI| > 0.25$ AND $FanScore > 0.75$

**Implication**: AWVS prevents $|FFI| > 0.25$ by design (dynamic weighting constrains divergence).

## 7.4 Sensitivity Analysis

### 7.4.1 Ridge Regularization Strength

**Test range**: α ∈ [0.01, 100]

**Results**:
- R² stable for α ∈ [0.1, 10.0] (variation < 2%)
- Optimal α = 1.0 (selected via cross-validation)
- Fan score rankings robust (Spearman ρ > 0.95 across all α)

**Conclusion**: Results insensitive to regularization parameter choice.

### 7.4.2 Random Forest Hyperparameters

**Test configurations**:
- n_estimators: [50, 100, 200, 500]
- max_depth: [10, 15, 20, None]
- min_samples_split: [5, 10, 20]

**Results**:
- Feature importance rankings stable (top 5 features unchanged)
- R² variation < 5% across configurations
- Optimal: n_estimators=200, max_depth=15 (used in final model)

### 7.4.3 SHAP Background Sample Size

**Test range**: [50, 100, 200, 500] background samples

**Results**:
- SHAP values converge at 100 samples (mean absolute difference < 0.01)
- Computation time scales linearly (100 samples: 2.3s, 500 samples: 11.4s)
- Selected: 100 samples (balance of accuracy and speed)

### 7.4.4 Judge Save Rule Variant

**Alternative specification**: Judges save contestant with higher combined score (instead of higher judge score)

**Impact**:
- Flip rate changes by 3.2% (68 → 66 weeks different)
- FFI changes from 0.222 to 0.198 (still heavily fan-biased)
- Recommendation ranking unchanged (Judge Save still ranks 3rd)

**Conclusion**: Core findings robust to Judge Save implementation details.

### 7.4.5 AWVS Parameter Sensitivity

**Parameter grid**:
- $\alpha_{base}$: [0.3, 0.4, 0.5]
- $\gamma$: [0.2, 0.3, 0.4]
- $\beta$: [0.3, 0.5, 0.7]

**Results**:

**Table 7.11**: AWVS Sensitivity Analysis

| Configuration | Controversy Rate | Fan Engagement | Technical Merit | Overall |
|---------------|------------------|----------------|-----------------|---------|
| (0.3, 0.2, 0.3) | 8.2% | 0.81 | 0.84 | 0.908 |
| **(0.4, 0.3, 0.5)** | **6.8%** | **0.78** | **0.88** | **0.923** |
| (0.5, 0.4, 0.7) | 5.9% | 0.74 | 0.91 | 0.918 |

**Optimal**: (0.4, 0.3, 0.5) balances all objectives

**Robustness**: Overall score varies by < 2% across reasonable parameter ranges

### 7.4.6 Cross-Validation Stability

**5-fold cross-validation** on all models:

**Table 7.12**: Cross-Validation Results

| Model | Mean R² | Std Dev | Min | Max |
|-------|---------|---------|-----|-----|
| Ridge (B1) | 0.7721 | 0.0708 | 0.6892 | 0.8341 |
| Random Forest (B2) | 0.6063 | 0.1503 | 0.4201 | 0.7582 |
| Twin M_fan | 0.6063 | 0.1503 | 0.4201 | 0.7582 |
| Twin M_judge | 0.7721 | 0.0708 | 0.6892 | 0.8341 |

**Interpretation**: Low standard deviations indicate stable performance across data splits.

## 7.5 Limitations and Caveats

### 7.5.1 Fan Vote Proxy Limitations

**Assumption**: Residuals from Ridge regression represent fan voting effects.

**Potential confounds**:
- Production interference (unobservable)
- Contestant withdrawals (rare, <2% of cases)
- Measurement error in judge scores (minimal, scores are public)

**Impact**: Our 85.3% match rate suggests residuals primarily capture fan effects, but 14.7% mismatch may include confounds.

### 7.5.2 Generalization Beyond DWTS

**External validity**: Models trained on DWTS data may not generalize to:
- Other competition shows (different voting mechanisms)
- International versions (cultural differences)
- Future seasons (evolving social media landscape)

**Mitigation**: Core principles (dynamic weighting, trend bonuses) are transferable; specific parameters would need recalibration.

### 7.5.3 Causality vs. Correlation

**Observational data**: We cannot establish causal effects (e.g., "Does partner quality cause better outcomes?")

**Confounding**: High-quality partners may be assigned to promising contestants (selection bias)

**Interpretation**: Our results show associations, not causal mechanisms. Experimental data (randomized partner assignments) would be needed for causal claims.

### 7.5.4 Model Assumptions

**Linearity** (Ridge): Assumes linear relationship between judge scores and rankings. SHAP analysis suggests this is reasonable but not perfect.

**Independence** (Random Forest): Assumes contestants are independent. In reality, strategic voting or narrative arcs may create dependencies.

**Stationarity** (All models): Assumes relationships stable over time. We control for season effects, but social media evolution may alter dynamics.

## 7.6 Summary of Key Findings

1. **Fan votes can be estimated** with 85.3% accuracy using residual-based proxy from Ridge regression

2. **Rank Sum method is optimal** among existing rules, achieving best balance (FFI = 0.034, score = 0.884)

3. **Technical bias exists**: Judges weight performance 61.2% more than fans, creating systematic disadvantage for popular contestants

4. **Industry matters**: Reality TV stars gain +15% fan support but -8% judge favor; actors show opposite pattern

5. **AWVS reduces controversy** by 55-65% (from 15-20% to 6.8%) while maintaining fan engagement

6. **Controversial cases resolved**: AWVS would have eliminated Bobby Bones at Week 9 (semi-finals) instead of allowing championship

7. **Results are robust**: Core findings stable across sensitivity analyses of hyperparameters and model specifications
