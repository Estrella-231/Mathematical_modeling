# 数据处理详细设计 (Data Processing Design)

## 1. 原始数据概览 (Raw Data Overview)
*   **Source:** `problem/primitive_data/2026_MCM_Problem_C_Data.csv`
*   **Key Columns:**
    *   `season` (Int): 1-34.
    *   `week` (Implicit): Embedded in column names (e.g., `week1_judge1_score`).
    *   `celebrity_name` (String): Unique identifier (mostly).
    *   `results` (String): e.g., "Eliminated Week 3", "1st Place".
    *   `placement` (Int): Final rank (1 = Winner).
    *   `judge_scores` (Float/String): `week[1-11]_judge[1-4]_score`. Values: 1-10, `N/A`.

## 2. 清洗规则 (Cleaning Rules)

### 2.1 评分矩阵 (Scoring Matrix)
*   **N/A 处理:**
    *   若某周某评委分为 `N/A` (如第4评委缺席)，不填补零，而是计算该周**有效评分的平均值**并乘以标准评委数 (3或4) 进行归一化，或直接使用 `mean(valid_scores)`。
    *   *Decision:* 使用 **标准化总分 (Standardized Total Score)**。
        $$ Score_{std} = \frac{\sum ValidScores}{\text{Count}(ValidScores)} \times 30 $$ (假设标准为3评委满分30，方便跨周比较)
*   **淘汰后处理:**
    *   一旦 `results` 指示 "Eliminated Week X"，该选手在 Week > X 的所有分数应设为 `NaN` (非零)，在统计时排除。
    *   原始数据中淘汰后的 `0` 分将被替换为 `NaN`。

### 2.2 结果解析 (Result Parsing)
需要从 `results` 文本字段解析出具体的 `elimination_week`。
*   "Eliminated Week X" -> `eliminated = X`
*   "X Place" (1st, 2nd, 3rd) -> `eliminated = MaxWeeks` (决赛周)
*   "Quit" / "Withdrew" -> 需特殊标记，视为非正常淘汰。

## 3. 特征工程 (Feature Engineering)

为岭回归 (Ridge) 和随机森林 (RF) 准备的特征集。

### 3.1 静态特征 (Static Features - Per Contestant)
*   `is_pro`: (Boolean) 暂无直接数据，需外部列表或忽略。
*   `gender`: (Categorical) 需从名字推断或外部补充 (本题仅限 CSV，可能需忽略或手动标注)。
*   `industry_category`: (Categorical) `celebrity_industry`. One-Hot Encoding.
*   `age_group`: (Categorical) Binning `celebrity_age_during_season` (e.g., <20, 20-30, ...).

### 3.2 动态特征 (Dynamic Features - Per Week)
*   `raw_judge_score`: 当周评委总分。
*   `relative_judge_score`: 当周评委分与当周所有选手平均分的差值 (Z-Score)。
    $$ Z_{i,t} = \frac{Score_{i,t} - \mu_t}{\sigma_t} $$
*   `rank_judge`: 当周评委给出的排名 (1, 2, ...).
*   `cumulative_average`: 截止到上周的平均评委分 (反映长期表现)。
*   `trend`: 本周分 - 上周分 (反映进步幅度)。
*   `is_bottom_2_judge`: (Boolean) 是否在评委分的倒数两名内。

### 3.3 目标变量 (Target Variables)
*   **For Regression:** `final_placement` (1, 2, ...).
*   **For Survival Analysis:** `is_eliminated_this_week` (0/1).
*   **For Latent Inference:** `implied_fan_rank_gap` = `rank_judge` - `rank_final` (正值表示评委分低但排名高 -> 粉丝多)。

## 4. 处理流水线 (Processing Pipeline)

### Step 1: Melt (宽转长)
将 `weekX_judgeY_score` 转换为长格式：
`[season, celebrity_name, week, judge_id, score]`

### Step 2: Aggregation (周级聚合)
计算每人每周的：
*   `judge_total`
*   `judge_rank_in_week` (Dense Rank)
*   `week_valid` (Boolean, if scores > 0)

### Step 3: Meta Join (合并元数据)
Join `celebrity_industry`, `age`, `placement` back to the weekly dataframe.

### Step 4: Feature Generation (生成衍生特征)
应用 3.2 中的公式计算 `relative_judge_score`, `cumulative_average` 等。

### Step 5: Split (数据集切分)
*   `Train Set`: S1-S27 (用于训练回归模型)
*   `Test Set`: S28-S34 (用于验证模型在规则变更后的表现)
*   *或者:* 随机 K-Fold (如果样本量太少)。

## 5. 输出文件规范 (Output Specification)
处理后的数据将保存至 `solution/Data/processed/`：
1.  `weekly_panel.csv`: 核心面板数据 (Row = Contestant-Week).
2.  `contestant_static.csv`: 选手级汇总数据 (Row = Contestant).
3.  `season_meta.csv`: 赛季级元数据 (周数、人数).
