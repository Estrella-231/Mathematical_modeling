# 逐节写作模板（可直接填空）

> 使用方式：按节填写“要点 + 图/表 + 结论 + 引用”。每节控制 1–2 页。完成后把各节合并到正文。

---

## 0 One-page Summary Sheet

**0.1 Problem in One Sentence**
- [一句话问题定义]

**0.2 Core Idea / Models**
- [模型流程：数据 → 逆向估计 → 监督预测 → 规则投影]

**0.3 Key Results（3条）**
- 结果1：[量化指标 + 对比对象]
- 结果2：[量化指标 + 对比对象]
- 结果3：[量化指标 + 对比对象]

**0.4 Recommendations**
- [建议1]
- [建议2]
- [建议3]

**0.5 Why It Matters**
- [公平性]
- [可解释性]
- [可执行性]

**图/表（1个）**
- 图名：________________
- 文件：`figures/________.png`

---

## 1 Memo

**To / From / Date / Subject**
- To:
- From:
- Date:
- Subject:

**What We Did（5–7行）**
- 

**What We Found（3条）**
- 

**What We Recommend（3条）**
- 

**Limitations（2–3条）**
- 

---

## 2 Introduction

**2.1 Problem Background**
- [DWTS规则与争议点]

**2.2 Restatement of the Problem**
- 子任务A：____
- 子任务B：____
- 子任务C：____

**2.3 Related Work（可选）**
- [投票机制/公平性/排名模型简述]

**2.4 Overview of Our Solution**
- [流程概述图说明]

**2.5 Our Contributions**
- 贡献1：____
- 贡献2：____
- 贡献3：____

**图/表**
- 流程图：`figures/________.png`

---

## 3 Assumptions and Justifications

**3.1 Data Availability**
- 假设：____
- 理由：____
- 影响：____
- 处理：____

**3.2 Behavioral**
- 

**3.3 Modeling**
- 

**3.4 Rule Assumptions**
- 

**3.5 Potential Violations & Impact**
- 

---

## 4 Notations

**4.1 Indices**
- s=season, t=week, i=contestant

**4.2 Observed Variables**
- judge_score, placement, elimination_week…

**4.3 Latent Variables**
- vote_share, popularity…

**4.4 Functions / Operators**
- rank(·), normalize(·), projection(·)

---

## 5 Data Preparation and EDA

**5.1 Dataset Overview**
- 来源：____
- 样本量：____
- 字段：____

**5.2 Cleaning & Preprocessing**
- 去重：____
- 异常处理：____
- 统一评分：____

**5.3 Judges Score Statistics**
- 分布/方差/一致性结论：____

**5.4 External Signals & Missingness**
- 外部信号：____
- 缺失机制假设：____

**5.5 Why Inverse Estimation**
- 解释：____
- 小例子：____

**图/表（2–3个）**
- 评委分分布：`figures/____.png`
- 缺失热力：`figures/____.png`
- 外部信号相关：`figures/____.png`

---

## 6 Model Construction

### 6.1 Model 0: Unifying Scoring Schemes
- 动机：____
- 归一化方法：____
- Sanity Check：____

### 6.2 Model 1: Inverse Vote Estimation
- 目标：____
- 潜变量形式：____
- 规则约束：____
- 目标函数：____
- 求解方法：____
- 输出（伪标签）：____

### 6.3 Model 2: Supervised Prediction
- 目标定义：____
- 特征工程：____
- 模型选择：____
- 验证协议：____
- 可解释性：____

### 6.4 Model 3: Rule Projection
- 动机：____
- 投影形式：____
- 算法：____
- 效果：____

### 6.5 Complexity & Practical Considerations
- 运行时间：____
- 缺失鲁棒性：____
- 可部署性：____

---

## 7 Evaluation Criteria

- 回归指标：MAE/RMSE/Spearman
- 分类指标：AUC/F1/Brier
- 规则一致性：____
- 公平性：____
- 跨季稳定性：____

---

## 8 Results, Discussion, Sensitivity

**8.1 Main Quantitative Results**
- 表格：____

**8.2 Key Visualizations**
- 图1：____
- 图2：____

**8.3 Interpretation**
- 驱动因素：____
- 冲突结构：____

**8.4 Sensitivity**
- followers 权重：____
- 约束松紧：____

---

## 9 Mechanism Design / Recommendation

**9.1 Problems with Current Rule**
- 

**9.2 Proposed Alternative Rule**
- 

**9.3 Counterfactual Evaluation**
- 

**9.4 Trade-offs**
- 

**9.5 Implementation Plan**
- 

---

## 10 Conclusion

- Summary of Findings：____
- Actionable Recommendations：____
- Limitations：____
- Future Work：____

---

## References
- [统一格式]

---

## Appendices

**Appendix A**: 表格补充
**Appendix B**: 关键代码片段
**Appendix C**: AI 使用说明
