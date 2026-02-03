




























# Q1 模型对比实验使用指南

本目录包含Q1问题的四种回归模型对比实验。

## 快速开始

### 运行完整对比实验

```bash
cd solution/src
python run_model_comparison.py
```

这将：
1. 训练4个模型（Ridge, Lasso, Elastic Net, SVR）
2. 在测试集上评估性能
3. 生成对比可视化
4. 保存训练好的模型
5. 输出详细报告

**预计运行时间**: ~30秒

## 输出文件

所有输出保存在 `solution/figures/model_comparison/`:

### 可视化文件
- `model_performance_comparison.png/pdf` - 性能指标对比
- `training_time_comparison.png/pdf` - 训练时间对比
- `residual_distribution_comparison.png/pdf` - 残差分布对比
- `prediction_scatter_comparison.png/pdf` - 预测vs实际散点图

### 模型文件
- `trained_models/ridge_model.pkl`
- `trained_models/lasso_model.pkl`
- `trained_models/elasticnet_model.pkl`
- `trained_models/svr_model.pkl`

### 报告文件
- `model_comparison_report.txt` - 详细的文本报告

## 实验结果摘要

| 模型 | R² | RMSE | MAE | 训练时间 |
|------|-----|------|-----|----------|
| Ridge | 0.2079 | 1.6344 | 1.2715 | 0.27s |
| Lasso | 0.2084 | 1.6340 | 1.2698 | 0.15s |
| Elastic Net | 0.2084 | 1.6340 | 1.2698 | 0.30s |
| **SVR** | **0.2276** | **1.6141** | **1.2173** | 24.62s |

**结论**: SVR在所有指标上表现最佳，R²提升9.5%。

## 使用训练好的模型

```python
import pickle
import pandas as pd

# 加载模型
with open('figures/model_comparison/trained_models/svr_model.pkl', 'rb') as f:
    model = pickle.load(f)

# 加载数据
test_df = pd.read_csv('Data/processed/test_panel.csv')

# 准备特征
X_test, y_test, groups_test, test_valid = model.prepare_features(test_df)

# 预测
y_pred = model.predict(X_test)

# 评估
metrics = model.evaluate(X_test, y_test)
print(f"R² Score: {metrics['r2']:.4f}")
```

## 模型说明

### Ridge回归
- **特点**: L2正则化，保留所有特征
- **优势**: 训练快速，稳定性好
- **适用**: 基准模型，特征相关性高时表现好

### Lasso回归
- **特点**: L1正则化，自动特征选择
- **优势**: 产生稀疏解，可解释性强
- **适用**: 高维数据，需要特征选择

### Elastic Net
- **特点**: L1+L2混合正则化
- **优势**: 结合Ridge和Lasso优点
- **适用**: 特征相关且需要特征选择

### SVR (推荐)
- **特点**: 非线性回归（RBF核）
- **优势**: 性能最佳，对异常值鲁棒
- **适用**: 需要捕捉非线性关系

## 超参数优化

所有模型使用5-fold Group Cross-Validation进行超参数优化：

- **Ridge**: alpha ∈ [0.001, 1000]
- **Lasso**: alpha ∈ [0.0001, 10]
- **Elastic Net**: alpha ∈ [0.0001, 10], l1_ratio ∈ [0.1, 0.99]
- **SVR**: C ∈ [0.1, 100], epsilon ∈ [0.01, 0.2], gamma ∈ ['scale', 'auto', 0.001, 0.1]

## 特征重要性

根据Lasso特征选择结果：

1. **judge_rank_in_week** (系数: -0.7468) - 最重要
2. **relative_judge_score** (系数: 0.1815) - 重要
3. **cumulative_average** (系数: ~0) - 被剔除

## 相关文档

- `docs/14_q1_model_comparison_summary.md` - 详细实验总结
- `paper/论文改进计划-模型多样性与评估完整性.md` - 改进计划原文

## 依赖包

```
numpy
pandas
scikit-learn
matplotlib
seaborn
scipy
```

## 常见问题

**Q: 为什么SVR训练时间这么长？**
A: SVR使用RBF核进行非线性变换，计算复杂度较高。但对于本任务的数据规模（~3500样本），24秒的训练时间是可接受的。

**Q: 如何选择模型？**
A:
- 性能优先 → SVR
- 速度优先 → Lasso
- 可解释性优先 → Lasso或Ridge

**Q: 可以调整超参数吗？**
A: 可以。在 `run_model_comparison.py` 中修改模型初始化参数，或设置 `find_params=False` 使用自定义参数。

## 论文引用

在论文中引用此实验时，建议包含：
1. 模型对比表格（Table X）
2. 性能对比图（Figure X）
3. 特征重要性分析
4. SVR优势的解释（非线性关系）

---

**最后更新**: 2026-02-02
**状态**: ✅ 实验完成
