# Model Design

## Modeling Objectives
1) Estimate weekly fan vote shares for each contestant.
2) Match observed eliminations under both rank and percent rules.
3) Quantify uncertainty in fan vote estimates.
4) Compare voting schemes across seasons and controversy cases.
5) Analyze pro dancer and celebrity characteristics impact.
6) Propose a fairer alternative system.

## Fan Vote Estimation: Candidate Approaches

### A) Constrained Optimization (Week-by-Week)
- Variables: fan share per contestant-week.
- Constraints: sum to 1, nonnegative, elimination ordering consistent with observed.
- Objective: minimize deviation from smoothness or from a baseline (e.g., judge score share).
- Output: feasible fan vote estimates + constraint slack as consistency metric.

### B) Latent Popularity Model (Season-Level)
- Fan share modeled as softmax(alpha * popularity + beta * judge_score + features).
- Popularity is contestant-level or time-varying latent variable.
- Fit parameters to maximize likelihood of observed eliminations.

### C) Feasible Region + Sampling
- Identify all fan vote vectors consistent with eliminations.
- Sample feasible region (or approximate) to compute uncertainty bands.

## Consistency Metrics
- Elimination match rate by week and season.
- Average rank error for eliminated contestant.
- Percent of weeks with feasible fan vote solutions under constraints.

## Uncertainty Metrics
- Feasible range width for fan share (min/max by contestant-week).
- Bootstrap over weeks or constraints.
- Posterior variance (if Bayesian model).

## Voting Scheme Comparison
- Apply rank method to all seasons, percent method to all seasons.
- Compare elimination differences and final placements.
- Quantify fan influence: sensitivity of elimination to fan share changes.

## Controversy Case Studies
- Season 2 Jerry Rice
- Season 4 Billy Ray Cyrus
- Season 11 Bristol Palin
- Season 27 Bobby Bones
For each: compute whether alternative scheme changes outcome.

## Pro Dancer and Celebrity Characteristics Analysis
- Outcome variables: placement, survival time, judge scores, fan share.
- Features: age, industry, home region, pro dancer.
- Methods: regression or mixed effects model; compare judge vs fan effects.

## Proposed Alternative System
- Define objective criteria (fairness, excitement, stability).
- Example: weighted z-score of judge and fan totals with cap on fan dominance.
- Demonstrate impacts on historical seasons.

## Claude Code Task Template
```
Using this model design, implement:
- Data loading and panel construction
- Fan vote estimation method A (baseline) with optimization
- Voting scheme simulation (rank/percent/judge-save)
- Consistency and uncertainty metrics
- Scripts to reproduce figures and tables
```
