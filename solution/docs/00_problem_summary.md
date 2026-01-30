# Problem Summary (2026 MCM/ICM C: Data With The Stars)

## Quick Restatement
You are given DWTS judge score data (seasons 1-34) and contestant metadata. Fan votes are unknown. Build models to estimate fan votes weekly, compare voting schemes (rank vs percent) across seasons, analyze controversial cases, quantify effects of pro dancers and celebrity characteristics, and propose a fairer system. Provide a 25-page report plus memo and AI use report.

## Required Outputs
- Estimated fan votes for each contestant-week with uncertainty.
- Consistency checks against weekly eliminations.
- Cross-season comparison of rank vs percent methods.
- Case studies: seasons 2, 4, 11, 27 (and any others found).
- Impact analysis of pro dancers and celebrity characteristics.
- Proposed alternative voting system with justification.

## Data Highlights (2026_MCM_Problem_C_Data.csv)
- Columns: contestant info, results, placement, and weekX_judgeY_score.
- Judges score 1-10; decimals possible; bonus points embedded.
- N/A means no 4th judge or week did not occur.
- Scores set to 0 after elimination.
- Different number of contestants and weeks per season.

## Assumed Voting Rules by Season (to confirm)
- Seasons 1-2: combined by rank.
- Seasons 3-27: combined by percent.
- Seasons 28-34: combined by rank and bottom-two judge save.

## Immediate Data Checks
- Count contestants and weeks per season.
- Identify weeks with no elimination and multiple eliminations.
- Verify zero scores post-elimination.
- Validate missing values patterns (N/A).

## Gemini CLI Prompt (Problem Extraction)
```
You are a modeling competition assistant. From the 2026 MCM/ICM C statement below, extract:
1) Objectives and required outputs
2) Key variables and constraints
3) Data description and caveats
4) Implied assumptions that must be stated
5) Modeling tasks, grouped by stage
6) Potential pitfalls or ambiguities

Statement:
[PASTE FULL PROBLEM TEXT]
```

## Gemini CLI Prompt (Dataset Focus)
```
Given the dataset description for 2026_MCM_Problem_C_Data.csv, list:
- Required preprocessing steps
- Week/season edge cases
- Features to derive for modeling fan votes
- Suggested validation checks

Description:
[PASTE DATA TABLE + NOTES]
```
