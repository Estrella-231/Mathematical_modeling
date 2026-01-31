# MCM/ICM C 题论文写作大纲（可直接做目录）

> 说明：这是按美赛论文常见结构整理的“目录级”大纲，风格参考你给的两张目录图。你可以把每一节当作一个写作清单：**这一节要回答什么、要放哪些图表/公式、要产出什么结论**。  
> 建议：先把每一节写成 3–8 行要点 + 1 张图/表，再逐步充实。

---

## 0 One-page Summary Sheet（单页摘要，必须 1 页）
0.1 **Problem in One Sentence**（一句话定义问题）  
0.2 **Core Idea / Models**（你用的核心建模思想：例如“逆向估计投票占比 + 监督学习预测 + 规则约束投影”）  
0.3 **Key Results**（最关键的 3 个定量结论：指标提升、规则一致率、跨季稳定性等）  
0.4 **Recommendations**（给节目机制的建议：保留/修改/替代 bottom-two judges save 等）  
0.5 **Why It Matters**（公平性、可解释性、可执行性）

> 只放 1 个最有说服力的图或表（例如：改进机制前后“误判风险/公平性指标”对比）。

---

## 1 Introduction（引言）
1.1 **Problem Background**（节目规则、评委分 + 观众投票的矛盾与争议点）  
1.2 **Restatement of the Problem**（把题目任务拆成可执行子任务：预测、解释、评估、改制）  
1.3 **Literature / Related Work (optional)**（类似"排名聚合、投票系统、公平性度量、受限优化"的思路综述）  
1.4 **Overview of Our Solution**（写成流程图/管线图：Data → Inverse Estimation → Predict → Project/Enforce Rules → Evaluate → Recommend）  
1.5 **Our Contributions**（明确"你新提出了什么"：新指标/新约束/新机制/新解释框架）

---

## 2 Assumptions and Justifications（假设与合理性说明）
2.1 **Data Availability Assumptions**（哪些字段可用、缺失如何处理）  
2.2 **Behavioral Assumptions**（观众投票偏好、评委打分一致性/偏差）  
2.3 **Modeling Assumptions**（可加性、线性/非线性、噪声分布等）  
2.4 **Rule Assumptions**（淘汰规则、加权方式、跨季规则变化的统一口径）  
2.5 **Potential Violations & Impact**（假设不成立会怎样、你如何缓解）

> 每条假设后写"理由 + 影响 + 处理"。

---

## 3 Notations（符号与记号）
3.1 **Indices**（季 s、周 t、选手 i 等）  
3.2 **Observed Variables**（评委分、观众投票结果、是否进入 bottom、是否淘汰等）  
3.3 **Latent Variables**（潜在投票占比、真实受欢迎度、评委偏置等）  
3.4 **Functions / Operators**（归一化、排名、投影/约束算子、损失函数）

---

## 3 Data Preparation and Exploratory Data Analysis（数据处理与 EDA）
3.1 **Dataset Overview**（数据来源、样本量、字段、跨季差异）  
3.2 **Cleaning & Preprocessing**（去重、异常、标准化、对齐不同赛季评分体系）  
3.3 **Judges Score Statistics**  
- 分布、方差、评委间一致性  
- 选手间可分性（是否"分数挤在一起"）  
3.4 **Followers / External Signals & Missingness（外部信号与缺失）**  
- 粉丝量/热度等外部变量与投票/淘汰的相关性  
- 缺失机制：MCAR/MAR/MNAR 的假设与处理  
3.5 **Why We Need an Inverse Estimation Step（为什么需要逆向估计）**
- 解释：投票占比不可观测，但规则给出约束 → 可反推“区间/最可能值”  
- 给出一个小例子（玩具数据）说明“只做监督学习会错在哪里”

> 这一章建议放 2–3 张图：评分分布、外部信号与结果相关性、缺失热力图。

---

## 4 Model Construction（模型构建：三段式结构）
> 推荐按你图里的风格写：**Model 1 / Model 2 / Model 3**，每个模型都包含：Data → Establishment → Solution。

### 4.1 Model 0: Unifying Scoring Schemes Across Seasons（跨季评分体系统一）
4.1.1 **Motivation**（不同赛季总分上限、评委人数等不同）  
4.1.2 **Normalization / Rescaling Strategy**（z-score、min-max、分位数映射等）  
4.1.3 **Sanity Checks**（统一后分布对齐、排名稳定性）

---

### 4.2 Model 1: Inverse Vote Share Estimation with Rule Constraints（逆向估计投票占比）
4.2.1 **Goal**（估计每周每位选手的潜在投票占比/相对强弱）  
4.2.2 **Latent Vote Model（潜变量模型）**  
- 设定 vote_share_{i,t} 的表示方式（logit、Dirichlet、softmax 等）  
4.2.3 **Elimination / Rule Constraints（淘汰规则约束）**  
- "被淘汰者必须在某个综合排名区间内"  
- "bottom-two + judges save" 等规则对应的可行域约束  
4.2.4 **Optimization Objective（目标函数）**  
- 最小化违反规则的惩罚 + 平滑项（周与周之间）+ 与外部信号一致性  
4.2.5 **Solution Method（求解）**  
- 线性/凸优化、QP、投影梯度、坐标下降等  
4.2.6 **Output & Pseudo Labels（输出与伪标签）**
- 生成用于下一步监督学习的标签：vote_share、rank 或 “at-risk” 概率

> 这部分建议画：**可行域示意图** 或 “约束如何缩小投票占比区间”。

