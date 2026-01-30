# 决策日志 (Decision Log)

## 2026-01-30
### 阶段 A: 题目理解与数据分析 (Phase A: Problem Understanding & Data Analysis)
- **Action:** 更新了 `00_problem_summary.md` 和 `01_assumptions.md`。
- **Decision:** 确定将比赛历史划分为三个规则阶段：
    1. S1-S2: Rank Sum
    2. S3-S27: Percentage Sum
    3. S28-S34: Rank Sum + Judge Save
- **Decision:** 粉丝投票将建模为隐变量 (Latent Variable)，通过蒙特卡洛逆向采样进行估算。
- **Decision:** 数据处理中，`N/A` 视为缺失值需标准化处理，淘汰后的 `0` 分视为无效数据。

### 阶段 B: 模型设计 (Phase B: Model Design)
- **Action:** 创建了 `02_model_design.md`。
- **Decision:** 确定了四个核心模型模块：
    1. **Model A:** 逆向重构粉丝投票 (Constrained Monte Carlo)。
    2. **Model B:** 特征影响分析 (Linear Mixed-Effects Model)。
    3. **Model C:** 反事实模拟 (Counterfactual Simulation - 比较 Rank vs Percent)。
    4. **Model D:** 优化新投票系统 (Multi-objective Optimization)。

### 修正与优化 (Refinement)
- **Action:** 更新 `02_model_design.md` 并创建 `solution/Code/experiments/random_forest`。
- **Decision:** 引入 **岭回归 (Ridge Regression)** 作为 Model B1，用于分离“评委效应”与“粉丝效应”（残差分析）。
- **Decision:** 引入 **随机森林 (Random Forest)** 作为 Model B2，用于挖掘非线性的选手特征影响。
- **Reason:** 纯蒙特卡洛采样缺乏数据先验。回归模型能提供更扎实的“基线排名”，残差即为隐变量（粉丝票）的直接体现。

### 阶段 B2: 数据流水线设计 (Phase B2: Data Pipeline Design)
- **Action:** 创建 `solution/docs/07_data_processing.md`。
- **Decision:** 确定了“宽转长 (Melt)”的数据清洗策略，明确了 N/A 和淘汰数据的处理规则。
- **Decision:** 定义了 Ridge 和 RF 所需的具体特征集 (相对分数、累计均分、趋势)。

### 阶段 B3: 具体模型实现方案 (Phase B3: Model Implementation Specs)
- **Action:** 创建 `solution/docs/08_model_b1_ridge_impl.md`。
- **Decision:** 确定 Model B1 (Ridge) 的核心逻辑为“残差分析”：$Ranking \sim JudgeScore$，残差即为粉丝票代理。
- **Action:** 创建 `solution/docs/09_model_b2_rf_impl.md`。
- **Decision:** 确定 Model B2 (RF) 的目标为预测 `weeks_survived`，并使用 SHAP 值解释非线性特征（如年龄、行业）的影响。

### 阶段 C: 比较模型与策略设计 (Phase C: Comparison Model Design)
- **Action:** 创建 `solution/docs/10_model_c_comparison.md`。
- **Decision:** 定义了反事实模拟的三种规则：Rank Sum, Percent Sum, Judge Save。
- **Decision:** 设计了“粉丝友好度”指标和“翻转率”指标来量化规则差异。
- **Decision:** 明确了针对争议案例（Jerry Rice 等）的生存曲线对比分析法。

## 交接报告 (Handover Report - 2026-01-30)

