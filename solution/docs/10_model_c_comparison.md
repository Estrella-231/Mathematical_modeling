# 模型 C 实现方案：投票机制对比与争议分析 (Model C: Voting Method Comparison & Controversy Analysis)

## 1. 目标 (Objective)
利用 Model B1/B2 估算出的粉丝投票 ($V_{fan}$) 作为基准真值 (Ground Truth)，进行**反事实模拟 (Counterfactual Simulation)**：
1.  **全局对比:** 在所有赛季应用不同的投票规则，比较结果差异。
2.  **偏差检测:** 判断哪种规则更倾向于粉丝 (Favor Fan Votes) 或评委 (Favor Judge Scores)。
3.  **争议重演:** 针对 Jerry Rice, Bobby Bones 等特定案例，检验不同规则是否会改变他们的命运。
4.  **系统推荐:** 基于量化指标推荐最佳投票机制。

## 2. 模拟引擎设计 (Simulation Engine Design)

### 2.1 输入 (Inputs)
*   **评委评分 ($S_{judge}$):** 历史真实数据 (不变)。
*   **粉丝投票 ($V_{fan}$):** 来自 Model B1 的估算值 (固定为主要估算值或通过蒙特卡洛采样引入不确定性)。
*   **规则集 (Rule Sets):**
    1.  **Rule A (Rank Sum):** $R_{judge} + R_{fan}$ (Min is bad/Max is bad depending on definition. We use: **Max Sum of Ranks = Eliminated**, assuming Rank 1=Best)。
    2.  **Rule B (Percent Sum):** $\%_{judge} + \%_{fan}$ (Min Sum = Eliminated)。
    3.  **Rule C (Judge Save):** Rank Sum determines Bottom 2 -> Judges eliminate lower $S_{judge}$。

### 2.2 模拟流程 (Simulation Loop)
对于每一个赛季 $s$，每一周 $w$：
1.  **加载数据:** 当周所有存活选手 $P_{alive}$。
2.  **计算得分:** 
    *   计算 Rule A 下的综合分 $Score_A$。
    *   计算 Rule B 下的综合分 $Score_B$。
    *   计算 Rule C 下的综合分 $Score_C$。
3.  **确定淘汰者:** 
    *   $E_A = \text{ArgMax}(Score_A)$ (Assuming Rank Sum, higher is worse)。
    *   $E_B = \text{ArgMin}(Score_B)$。
    *   $E_C$: Find Bottom 2 via Rule A, then select one with lower $S_{judge}$。
4.  **记录差异:** 
    *   记录 $E_A, E_B, E_C$ 是否相同。
    *   如果不同，记录“谁被救了 (Saved)”和“谁被杀了 (Killed)”。

## 3. 分析指标 (Analysis Metrics)

### 3.1 倾向性指标 (Bias Metric)
定义“粉丝友好度” (Fan Favorability):
$$ \text{FanFavor} = \text{Corr}(\text{FinalRank}, \text{FanRank}) - \text{Corr}(\text{FinalRank}, \text{JudgeRank}) $$ 
*   比较 Rule A 和 Rule B 下的 $\text{FanFavor}$ 指标。
*   *Hypothesis:* Percent Method 可能更偏向粉丝（因为粉丝票通常是长尾分布，头部明星票数极高，能淹没评委分）。

### 3.2 翻转率 (Flip Rate)
$$ \text{FlipRate} = \frac{\text{Count}(E_A \neq E_B)}{\text{Total Weeks}} $$ 
*   量化两种规则产生不同结果的频率。

### 3.3 争议案例深度分析 (Case Studies)
针对 Jerry Rice (S2), Billy Ray Cyrus (S4), Bristol Palin (S11), Bobby Bones (S27)：
*   **生存曲线对比:** 绘制他们在 Rule A vs Rule B 下的“理论存活周数”。
*   **关键周次:** 找出他们本应被淘汰但被规则“拯救”的具体周次。
*   **Judge Save 影响:** 检验如果引入 "Judge Save"，这些争议选手是否会被更早淘汰？（通常是的，因为他们评委分低）。

## 4. 推荐系统逻辑 (Recommendation Framework)
构建一个**多目标评价矩阵**：
1.  **公平性 (Fairness):** 最终排名与“技术实力”（评委分）的相关性。
2.  **参与度 (Engagement):** 粉丝投票对结果的决定权（不能太低，否则粉丝不投了）。
3.  **抗干扰性 (Robustness):** 防止极低评委分的选手仅靠狂热粉丝夺冠（Bobby Bones Effect）。

**推荐策略:** 
*   如果目标是避免 Bobby Bones 情况 $\rightarrow$ 推荐 Rule C (Judge Save) 或 Rule B (Percent) with Weighting?
*   (分析结果可能显示 Rule C 最能平衡，因为它保留了粉丝决定 Bottom 2 的权力，但给了评委最后的把关权)。

## 5. 输出文件 (Outputs)
*   `solution/Data/simulation_results.csv`: 包含所有模拟周次的结果对比。
*   `solution/Draw_picture/comparison_plots/`:
    *   `flip_rate_by_season.png`
    *   `bias_comparison.png`
    *   `case_study_trajectories.png` (Jerry Rice 等人的生存线)

## 6. 实现步骤 (Implementation Steps)
1.  **Load:** Estimates from `fan_scores.csv`。
2.  **Simulate:** 编写 `VotingSimulator` 类，实现三种规则逻辑。
3.  **Run:** 遍历所有数据，生成对比表。
4.  **Analyze:** 计算 Flip Rate 和 Bias Metrics。
5.  **Visualize:** 画图。
