# 材料索引 (Materials Index)

## 1. 文档资源 (Documentation)

### 核心设计文档
- `docs/00_problem_summary.md` - 问题总结与核心任务
- `docs/01_assumptions.md` - 假设与合理性说明
- `docs/02_model_design.md` - 模型设计总览（Model A/B/C/D）
- `docs/06_decision_log.md` - 完整决策日志

### 模型实现文档
- `docs/08_model_b1_ridge_impl.md` - Ridge回归实现
- `docs/09_model_b2_rf_impl.md` - 随机森林实现
- `docs/10_model_c_comparison.md` - 规则比较模型
- `docs/11_model_d_impact_analysis.md` - 影响因素分析（Twin RF）
- `docs/13_model_e_new_system_impl.md` - 新系统AWVS设计

### 结果报告
- `docs/10_model_b1_report.md` - Ridge模型结果
- `docs/11_model_b1_v2_report.md` - Ridge模型v2结果
- `docs/14_model_b2_report.md` - 随机森林结果
- `docs/16_fixes_and_shap_report.md` - SHAP分析报告
- `docs/11_model_c_implementation_summary.md` - 规则比较实现总结
- `docs/12_model_d_implementation_summary.md` - Twin RF实现总结

## 2. 图表资源 (Figures)

### 淘汰匹配率分析 (Elimination Match Rate)
- `figures/elimination_match_rate/match_rate_by_season.png` - 按季节的匹配率
- `figures/elimination_match_rate/match_rate_by_week.png` - 按周次的匹配率
- `figures/elimination_match_rate/match_rate_by_size.png` - 按参赛人数的匹配率
- `figures/elimination_match_rate/cumulative_match_rate.png` - 累积匹配率
- `figures/elimination_match_rate/match_rate_summary.png` - 匹配率总结

### Ridge回归分析 (Ridge Regression)
- `figures/ridge/actual_vs_predicted.png` - 实际vs预测排名
- `figures/ridge/residual_distribution.png` - 残差分布
- `figures/ridge/residual_vs_judge_rank.png` - 残差vs评委排名
- `figures/ridge/fan_score_distribution.png` - 粉丝得分分布
- `figures/ridge/fan_score_by_season.png` - 按季节的粉丝得分
- `figures/ridge/top_20_fan_support.png` - Top 20粉丝支持度

### 随机森林分析 (Random Forest)
- `figures/random_forest/feature_importance.png` - 特征重要性
- `figures/random_forest/feature_importance_pie.png` - 特征重要性饼图
- `figures/random_forest/actual_vs_predicted.png` - 实际vs预测
- `figures/random_forest/residual_distributions.png` - 残差分布
- `figures/random_forest/fan_effect_by_age.png` - 年龄对粉丝效应的影响
- `figures/random_forest/fan_effect_by_industry.png` - 行业对粉丝效应的影响

### SHAP可解释性分析 (SHAP Analysis)
- `figures/shap_analysis/shap_summary_plot.png` - SHAP总结图
- `figures/shap_analysis/shap_bar_plot.png` - SHAP条形图
- `figures/shap_analysis/shap_dependence_age.png` - 年龄依赖图
- `figures/shap_analysis/shap_dependence_week.png` - 周次依赖图
- `figures/shap_analysis/shap_dependence_judge_rank_in_week.png` - 评委排名依赖图
- `figures/shap_analysis/shap_dependence_partner.png` - 舞伴依赖图
- `figures/shap_analysis/shap_dependence_cumulative_average.png` - 累积平均依赖图
- `figures/shap_analysis/shap_force_highest_fan_support.png` - 最高粉丝支持力图
- `figures/shap_analysis/shap_force_median_fan_support.png` - 中位粉丝支持力图
- `figures/shap_analysis/shap_force_lowest_fan_support.png` - 最低粉丝支持力图

