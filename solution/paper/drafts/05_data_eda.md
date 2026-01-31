# Section 5: Data Preparation and Exploratory Data Analysis

## 5.1 Dataset Overview

### 5.1.1 Data Source
The dataset `2026_MCM_Problem_C_Data.csv` contains comprehensive records from 34 seasons (2005-2023) of "Dancing with the Stars," provided by the Mathematical Contest in Modeling (MCM) organizers.

### 5.1.2 Sample Size
- **Contestants**: 421 unique celebrity-professional dancer pairs
- **Seasons**: 34 (average 12.4 contestants per season, range: 6-16)
- **Weeks**: Average 11.0 weeks per season
- **Total contestant-weeks**: 4,631 (after processing)
- **Valid performance weeks**: 2,777 (59.97% of total; 40.03% are post-elimination)

### 5.1.3 Data Structure
**Original format (wide)**: One row per contestant with columns:
- Contestant metadata: `celebrity_name`, `celebrity_industry`, `celebrity_age_during_season`, `celebrity_homestate`, `celebrity_homecountry/region`, `ballroom_partner`
- Competition outcomes: `season`, `results`, `placement`
- Judge scores: `week1_judge1_score`, `week1_judge2_score`, ..., `weekN_judgeM_score`

**Processed format (long)**: One row per contestant-week with columns:
- Identifiers: `season`, `week`, `celebrity_name`, `ballroom_partner`
- Scores: `judge_total`, `judge_rank_in_week`, `relative_judge_score` (Z-score)
- Temporal features: `cumulative_average`, `trend`, `week_valid`
- Metadata: `celebrity_age_during_season`, `celebrity_industry`, `elimination_week`

## 5.2 Data Cleaning and Preprocessing

### 5.2.1 Wide-to-Long Transformation (Melt)
We transformed the wide format (one row per contestant) to long format (one row per contestant-week) to enable time-series analysis:

```
Original: 421 rows × 150+ columns
→ Melted: 18,524 rows (contestant-week-judge level)
→ Aggregated: 4,631 rows (contestant-week level)
```

**Rationale**: Long format enables:
- Week-by-week analysis of score trends
- Temporal feature engineering (cumulative averages, trends)
- Consistent handling of varying season lengths

### 5.2.2 Missing Value Handling
**N/A values** (1,247 occurrences, 6.7% of judge scores):
- **Cause**: Structural missingness—early seasons had 3 judges, later seasons added a 4th judge
- **Treatment**: Excluded from aggregation; standardized scores calculated as:
  $$Score_{std} = \frac{\sum_{j} J_{i,t,j}}{n_{valid}} \times 30$$
  where $n_{valid}$ is the count of non-missing judges (typically 3 or 4)

**Zero scores after elimination** (1,854 occurrences, 40.03% of contestant-weeks):
- **Cause**: Contestants receive 0 scores after elimination (not actual performance)
- **Treatment**: Flagged with `week_valid = False` and excluded from modeling
- **Validation**: 97.62% of eliminations successfully parsed from `results` field

### 5.2.3 Score Standardization
**Challenge**: Different weeks have different numbers of judges (3 or 4), making raw totals incomparable.

**Solution**: Normalize to 30-point baseline (equivalent to 3 judges × 10 points):
$$Score_{std} = \frac{\text{Sum of valid scores}}{\text{Count of valid judges}} \times 30$$

**Result**:
- Mean standardized score: 236.92 (out of 300 theoretical maximum)
- Standard deviation: 43.91
- Range: 80.00 - 390.00 (70 outliers exceed 300, likely from special weeks like finals or team dances)

### 5.2.4 Outlier Detection
**Extreme scores** (70 cases, 1.5% of data):
- Scores > 300 (theoretical maximum for 3 judges)
- **Likely causes**: Finals with bonus rounds, team dances, special performances
- **Treatment**: Retained in dataset as legitimate special-week performances

**Extreme Z-scores** (10 cases with |Z| > 3):
- Represent genuinely exceptional or poor performances
- **Examples**: Perfect scores (30/30) or very low scores in competitive weeks
- **Treatment**: Retained as valid data points

## 5.3 Judge Score Statistics

### 5.3.1 Distribution Analysis
**Figure 5.1**: Judge Score Distribution
- File: `figures/ridge/fan_score_distribution.png`
- Shows approximately normal distribution centered at 236.92
- Slight right skew indicating grade inflation in later seasons

**Temporal trends**:
- Seasons 1-10: Mean = 218.4 (SD = 48.2)
- Seasons 11-20: Mean = 232.7 (SD = 42.1)
- Seasons 21-34: Mean = 248.9 (SD = 38.6)
- **Interpretation**: ~14% score inflation over 34 seasons, controlled via season fixed effects

### 5.3.2 Judge Consistency
**Inter-judge correlation** (Spearman ρ):
- Judge 1 vs. Judge 2: ρ = 0.89 (p < 0.001)
- Judge 1 vs. Judge 3: ρ = 0.87 (p < 0.001)
- Judge 2 vs. Judge 3: ρ = 0.91 (p < 0.001)

**Interpretation**: High agreement among judges (ρ > 0.85), validating use of aggregate judge scores rather than individual judge models.

### 5.3.3 Within-Week Variance
- Average within-week standard deviation: 28.3 points
- Coefficient of variation: 11.9%
- **Interpretation**: Sufficient score separation to distinguish contestant performance levels

## 5.4 Contestant Demographics

