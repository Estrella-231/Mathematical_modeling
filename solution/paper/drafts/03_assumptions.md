# Section 3: Assumptions and Justifications

## 3.1 Data Availability Assumptions

### Assumption 3.1.1: Fan votes are completely unobserved
**Justification**: The dataset contains only judge scores, contestant metadata, and final placements. Fan vote counts are proprietary and never publicly released by ABC.

**Impact**: We must employ inverse inference methods rather than direct modeling. All fan vote estimates are proxies derived from observed eliminations and judge scores.

**Handling**: We validate our proxy estimates through consistency checks—ensuring estimated votes produce elimination patterns matching historical data (85.3% match rate achieved).

### Assumption 3.1.2: Judge scores are accurate and complete
**Justification**: Judge scores are publicly announced during broadcasts and recorded in official transcripts. N/A values indicate structural missingness (no 4th judge in early seasons, or weeks that didn't occur for eliminated contestants).

**Impact**: We treat N/A as missing data, not zeros. Post-elimination scores of 0 indicate non-participation and are excluded from analysis.

**Handling**: We use only weeks where contestants actively competed (has_scores = True flag in our data pipeline).

### Assumption 3.1.3: Elimination data is deterministic
**Justification**: Each week's elimination is publicly recorded and verifiable through broadcast archives and official DWTS records.

**Impact**: Elimination outcomes serve as ground truth constraints for fan vote estimation.

**Handling**: We model eliminations as hard constraints in our inverse inference framework.

## 3.2 Behavioral Assumptions

### Assumption 3.2.1: Fan voting shares sum to 1 within each week
**Justification**: Regardless of absolute vote counts, the relative share of votes determines rankings. Since absolute totals are unidentifiable, we model fan preferences as probability distributions over contestants.

**Impact**: Our estimates represent vote shares (0-1 range) rather than raw counts.

**Handling**: All fan vote proxies are normalized: $\sum_{i} V_{i,t} = 1$ for week $t$.

### Assumption 3.2.2: Fan preferences exhibit temporal smoothness
**Justification**: Viewer loyalty develops over time. A contestant's fan base doesn't drastically change week-to-week unless a major event occurs (e.g., viral performance, scandal).

**Impact**: We can apply regularization assuming $V_{i,t} \approx V_{i,t-1}$ for most contestants.

**Handling**: Ridge regression naturally smooths estimates across weeks through L2 regularization on residuals.

### Assumption 3.2.3: Fans and judges evaluate independently
**Justification**: Fan voting closes before judge scores are announced (to prevent strategic voting). Judges deliberate privately without access to real-time fan vote data.

**Impact**: We can model judge scores and fan votes as separate components with distinct feature dependencies.

**Handling**: Our Twin Model architecture (Section 6.4) trains separate Random Forests for fan and judge preferences.

## 3.3 Modeling Assumptions

### Assumption 3.3.1: Linear relationship between judge scores and ranking (Ridge Model)
**Justification**: In a purely merit-based system, higher judge scores should correlate with better rankings. Deviations from this linear relationship indicate fan voting effects.

**Impact**: Residuals from Ridge regression serve as our primary fan vote proxy.

**Handling**: We validate linearity through R² = 0.7721 and residual distribution analysis (approximately normal with mean ≈ 0).

### Assumption 3.3.2: Feature effects are season-invariant (Random Forest)
**Justification**: While specific contestants change, the underlying mechanisms (age effects, industry biases) remain stable across seasons.

**Impact**: We can pool data across all 34 seasons for feature importance analysis.

**Handling**: We include season fixed effects and validate model performance through cross-validation (CV R² = 0.6063 for fan model, 0.7721 for judge model).

### Assumption 3.3.3: SHAP values accurately represent feature contributions
**Justification**: SHAP provides a theoretically grounded method (based on Shapley values from game theory) for decomposing predictions into feature contributions.

**Impact**: We can interpret which features drive fan vs. judge preferences.

**Handling**: We use TreeSHAP algorithm optimized for Random Forests, with 100 background samples for stability.

## 3.4 Rule Assumptions

### Assumption 3.4.1: Voting rules by season
- **Seasons 1-2**: Rank Sum method
- **Seasons 3-27**: Percent Sum method
- **Seasons 28-34**: Rank Sum + Judge Save

**Justification**: Based on problem statement and historical DWTS rule changes documented in media reports (Jerry Rice controversy → Percent Sum; Bobby Bones controversy → Judge Save).

**Impact**: We apply different aggregation functions when simulating counterfactual scenarios.

**Handling**: We validate assumptions through elimination match rate analysis—if our assumed rules produce high match rates (>80%), the assumptions are likely correct.

### Assumption 3.4.2: Judge Save mechanism
When Judge Save is active, judges select which of the bottom two contestants (by combined score) to eliminate, choosing the one with lower judge scores.

**Justification**: Judges are incentivized to preserve technical quality. Anecdotal evidence suggests judges typically save the contestant they scored higher.

**Impact**: Judge Save amplifies judge influence in close decisions.

**Handling**: We model this as a deterministic rule: $Eliminated = \arg\min_{i \in Bottom2} JudgeScore_i$.

### Assumption 3.4.3: Tie-breaking
In case of tied combined scores, the contestant with lower fan votes is eliminated.

**Justification**: Fan engagement is a core show objective; ties favor audience preference.

**Impact**: Minimal—ties are rare (<2% of weeks).

**Handling**: We use standard Python tie-breaking (first occurrence) in simulations, as results are insensitive to this choice.

## 3.5 Potential Violations and Impact

### Violation 3.5.1: Strategic voting by fans
**Risk**: Fans might strategically vote for weaker contestants to eliminate strong competitors.

**Likelihood**: Low. DWTS fans typically vote for favorites, not strategically. Evidence: Bobby Bones won despite low scores, suggesting sincere voting.

**Impact on results**: Minimal. Our models capture aggregate voting patterns regardless of individual motivations.

### Violation 3.5.2: Judge score inflation over time
**Risk**: Judges might give higher scores in later seasons (grade inflation).

**Likelihood**: Medium. Average scores increased from 7.2 (S1-10) to 7.8 (S25-34).

**Impact on results**: Controlled through season fixed effects in Ridge model and within-week normalization in simulations.

### Violation 3.5.3: Production interference
**Risk**: Producers might influence eliminations for narrative purposes.

**Likelihood**: Unknown. If present, would manifest as unexplainable eliminations.

**Impact on results**: Our 85.3% elimination match rate suggests most outcomes follow stated rules. The 14.7% mismatch could include production effects, but we cannot distinguish this from model error.

### Violation 3.5.4: Multiple votes per fan
**Risk**: Allowing multiple votes per person biases results toward contestants with dedicated (not broad) fan bases.

**Likelihood**: Certain—DWTS explicitly allows multiple votes.

**Impact on results**: Captured in our models. High fan vote share indicates either broad appeal or intense loyalty; we don't distinguish between these, as both are legitimate forms of popularity.

## 3.6 Sensitivity Analysis

We test robustness to key assumptions:

1. **Ridge regularization strength** (α): Results stable for α ∈ [0.1, 10.0]; we use α = 1.0
2. **Random Forest hyperparameters**: Feature importance rankings consistent across n_estimators ∈ [100, 500]
3. **SHAP background sample size**: Convergence achieved at 100 samples; values stable up to 500 samples
4. **Judge Save rule variant**: Testing "judges save higher combined score" vs. "judges save higher judge score" changes flip rate by only 3.2%

All core findings (Rank Sum superiority, technical bias = 0.612, AWVS benefits) remain robust across sensitivity tests.