### 规则模拟与比较 (Simulation & Comparison)
- `figures/simulation/ffi_comparison.png` - FFI对比
- `figures/simulation/ffi_distribution.png` - FFI分布
- `figures/simulation/ffi_by_season.png` - 按季节的FFI
- `figures/simulation/flip_rate_by_season.png` - 按季节的翻转率
- `figures/simulation/flip_rate_by_size.png` - 按参赛人数的翻转率
- `figures/simulation/overall_flip_rate.png` - 总体翻转率
- `figures/simulation/rule_consistency_matrix.png` - 规则一致性矩阵
- `figures/simulation/recommendation_scores.png` - 推荐得分

### 争议案例研究 (Case Studies)
- `figures/simulation/case_study_Jerry_Rice_S2.png` - Jerry Rice (S2)
- `figures/simulation/case_study_Master_P_S2.png` - Master P (S2)
- `figures/simulation/case_study_Billy_Ray_Cyrus_S4.png` - Billy Ray Cyrus (S4)
- `figures/simulation/case_study_Sabrina_Bryan_S5.png` - Sabrina Bryan (S5)
- `figures/simulation/case_study_Kim_Kardashian_S7.png` - Kim Kardashian (S7)
- `figures/simulation/case_study_Kate_Gosselin_S10.png` - Kate Gosselin (S10)
- `figures/simulation/case_study_Bristol_Palin_S11.png` - Bristol Palin (S11)
- `figures/simulation/case_study_Bobby_Bones_S27.png` - Bobby Bones (S27)

### Twin模型与新系统 (Twin Model & New System)
- `figures/twin_model/feature_importance_comparison.png` - 特征重要性对比
- `figures/twin_model/industry_bias.png` - 行业偏见
- `figures/twin_model/system_comparison.png` - 系统对比
- `figures/twin_model/awvs_benefits.png` - AWVS优势
- `figures/twin_model/weight_evolution.png` - 权重演化

## 3. 数据文件 (Data Files)

### 原始数据
- `Data/raw/2026_MCM_Problem_C_Data.csv` - 原始数据集

### 处理后数据
- `Data/processed/` - 处理后的数据文件

### 模型输出
- `Data/models/` - 模型训练结果
- `Data/simulation/` - 模拟结果数据
- `Data/twin_model/` - Twin模型结果

## 4. 模型完成情况

### ✅ 已完成模型
- **Model B1 (Ridge Regression)**: 评委分-排名回归，残差作为粉丝效应代理
- **Model B2 (Random Forest)**: 非线性特征重要性分析 + SHAP可解释性
- **Model C (Rule Comparison)**: 三种规则的反事实模拟（Rank/Percent/Judge Save）
- **Model D (Twin RF)**: 双子随机森林，分别预测粉丝票和评委分
- **Model E (AWVS)**: 自适应加权投票系统设计

### 📊 关键指标
- 淘汰匹配率 (Elimination Match Rate)
- 粉丝友好度指数 (Fan Friendliness Index, FFI)
- 翻转率 (Flip Rate)
- 特征重要性 (Feature Importance)
- SHAP值 (SHAP Values)

## 5. 论文章节映射

### Summary Sheet (0)
- 使用: 所有模型的核心结果
- 关键图: `simulation/recommendation_scores.png`

### Introduction (1-2)
- 使用: `00_problem_summary.md`, `01_assumptions.md`

### Data & EDA (5)
- 使用: `07_data_processing.md`, `11_data_processing_report.md`
- 关键图: 淘汰匹配率系列图

### Model Construction (6)
- 使用: `02_model_design.md`, `08-13`系列实现文档
- 关键图: 流程图（需创建）

### Results (7-8)
- 使用: 所有报告文档
- 关键图: Ridge/RF/SHAP/Simulation全系列

### Mechanism Design (9)
- 使用: `13_model_e_new_system_impl.md`
- 关键图: `twin_model/system_comparison.png`, `twin_model/awvs_benefits.png`

### Conclusion (10)
- 使用: 所有文档的总结