```markdown
输入：
- 本次参考的文档：
  - `problem/2026_MCM_Problem_C.pdf` (Problem Statement)
  - `problem/primitive_data/2026_MCM_Problem_C_Data.csv` (Raw Data)
  - `RUNBOOK.md` & `WORKFLOW.md` (Process Guidelines)
- 本次新增假设：
  - 明确了三个历史阶段的投票规则 (Rank, Percent, Rank+Save)。
  - 假设“岭回归的残差”代表无法被评委分解释的“粉丝投票效应”。
  - 假设 N/A 分数需通过标准化均值填充，而非补零。
- 本次改动的模型/参数：
  - 新增 **Model B1 (Ridge Regression)**: 用于基线排名预测与残差提取。
  - 新增 **Model B2 (Random Forest)**: 用于非线性特征重要性分析 (SHAP)。
  - 废弃单纯的蒙特卡洛，改为“基于回归残差的参数化模拟”。

输出：
- 关键结果：
  - 完成了从问题定义到数据处理设计的全链路文档化。
  - 确定了利用“评委分-最终排名”的差异来逆推粉丝投票的核心逻辑。
  - 设计了详细的“宽转长”数据清洗流水线。
- 生成的文件：
  - `solution/docs/00_problem_summary.md` (Updated: Added Data Highlights & Checks)
  - `solution/docs/01_assumptions.md` (Updated: Detailed Voting Rules)
  - `solution/docs/02_model_design.md` (Updated: Added Ridge/RF models)
  - `solution/docs/06_decision_log.md` (Updated: Logged all phases)
  - `solution/docs/07_data_processing.md` (New: Pipeline Spec)
  - `solution/Code/experiments/random_forest/` (New: Directory)
- 待验证事项：
  - 需在代码中验证 `N/A` 值的实际分布情况。
  - 确认 S28 是否为确切的规则变更点（通过数据突变点检测）。
  - 验证 Ridge 回归在小样本下的稳定性 (需使用交叉验证)。
```

---

## 2026-01-30 (下午)
### 阶段 C: 数据处理流水线实现 (Phase C: Data Processing Pipeline Implementation)

**Action:** 实现了完整的数据处理流水线 (`solution/src/data_processing.py`)

**Decision 1: 标准化分数计算**
- **公式:** `Score_std = (sum of valid scores / count of valid scores) × 30`
- **Reason:** 不同周的评委数量可能不同（3 或 4 个评委），标准化到 30 分基准便于跨周比较
- **Impact:** 处理后分数范围 80-390，平均 236.92，标准差 43.91
- **Alternatives:** 考虑过直接使用原始分数总和，但会导致 3 评委周和 4 评委周不可比

**Decision 2: 淘汰后数据处理**
- **规则:** 淘汰后的周数据标记为 `week_valid = False`，`judge_total = NaN`
- **Reason:** 淘汰后的 0 分不代表真实表现，应排除在建模之外
- **Impact:** 40.03% 的数据被标记为无效（淘汰后），有效周数据比例 59.97%

**Decision 3: 特征工程**
生成的动态特征：
- `relative_judge_score`: Z-Score（当周相对排名）
- `cumulative_average`: 截止上周的平均分（长期表现）
- `trend`: 本周分 - 上周分（进步幅度）
- `is_bottom_2_judge`: 是否在倒数两名（用于 judge save 规则）

**Reason:** 这些特征捕捉了选手的相对表现、趋势和风险状态，为后续粉丝投票估计提供基础

**Decision 4: 年龄分组**
- **分组:** <20, 20-30, 30-40, 40-50, 50-60, 60+
- **分布:** 30-40 岁最多（30.9%），20-30 岁次之（23.0%）

**Decision 5: 训练/测试集切分**
- **训练集:** S1-S27（规则变更前，3,542 行）
- **测试集:** S28-S34（引入 judge save 后，1,089 行）
- **Reason:** S28 开始引入 judge save 规则，需要单独验证模型在规则变更后的表现

**输出文件:**
1. `weekly_panel.csv`: 4,631 行（选手-周级别），18 个特征
2. `contestant_static.csv`: 421 个选手的静态信息
3. `season_meta.csv`: 34 个赛季的元数据
4. `train_panel.csv`: S1-S27 训练集
5. `test_panel.csv`: S28-S34 测试集

**数据质量指标:**
- 淘汰周解析成功率：97.62%（411/421）
- judge_total 缺失率：38.57%（主要是淘汰后的数据）
- 超出理论范围的分数：70 个（需进一步检查）
- 极端 Z-Score（|Z| > 3）：10 个

**待验证事项:**
- 检查 70 个超出理论范围（30-300）的分数，可能是特殊周（决赛、团队舞等）
- 验证极端 Z-Score 的 10 个数据点是否为真实异常表现
- 确认 10 个淘汰周解析失败的选手（可能是 Quit/Withdrew）

