# 模型 D 实现方案：因素影响的双重对比分析 (Model D: Comparative Impact Analysis)

## 1. 目标 (Objective)
**核心目标：回答“选手特征和职业舞者对‘评委评分’与‘粉丝投票’的影响是否相同？”**

我们不通过单一模型回答，而是构建**双子模型 (Twin Models)**：
1.  **Model $M_{fan}$:** 解释粉丝投票 (Fan Estimates)。
2.  **Model $M_{judge}$:** 解释评委评分 (Judge Scores)。
通过对比两个模型的特征重要性和偏效应 (Partial Effects)，量化两者偏好的差异。

## 2. 特征工程：职业舞者与选手画像 (Feature Engineering)

为了深入分析“职业舞者”的影响，我们需要比 One-Hot 编码更深层的特征：

### 2.1 职业舞者特征 ($X_{partner}$)
*   **`partner_history_avg_place`**: 该舞伴在**当前赛季之前**所有赛季的平均最终排名。
    *   *意义:* 衡量舞伴的“带飞能力” (Carry Capability)。
*   **`partner_experience`**: 该舞伴此前参加过的赛季数。
    *   *意义:* 衡量舞伴的经验值。
*   **`partner_win_rate`**: 该舞伴进入决赛或夺冠的频率。

### 2.2 选手特征 ($X_{celeb}$)
*   **`age`**: 数值型。
*   **`industry`**: 分类变量 (Actor, Athlete, Reality Star, etc.)。
*   **`gender`**: 分类变量。
*   **`home_region`**: 是否是该国（美国）本土选手 (如果是国际版数据)。

## 3. 双子模型架构 (Twin Model Architecture)

### 模型 1: 粉丝偏好模型 ($M_{fan}$)
*   **算法:** Random Forest Regressor
*   **输入 ($X$):** $X_{partner} + X_{celeb}$
*   **目标 ($Y_{fan}$):** Model B1 估算出的 **粉丝投票份额 (Fan Vote Share)** 或 **粉丝效应残差 (Fan Residual)**。

### 模型 2: 评委偏好模型 ($M_{judge}$)
*   **算法:** Random Forest Regressor
*   **输入 ($X$):** $X_{partner} + X_{celeb}$ (完全相同)
*   **目标 ($Y_{judge}$):** **标准化评委总分 (Standardized Judge Total)**。

## 4. 对比分析方法 (Comparison Methodology)

### 4.1 重要性排序对比 (Rank Correlation)
*   列出 $M_{fan}$ 和 $M_{judge}$ 的 Feature Importance (MDI 或 Permutation)。
*   计算 **Spearman 相关系数**。
    *   如果相关性高 $ightarrow$ 评委和粉丝看重同样的东西。
    *   如果相关性低 $ightarrow$ 他们的口味不同（例如粉丝看重行业，评委看重舞伴实力）。

### 4.2 SHAP 依赖图叠加 (Overlaid SHAP Dependence)
*   针对关键特征（如 `Age`），在同一张图上绘制两个模型的 SHAP Trend 线（归一化后）。
    *   **Case A (同向):** 随着年龄增加，粉丝分和评委分都下降 $ightarrow$ 年龄是硬伤。
    *   **Case B (背离):** 随着年龄增加，评委分下降（技术下降），但粉丝分上升（敬老/同情分） $ightarrow$ **关键发现！**

### 4.3 行业偏好热图 (Industry Preference Heatmap)
*   计算各行业 (`industry`) 在两个模型中的平均 SHAP 值。
*   绘制双柱状图：
    *   Bar 1: Judge Bias (e.g., Dancers/Singers get +Scores)。
    *   Bar 2: Fan Bias (e.g., Reality Stars/Influencers get +Votes)。
    *   *Analysis:* 找出“粉丝溢价”最高的行业（Fan Bias >> Judge Bias）。

## 5. 实现步骤 (Implementation Steps)
1.  **Pre-process:**
    *   构建 `pro_dancer_stats.csv`: 根据历史数据计算舞伴的 `avg_place` 等指标（注意防止数据泄露，S10的舞伴特征只能用S1-S9计算）。
    *   Merge 到主面板数据。
2.  **Train:** 训练 $M_{fan}$ 和 $M_{judge}$。
3.  **Explain:** 计算 SHAP values。
4.  **Visualize:** 生成对比图表 (`solution/Draw_picture/impact_comparison/`).
5.  **Report:** 撰写文字结论，回答“职业舞者有多大影响？”（看 Feature Importance）以及“影响是否相同？”（看对比图）。

## 6. 预期结论示例 (Hypothesis)
*   *职业舞者影响:* 对评委分影响更大（技术加成），对粉丝票影响较小（除非舞伴本身也是明星）。
*   *年龄影响:* 评委对高龄惩罚严重，粉丝较宽容。
*   *行业影响:* 真人秀明星 (Reality) 评委分低，粉丝票极高。
