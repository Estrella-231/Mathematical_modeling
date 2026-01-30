# 模型设计 | Model Design

## 建模目标 | Modeling Objectives
1) 估算每个选手的周粉丝投票份额
   Estimate weekly fan vote shares for each contestant.
2) 匹配排名法和百分比法下的观测淘汰结果
   Match observed eliminations under both rank and percent rules.
3) 量化粉丝投票估计的不确定性
   Quantify uncertainty in fan vote estimates.
4) 跨季节和争议案例比较投票方案
   Compare voting schemes across seasons and controversy cases.
5) 分析职业舞者和名人特征的影响
   Analyze pro dancer and celebrity characteristics impact.
6) 提议更公平的替代系统
   Propose a fairer alternative system.

## 粉丝投票估算：候选方法 | Fan Vote Estimation: Candidate Approaches

### A) 约束优化（逐周）| Constrained Optimization (Week-by-Week)
- 变量：每个选手-周次的粉丝份额
  Variables: fan share per contestant-week.
- 约束：总和为1，非负，淘汰顺序与观测一致
  Constraints: sum to 1, nonnegative, elimination ordering consistent with observed.
- 目标：最小化与平滑性或基线的偏差（如评委分数份额）
  Objective: minimize deviation from smoothness or from a baseline (e.g., judge score share).
- 输出：可行的粉丝投票估计 + 约束松弛作为一致性度量
  Output: feasible fan vote estimates + constraint slack as consistency metric.

### B) 潜在流行度模型（季节级）| Latent Popularity Model (Season-Level)
- 粉丝份额建模为 softmax(alpha * 流行度 + beta * 评委分数 + 特征)
  Fan share modeled as softmax(alpha * popularity + beta * judge_score + features).
- 流行度是选手级或时变潜在变量
  Popularity is contestant-level or time-varying latent variable.
- 拟合参数以最大化观测淘汰的似然
  Fit parameters to maximize likelihood of observed eliminations.

### C) 可行域 + 抽样 | Feasible Region + Sampling
- 识别所有与淘汰一致的粉丝投票向量
  Identify all fan vote vectors consistent with eliminations.
- 从可行域抽样（或近似）计算不确定性区间
  Sample feasible region (or approximate) to compute uncertainty bands.

## 一致性度量 | Consistency Metrics
- 按周和季节的淘汰匹配率
  Elimination match rate by week and season.
- 被淘汰选手的平均排名误差
  Average rank error for eliminated contestant.
- 约束下具有可行粉丝投票解的周次百分比
  Percent of weeks with feasible fan vote solutions under constraints.

## 不确定性度量 | Uncertainty Metrics
- 粉丝份额的可行范围宽度（按选手-周次的最小/最大值）
  Feasible range width for fan share (min/max by contestant-week).
- 对周次或约束进行自助法（Bootstrap）
  Bootstrap over weeks or constraints.
- 后验方差（如果是贝叶斯模型）
  Posterior variance (if Bayesian model).

## 投票方案比较 | Voting Scheme Comparison
- 对所有季节应用排名法，对所有季节应用百分比法
  Apply rank method to all seasons, percent method to all seasons.
- 比较淘汰差异和最终名次
  Compare elimination differences and final placements.
- 量化粉丝影响：淘汰对粉丝份额变化的敏感性
  Quantify fan influence: sensitivity of elimination to fan share changes.

## 争议案例研究 | Controversy Case Studies
- 第2季 Jerry Rice
  Season 2 Jerry Rice
- 第4季 Billy Ray Cyrus
  Season 4 Billy Ray Cyrus
- 第11季 Bristol Palin
  Season 11 Bristol Palin
- 第27季 Bobby Bones
  Season 27 Bobby Bones
对每个案例：计算替代方案是否改变结果
For each: compute whether alternative scheme changes outcome.

## 职业舞者和名人特征分析 | Pro Dancer and Celebrity Characteristics Analysis
- 结果变量：名次、存活时间、评委分数、粉丝份额
  Outcome variables: placement, survival time, judge scores, fan share.
- 特征：年龄、行业、家乡地区、职业舞者
  Features: age, industry, home region, pro dancer.
- 方法：回归或混合效应模型；比较评委与粉丝效应
  Methods: regression or mixed effects model; compare judge vs fan effects.

## 提议的替代系统 | Proposed Alternative System
- 定义客观标准（公平性、兴奋度、稳定性）
  Define objective criteria (fairness, excitement, stability).
- 示例：评委和粉丝总分的加权z分数，限制粉丝主导性
  Example: weighted z-score of judge and fan totals with cap on fan dominance.
- 展示对历史季节的影响
  Demonstrate impacts on historical seasons.

## Claude 代码任务模板 | Claude Code Task Template
```
使用此模型设计，实现：
- 数据加载和面板构建
- 粉丝投票估算方法A（基线）与优化
- 投票方案模拟（排名/百分比/评委拯救）
- 一致性和不确定性度量
- 重现图表的脚本

Using this model design, implement:
- Data loading and panel construction
- Fan vote estimation method A (baseline) with optimization
- Voting scheme simulation (rank/percent/judge-save)
- Consistency and uncertainty metrics
- Scripts to reproduce figures and tables
```