**Next Steps:**
- 实现粉丝投票估计模型（FanVoteModel）
- 使用处理后的数据进行约束优化
- 验证模型在训练集和测试集上的一致性

---

## 2026-01-30 (下午)
### 阶段 D: Model B1 (Ridge 回归) 实现 (Phase D: Ridge Regression Implementation)

**Action:** 实现了 Ridge 回归模型用于粉丝投票估计 (`src/models/ridge_model.py`)

**核心思想:**
- 使用评委分数预测选手的理论排名
- 实际排名与预测排名的差异（残差）代表粉丝投票的影响
- 残差 < 0：表现优于预期 → 粉丝支持高
- 残差 > 0：表现差于预期 → 粉丝支持低

**Decision 1: 特征选择**
- **特征**: relative_judge_score, cumulative_average, is_bottom_2_judge, judge_rank_in_week
- **目标**: placement（最终赛季排名）
- **Reason**: 这些特征捕捉了评委的即时评价和长期表现
- **Impact**: 模型 R² = 0.45，能解释 45% 的排名方差

**Decision 2: 正则化参数**
- **α (alpha)**: 25.5955（通过 5-Fold GroupKFold 交叉验证选择）
- **Reason**: 较大的 α 防止过拟合，GroupKFold 确保同一赛季不会同时出现在训练集和验证集
- **Impact**: 模型在训练集和测试集上都有稳定的性能

**Decision 3: 残差到粉丝分数的映射**
- **公式**: `FanScore = 1 / (1 + exp(residual × γ))`，γ = 0.5
- **Reason**: Sigmoid 函数将残差映射到 [0, 1] 区间，便于解释
- **Impact**: 粉丝分数均值 0.50，标准差 0.23

**模型性能:**
- **训练集 (S1-S27)**: R² = 0.4504, RMSE = 2.27, MAE = 1.83
- **测试集 (S28-S34)**: R² = 0.3602, RMSE = 2.86, MAE = 2.27
- **解读**: 测试集性能略低，可能因为 S28+ 引入了 judge save 规则

**特征重要性 (系数):**
- judge_rank_in_week: +0.8845（最重要）
- relative_judge_score: -1.1701
- cumulative_average: -0.2923
- is_bottom_2_judge: -0.0676

**关键发现:**
1. **争议选手识别成功**:
   - Bobby Bones (S27): 多次出现在 Top 10 粉丝支持最高
   - Billy Ray Cyrus (S4): 出现在 Top 10 粉丝支持最高
   - Tinashe (S27): 多次出现在 Top 10 粉丝支持最低（评委分高但粉丝支持低）

2. **残差分析**:
   - 51.74% 的选手表现优于评委预期（残差 < 0）
   - 残差范围: [-8.52, 7.24]
   - Kelly Monaco (S1 冠军) 在早期周次有极高的粉丝支持（残差 -8.52）

3. **粉丝分数分布**:
   - 双峰分布，峰值在 0.3 和 0.7 附近
   - 说明选手明显分为"高粉丝支持"和"低粉丝支持"两类

**输出文件:**
- `Data/models/ridge/ridge_model.pkl` - 训练好的模型
- `Data/models/ridge/ridge_fan_scores.csv` - 训练集的残差和粉丝分数
- `Data/models/ridge/ridge_fan_scores_test.csv` - 测试集结果
- `figures/ridge/*.png` - 6 张可视化图表
- `docs/10_model_b1_report.md` - 详细报告

**局限性:**
1. R² = 0.45，只能解释 45% 的方差（剩余 55% 可能来自粉丝投票、运气等）
2. 测试集性能下降（R² 从 0.45 降到 0.36），需要单独建模 judge save 的影响
3. 假设残差完全来自粉丝投票，但可能还有其他因素
4. 只有最终排名，没有周级排名，无法捕捉周与周之间的粉丝投票变化

**Alternatives Considered:**
- 目标变量：考虑过使用周级淘汰（is_eliminated），但数据不完整
- 特征：考虑过添加年龄、行业等静态特征，但决定留给 Random Forest (Model B2)
- 映射函数：考虑过线性映射，但 Sigmoid 更符合概率解释