---

### 4.3 Model 2: Supervised Prediction (Learning from Pseudo Labels)（监督预测模型）
4.3.1 **Target Definition**（预测目标：vote share / elimination risk / final placement）  
4.3.2 **Feature Engineering**  
- 分数特征：当前分、变化率、相对排名  
- 外部特征：followers、趋势量  
- 结构特征：评委分差、周次、主题周等  
4.3.3 **Model Choice**  
- Baseline：线性回归/Logistic、Random Forest、XGBoost、简单 NN  
- 为什么选它（可解释性 vs 性能）  
4.3.4 **Validation Protocol**  
- 按赛季划分的时间序列验证（避免信息泄漏）  
- 指标：回归误差、分类 AUC、校准度等  
4.3.5 **Interpretability**（SHAP/特征重要性/部分依赖）

---

### 4.4 Model 3: Rule Projection on Predictions（对预测结果做规则投影/修正）
4.4.1 **Motivation**（纯预测可能违背淘汰规则/现实机制）  
4.4.2 **Projection Formulation**（把预测结果投影到规则可行域）  
4.4.3 **Algorithm**（投影算子、修正最小改动原则）  
4.4.4 **Effect**（投影前后：性能变化 + 规则一致性变化）

---

### 4.5 Complexity and Practical Considerations（复杂度与工程可行性）
4.5.1 **Runtime / Memory**  
4.5.2 **Robustness to Missing Data**  
4.5.3 **Deployment in Real Show Setting（可执行性）**

---

## 5 Model Evaluation Criteria（评估指标）
5.1 **Regression Accuracy（回归准确性）**  
- MAE/RMSE、Spearman（排名相关）  
5.2 **Classification / Risk Accuracy（淘汰风险）**  
- AUC、F1、Brier score（校准）  
5.3 **Rule Consistency / Feasibility（规则一致性）**  
- 预测是否落在可行域  
- 违反约束次数/比例  
5.4 **Fairness Metrics（公平性度量，强烈建议加）**  
- 对不同"群体/属性"（例如：高关注 vs 低关注，或早出场 vs 晚出场）误差差异  
- 机制偏置指标（例如对 followers 的敏感度）  
5.5 **Stability Across Seasons（跨季稳定性）**
- 指标在不同赛季方差

---

## 6 Results, Discussion, and Sensitivity Analysis（结果、讨论与敏感性）
6.1 **Main Quantitative Results（主结果表）**  
- Baseline vs Model1/2/3  
- 分赛季汇总 + 全赛季汇总  
6.2 **Key Visualizations（关键可视化）**  
- 真实 vs 预测 scatter / rank plot  
- 规则可行域与投影效果  
- 典型争议周的 case study（为什么会出现 judges save 争议）  
6.3 **Interpretation（解释与洞察）**  
- 哪些因素驱动淘汰风险  
- 评委分与观众投票冲突的结构性原因  
6.4 **Sensitivity Analysis（敏感性分析）**  
- followers 权重/噪声水平  
- 约束松紧度（惩罚系数）  
- 不同缺失处理策略

---

## 7 Mechanism Design / Recommendation（机制改进建议：C 题通常很看重）
7.1 **What's Wrong with Current Rule（现行规则的问题）**  
- 公平性、可解释性、操纵空间  
7.2 **Proposed Alternative Rule（你的新机制）**  
- 方案 A：调整 judges save 触发条件  
- 方案 B：引入"安全阈值/保护机制"  
- 方案 C：改加权方式（随周次变化等）  
7.3 **Simulation / Counterfactual Evaluation（反事实评估）**  
- 用历史数据模拟"如果用新机制，淘汰会怎么变"  
7.4 **Trade-offs（取舍）**  
- 公平 vs 戏剧性、透明度 vs 操作复杂度  
7.5 **Implementation Plan（落地执行）**

---

## 8 Conclusion（结论）
8.1 **Summary of Findings**  
8.2 **Actionable Recommendations**  
8.3 **Limitations**  
8.4 **Future Work**（更强的因果、更多外部信号、更好的规则博弈模型等）

---

## References（参考文献）
- 统一格式（APA/IEEE 任一即可），至少覆盖：排名聚合/投票系统/公平性/受限优化/缺失数据处理。

---

## Appendices（附录）
### Appendix A: Supplementary Tables（补充表格）
A.1 Per-season Performance（分赛季性能表）  
A.2 Rule Consistency（分赛季规则一致率表）  
A.3 Hyperparameters（参数表）

### Appendix B: Key Implementation Snippets（关键代码片段）
- 逆向估计求解器  
- 特征工程  
- 规则投影函数

### Appendix C: Use of AI（AI 使用说明，必须）
C.1 **Tools Used**（使用了哪些 AI 工具、做了什么）  
C.2 **Human Verification**（你如何验证正确性：复算、对照、抽检）  
C.3 **Limitations & Compliance**（没有用 AI 生成虚构数据/引用等）

---

## （可选）写作节奏建议（你可以按这个顺序写）
1) 先写 Summary Sheet 的骨架（逼迫自己先有“主结论”）  
2) 写 Data/EDA（确保你“真有数据支撑”）  
3) 写 Model 1（逆向估计）→ 产出伪标签  
4) 写 Model 2（监督学习）→ 产出预测  
5) 写 Model 3（规则投影）→ 让结果“符合现实机制”  
6) 写 Evaluation + Results + Sensitivity  
7) 最后回到 Mechanism Design（给出建议与模拟）

