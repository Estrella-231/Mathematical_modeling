# Refactoring Plan: v2.0 (Problem-Centric, Expanded Structure)

**Date:** 2026-02-01
**Objective:** Restructure the paper to strictly follow the MCM Problem Statement order while preserving standard thesis sections (Assumptions, Notations, Conclusion, etc.).
**Constraint:** Do NOT merge Assumptions/Notations. Keep separate sections for Strengths/Weaknesses and Conclusion.

---

## Final Structure Layout

| Section Number | Title | Content Focus |
| :--- | :--- | :--- |
| **1** | **Introduction** | Background, Restatement, Literature Review, Overview. |
| **2** | **Assumptions and Justifications** | **STANDALONE.** The 4 assumption categories (Data, Behavioral, Modeling, Rule). |
| **3** | **Notations** | **STANDALONE.** The variable definitions table. |
| **4** | **Data Preparation and EDA** | Data cleaning, standardizing scores, initial data description. |
| **5** | **Problem 1: Estimation of Latent Fan Votes** | **Method + Results for Q1.** <br> - Ridge Regression (Method) <br> - Certainty Analysis (Method/Result) <br> - Match Rate Verification (Result) <br> - Top 20 Fan List (Result) |
| **6** | **Problem 2: Mechanism Comparison** | **Method + Results for Q2.** <br> - Simulator Setup (Method) <br> - Flip Rate & FFI Analysis (Results) <br> - Case Studies: Jerry Rice, Bobby Bones (Results) |
| **7** | **Problem 3: Determinants of Success** | **Method + Results for Q3.** <br> - Twin RF Architecture (Method) <br> - SHAP Analysis & Technical Bias Coeff (Results) <br> - Industry Bias Analysis (Results) |
| **8** | **Problem 4: System Optimization** | **Method + Results + Rec for Q4.** <br> - AWVS Design & Formula (Method) <br> - System Comparison Metrics (Results) <br> - Final Recommendation to Producers (Policy) |
| **9** | **Strengths and Weaknesses** | **STANDALONE.** Self-evaluation of the models. |
| **10** | **Conclusion** | **STANDALONE.** Final summary of findings. |
| **--** | **References & Appendices** | As before. |

---

## Detailed Content Migration Map

### Section 5: Problem 1 (The "Estimation" Chapter)
*   *Source:* Old Section 5.2 (Method) + Old Section 6.1 (Results).
*   **5.1 Inverse Inference Model:** Describe the Ridge Proxy logic ($Ranking \sim Judge + Fan$).
*   **5.2 Uncertainty Quantification:** Explain how we calculate standard errors for the estimates.
*   **5.3 Results: The Hidden Vote Revealed:**
    *   Show the **Elimination Match Rate** (85.3%) table.
    *   Show the **Top 10 Fan Favorites** table.
    *   Show the **Residual Distribution** plot.

### Section 6: Problem 2 (The "Comparison" Chapter)
*   *Source:* Old Section 5.4 (Method) + Old Section 6.2 (Results) + Old Case Studies.
*   **6.1 Counterfactual Simulation Framework:** Define Rank Sum, Percent Sum, Judge Save.
*   **6.2 Quantitative Comparison:**
    *   Show **Flip Rate Matrix**.
    *   Show **FFI (Fairness)** histograms.
*   **6.3 Anatomy of Controversies (Case Studies):**
    *   Subsection for **Bobby Bones (S27)**.
    *   Subsection for **Jerry Rice (S2)**.
    *   Include the "What-if" simulation charts for them.

### Section 7: Problem 3 (The "Impact" Chapter)
*   *Source:* Old Section 5.3/5.5 (Method) + Old Section 6.3 (Results).
*   **7.1 Twin-Model Architecture:** Define $RF_{fan}$ vs $RF_{judge}$.
*   **7.2 Divergence Analysis:**
    *   Show the **Feature Importance Comparison** (The Butterfly/Bar Chart).
    *   State the **Technical Bias Coefficient**.
*   **7.3 Industry and Partner Effects:**
    *   Show the **Industry Bias Table**.
    *   Discuss the impact of "Pro Dancer" partners.

### Section 8: Problem 4 (The "Optimization" Chapter)
*   *Source:* Old Section 5.6 (Method) + Old Section 6.4 (Results) + Old Section 7 (Recs).
*   **8.1 The Adaptive Weighted Voting System (AWVS):** Define the dynamic $\alpha(t)$ formula.
*   **8.2 System Evaluation:**
    *   Show the **Controversy Rate Reduction** table.
*   **8.3 Final Recommendation:**
    *   The "Policy Memo" content: Adopt Rank Sum now, Pilot AWVS later.

---

## Implementation Checklist

1.  [ ] **Break Linkage:** Stop referring to "Model B1/B2". Use "The Estimation Model", "The Twin Model".
2.  [ ] **Explicit Headers:** Ensure headers match the specific MCM questions (e.g., "Problem 1:", "Problem 2:").
3.  [ ] **Preserve Structure:** Ensure Sec 2, 3, 9, 10 are untouched/only slightly polished.
4.  [ ] **Merge Recs:** Move the content from the old "7 Mechanism Design" into the new "Section 8: Problem 4".