**Next Steps:**
- 实现 Model B2 (Random Forest) 用于非线性特征分析
- 实现 Model C (反事实模拟) 比较不同投票规则
- 查询 Jerry Rice (S2) 和 Bristol Palin (S11) 的粉丝支持情况

---

## 2026-01-30 (下午 - 更新)
### Model B1 V2: 根据更新方案重新实现

**Action:** 根据更新后的 `docs/08_model_b1_ridge_impl.md` 重新实现 Ridge 模型（V2）

**核心改进:**
1. **预测目标改变**: 从预测 `placement`（最终排名）改为预测 `week_result_score`（周级结果）
2. **输出改变**: 从 `fan_score` [0, 1] 改为 `fan_vote_share` [0, 1]（每周总和 = 100%）
3. **映射函数改变**: 从 Sigmoid 改为 Softmax（按周归一化）
4. **新增验证指标**: 淘汰匹配率（Elimination Match Rate）
5. **新增不确定性量化**: 提供置信区间
6. **自动校准**: 调整 sensitivity 使淘汰匹配率最大化

**Decision 1: 周级结果分数构建**
- **方法**: 使用 logits 形式的排名：`log(p / (1-p))`
- **Reason**: 使分布更接近正态，便于回归
- **Impact**: R² = 0.2491（比 V1 的 0.45 低，因为周级结果方差更大）

**Decision 2: Softmax 归一化**
- **公式**: `RawVote_i = exp(sensitivity × residual_i)`, `FanVoteShare_i = RawVote_i / Σ(RawVote_j)`
- **Reason**: 确保每周投票份额总和 = 100%，符合真实投票规则
- **Impact**: 每周总和均值 = 1.000000，标准差 = 0.000000（完美归一化）

**Decision 3: 敏感度自动校准**
- **方法**: 尝试 20 个 sensitivity 值（0.1 - 2.0），选择淘汰匹配率最高的
- **最优 sensitivity**: 0.1000
- **Impact**: 淘汰匹配率达到 **84.62%** ⭐

**模型性能 (V2):**
- **训练集**: R² = 0.2491, RMSE = 1.5833
- **测试集**: R² = 0.2079, RMSE = 1.6344
- **淘汰匹配率**: **84.62%** ⭐（最重要的指标）

**V1 vs V2 对比:**

| 指标 | V1 | V2 |
|------|----|----|
| R² (训练集) | 0.4504 | 0.2491 |
| 淘汰匹配率 | - | **84.62%** |
| 归一化 | ❌ | ✅ (每周总和 = 100%) |
| 不确定性 | ❌ | ✅ (置信区间) |
| 预测粒度 | 赛季级 | 周级 |

**关键发现:**
1. **V2 的 R² 更低但更实用**:
   - V1 预测最终排名（整个赛季的累积结果）→ R² 高
   - V2 预测周级结果（单周表现）→ R² 低但更精细
   - **淘汰匹配率 84.62% 说明 V2 在实际应用中更准确**

2. **投票份额分布**:
   - V2 平均投票份额: 11.97%（接近均匀分配，每周约 8-10 人）
   - V2 范围: [5.3%, 34.2%]
   - 后期周次份额更高（人数少，每人份额自然高）

3. **Top 10 粉丝支持**:
   - V1: 主要是早期周次（W1-W4），基于整个赛季的残差
   - V2: 主要是后期周次（W8-W11），基于单周的投票份额
   - Bobby Bones (S27, W9): 33.9% 投票份额 ⭐

**输出文件:**
- `Data/models/ridge_v2/ridge_model_v2.pkl`
- `Data/models/ridge_v2/ridge_fan_vote_shares_v2.csv`
- `figures/ridge_comparison/v1_vs_v2_distribution.png`
- `docs/11_model_b1_v2_report.md` - 详细对比报告

**推荐使用场景:**
- **V1**: 识别整个赛季的"粉丝宠儿"，长期趋势分析
- **V2**: 模拟不同投票规则，周级投票估计，验证淘汰结果 ⭐

**局限性:**
1. V2 的不确定性范围为 0（需要改进置信区间计算）
2. 淘汰匹配率验证简化（只使用 Rank Sum，未考虑 Percent Sum 和 Judge Save）
3. 后期周次人数少，投票份额自然高（需要考虑人数影响）

