# Summary Sheet

## Problem in One Sentence

Estimate unknown fan votes in "Dancing with the Stars" (34 seasons) from judge scores and elimination data, compare voting schemes (rank vs. percent methods), analyze controversial cases, and propose a fairer voting system.

## Core Approach

We developed a **four-stage modeling pipeline**:

1. **Fan Vote Estimation (Ridge Regression)**: Model ranking as a function of judge scores; residuals represent fan voting effects (R² = 0.7721)
2. **Feature Impact Analysis (Random Forest + SHAP)**: Identify non-linear effects of contestant characteristics on fan vs. judge preferences
3. **Counterfactual Simulation**: Compare three voting rules (Rank Sum, Percent Sum, Judge Save) across 241 elimination weeks
4. **Adaptive System Design (AWVS)**: Propose dynamic weighting that adjusts judge influence from 40% (early weeks) to 70% (finals) with trend-based rewards

## Key Results

1. **Fan Vote Estimation Accuracy**: Ridge regression achieves R² = 0.7721 with residual-based fan score proxy. Top controversial cases identified: Bobby Bones (S27, FFI = +0.45), Bristol Palin (S11, FFI = +0.38), Jerry Rice (S2, FFI = +0.32).

2. **Voting Rule Comparison**: Rank Sum method is most balanced (FFI = 0.034, closest to zero), with 45.6% fan-favored and 34.4% judge-favored eliminations. Percent Sum shows judge bias (FFI = -0.046), while Judge Save heavily favors fans (FFI = 0.222). Overall flip rate between rules: 23-38%.

3. **Feature Impact Divergence**: Fans prioritize temporal loyalty (week importance: 63.9%) and celebrity popularity, while judges focus on technical scores (84.6% importance). Industry bias exists: Reality TV stars gain +15% fan support but -8% judge scores relative to actors.

## Recommendations

1. **Adopt Rank Sum Method**: Achieves best balance (comprehensive score: 0.884/1.0) with fairness (0.966), balance (0.913), and stability (0.747). Eliminates 76.8% of controversies compared to current mixed system.

2. **Implement AWVS for Long-term**: Dynamic weighting ($\alpha(t) = 0.4 + 0.3 \cdot t/T_{max}$) with trend bonus ($\beta = 0.5$) reduces controversy rate from 15-20% to 5-8% while maintaining fan engagement (40-50% voting power in early rounds).

3. **Retire Judge Save Rule**: Creates highest bias (FFI = 0.222) and 38% flip rate vs. Percent Sum. Would have eliminated Bobby Bones at Week 8 (S27) but fails to address systemic issues.

## Why It Matters

- **Fairness**: Quantifies and corrects systematic biases (technical bias = 0.612) that disadvantage popular contestants
- **Transparency**: Provides mathematical framework for producers to predict and explain outcomes
- **Engagement**: Maintains fan influence (40-70% weight) while ensuring technical merit determines champions
- **Reproducibility**: All models validated on 34 seasons (2,014 contestant-weeks) with cross-validation

## Supporting Figure

**Figure 1**: Recommendation Scores Comparison
- File: `figures/simulation/recommendation_scores.png`
- Shows Rank Sum achieving 0.884 overall score vs. 0.806 (Percent Sum) and 0.710 (Judge Save)
