# 模型设计 (Model Design)

## 1. 核心模型：粉丝投票逆向重构 (Model A: Inverse Fan Vote Reconstruction)

### 1.1 目标 (Objective)
由于粉丝投票数据不可见，我们需要根据每周的“淘汰结果”和“评委评分”推算出粉丝投票的**可行域 (Feasible Region)** 或 **后验分布 (Posterior Distribution)**。

### 1.2 数学表述 (Mathematical Formulation)
假设第 $s$ 季第 $w$ 周有 $N$ 位选手。
令 $J_i$ 为选手 $i$ 的评委得分，$V_i$ 为选手 $i$ 的粉丝投票份额 ($\sum V_i = 1, V_i > 0$)。

**约束条件 (Constraints):**
已知选手 $E$ 被淘汰（综合得分最差）。

*   **Rank Method (S1-S2, S28+):**
    设 $R^J_i$ 为评委排名，$R^F_i$ 为粉丝排名（数值越小排名越高）。
    淘汰条件：$R^J_E + R^F_E \ge R^J_i + R^F_i, \forall i \neq E$
    *(注：这里假设排名数值大=差。S28+ 需考虑 Bottom 2 规则)*

*   **Percent Method (S3-S27):**
    设 $P^J_i = J_i / \sum J_k$。
    淘汰条件：$P^J_E + V_E \le P^J_i + V_i, \forall i \neq E$

### 1.3 求解算法：受约束的蒙特卡洛采样 (Constrained Monte Carlo Sampling)
1.  **先验 (Prior):** 假设粉丝投票服从狄利克雷分布 $V \sim Dirichlet(\alpha)$，其中 $\alpha$ 可设为均匀 (1,1,...) 或基于选手流行度调整。
2.  **采样 (Sampling):** 生成大量随机投票向量 $\mathbf{V}^{(k)}$。
3.  **筛选 (Filtering):** 仅保留满足上述“淘汰约束”的样本。
4.  **时间平滑 (Time Smoothing):** 引入马尔可夫链约束，假设 $V_{i, w} \approx V_{i, w-1}$。
    *   *实现:* 使用 MCMC (如 Metropolis-Hastings) 或简单的拒绝采样（若维度允许）。考虑到 $N$ 较小 (<15)，拒绝采样在大规模并行下可行。

## 2. 辅助模型：特征与残差分析 (Model B: Feature & Residual Analysis)

### 2.1 Model B1: 岭回归残差分析 (Ridge Regression Residual Analysis)
*   **目标 (Objective):** 利用线性模型捕捉评委分对排名的解释力，将**无法解释的残差**定义为“粉丝投票效应”。
*   **方法 (Method):**
    *   公式: $Ranking \sim \beta_0 + \beta_1 \cdot JudgeScore + \beta_2 \cdot SeasonEffect + \epsilon$
    *   使用 **岭回归 (Ridge Regression)** 处理评委评分间的高度共线性。
    *   **残差定义:** $\epsilon = Ranking_{actual} - Ranking_{predicted}$。
        *   若 $\epsilon < 0$ (实际排名 < 预测排名)，说明选手表现比评委预期好 -> **高粉丝票**。
        *   若 $\epsilon > 0$，说明选手表现比评委预期差 -> **低粉丝票**。

### 2.2 Model B2: 随机森林回归 (Random Forest Regression)
*   **目标 (Objective):** 捕捉非线性的粉丝偏好特征（如特定年龄段或行业的“爆红”现象）。
*   **方法 (Method):**
    *   **输入 ($X$):** 选手特征（年龄、行业、性别、地区）、历史评委分、是否职业舞者。
    *   **输出 ($Y$):** 最终排名 (Final Placement) 或 存活周数 (Survival Weeks)。
    *   **分析:** 使用 **SHAP 值** 或 **Feature Importance** 识别关键驱动因素。
    *   **优势:** 不需要预设线性假设，能发现特征间的交互作用（如“年轻”+“运动员”可能比单纯“年轻”更受欢迎）。

## 3. 比较模型：反事实模拟 (Model C: Counterfactual Simulation)

### 3.1 目标 (Objective)
回答“如果S2使用百分比法，Jerry Rice是否会更早被淘汰？”

### 3.2 流程 (Process)
1.  **固定输入:** 保持历史评委评分 $J$ 不变。
2.  **变量输入:** 使用 Model A 生成的粉丝投票样本集 {$\mathbf{V}^{(k)}$}。
3.  **规则替换:**
    *   对每个样本 $\mathbf{V}^{(k)}$，应用**另一种**计分规则（如将 Rank 换为 Percent）。
    *   计算新的淘汰者 $E'_{new}$。
4.  **统计指标:**
    *   **翻转率 (Flip Rate):** $P(E'_{new} \neq E_{original})$。
    *   **生存差异:** 统计特定选手在反事实规则下的预期生存周数。

## 4. 优化模型：新系统设计 (Model D: Fair Voting System Optimization)

### 4.1 设计空间 (Design Space)
定义广义综合得分：
$$ S_{total} = w \cdot f(Score_{Judge}) + (1-w) \cdot g(Vote_{Fan}) $$
其中 $f, g$ 为归一化函数（如 Rank, Z-score, MinMax），$w$ 为权重。

### 4.2 目标函数 (Objectives)
*   **$O_1$ 公平性 (Fairness):** 最终排名与评委评分的相关性 (Spearman Corr)。
*   **$O_2$ 悬念/娱乐性 (Excitement):** 弱势选手逆袭的概率（但不能太高，否则显得随机）。

### 4.3 求解
遍历 $w \in [0, 1]$ 和不同的 $f, g$ 组合，在 Model A 的模拟数据上评估 $O_1, O_2$，寻找帕累托最优解。

---

## 下一步 (Next Steps) - Claude Code 任务
1.  **数据清洗:** 处理 CSV，转换宽表为长表 (Season, Week, Contestant, JudgeScore, Result)。
2.  **基线实现:** 编写 `FanVoteSampler` 类，实现基于拒绝采样的 Model A。
3.  **验证:** 在已知粉丝投票（如有）或合成数据上验证模型能否恢复真实参数。