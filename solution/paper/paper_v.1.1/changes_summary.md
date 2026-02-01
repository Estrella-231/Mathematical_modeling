## Change Log

记录论文结构与内容调整，按时间持续追加。

### 2026-02-01 (早)
- 结构改为 Q1–Q4 问题驱动，并对齐结果段落。
- 抽象与 Overview 改为"四步逻辑"。
- 主要图表按 Q1–Q4 重新分组与放置。
- 术语清理：B1/B2 标注改为 Q1/Q3。
- Problem 1 扩写为"观察→建模→改进→验证"，并补充 Ridge V1/V2 细节。
- 新增两张图并插入：`judge_score_vs_placement.png`、`jerry_rice_fan_share_timeseries.png`。
- Problem 4 重写：合并原 "Mechanism Design / Recommendation" 段落，按 AWVS 设计→评估→推荐 三段式组织；补充 Bobby Bones / Jerry Rice 测试、参数敏感度表、实施路线图。
- Strengths and Weaknesses 重写：S1–S6 六条优势（逆向推断框架、多模型交叉验证、定量回答、可操作建议、可复现性、敏感度鲁棒性）；W1–W5 五条局限（未观测真值、因果关系、单节目范围、实现复杂度、时间假设）。
- Conclusion 重写：Q1–Q4 汇总表、五项主要贡献、更广泛影响、最终建议（三步路线图）。

### 2026-02-01 (晚)
**Problem 2: Mechanism Comparison (Section 6) - 新增完整章节**
- 新增 6.1 Counterfactual Framework：定义反事实模拟框架，241个淘汰周×3种投票规则
- 新增 6.2 Voting Mechanisms：详述三种机制 (Rank Sum, Percent Sum, Judge Save)
- 新增 6.3 Fan Favorability Index (FFI)：公式 $(R^J - R^F)/(N_t - 1)$，范围 [-1, +1]
- 新增 6.4 Simulation Results：Match Rate 85.3%，Rank Sum Score 0.884，关键发现表格

**Problem 3: Determinants of Success (Section 7) - 重构简化**
- 原结构 7.1–7.9 共9个小节，精简为5个小节
- 7.1 Twin Random Forest：$M_{fan}$ vs $M_{judge}$ 架构，特征重要性对比
- 7.2 SHAP Analysis：TreeSHAP 解释，特征交互效应
- 7.3 Technical Bias Coefficient：TBC = 0.612 公式推导
- 7.4 Industry Bias：行业分组分析 (Entertainment/Sports/Music)
- 7.5 Synthesis：关键发现总结

**Problem 4: System Optimization (Section 8) - 独立成节**
- 从 Problem 3 中分离，创建独立 Section 8
- 保持 AWVS 设计→评估→推荐 结构

**结构验证**
- 使用 Select-String 确认最终章节结构正确
- LaTeX 编译无错误

### 2026-02-01 (晚 22:00+)
**Section 6 案例图片精简**
- 删除6张单独的 case study 图片 (Bobby Bones, Jerry Rice, Bristol Palin 各一张单独图 + Billy Ray Cyrus/Sabrina Bryan 组图 + Master P/Kim Kardashian 组图)
- 合并为1张组图：Bobby Bones (S27) 和 Jerry Rice (S2) 并排展示
- 保留两个最具代表性案例 (Bobby Bones 争议冠军 + Jerry Rice 触发规则变更)
- Bristol Palin、Billy Ray Cyrus、Master P、Sabrina Bryan 改为文字描述 + 汇总表格
- 减少版面占用，提升美观度

**Section 8 (Problem 4) 图片精简**
- 删除 Figure 20 组图 (system_comparison.png + awvs_benefits.png)
- 保留表格 "AWVS vs. existing rules: comprehensive comparison" 展示数据
- 表格已清晰展示所有指标对比，图片冗余

### 2026-02-01 (晚 23:30+)
**全文数学公式排版改进 - 参考O奖论文风格**
- 将重要的内联公式改为独立显示公式 (display math)，使公式与正文分开

**Section 1.4 Overview (5个公式)**
- Ridge回归模型: `Ranking ~ β₀ + β₁·JudgeScore + ...`
- FFI定义: `FFI = (R^J - R^F)/(N-1)`
- AWVS综合评分: `S^{AWVS} = α(t)·Z^J + (1-α(t))·Z^F + β·Trend`
- 权重函数: `α(t) = 0.4 + 0.3·t/T_max`
- 趋势奖励: `Trend = max(0, Score^J - MA^J)`

**Section 2 Assumptions (3个公式)**
- 投票份额归一化: `∑V_{i,t} = 1`
- 时间平滑性: `V_{i,t} ≈ V_{i,t-1}`
- Judge Save机制: `Eliminated = argmin J_{i,t}`

**Section 4 Data Preparation (1个公式)**
- 分数标准化: `Score_std = (∑J_{i,t,j}/n_valid) × 30`

**Section 5 Problem 1 (5个公式)**
- 核心排名模型: `Ranking = α·JudgeScore + β·FanVote + ε`
- Ridge代理: `R_{i,s} = β₀ + β₁·J_{avg} + β₂·S_s + ε`
- Ridge目标函数: `min Σ(R - R̂)² + λ||β||²`
- Sigmoid映射: `FanScore = 1/(1+exp(γ·ε))`
- Softmax周级份额: `FanShare = exp(ε̂)/Σexp(ε̂)`

**Section 6 Problem 2 (3个公式)**
- 评分标准三公式改为独立显示: S_fair, S_balance, S_stable

**Section 8 Problem 4 (3个公式)**
- 动态权重函数: `α(t) = α_base + γ·t/T_max`
- 改进奖励公式: `Trend = max(0, J - MA^J)`
- 奖励计算: `Bonus = β·(J - MA^J)`

**总计**: 约20个重要公式从内联改为独立显示，提升论文专业性和可读性

### 2026-02-02 (凌晨)
**Section 5 (Problem 1) 进一步优化**
- 删除 Figure "Residuals versus judge rank in week" (`residual_vs_judge_rank.png`) - 视觉效果不理想
- 改进文本结构：删除内联 `\textbf{}` 标记，改用 `\subsubsection` 层级
- 分离公式与文本：每个公式前后都有独立的说明段落
- 参数说明独立化：如 `γ = 0.5` 等参数从公式内移到文字说明中
