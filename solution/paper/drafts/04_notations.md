# Section 4: Notations

## 4.1 Indices and Sets

| Symbol | Description |
|--------|-------------|
| $s$ | Season index, $s \in \{1, 2, \ldots, 34\}$ |
| $t$ | Week index within a season, $t \in \{1, 2, \ldots, T_s\}$ |
| $i$ | Contestant index within a season, $i \in \{1, 2, \ldots, N_s\}$ |
| $j$ | Judge index, $j \in \{1, 2, 3, 4\}$ (note: not all seasons have 4 judges) |
| $N_s$ | Number of contestants in season $s$ |
| $T_s$ | Number of weeks in season $s$ |
| $\mathcal{C}_{s,t}$ | Set of active contestants in season $s$, week $t$ (not yet eliminated) |

## 4.2 Observed Variables

### Judge Scores
| Symbol | Description |
|--------|-------------|
| $J_{i,t,j}$ | Score given by judge $j$ to contestant $i$ in week $t$ (range: 1-10) |
| $J_{i,t}$ | Total judge score for contestant $i$ in week $t$: $J_{i,t} = \sum_{j} J_{i,t,j}$ |
| $\bar{J}_{i,t}$ | Average judge score: $\bar{J}_{i,t} = J_{i,t} / n_{judges}$ |
| $J^{norm}_{i,t}$ | Normalized judge score within week: $J^{norm}_{i,t} = J_{i,t} / \sum_{k \in \mathcal{C}_{s,t}} J_{k,t}$ |

### Rankings and Outcomes
| Symbol | Description |
|--------|-------------|
| $R_{i,s}$ | Final placement of contestant $i$ in season $s$ (1 = winner) |
| $W_{i,s}$ | Number of weeks contestant $i$ survived in season $s$ |
| $E_{s,t}$ | Contestant eliminated in season $s$, week $t$ |
| $R^J_{i,t}$ | Rank of contestant $i$ by judge scores in week $t$ (1 = highest score) |
| $R^F_{i,t}$ | Rank of contestant $i$ by fan votes in week $t$ (1 = highest votes) |

### Contestant Features
| Symbol | Description |
|--------|-------------|
| $A_i$ | Age of contestant $i$ during competition |
| $I_i$ | Industry/profession of contestant $i$ (categorical) |
| $P_i$ | Professional dancer partner of contestant $i$ |
| $H_i$ | Home state/country of contestant $i$ |
| $\bar{P}_P$ | Historical average placement of professional dancer $P$ |
| $E_P$ | Experience (number of seasons) of professional dancer $P$ |
| $W_P$ | Win rate of professional dancer $P$ |

## 4.3 Latent Variables (Estimated)

### Fan Votes
| Symbol | Description |
|--------|-------------|
| $V_{i,t}$ | Fan vote share for contestant $i$ in week $t$: $\sum_{i \in \mathcal{C}_{s,t}} V_{i,t} = 1$ |
| $\hat{V}_{i,t}$ | Estimated fan vote share (from Ridge residuals) |
| $V^{raw}_{i,t}$ | Absolute fan vote count (unobservable) |

### Derived Scores
| Symbol | Description |
|--------|-------------|
| $\epsilon_{i,t}$ | Ridge regression residual: $\epsilon_{i,t} = R_{i,s} - \hat{R}_{i,s}(J_{i,t})$ |
| $F_{i,t}$ | Fan score proxy: $F_{i,t} = -\epsilon_{i,t}$ (negative residual = high fan support) |
| $Z^J_{i,t}$ | Standardized judge score: $Z^J_{i,t} = (J_{i,t} - \mu_t) / \sigma_t$ |
| $Z^F_{i,t}$ | Standardized fan score: $Z^F_{i,t} = (F_{i,t} - \mu^F_t) / \sigma^F_t$ |

## 4.4 Combined Scores (Voting Rules)

