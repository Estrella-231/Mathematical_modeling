# 实验计划 | Experiments Plan

## 数据准备 | Data Preparation
- 加载CSV，强制转换分数为数值，保留N/A作为缺失值
  Load CSV, coerce scores to numeric, keep N/A as missing.
- 构建周级面板数据，包含每个选手-周次的评委总分
  Build week-level panel with total judge score per contestant-week.
- 从建模中移除淘汰后的周次
  Remove post-elimination weeks from modeling.

## 基线方法 | Baselines
- 粉丝份额与评委分数份额成比例
  Fan share proportional to judge score share.
- 剩余选手间的均匀粉丝份额
  Uniform fan share across remaining contestants.

## 粉丝投票估算 | Fan Vote Estimation
- 首先实现约束优化方法(A)
  Implement constrained optimization (A) first.
- 时间允许的话，与潜在流行度模型(B)比较
  Compare to latent popularity model (B) if time permits.

## 方案模拟 | Scheme Simulation
- 对所有季节应用排名法
  Rank method on all seasons.
- 对所有季节应用百分比法
  Percent method on all seasons.
- 对第28-34季应用排名法+评委拯救权
  Rank + judge save for seasons 28-34.

## 验证 | Validation
- 淘汰匹配率
  Elimination match rate.
- 被淘汰选手的排名误差
  Rank error for eliminated contestants.
- 对正则化的敏感性
  Sensitivity to regularization.

## 案例研究 | Case Studies
- 对第2、4、11、27季进行详细分析
  Run detailed analysis for seasons 2, 4, 11, 27.

## 图表 | Figures and Tables
- 表格：按季节和方法的一致性度量
  Table: consistency metrics by season and method.
- 图表：关键选手的粉丝份额与评委分数对比
  Plot: fan share vs judge score for key contestants.
- 柱状图：职业舞者和名人特征的影响
  Bar chart: impact of pro dancer and celebrity features.

## 代码审查清单 | Codex Review Checklist
- 边界情况：无淘汰周、多人淘汰周
  Edge cases: no elimination, multiple elimination weeks.
- 一致处理N/A和0分
  Consistent handling of N/A and 0 scores.
- 随机种子、可重现性和配置默认值
  Seeds, reproducibility, and config defaults.
