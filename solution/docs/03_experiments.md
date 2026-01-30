# Experiments Plan

## Data Preparation
- Load CSV, coerce scores to numeric, keep N/A as missing.
- Build week-level panel with total judge score per contestant-week.
- Remove post-elimination weeks from modeling.

## Baselines
- Fan share proportional to judge score share.
- Uniform fan share across remaining contestants.

## Fan Vote Estimation
- Implement constrained optimization (A) first.
- Compare to latent popularity model (B) if time permits.

## Scheme Simulation
- Rank method on all seasons.
- Percent method on all seasons.
- Rank + judge save for seasons 28-34.

## Validation
- Elimination match rate.
- Rank error for eliminated contestants.
- Sensitivity to regularization.

## Case Studies
- Run detailed analysis for seasons 2, 4, 11, 27.

## Figures and Tables
- Table: consistency metrics by season and method.
- Plot: fan share vs judge score for key contestants.
- Bar chart: impact of pro dancer and celebrity features.

## Codex Review Checklist
- Edge cases: no elimination, multiple elimination weeks.
- Consistent handling of N/A and 0 scores.
- Seeds, reproducibility, and config defaults.
