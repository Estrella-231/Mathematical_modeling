# 模型 B1 实现方案：岭回归逆向估算粉丝投票 (Model B1: Inverse Fan Vote Estimation via Ridge Regression)

## 1. 目标 (Objective)
**核心目标：估算每周每位选手的隐变量——粉丝投票份额 (Fan Vote Share)。**

由于粉丝投票不可观测，我们采用**逆向推断 (Inverse Inference)** 策略：
1.  假设：`最终结果` = `评委评分` + `粉丝投票` + `噪音`。
2.  方法：构建回归模型预测基于评委分的“理论结果”。
3.  推断：`实际结果` 与 `理论结果` 的差异（残差），主要由**粉丝投票**贡献。
4.  输出：将残差映射为具体的**粉丝投票份额 (0-100%)**，并提供估算的**置信区间 (Uncertainty)**。

## 2. 输入数据 (Input Data)
*   **Source:** `solution/Data/processed/weekly_panel.csv`
*   **Scope:** S1-S27 (用于参数拟合), S28-S34 (用于测试/外推)。
*   **Exclusions:** 决赛周 (Finals) - 规则通常不同。

## 3. 特征工程 (Feature Engineering)
### 自变量 ($X$) - 代表“技术表现”
1.  `relative_judge_score`: 标准化评委分 $Z_{score} = (Score_i - \mu_{week}) / \sigma_{week}$。
2.  `judge_rank`: 评委给出的排名 (1=Best)。
3.  `cumulative_score`: 赛季累计表现。

### 因变量 ($Y$) - 代表“综合结果”
*   `week_result_score`: 构建一个连续变量代表当周结果。
    *   若晋级：$Y = 1$ (或基于当周排名的分数，如果已知)。
    *   若淘汰：$Y = 0$ (或基于淘汰顺序的负分)。
    *   **策略:** 使用 **Logits (对数几率)** 形式的排名作为 $Y$，使分布更接近正态。

## 4. 核心逻辑：从残差到投票 (Residuals to Votes)

### Step 1: 训练基线模型 (Baseline Model)
$$ \hat{Y}_{tech} = \text{Ridge}(X_{judge}) $$
$\\hat{Y}_{tech}$ 代表仅凭技术（评委分）应得的理论结果。

### Step 2: 提取粉丝效应 (Extract Fan Effect)
计算残差 $R_i = Y_{actual} - \hat{Y}_{tech}$。
*   $R_i > 0$: 实际结果优于评委预期 $\rightarrow$ **高粉丝票**。
*   $R_i < 0$: 实际结果差于评委预期 $\rightarrow$ **低粉丝票**。

### Step 3: 映射为投票份额 (Map to Vote Share)
题目要求估算“粉丝投票”。我们需要构建映射函数 $f(R_i) \rightarrow V_i$。
假设粉丝投票服从 Log-Normal 或 Softmax 分布：
$$ \text{RawVote}_i = \exp(\alpha \cdot R_i + \text{Base}) $$
$$ \text{FanVoteShare}_i = \frac{\text{RawVote}_i}{\sum_{j \in Week} \text{RawVote}_j} $$
*   $\alpha$: 敏感度系数 (超参数，需校准)。

## 5. 确定性与一致性 (Certainty & Consistency)

### 5.1 确定性指标 (Certainty Metric)
题目问：“产生的粉丝投票总数有多少确定性？”
利用岭回归的**预测区间 (Prediction Interval)**：
$$ \sigma^2_{pred} = \sigma^2_{model} + \text{Var}(X^T \beta) $$
*   对于每个估算的 $\\hat{V}_i$，其不确定性 $U_i$ 与模型在该点的预测方差成正比。
*   **观察:** 评委分极端（极高或极低）的选手，模型预测通常较准，粉丝票估算的确定性较高。
*   **观察:** 处于中游的选手，模型预测方差大，粉丝票估算的不确定性也大。

### 5.2 一致性检查 (Consistency Check)
题目问：“模型是否正确估算了每周被淘汰者？”
*   **验证方法:** 将估算的 $\\text{FanVoteShare}_i$ 代入当季的规则（如 Rank Sum 或 Percent Sum）。
*   **计算:** `Reconstructed_Result` = Rule(`JudgeScore`, `Est_FanVote`).
*   **指标:** **淘汰匹配率 (Elimination Match Rate)**。即我们估算的票数是否真的会导致实际上那个人被淘汰？

## 6. 实现步骤 (Implementation Steps)
1.  **Fit:** 训练 Ridge 回归，得到残差 $R$。
2.  **Calibrate:** 调整 $\alpha$ (敏感度)，使得生成的投票在 S1-S27 上的“淘汰匹配率”最大化。
3.  **Generate:** 输出每位选手每周的 `Est_Fan_Vote_Share` 和 `Uncertainty_Bound`。
4.  **Validate:** 检查“争议案例”（如 Jerry Rice）是否显示出异常高的粉丝票。