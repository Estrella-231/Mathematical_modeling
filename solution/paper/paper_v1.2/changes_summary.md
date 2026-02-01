## Change Log - Paper v1.2

### 2026-02-02 (凌晨 - 基于 v1.1 进行优化)

**Notation 表格精简 (参考O奖论文风格)**
- 从约70行的 `longtable` (3列，9个分组) 精简为15个核心符号的 `table` (2列)
- 删除了详细的分组标题，只保留最关键的符号
- 使用 `p{3.5cm}p{9cm}` 列宽，内容居中，避免表格挤在中间
- 保留符号：基本索引 ($s, t, i, N_t$)、核心变量 ($J, V, R$)、评分规则 ($S^{rank}, S^{percent}, S^{AWVS}$)、关键指标 ($FFI, \alpha(t), Trend$)、统计量 ($\rho, R^2$)

**Section 1.4 Overview of Our Solution - 公式分离**
- 将长达4行的单段文本拆分为4个独立的Stage段落
- Stage 1: Ridge回归模型公式独立显示
- Stage 2: FFI定义公式独立显示
- Stage 4: AWVS三个公式（综合评分、权重函数、趋势奖励）独立显示
- 每个公式前有独立说明，公式后有解释文本

**Section 4 Data Preparation - 公式与文本分离 + 删除重复内容**
- Cleaning and Preprocessing 部分：
  - Wide-to-long transformation 用列表展示数据转换过程
  - 删除重复的 `Score_std` 公式（之前出现两次）
  - 使用 `\subsubsection` 替代 `\textbf{}` 标记
  - 公式独立成行，参数说明在公式下方
- Judges Score Statistics 部分：
  - 删除重复内容（之前Distribution、Judge consistency各有两段）
  - 将 `\[ \begin{array}... \]` 改为正式的 `table` 环境
  - 统计量用独立公式展示：$\bar{J} = 236.92, \sigma_J = 43.91$
  - 表格都添加了 `\caption` 和 `\label`
  - 用 `\subsubsection` 分层：Distribution、Judge Consistency、Within-Week Variance

**整体改进**
- 公式与正文完全分离，符合O奖论文风格
- 结构更清晰，层级分明（使用 `\subsubsection`）
- 删除冗余内容，避免重复
- 表格和公式都规范化命名

### 2026-02-02 (早晨 - 新增高质量可视化)

**Section 7 (Problem 3) - 新增两张O奖风格图表**
- **Figure: Feature Correlation Heatmap** (`twin_model/correlation_heatmap.png`)
  - 位置：Section 7.1 Twin-Model Architecture，新增 `\subsubsection{Feature Correlation Structure}`
  - 用途：展示judge scores与fan votes的相关性结构差异（0.615中等相关）
  - 关键发现：Age↔Judge Score: -0.381, Week↔Fan Vote: 0.650, 证明需要Twin模型
  - 包含列表形式的关键观察点
  
- **Figure: Contestant Clustering** (`twin_model/contestant_clustering.png`)
  - 位置：Industry Bias Analysis之后，新增 `\subsection{Contestant Archetypes: A Clustering Analysis}`
  - 用途：K-Means聚类（k=4）将421名选手分为4种类型
  - 四种类型：
    - Superstars (39.0%, n=164): 高judge高fan，平均第3名
    - Tech Giants (21.4%, n=90): 高judge低fan，平均第7.6名（如Sabrina Bryan）
    - Fan Favorites (3.6%, n=15): 低judge高fan，争议cluster（Bobby Bones, Jerry Rice, Bristol Palin）
    - Underdogs (36.1%, n=152): 低judge低fan，平均第10.6名
  - 分析意义：3.6%的Fan Favorites集中了多个决赛选手和冠军，支持AWVS设计必要性
  - 添加了详细的archetype描述和implications for system design

**删除冗余/低质量图表**
- 删除 Figure "Feature importance comparison" (`feature_importance_comparison.png`)
  - 原因：与前面的Feature importance comparison表格重复
  - 表格已经清晰展示了所有数值（week +0.572, relative_judge_score -0.650），图表冗余
- 删除 Figure "Distribution of fan support scores" (`fan_score_distribution.png`)
  - 原因：与residual distribution图信息重复，视觉效果不佳
- 删除 Figure "FFI distribution histograms" (`ffi_distribution.png`)
  - 原因：与FFI comparison图和表格重复，柱状图不如对比图直观
- 删除 Figure "Counterfactual trajectories" 组图 (`case_study_Bobby_Bones_S27.png` & `case_study_Jerry_Rice_S2.png`)
  - 原因：已有详细的表格展示counterfactual结果，图表冗余
- 删除 Figure "Fan effect by age group" (`fan_effect_by_age.png`)
  - 原因：SHAP dependence age图已展示年龄效应，此图重复且质量较低
- 删除 Figure "FFI comparison across voting rules" (`ffi_comparison.png`)
  - 原因：FFI statistics表格已清晰展示各规则的FFI均值和分布，图表冗余
- 删除 Figure 3 "Jerry Rice (S2): weekly fan vote share with uncertainty bands" (`ridge/jerry_rice_fan_share_timeseries.png`)
  - 原因：按用户要求移除该图

**调整图片尺寸以优化版面**
- Correlation Heatmap: 从0.85\textwidth → 0.70\textwidth → 0.60\textwidth（最终）
- Contestant Clustering: 从0.85\textwidth → 0.72\textwidth → 0.65\textwidth（最终）
- 目的：避免图片占据整个页面，使文字和图片比例更加和谐，留出更多空间给正文

**替换图表为高质量可视化**
- 将 `recommendation_scores.png` 替换为 `advanced/radar_chart.png`（雷达图）
  - 更直观展示三种规则在 Fairness、Balance、Stability 三个维度的对比
- 新增 `advanced/temporal_trend_linechart.png`（折线图）
  - 从 `weekly_panel.csv` 计算34季的平均分数
  - 展示分数膨胀趋势：早期(S1-S10)均值~218 → 后期(S21-S34)均值~240
  - 包含±1 SD置信带
- 将 Table 2 (Temporal trend) 改为折线图，与 Distribution 图并排显示
  - 原表格只有3行汇总数据，折线图展示全部34季细节
  - 两图并排(0.48\textwidth each)，更紧凑美观