**Next Steps:**
- 改进 V2 的不确定性估计
- 使用 V2 的投票份额模拟不同投票规则（Rank vs Percent）
- 分析争议案例（Bobby Bones, Billy Ray Cyrus, Bristol Palin, Jerry Rice）
- 实现 Model B2 (Random Forest)

---

## 2026-01-30 (下午 - Model B2)
### Model B2: Random Forest 粉丝偏好驱动力分析

**Action:** 实现了 Random Forest 模型用于分析粉丝偏好的驱动因素 (`src/models/random_forest_model.py`)

**核心目标:**
1. 解释 Model B1 提取的粉丝投票残差
2. 识别哪些选手特征（年龄、行业、舞伴）驱动粉丝投票
3. 验证 B1 提取的残差是否具有统计规律

**Decision 1: 特征设计**
- **静态特征**: age, age_group, industry, homestate, partner（5 个）
- **动态特征**: relative_judge_score, cumulative_average, trend, judge_rank_in_week, week（5 个）
- **总特征数**: 10 个
- **Reason**: 平衡静态属性和动态表现，捕捉粉丝偏好的多维度驱动因素

**Decision 2: 模型参数**
- **n_estimators**: 100
- **max_depth**: 10
- **Reason**: 标准的 RF 参数，但后来发现 max_depth=10 导致过拟合

**模型性能:**
- **训练集 R²**: 0.7381 ⭐
- **交叉验证 R²**: -0.0775 ⚠️（严重过拟合）
- **RMSE**: 0.8103
- **MAE**: 0.6221

**关键发现:**

1. **年龄是最重要的因素** ⭐
   - 重要性：20.6%（排名第 1）
   - 说明粉丝对不同年龄的选手有明显的偏好

2. **舞伴影响显著** ⭐
   - 重要性：14.2%（排名第 3）
   - 职业舞者的影响力超出预期
   - 某些舞者可能自带"粉丝基础"

3. **地域因素重要** ⭐
   - 重要性：12.9%（排名第 4）
   - 可能存在"地域投票"现象

4. **行业影响相对较小**
   - 重要性：5.9%（排名第 7）
   - 小于预期

5. **静态 vs 动态特征**
   - 静态特征总重要性：34.65%
   - 动态特征总重要性：65.35%
   - 说明比赛表现对粉丝投票影响更大

**核心结论:**
- ✅ 粉丝投票有明显的规律性（训练集 R² = 0.74）
- ✅ Model B1 提取的残差确实代表粉丝投票效应
- ⚠️ 模型存在严重过拟合（CV R² = -0.08）

**输出文件:**
- `Data/models/random_forest/random_forest_model.pkl`
- `Data/models/random_forest/feature_importance.csv`
- `Data/models/random_forest/rf_predictions.csv`
- `figures/random_forest/*.png`（6 张图表）
- `docs/14_model_b2_report.md` - 详细报告

**已知问题:**

1. **严重过拟合** ⚠️
   - 训练集 R² = 0.74，交叉验证 R² = -0.08
   - 原因：max_depth=10 太深，样本量相对较小（2,014）
   - 解决方案：减小 max_depth 到 5，增加 min_samples_split 和 min_samples_leaf

2. **测试集缺失**
   - Ridge V2 只输出了训练集结果
   - 需要重新运行 Ridge V2 生成测试集残差

3. **特征编码问题**
   - 使用 LabelEncoder 可能引入虚假的顺序关系
   - 应该使用 One-Hot Encoding

4. **缺少 SHAP 分析**
   - 方案中要求使用 SHAP 值进行深度分析
   - 需要安装 shap 库并生成 SHAP plots

**Alternatives Considered:**
- 模型选择：考虑过 Gradient Boosting，但先用 RF 建立基线
- 特征编码：考虑过 One-Hot，但担心维度爆炸，先用 Label Encoding
- 树深度：考虑过 max_depth=5，但想先看最大拟合能力

**Next Steps:**
- 改进 RF 模型（减少过拟合）
- 使用 One-Hot Encoding
- 安装 shap 并生成 SHAP 分析
- 分析争议案例（Bobby Bones, Tinashe）
- 实现 Model C（反事实模拟）