### Rank Sum Method
$$S^{rank}_{i,t} = R^J_{i,t} + R^F_{i,t}$$
Elimination: $E_{s,t} = \arg\max_{i \in \mathcal{C}_{s,t}} S^{rank}_{i,t}$ (highest sum eliminated)

### Percent Sum Method
$$S^{percent}_{i,t} = J^{norm}_{i,t} + V_{i,t}$$
Elimination: $E_{s,t} = \arg\min_{i \in \mathcal{C}_{s,t}} S^{percent}_{i,t}$ (lowest sum eliminated)

### Judge Save Method
$$\mathcal{B}_t = \{i_1, i_2\} \text{ where } S^{rank}_{i_1,t}, S^{rank}_{i_2,t} \text{ are two highest}$$
$$E_{s,t} = \arg\min_{i \in \mathcal{B}_t} J_{i,t}$$
(Bottom two identified by rank sum; judges eliminate lower judge score)

## 4.5 Evaluation Metrics

### Fan Favorability Index (FFI)
$$FFI_{i,t} = \frac{R^J_{i,t} - R^F_{i,t}}{|\mathcal{C}_{s,t}| - 1}$$
- $FFI > 0$: Fans favor contestant more than judges
- $FFI < 0$: Judges favor contestant more than fans
- $FFI \approx 0$: Agreement between fans and judges
- Range: $[-1, 1]$

### Flip Rate
$$\text{FlipRate}(Rule_A, Rule_B) = \frac{1}{T_{total}} \sum_{s,t} \mathbb{1}[E^A_{s,t} \neq E^B_{s,t}]$$
Proportion of weeks where two rules produce different eliminations.

### Elimination Match Rate
$$\text{MatchRate} = \frac{1}{T_{total}} \sum_{s,t} \mathbb{1}[\hat{E}_{s,t} = E^{actual}_{s,t}]$$
Proportion of weeks where model prediction matches historical elimination.

### Model Performance
| Symbol | Description |
|--------|-------------|
| $R^2$ | Coefficient of determination for regression models |
| $MAE$ | Mean Absolute Error: $\frac{1}{n}\sum \|y_i - \hat{y}_i\|$ |
| $RMSE$ | Root Mean Squared Error: $\sqrt{\frac{1}{n}\sum (y_i - \hat{y}_i)^2}$ |
| $\rho$ | Spearman rank correlation coefficient |

## 4.6 AWVS (Adaptive Weighted Voting System) Parameters

### Dynamic Weighting Function
$$\alpha(t) = \alpha_{base} + \gamma \cdot \frac{t}{T_{max}}$$
- $\alpha_{base}$: Initial judge weight (default: 0.4)
- $\gamma$: Weight increase rate (default: 0.3)
- $T_{max}$: Total weeks in season

### Trend Bonus
$$Trend_{i,t} = \max(0, J_{i,t} - MA^J_{i,t-1})$$
- $MA^J_{i,t-1}$: Moving average of contestant $i$'s judge scores up to week $t-1$
- $\beta$: Trend bonus coefficient (default: 0.5)

### AWVS Combined Score
$$S^{AWVS}_{i,t} = \alpha(t) \cdot Z^J_{i,t} + (1-\alpha(t)) \cdot Z^F_{i,t} + \beta \cdot Trend_{i,t}$$

## 4.7 SHAP Values

| Symbol | Description |
|--------|-------------|
| $\phi_k(x_i)$ | SHAP value for feature $k$ in prediction for instance $i$ |
| $\Phi_k$ | Average absolute SHAP value for feature $k$: $\Phi_k = \frac{1}{n}\sum_i \|\phi_k(x_i)\|$ |
| $\text{Importance}_k$ | Normalized feature importance: $\text{Importance}_k = \Phi_k / \sum_j \Phi_j$ |

## 4.8 Statistical Tests

| Symbol | Description |
|--------|-------------|
| $p$ | p-value for hypothesis tests |
| $\alpha_{sig}$ | Significance level (typically 0.05) |
| $CI_{95\%}$ | 95% confidence interval |
| $CV$ | Cross-validation (typically 5-fold) |
