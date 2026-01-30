# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **2026 MCM/ICM Problem C** workspace for analyzing "Dancing with the Stars" competition data. The goal is to estimate unknown fan votes from judge scores and elimination data, compare voting schemes across seasons, analyze controversial cases, and propose a fairer voting system.

**Key Challenge**: Fan votes are not provided in the dataset. All fan vote estimates must be inferred from judge scores and observed eliminations under different voting rules.

## Collaborative Workflow

This project uses a three-agent workflow (see WORKFLOW.md):
- **Gemini CLI**: Long-text analysis, problem decomposition, literature review
- **Claude Code**: Implementation, experiments, code scaffolding
- **Codex**: Code review, debugging, consistency checks

**Your role as Claude Code**: Implement models and experiments based on design documents in `solution/docs/`, generate reproducible results, and maintain code quality.

## Directory Structure

```
problem/
  2026_MCM_Problem_C.pdf           # Problem statement
  primitive_data/
    2026_MCM_Problem_C_Data.csv    # Raw dataset

solution/
  src/                              # Main codebase
    main.py                         # Entry point
    config.py                       # Path configuration
    pipeline.py                     # Voting scheme simulation logic
    models/
      fan_vote_model.py             # Fan vote estimation (stub)
    utils/
      data.py                       # Data loading and panel construction
  docs/                             # Design documents (numbered)
    00_problem_summary.md
    01_assumptions.md
    02_model_design.md
    03_experiments.md
    04_results.md
    05_paper_outline.md
    06_decision_log.md
  Data/                             # Processed data
    raw/                            # Copy of raw data here
  figures/                          # Generated plots
  tests/                            # Unit tests (empty)
```

## Running the Code

**Setup**:
```bash
cd solution
# Copy raw data to expected location
mkdir -p Data/raw
cp ../problem/primitive_data/2026_MCM_Problem_C_Data.csv Data/raw/

# Install dependencies (pandas, numpy, scipy, matplotlib, etc.)
# No requirements.txt yet - infer from imports
```

**Run main pipeline**:
```bash
cd solution/src
python main.py
```

**Current status**: `main.py` loads data and builds week-level panel. Fan vote estimation (`pipeline.py:estimate_fan_votes`) is not yet implemented.

## Data Architecture

**Raw Data** (`2026_MCM_Problem_C_Data.csv`):
- Columns: `celebrity_name`, `ballroom_partner`, `celebrity_industry`, `celebrity_age_during_season`, `celebrity_homestate`, `celebrity_homecountry/region`, `season`, `results`, `placement`, `week1_judge1_score`, `week1_judge2_score`, ..., `weekN_judgeM_score`
- Judge scores: 1-10 scale, decimals allowed, N/A for missing judges/weeks
- Scores become 0 after contestant elimination
- Different seasons have different numbers of weeks and contestants

**Panel Data** (built by `utils/data.py:build_week_panel`):
- Transforms wide format (one row per contestant) to long format (one row per contestant-week)
- Adds `week`, `judge_total` (sum of judge scores), `has_scores` (boolean)
- Preserves all contestant metadata columns

## Voting Schemes (Implemented in `pipeline.py`)

Three methods for combining judge scores and fan votes:

1. **Rank Method** (`combine_rank`): Rank contestants by judge total and fan votes separately, sum ranks (lower is better)
2. **Percent Method** (`combine_percent`): Convert to percentages, sum percentages (higher is better)
3. **Judge Save** (`select_eliminated` with `judge_save=True`): Identify bottom two by combined score, judges eliminate contestant with lower judge total

**Assumed season rules** (from `docs/00_problem_summary.md`):
- Seasons 1-2: rank method
- Seasons 3-27: percent method
- Seasons 28-34: rank method + judge save

## Key Modeling Tasks

**Priority 1: Fan Vote Estimation** (see `docs/02_model_design.md`)
- Implement `FanVoteModel` in `src/models/fan_vote_model.py`
- Recommended approach: constrained optimization (week-by-week)
  - Variables: fan share per contestant-week
  - Constraints: sum to 1, nonnegative, elimination ordering consistent with observed
  - Objective: minimize deviation from smoothness or judge score baseline
- Output: estimated fan shares + uncertainty bounds

**Priority 2: Consistency Metrics**
- Elimination match rate by week and season
- Feasibility check: can any fan vote vector explain observed eliminations?

**Priority 3: Cross-Season Comparison**
- Apply rank method to all seasons, percent method to all seasons
- Compare elimination differences and final placements

**Priority 4: Controversy Case Studies**
- Season 2: Jerry Rice
- Season 4: Billy Ray Cyrus
- Season 11: Bristol Palin
- Season 27: Bobby Bones
- For each: compute whether alternative scheme changes outcome

## Important Constraints

**Data Handling**:
- Use `pd.to_numeric(..., errors='coerce')` for judge scores (handles N/A)
- Filter out weeks where `has_scores == False` after elimination
- Handle missing values explicitly (N/A ≠ 0)

**Reproducibility**:
- Set random seeds for any stochastic methods
- Log all parameter choices in `docs/06_decision_log.md`
- Save intermediate results to `Data/processed/`

**Documentation Requirements** (from RUNBOOK.md):
- All modeling decisions must be recorded in `docs/` with numbered files
- Update `docs/06_decision_log.md` for any assumption changes
- Maintain consistency between code, experiments, and paper

## Code Style

- Use type hints where helpful (already present in `pipeline.py`)
- Prefer pandas operations over loops for performance
- Keep functions focused and testable
- Use descriptive variable names (`judge_total`, `fan_votes`, not `x`, `y`)

## Common Pitfalls

1. **Zero scores after elimination**: These indicate non-participation, not actual scores. Filter by `has_scores` flag.
2. **N/A vs 0**: N/A means missing data (no 4th judge, week didn't occur). Don't treat as zero.
3. **Multiple eliminations**: Some weeks eliminate multiple contestants. Use `n_eliminate` parameter.
4. **Infeasible fan votes**: Not all elimination patterns may be explainable by any fan vote distribution. Track feasibility.
5. **Season rule changes**: Don't assume all seasons use the same voting method.

## Next Steps

When implementing fan vote estimation:
1. Read `docs/02_model_design.md` for detailed approach
2. Implement optimization-based method in `models/fan_vote_model.py`
3. Add consistency checks to validate against observed eliminations
4. Generate uncertainty bounds (feasible range or bootstrap)
5. Create visualization scripts for `figures/`
6. Update `docs/03_experiments.md` with results

## Handoff Protocol

When completing work, provide:
- **Input**: Documents referenced, assumptions added, model/parameter changes
- **Output**: Key results, generated files, items needing verification
- **Next**: Recommended next steps or open questions

See RUNBOOK.md for detailed handoff template.
