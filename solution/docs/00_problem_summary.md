# 问题总结 (2026 MCM/ICM C: Data With The Stars)
# Problem Summary (2026 MCM/ICM C: Data With The Stars)

## 快速问题重述 | Quick Restatement
给定《与星共舞》(DWTS) 评委评分数据（第1-34季）和选手元数据。粉丝投票未知。需要：
- 建立模型估算粉丝每周投票
- 比较投票方案（排名法 vs 百分比法）跨季变化
- 分析有争议的淘汰案例
- 量化职业舞者和名人特征的影响
- 提议更公平的系统
- 提交25页报告+备忘录+AI使用报告

You are given DWTS judge score data (seasons 1-34) and contestant metadata. Fan votes are unknown. Build models to estimate fan votes weekly, compare voting schemes (rank vs percent) across seasons, analyze controversial cases, quantify effects of pro dancers and celebrity characteristics, and propose a fairer system. Provide a 25-page report plus memo and AI use report.

## 所需输出 | Required Outputs
- 每个选手-周次的粉丝投票估计值（含不确定性）
- 与每周淘汰结果的一致性检查
- 两种方法跨季对比分析
- 案例研究：第2、4、11、27季（及其他发现的争议案例）
- 职业舞者和名人特征的影响分析
- 提议的替代投票系统及其合理性说明

- Estimated fan votes for each contestant-week with uncertainty.
- Consistency checks against weekly eliminations.
- Cross-season comparison of rank vs percent methods.
- Case studies: seasons 2, 4, 11, 27 (and any others found).
- Impact analysis of pro dancers and celebrity characteristics.
- Proposed alternative voting system with justification.

## 核心任务与建模方向 | Core Tasks & Modeling Directions (Derived)
Based on analysis, the following tasks are prioritized:

1.  **粉丝投票估算 (Fan Vote Estimation):**
    -   *Method:* 逆向推理模型 (Inverse Inference Model). 利用已知淘汰结果和评委分，构建不等式约束系统或概率模型（如贝叶斯网络/MCMC），反解出能导致该结果的粉丝投票可行域。
    -   *Goal:* Estimate fan vote distribution.

2.  **投票机制对比 (Voting Method Comparison):**
    -   *Method:* 蒙特卡洛模拟 (Monte Carlo Simulation). 在可行域内生成大量粉丝投票样本，模拟不同投票规则（Rank vs Percent）下的晋级情况，计算“结果翻转率” (Flip Rate)。
    -   *Goal:* Compare voting schemes.

3.  **特征影响量化 (Feature Impact):**
    -   *Method:* 生存分析/逻辑回归 (Survival Analysis / Regression). 以“是否被淘汰”为因变量，评委分、选手特征为自变量。残差部分可解释为“粉丝效应”。
    -   *Goal:* Quantify feature impact.

4.  **争议案例分析 (Controversy Analysis):**
    -   *Method:* 反事实分析 (Counterfactual Analysis). 针对 Jerry Rice 等案例，固定评委分，调整投票规则，观察其生存周期的变化。

5.  **新系统提议 (New System Proposal):**
    -   *Method:* 多目标优化 (Multi-objective Optimization). 设计新规则，最大化“公平性”（与评委分的相关性）和“娱乐性”（结果的不确定性/粉丝参与度）的加权和。

## 关键变量与指标 | Key Variables & Indicators
-   **输入变量 (Input Variables):**
    -   **选手元数据:** `celebrity_name`, `celebrity_industry`, `celebrity_age_during_season`, `celebrity_homestate/country`, `ballroom_partner`.
    -   **评委评分:** `weekX_judgeY_score` (1-10分, 含小数/加分). *Note:* N/A exists.
    -   **赛果:** `results`, `placement`.
-   **潜在/衍生变量 (Latent/Derived Variables):**
    -   **粉丝投票 (Fan Votes):** **未知 (Latent)**.
    -   **综合得分 (Combined Score):** 评委分与粉丝票的聚合值.
    -   **评委总分 (Judge Total):** $\sum Score_{judge}$.
    -   **粉丝得票份额 (Fan Vote Share):** $V_{fan} / \sum V_{fan}$.

## 数据亮点 (2026_MCM_Problem_C_Data.csv) | Data Highlights
- 列名：选手信息、比赛成绩、名次、weekX_judgeY_score（每周每位评委评分）
- 评委评分范围1-10分；可能包含小数；包含加分
- N/A 表示无第4位评委或该周未进行
- 淘汰后评分设为0
- 各季节选手数和周次数不同

- Columns: contestant info, results, placement, and weekX_judgeY_score.
- Judges score 1-10; decimals possible; bonus points embedded.
- N/A means no 4th judge or week did not occur.
- Scores set to 0 after elimination.
- Different number of contestants and weeks per season.

## 各季节的假设投票规则（待确认）| Assumed Voting Rules by Season (to confirm)
- 第1-2季：排名法综合投票 (Rank Sum)
- 第3-27季：百分比法综合投票 (Percentage Sum)
- 第28-34季：排名法 + 最后两名的评委拯救权 (Rank Sum + Judge Save)

- Seasons 1-2: combined by rank.
- Seasons 3-27: combined by percent.
- Seasons 28-34: combined by rank and bottom-two judge save.

## 立即数据检查 | Immediate Data Checks
- [ ] 统计每季节的选手数和周次数 (Count contestants and weeks per season).
- [ ] 找出无淘汰的周次和多人淘汰的周次 (Identify weeks with no/multiple eliminations).
- [ ] 验证淘汰后评分是否为零 (Verify zero scores post-elimination).
- [ ] 验证缺失值（N/A）的模式 (Validate missing values patterns).
- [ ] 检查是否有分数为 0 但未被淘汰的异常情况.

## Gemini CLI 提示（问题提取）| Gemini CLI Prompt (Problem Extraction)
```
你是建模竞赛助手。从下面的2026 MCM/ICM C问题陈述中提取：
1) 目标和所需输出
2) 关键变量和约束
3) 数据描述和注意事项
4) 必须声明的隐含假设
5) 建模任务（按阶段分组）
6) 潜在的陷阱或歧义
```

## Gemini CLI 提示（数据集重点）| Gemini CLI Prompt (Dataset Focus)
```
给定2026_MCM_Problem_C_Data.csv的数据集描述，列出：
- 所需的预处理步骤
- 周/季节的边界情况
- 粉丝投票建模的衍生特征
- 建议的验证检查
```