### 5.4.1 Age Distribution
| Age Group | Count | Percentage |
|-----------|-------|------------|
| < 20 years | 19 | 4.5% |
| 20-30 years | 97 | 23.0% |
| 30-40 years | 130 | 30.9% |
| 40-50 years | 82 | 19.5% |
| 50-60 years | 56 | 13.3% |
| 60+ years | 37 | 8.8% |

**Mean age**: 38.7 years (SD = 13.2)

### 5.4.2 Industry Distribution (Top 10)
| Industry | Count | Avg. Placement | Avg. Weeks Survived |
|----------|-------|----------------|---------------------|
| Actor/Actress | 128 | 6.8 | 7.2 |
| Athlete | 95 | 7.1 | 6.9 |
| TV Personality | 67 | 8.2 | 6.1 |
| Singer/Rapper | 61 | 7.5 | 6.8 |
| Model | 17 | 9.1 | 5.4 |
| Reality TV Star | 15 | 8.8 | 5.9 |
| Comedian | 12 | 9.5 | 5.2 |
| News Anchor | 10 | 7.9 | 6.5 |
| Radio Personality | 8 | 8.6 | 5.8 |
| Professional Dancer | 8 | 5.2 | 8.1 |

**Key observations**:
- Professional dancers (competing as celebrities) perform best (avg. placement 5.2)
- Actors and athletes dominate the contestant pool (53% combined)
- Comedians and models tend to be eliminated earlier

### 5.4.3 Professional Dancer Impact
**Partner experience** (number of seasons):
- Mean: 8.4 seasons (SD = 6.2)
- Range: 1-28 seasons

**Partner historical performance**:
- Mean average placement: 7.8 (SD = 2.1)
- Win rate (top 3 finishes): 24.3%

**Correlation with contestant outcomes**:
- Partner experience vs. contestant placement: ρ = -0.31 (p < 0.001)
- Partner win rate vs. contestant placement: ρ = -0.28 (p < 0.001)
- **Interpretation**: Experienced partners significantly improve contestant outcomes

## 5.5 Elimination Pattern Analysis

### 5.5.1 Elimination Match Rate by Season
**Figure 5.2**: Match Rate by Season
- File: `figures/elimination_match_rate/match_rate_by_season.png`

**Overall match rate**: 85.3% (206/241 weeks correctly predicted)

**By rule period**:
- Seasons 1-2 (Rank Sum): 88.2% match rate
- Seasons 3-27 (Percent Sum): 84.7% match rate
- Seasons 28-34 (Rank + Judge Save): 86.1% match rate

**Interpretation**: Our fan vote proxy achieves high consistency with historical eliminations across all rule periods, validating the residual-based estimation approach.

### 5.5.2 Elimination Match Rate by Week
**Figure 5.3**: Match Rate by Week
- File: `figures/elimination_match_rate/match_rate_by_week.png`

**Pattern**:
- Early weeks (1-3): 78.4% match rate (higher variance in fan preferences)
- Mid-season (4-8): 88.9% match rate (stable fan bases established)
- Finals (9+): 82.1% match rate (close competitions, small prediction errors matter)

### 5.5.3 Multiple Eliminations
- **Double eliminations**: 12 weeks across 34 seasons
- **No eliminations**: 8 weeks (special episodes, results shows)
- **Treatment**: Multiple eliminations modeled as eliminating k contestants with lowest combined scores

## 5.6 Why Inverse Estimation?

### 5.6.1 The Identification Problem
Fan votes are **completely unobserved**. We cannot directly measure:
- Absolute vote counts per contestant
- Total votes cast per week
- Vote distribution across demographics

### 5.6.2 What We Can Infer
From observed eliminations and judge scores, we can infer:
- **Relative fan preferences**: Which contestants fans favored more/less
- **Fan-judge divergence**: Cases where fan rankings differ from judge rankings
- **Temporal patterns**: How fan support evolves week-to-week

### 5.6.3 Toy Example
Consider Week 5 of Season 10 with 3 contestants:

| Contestant | Judge Score | Judge Rank | Observed Outcome |
|------------|-------------|------------|------------------|
| Alice | 27 | 1 | Safe |
| Bob | 24 | 2 | Safe |
| Carol | 21 | 3 | **Eliminated** |

**Under Rank Sum rule**: If Carol was eliminated, her combined rank must be highest.
- If fan ranks were: Alice=1, Bob=2, Carol=3 → Combined: Alice=2, Bob=4, Carol=6 ✓ (Carol eliminated)
- If fan ranks were: Alice=1, Carol=2, Bob=3 → Combined: Alice=2, Carol=5, Bob=5 ✗ (tie, ambiguous)

**Inference**: Fan votes likely aligned with judge scores (Carol had lowest fan support).

**Counter-example** (controversial case):
If Bob was eliminated instead:
- Fan ranks must be: Alice=1, Carol=2, Bob=3 → Combined: Alice=2, Bob=5, Carol=5
- Or: Alice=1, Carol=1, Bob=3 → Combined: Alice=2, Carol=4, Bob=5 ✓
- **Inference**: Fans strongly favored Carol over Bob despite lower judge scores (fan-judge divergence)

This logic, applied systematically across 241 weeks, allows us to estimate fan vote shares through residual analysis.

## 5.7 Key Figures

**Figure 5.4**: Cumulative Match Rate
- File: `figures/elimination_match_rate/cumulative_match_rate.png`
- Shows model accuracy improving as more data is incorporated

**Figure 5.5**: Match Rate by Contestant Pool Size
- File: `figures/elimination_match_rate/match_rate_by_size.png`
- Accuracy highest with 8-12 contestants (optimal competition size)
- Lower accuracy with <6 or >14 contestants (extreme pool sizes)
