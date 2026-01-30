# 模型 E 实现方案：自适应动态加权系统 (Model E: Adaptive Weighted Voting System Implementation)

## 1. 系统定义 (System Definition) 

我们提议一种 **自适应动态加权系统 (AWVS)**，它不再使用固定的“排名相加”或“百分比相加”，而是引入**时间维度**和**成长维度**。

### 1.1 核心公式
每位选手 $i$ 在第 $t$ 周的最终得分 $S_{i,t}$ 定义为：

$$ S_{i,t} = \alpha(t) \cdot Z^{Judge}_{i,t} + (1 - \alpha(t)) \cdot Z^{Fan}_{i,t} + \beta \cdot \text{Trend}_{i,t} $$

其中：
*   **$Z^{Judge}_{i,t}$**: 标准化评委得分 (Z-Score)。
*   **$Z^{Fan}_{i,t}$**: 标准化粉丝投票份额 (Z-Score, 来自 Model B1 估算)。
*   **$\\alpha(t)$**: **动态评委权重函数**。
*   **$\\text{Trend}_{i,t}$**: **进步奖励分**。

### 1.2 动态权重函数 $\\alpha(t)$
为了平衡娱乐性（前期）和专业性（后期）：
$$ \\alpha(t) = \\alpha_{base} + \\gamma \cdot \frac{t}{T_{max}} $$
*   **前期 ($t=1$):** 评委权重较低 ($\\approx \\alpha_{base}$)，保护有人气但技术尚浅的选手。
*   **决赛 ($t=T_{max}$):** 评委权重达到最高 ($\\alpha_{base} + \\gamma$)，确保冠军具备硬实力。
*   *建议初始参数:* $\\alpha_{base}=0.4, \\gamma=0.3$ (权重从 40% 升至 70%)。

### 1.3 进步奖励 $\\text{Trend}_{i,t}$
为了鼓励选手成长（这也是粉丝最爱看的故事）：
$$ \\text{Trend}_{i,t} = \\max(0, \\text{Score}^{Judge}_{i,t} - \\text{MA}^{Judge}_{i, t-1}) $$
*   如果本周表现优于过去均值 (Moving Average)，获得额外加分。
*   $\\beta$: 奖励系数 (建议 0.5，即每进步1分，总分加0.5个标准差)。

## 2. 优化与调优 (Optimization)

我们不能随意定参数，需要用数据说话。

### 2.1 目标函数
寻找最优参数组 $(\\alpha_{base}, \\gamma, \\beta)$，最大化以下综合指标 $J$:
$$ J = w_1 \cdot \\text{Fairness} + w_2 \cdot \\text{Engagement} - w_3 \cdot \\text{Controversy} $$
*   **Fairness:** 最终排名与评委排名的 Spearman 相关系数。
*   **Engagement:** 粉丝投票权重 $>0.3$ 的周次比例（保证粉丝觉得投票有用）。
*   **Controversy:** “低分高能”选手（如 Bobby Bones）进入决赛的概率。

### 2.2 训练过程
1.  **Grid Search:** 在 S1-S27 数据上遍历参数。
2.  **Validation:** 找出能让 Bobby Bones 在 S27 止步于半决赛（例如 Week 8-9），同时让 Bristol Palin (S11) 止步于 Week 7 的参数组合。

## 3. 验证与支持证据 (Support for Adoption)

为了说服制作人，我们需要产出以下对比证据：

### 3.1 案例重演 (The "Bobby Bones Test")
*   **现状:** Bobby Bones 夺冠 (S27)。
*   **AWVS:** 在 Week 9，由于 $\\alpha(t)$ 增加到 0.65 且他的 `Trend` 为负（技术停滞），他的综合分跌出前三 $\\rightarrow$ **被合理淘汰**。
*   *结论:* AWVS 修正了“系统漏洞”，同时保留了他前期的娱乐价值。

### 3.2 兴奋度维持 (Excitement Retention)
*   展示 AWVS 下的“翻盘率”：虽然限制了极端偏差，但对于中游选手，粉丝投票依然能决定生死（40%-50% 权重）。
*   展示“进步奖励”如何让一位努力的选手（如得分为 6->7->8）逆袭一位停滞的选手（8->8->8）。

## 4. 实现代码结构 (Code Structure)
在 `solution/Code/models/new_system.py` 中实现：
```python
def calculate_awvs(df, alpha_base=0.4, gamma=0.3, beta=0.5):
    # Calculate Z-scores
    # Calculate Trend
    # Apply Formula
    return final_scores

def simulate_season(season_data, system='awvs'):
    # Run weekly simulation
    # Return elimination_order
```

## 5. 输出图表
1.  **权重变化曲线图:** 展示评委话语权如何随赛季深入而提升。
2.  **S27 排名走势对比:** 真实排名 vs AWVS 排名（Bobby Bones 的两条线）。
