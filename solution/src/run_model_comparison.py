"""
Q1模型对比实验
比较Ridge、Lasso、Elastic Net和SVR四种回归模型的性能

实验设计：
1. 使用相同的训练/测试集划分
2. 对每个模型进行超参数优化
3. 评估预测性能（R2, RMSE, MAE）
4. 生成对比可视化
5. 输出详细的对比报告
"""

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
import pickle
import time

# 导入模型
from models.ridge_model_v2 import RidgeFanVoteModelV2
from models.comparison_models import LassoFanVoteModel, ElasticNetFanVoteModel, SVRFanVoteModel

# 配置matplotlib
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['figure.titlesize'] = 14


def load_data():
    """加载训练和测试数据"""
    data_dir = Path(__file__).parent.parent / 'Data' / 'processed'

    train_df = pd.read_csv(data_dir / 'train_panel.csv')
    test_df = pd.read_csv(data_dir / 'test_panel.csv')

    print(f"训练集: {len(train_df)} 观测")
    print(f"测试集: {len(test_df)} 观测")

    return train_df, test_df


def train_all_models(train_df):
    """训练所有对比模型"""
    models = {}
    training_times = {}

    # 1. Ridge回归（基准模型）
    print("\n" + "="*80)
    print("模型 1/4: Ridge 回归")
    print("="*80)
    start_time = time.time()
    ridge_model = RidgeFanVoteModelV2(sensitivity=1.0)
    X_train, y_train, groups_train, train_valid = ridge_model.prepare_features(train_df)
    ridge_model.fit(X_train, y_train, groups_train, find_alpha=True)
    training_times['Ridge'] = time.time() - start_time
    models['Ridge'] = (ridge_model, X_train, y_train, groups_train, train_valid)

    # 2. Lasso回归
    print("\n" + "="*80)
    print("模型 2/4: Lasso 回归")
    print("="*80)
    start_time = time.time()
    lasso_model = LassoFanVoteModel(sensitivity=1.0)
    X_train, y_train, groups_train, train_valid = lasso_model.prepare_features(train_df)
    lasso_model.fit(X_train, y_train, groups_train, find_alpha=True)
    training_times['Lasso'] = time.time() - start_time
    models['Lasso'] = (lasso_model, X_train, y_train, groups_train, train_valid)

    # 3. Elastic Net回归
    print("\n" + "="*80)
    print("模型 3/4: Elastic Net 回归")
    print("="*80)
    start_time = time.time()
    enet_model = ElasticNetFanVoteModel(sensitivity=1.0)
    X_train, y_train, groups_train, train_valid = enet_model.prepare_features(train_df)
    enet_model.fit(X_train, y_train, groups_train, find_params=True)
    training_times['ElasticNet'] = time.time() - start_time
    models['ElasticNet'] = (enet_model, X_train, y_train, groups_train, train_valid)

    # 4. SVR
    print("\n" + "="*80)
    print("模型 4/4: SVR (Support Vector Regression)")
    print("="*80)
    start_time = time.time()
    svr_model = SVRFanVoteModel(sensitivity=1.0)
    X_train, y_train, groups_train, train_valid = svr_model.prepare_features(train_df)
    svr_model.fit(X_train, y_train, groups_train, find_params=True)
    training_times['SVR'] = time.time() - start_time
    models['SVR'] = (svr_model, X_train, y_train, groups_train, train_valid)

    return models, training_times


def evaluate_all_models(models, test_df):
    """在测试集上评估所有模型"""
    results = {}

    print("\n" + "="*80)
    print("测试集评估")
    print("="*80)

    for model_name, (model, _, _, _, _) in models.items():
        print(f"\n[{model_name}]")

        # 准备测试数据
        X_test, y_test, groups_test, test_valid = model.prepare_features(test_df)

        # 评估
        metrics = model.evaluate(X_test, y_test, groups_test)

        print(f"  - R2 Score: {metrics['r2']:.4f}")
        print(f"  - RMSE: {metrics['rmse']:.4f}")
        print(f"  - MAE: {metrics['mae']:.4f}")

        results[model_name] = {
            'metrics': metrics,
            'X_test': X_test,
            'y_test': y_test,
            'groups_test': groups_test,
            'test_valid': test_valid
        }

    return results


def create_comparison_visualizations(models, results, training_times, output_dir):
    """创建对比可视化"""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 性能对比柱状图
    print("\n[可视化 1/4] 性能对比柱状图...")
    create_performance_comparison(results, output_dir)

    # 2. 训练时间对比
    print("[可视化 2/4] 训练时间对比...")
    create_training_time_comparison(training_times, output_dir)

    # 3. 残差分布对比
    print("[可视化 3/4] 残差分布对比...")
    create_residual_comparison(models, results, output_dir)

    # 4. 预测vs实际散点图
    print("[可视化 4/4] 预测vs实际对比...")
    create_prediction_scatter(models, results, output_dir)


