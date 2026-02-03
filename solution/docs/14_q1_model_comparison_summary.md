# Q1 模型对比实验总结

**实验日期**: 2026-02-02
**实验目的**: 根据论文改进计划，增加对比模型以增强模型多样性评估

---

## 1. 实验设计

### 1.1 对比模型

根据改进计划，实现了以下四种回归模型：

1. **Ridge回归** (基准模型)
   - L2正则化
   - 保留所有特征，系数收缩
   - 训练速度快，稳定性好

2. **Lasso回归**
   - L1正则化
   - 特征选择能力（产生稀疏解）
   - 自动识别重要特征

3. **Elastic Net**
   - L1+L2混合正则化
   - 结合Ridge和Lasso优点
   - 在相关特征存在时更稳定

4. **SVR (Support Vector Regression)**
   - 非线性回归能力（RBF核）
   - 对异常值鲁棒
   - 可捕捉复杂非线性关系

### 1.2 实验设置

- **特征**:
  - `relative_judge_score`: 相对评委分数（Z-Score标准化）
  - `judge_rank_in_week`: 评委排名
  - `cumulative_average`: 累积平均分

- **目标变量**: `week_result_score` (周级结果分数，logits形式)

- **数据划分**:
  - 训练集: 3542 观测
  - 测试集: 1089 观测

- **超参数优化**: 5-fold Group Cross-Validation (按season分组)

- **评估指标**: R², RMSE, MAE

---

## 2. 实验结果

### 2.1 测试集性能对比

| 模型 | R² Score | RMSE | MAE | 训练时间 |
|------|----------|------|-----|----------|
| **Ridge** | 0.2079 | 1.6344 | 1.2715 | 0.27s |
| **Lasso** | 0.2084 | 1.6340 | 1.2698 | 0.15s |
| **Elastic Net** | 0.2084 | 1.6340 | 1.2698 | 0.30s |
| **SVR** | **0.2276** | **1.6141** | **1.2173** | 24.62s |

**关键发现**:
- **SVR在所有评估指标上均表现最佳**
  - R²提升: 0.2276 vs 0.2079 (Ridge基准) = +9.5%
  - RMSE降低: 1.6141 vs 1.6344 = -1.2%
  - MAE降低: 1.2173 vs 1.2715 = -4.3%

- **线性模型性能相近**
  - Ridge, Lasso, Elastic Net三者性能几乎相同
  - 说明特征之间相关性不强，L1正则化的特征选择优势不明显

- **训练时间权衡**
  - Lasso最快 (0.15s)
  - SVR最慢 (24.62s)，但性能提升显著

### 2.2 特征重要性分析

#### Ridge回归系数
```
relative_judge_score:  0.2123
judge_rank_in_week:   -0.7401  (最重要)
cumulative_average:   -0.0209
Intercept:             0.5239
```

#### Lasso回归系数（特征选择）
```
relative_judge_score:  0.1815
judge_rank_in_week:   -0.7468  (最重要)
cumulative_average:   -0.0000  (被剔除)
非零特征数: 2/3
```

**解读**:
- `judge_rank_in_week` 是最重要的特征（系数绝对值最大）
- Lasso自动剔除了 `cumulative_average`，说明其预测能力较弱
- `relative_judge_score` 保留，说明标准化后的评委分数有一定预测价值

### 2.3 SVR模型特点

- **最优超参数**: C=1.0, epsilon=0.01, gamma='scale'
- **支持向量数**: 2004 / 2014 = 99.5%
- **非线性能力**: RBF核能够捕捉特征之间的非线性交互

---

## 3. 可视化结果

生成的可视化文件位于 `solution/figures/model_comparison/`:

1. **model_performance_comparison.png/pdf**
   - 三个指标的柱状图对比
   - 清晰展示SVR的性能优势

2. **training_time_comparison.png/pdf**
   - 训练时间对比
   - SVR训练时间显著高于线性模型

3. **residual_distribution_comparison.png/pdf**
   - 四个模型的残差分布
   - 所有模型残差近似正态分布

4. **prediction_scatter_comparison.png/pdf**
   - 预测值 vs 实际值散点图
   - SVR的R²最高，拟合效果最好

---

## 4. 结论与建议

### 4.1 模型选择建议

