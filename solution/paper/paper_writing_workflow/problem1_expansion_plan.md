# Problem 1 Expansion Plan: Estimation of Latent Fan Votes

**Objective:** Rewrite "Problem 1" to match the depth, narrative flow, and rigorousness of an O-Prize winner (specifically referencing Team #2401298's approach).
**Current Status:** Too brief. Jumps straight to the Ridge formula without exploring the data or justifying the "Why".
**Target Style:** Exploratory $\to$ Mathematical Formulation $\to$ Refinement $\to$ Validation.

---

## 1. Analysis of the Reference (Team #2401298)
The reference paper didn't just say "We calculated AUC." They followed a logical chain:
1.  **Observation:** They first looked at "Points Difference" (Fig 2) and realized server impact was stable.
2.  **Iterative Modeling:**
    *   *Attempt 1:* Sliding Point Interval. (Good, but ignores time).
    *   *Attempt 2:* Sliding Time Window. (Better, but noisy).
    *   *Refinement:* AUC approach. (Final solution).
3.  **Visual Evidence:** Every step had a corresponding graph for *one specific match* to ground the theory.

---

## 2. The New Narrative Arc for "Problem 1: Estimation of Latent Fan Votes"

We will expand Section 5 (Problem 1) into roughly 2-3 pages with the following subsections:

### 5.1 The "Meritocracy Gap": Why Judge Scores Are Not Enough
*   **Goal:** Prove that looking *only* at Judge Scores fails to explain eliminations.
*   **Narrative:**
    *   "If DWTS were purely a dance competition, judge scores would perfectly predict rankings."
    *   "We visualize the correlation between Average Judge Score and Final Placement."
    *   **Action:** Add a scatter plot (Judge Score vs. Rank). Highlight outliers (e.g., Bobby Bones: Low Score, High Rank).
    *   **Mathematical Gap:** Define the "Unexplained Variance" ($1 - R^2$) of a simple Judge-only model. This justifies the need for a "Fan Vote Model."

### 5.2 The Inverse Inference Strategy (The Core Model)
*   **Goal:** Mathematically define how we extract the "Dark Matter" (Fan Votes).
*   **Narrative:**
    *   "Since Fan Votes ($V$) are unobserved, we treat them as the latent residual."
    *   **Formalization:**
        *   $Ranking_{i,t} = \alpha \cdot JudgeScore_{i,t} + \beta \cdot FanVote_{i,t} + \epsilon$
        *   Since we observe Ranking and JudgeScore, we inverse this:
        *   $\hat{FanVote}_{i,t} \propto Residuals(Ranking | JudgeScore)$
    *   **The Ridge Solution:** Explain *why* Ridge? (To handle multicollinearity between judge scores and season trends).
    *   *Equation:* Present the full Ridge objective function (already in v1.1, but expand the explanation of terms).

### 5.3 Model Refinement: Handling Seasonality and Uncertainty
*   **Goal:** Address the "Sliding Window" equivalent – ensuring scores are comparable across 34 seasons.
*   **Narrative:**
    *   "A residual of +2 in Season 1 is not the same as +2 in Season 30 due to score inflation."
    *   **Step 1: Standardization.** Explain the $Z$-score transformation within each week.
    *   **Step 2: Uncertainty Quantification.**
        *   "Unlike actual votes, our estimates have error bars."
        *   Define the **Certainty Metric**: $Certainty_{i,t} = 1 / SD(Residuals)$.
    *   **Visual:** Plot "Fan Vote Estimate with Error Bars" for a specific controversial celebrity (e.g., Jerry Rice) over time. Show how certainty narrows or widens.

### 5.4 Validation: The "Elimination Match Rate" Test
*   **Goal:** The equivalent of the Reference's "Inference on Match Data".
*   **Narrative:**
    *   "To validate this latent proxy, we test if it can 'postdict' historical eliminations."
    *   **Metric:** Define "Elimination Match Rate" (Did the person with the lowest Estimated Combined Score actually go home?).
    *   **Results Table:** Show the 85.3% accuracy. Break it down by Season Era (Early vs. Late).
    *   **Deep Dive:** Explicitly mention the 14.7% mismatches—are they model failures, or "Shock Eliminations" (which validates the model's ability to detect anomalies)?

---

## 3. Detailed Content Generation Tasks

| Subsection | Content to Write | Figures/Tables Needed |
| :--- | :--- | :--- |
| **5.1** | Analysis of $Corr(Judge, Rank)$. The failure of the "Merit" hypothesis. | **Figure 5.1:** Scatter plot of Judge Score vs Placement (Show the messiness). |
| **5.2** | Derivation of the Inverse Model. Justification of Ridge (L2 penalty). | **Equation:** The Ridge Loss Function. <br> **Figure 5.2:** Diagram of "Extracting the Residual". |
| **5.3** | Normalization math. Certainty calculation. | **Figure 5.3:** Time-series of Estimated Fan Vote for 1 contestant (with shaded confidence intervals). |
| **5.4** | Validation logic. The "Match Rate" definition. | **Table 5.1:** Elimination Match Rate by Season Block. <br> **Figure 5.4:** Confusion Matrix of Predictions. |

---

## 4. Comparison with Reference

| Reference Paper (Tennis) | Our Plan (DWTS) |
| :--- | :--- |
| **3.1 Impact of Server** (Initial Check) | **5.1 The Meritocracy Gap** (Initial Check of Judge Scores) |
| **3.2 Sliding Interval** (Naive Model) | **5.2 Inverse Inference** (Linear Proxy Model) |
| **3.3 Sliding Time/AUC** (Refinement) | **5.3 Normalization & Certainty** (Refinement) |
| **Figure 5: AUC Plot** (Visual Result) | **Figure 5.3: Fan Vote Time Series** (Visual Result) |

## 5. Next Steps for User
1.  **Generate Figure 5.1:** Use Python to plot `judge_total` vs `placement`.
2.  **Generate Figure 5.3:** Use Python to plot the Ridge Residuals for 'Jerry Rice' with error bars.
3.  **Rewrite Text:** Use the structure above to rewrite Section 5 in `mcmthesis-demo.tex`.