def create_performance_comparison(results, output_dir):
    """性能指标对比柱状图"""
    metrics_df = pd.DataFrame({
        model_name: result['metrics']
        for model_name, result in results.items()
    }).T

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=300)

    metrics_to_plot = ['r2', 'rmse', 'mae']
    titles = ['R² Score (Higher is Better)', 'RMSE (Lower is Better)', 'MAE (Lower is Better)']
    colors = ['#2ecc71', '#e74c3c', '#f39c12']

    for ax, metric, title, color in zip(axes, metrics_to_plot, titles, colors):
        values = metrics_df[metric].values
        models = metrics_df.index.values

        bars = ax.bar(models, values, color=color, alpha=0.7, edgecolor='black', linewidth=1.2)

        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.4f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_ylabel(metric.upper(), fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

        # 旋转x轴标签
        ax.set_xticklabels(models, rotation=45, ha='right')

    plt.suptitle('Model Performance Comparison on Test Set', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    plt.savefig(output_dir / 'model_performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'model_performance_comparison.pdf', bbox_inches='tight')
    plt.close()


def create_training_time_comparison(training_times, output_dir):
    """训练时间对比"""
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    models = list(training_times.keys())
    times = list(training_times.values())

    bars = ax.bar(models, times, color='#3498db', alpha=0.7, edgecolor='black', linewidth=1.2)

    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.2f}s',
               ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_ylabel('Training Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Model Training Time Comparison', fontsize=13, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(output_dir / 'training_time_comparison.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'training_time_comparison.pdf', bbox_inches='tight')
    plt.close()


def create_residual_comparison(models, results, output_dir):
    """残差分布对比"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=300)
    axes = axes.flatten()

    for idx, (model_name, (model, _, _, _, _)) in enumerate(models.items()):
        ax = axes[idx]

        X_test = results[model_name]['X_test']
        y_test = results[model_name]['y_test']

        residuals, y_pred = model.compute_residuals(X_test, y_test)

        # 绘制残差直方图
        ax.hist(residuals, bins=50, color='steelblue', alpha=0.7, edgecolor='black')

        # 添加正态分布拟合
        mu, std = residuals.mean(), residuals.std()
        x = np.linspace(residuals.min(), residuals.max(), 100)
        from scipy.stats import norm
        ax.plot(x, norm.pdf(x, mu, std) * len(residuals) * (residuals.max() - residuals.min()) / 50,
               'r-', linewidth=2, label=f'Normal(μ={mu:.3f}, σ={std:.3f})')

        ax.set_xlabel('Residuals', fontsize=11, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax.set_title(f'{model_name} - Residual Distribution', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3, linestyle='--')

    plt.suptitle('Residual Distribution Comparison', fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()

    plt.savefig(output_dir / 'residual_distribution_comparison.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'residual_distribution_comparison.pdf', bbox_inches='tight')
    plt.close()


def create_prediction_scatter(models, results, output_dir):
    """预测vs实际散点图"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12), dpi=300)
    axes = axes.flatten()

    for idx, (model_name, (model, _, _, _, _)) in enumerate(models.items()):
        ax = axes[idx]

        X_test = results[model_name]['X_test']
        y_test = results[model_name]['y_test']
        y_pred = model.predict(X_test)

        # 散点图
        ax.scatter(y_test, y_pred, alpha=0.5, s=20, color='steelblue', edgecolors='black', linewidth=0.5)

        # 添加y=x参考线
        min_val = min(y_test.min(), y_pred.min())
        max_val = max(y_test.max(), y_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')

        # 计算R2
        r2 = results[model_name]['metrics']['r2']

        ax.set_xlabel('Actual Values', fontsize=11, fontweight='bold')
        ax.set_ylabel('Predicted Values', fontsize=11, fontweight='bold')
        ax.set_title(f'{model_name} (R² = {r2:.4f})', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3, linestyle='--')
        ax.set_aspect('equal', adjustable='box')

    plt.suptitle('Predicted vs Actual Values Comparison', fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()

    plt.savefig(output_dir / 'prediction_scatter_comparison.png', dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / 'prediction_scatter_comparison.pdf', bbox_inches='tight')
    plt.close()


def generate_comparison_report(models, results, training_times, output_dir):
    """生成详细的对比报告"""
    report_path = output_dir / 'model_comparison_report.txt'

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("Q1 模型对比实验报告\n")
        f.write("="*80 + "\n\n")

        f.write("实验设置:\n")
        f.write("-" * 80 + "\n")
        f.write("- 对比模型: Ridge, Lasso, Elastic Net, SVR\n")
        f.write("- 特征: relative_judge_score, judge_rank_in_week, cumulative_average\n")
        f.write("- 评估指标: R2, RMSE, MAE\n")
        f.write("- 超参数优化: 5-fold Group Cross-Validation\n\n")

        f.write("="*80 + "\n")
        f.write("1. 测试集性能对比\n")
        f.write("="*80 + "\n\n")

        # 创建性能对比表格
        metrics_df = pd.DataFrame({
            model_name: result['metrics']
            for model_name, result in results.items()
        }).T

        f.write(metrics_df.to_string() + "\n\n")

        # 找出最佳模型
        best_r2_model = metrics_df['r2'].idxmax()
        best_rmse_model = metrics_df['rmse'].idxmin()
        best_mae_model = metrics_df['mae'].idxmin()

        f.write("最佳模型:\n")
        f.write(f"  - R2 Score: {best_r2_model} ({metrics_df.loc[best_r2_model, 'r2']:.4f})\n")
        f.write(f"  - RMSE: {best_rmse_model} ({metrics_df.loc[best_rmse_model, 'rmse']:.4f})\n")
        f.write(f"  - MAE: {best_mae_model} ({metrics_df.loc[best_mae_model, 'mae']:.4f})\n\n")

        f.write("="*80 + "\n")
        f.write("2. 训练时间对比\n")
        f.write("="*80 + "\n\n")

        for model_name, train_time in training_times.items():
            f.write(f"  - {model_name}: {train_time:.2f} seconds\n")

        fastest_model = min(training_times, key=training_times.get)
        f.write(f"\n最快模型: {fastest_model} ({training_times[fastest_model]:.2f}s)\n\n")

        f.write("="*80 + "\n")
        f.write("3. 模型特点总结\n")
        f.write("="*80 + "\n\n")

        f.write("Ridge回归:\n")
        f.write("  - L2正则化，防止过拟合\n")
        f.write("  - 保留所有特征，系数收缩\n")
        f.write("  - 训练速度快，稳定性好\n\n")

        f.write("Lasso回归:\n")
        f.write("  - L1正则化，特征选择\n")
        f.write("  - 可产生稀疏解，自动识别重要特征\n")
        f.write("  - 适合高维数据\n\n")

        f.write("Elastic Net:\n")
        f.write("  - L1+L2混合正则化\n")
        f.write("  - 结合Ridge和Lasso优点\n")
        f.write("  - 在相关特征存在时更稳定\n\n")

        f.write("SVR:\n")
        f.write("  - 非线性回归能力（RBF核）\n")
        f.write("  - 对异常值鲁棒\n")
        f.write("  - 可捕捉复杂非线性关系\n\n")

        f.write("="*80 + "\n")
        f.write("4. 结论与建议\n")
        f.write("="*80 + "\n\n")

        # 综合评估
        if best_r2_model == best_rmse_model == best_mae_model:
            f.write(f"推荐模型: {best_r2_model}\n")
            f.write(f"  - 在所有评估指标上均表现最佳\n")
        else:
            f.write("推荐模型: 根据具体需求选择\n")
            f.write(f"  - 预测准确性优先: {best_r2_model}\n")
            f.write(f"  - 误差最小化优先: {best_rmse_model}\n")
            f.write(f"  - 训练速度优先: {fastest_model}\n")

        f.write("\n" + "="*80 + "\n")

    print(f"\n[OK] 对比报告已保存: {report_path}")


def save_models(models, output_dir):
    """保存所有训练好的模型"""
    models_dir = output_dir / 'trained_models'
    models_dir.mkdir(parents=True, exist_ok=True)

    for model_name, (model, _, _, _, _) in models.items():
        model_path = models_dir / f'{model_name.lower()}_model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"[OK] {model_name} 模型已保存: {model_path}")


def main():
    """主函数"""
    print("="*80)
    print("Q1 模型对比实验")
    print("="*80)
    print("\n对比模型: Ridge, Lasso, Elastic Net, SVR")
    print("目标: 评估不同回归模型在粉丝投票估算任务上的性能\n")

    # 1. 加载数据
    print("\n[步骤 1/6] 加载数据...")
    train_df, test_df = load_data()

    # 2. 训练所有模型
    print("\n[步骤 2/6] 训练所有模型...")
    models, training_times = train_all_models(train_df)

    # 3. 测试集评估
    print("\n[步骤 3/6] 测试集评估...")
    results = evaluate_all_models(models, test_df)

    # 4. 创建输出目录
    output_dir = Path(__file__).parent.parent / 'figures' / 'model_comparison'
    output_dir.mkdir(parents=True, exist_ok=True)

    # 5. 生成可视化
    print("\n[步骤 4/6] 生成对比可视化...")
    create_comparison_visualizations(models, results, training_times, output_dir)

    # 6. 生成报告
    print("\n[步骤 5/6] 生成对比报告...")
    generate_comparison_report(models, results, training_times, output_dir)

    # 7. 保存模型
    print("\n[步骤 6/6] 保存训练好的模型...")
    save_models(models, output_dir)

    print("\n" + "="*80)
    print("实验完成！")
    print("="*80)
    print(f"\n输出目录: {output_dir}")
    print("\n生成文件:")
    print("  - model_performance_comparison.png/pdf")
    print("  - training_time_comparison.png/pdf")
    print("  - residual_distribution_comparison.png/pdf")
    print("  - prediction_scatter_comparison.png/pdf")
    print("  - model_comparison_report.txt")
    print("  - trained_models/*.pkl")


if __name__ == '__main__':
    main()