**推荐模型**: **SVR (Support Vector Regression)**

**理由**:
1. ✅ 在所有评估指标上均表现最佳
2. ✅ 非线性建模能力强，能捕捉复杂关系
3. ✅ 对异常值鲁棒
4. ⚠️ 训练时间较长（24.62s），但对于本任务规模可接受

**备选模型**: **Lasso回归**

**理由**:
1. ✅ 训练速度最快（0.15s）
2. ✅ 自动特征选择，模型可解释性强
3. ✅ 性能与Ridge接近
4. ⚠️ 性能略低于SVR

### 4.2 论文写作建议

根据改进计划，在论文中应包含以下内容：

#### Section 4.2 模型对比实验

**内容结构**:
```
4.2.1 对比模型介绍
  - Ridge, Lasso, Elastic Net, SVR的原理和特点
  - 超参数优化方法

4.2.2 实验设置
  - 数据划分
  - 特征工程
  - 评估指标

4.2.3 结果分析
  - 性能对比表格（Table X）
  - 特征重要性分析
  - 残差分布对比（Figure X）
  - 预测散点图（Figure X）

4.2.4 模型选择
  - SVR性能最优的原因分析
  - 非线性关系的发现
  - 计算复杂度权衡
```

**关键论点**:
1. **模型多样性**: 对比了线性（Ridge, Lasso, Elastic Net）和非线性（SVR）模型
2. **性能提升**: SVR相比线性模型R²提升9.5%
3. **特征洞察**: Lasso特征选择表明 `judge_rank_in_week` 最重要
4. **非线性关系**: SVR的优势说明评委分数与粉丝投票存在非线性关系

### 4.3 后续工作

1. **集成学习**: 可尝试Random Forest, Gradient Boosting等集成方法
2. **深度学习**: 对于更大规模数据，可尝试神经网络
3. **特征工程**: 基于Lasso的特征选择结果，可进一步优化特征集
4. **交叉验证**: 可增加更多fold数以获得更稳定的性能估计

---

## 5. 文件清单

### 5.1 代码文件

- `src/models/comparison_models.py`: Lasso, Elastic Net, SVR模型实现
- `src/run_model_comparison.py`: 对比实验主脚本

### 5.2 输出文件

**模型文件** (`figures/model_comparison/trained_models/`):
- `ridge_model.pkl`
- `lasso_model.pkl`
- `elasticnet_model.pkl`
- `svr_model.pkl`

**可视化文件** (`figures/model_comparison/`):
- `model_performance_comparison.png/pdf`
- `training_time_comparison.png/pdf`
- `residual_distribution_comparison.png/pdf`
- `prediction_scatter_comparison.png/pdf`

**报告文件**:
- `model_comparison_report.txt`: 详细的文本报告

---

## 6. 与改进计划的对应

根据 `论文改进计划-模型多样性与评估完整性.md`:

### ✅ 已完成

- [x] **Q1.1**: 实现Lasso回归模型
- [x] **Q1.2**: 实现Elastic Net模型
- [x] **Q1.3**: 实现SVR模型
- [x] **Q1.4**: 统一的对比实验框架
- [x] **Q1.5**: 超参数优化（交叉验证）
- [x] **Q1.6**: 性能对比可视化
- [x] **Q1.7**: 详细的对比报告

### 📊 实验结果符合预期

- 模型多样性增强：线性 + 非线性
- 性能评估完整：R², RMSE, MAE, 训练时间
- 可视化丰富：4种对比图表
- 结论明确：SVR表现最佳

---

## 附录：代码示例

### 使用训练好的模型进行预测

```python
import pickle
import pandas as pd

# 加载模型
with open('figures/model_comparison/trained_models/svr_model.pkl', 'rb') as f:
    svr_model = pickle.load(f)

# 准备数据
test_df = pd.read_csv('Data/processed/test_panel.csv')
X_test, y_test, groups_test, test_valid = svr_model.prepare_features(test_df)

# 预测
y_pred = svr_model.predict(X_test)

# 评估
metrics = svr_model.evaluate(X_test, y_test)
print(f"R² Score: {metrics['r2']:.4f}")
```

---

**实验完成时间**: 2026-02-02
**实验负责人**: Claude Code
**状态**: ✅ 完成
