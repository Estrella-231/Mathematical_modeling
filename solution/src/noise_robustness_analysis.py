"""
噪声鲁棒性分析 - Noise Robustness Analysis
测试模型对三种数据扰动的鲁棒性：
1. 高斯噪声注入 (Gaussian Noise Injection)
2. 数据缺失实验 (Missing Data Experiments)
3. 异常值注入 (Outlier Injection)

这是O奖论文的标配内容
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pickle
import sys
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# 添加路径
sys.path.append(str(Path(__file__).parent))
from config import DATA_DIR, ROOT

# 设置科研绘图风格
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 13,
    'text.usetex': False,
    'axes.unicode_minus': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
    'axes.axisbelow': True
})


def load_trained_models():
    """加载已训练的模型"""
    model_dir = ROOT / 'figures' / 'model_comparison' / 'trained_models'

    models = {}
    model_names = ['ridge', 'lasso', 'elasticnet', 'svr']

    for name in model_names:
        model_path = model_dir / f'{name}_model.pkl'
        if model_path.exists():
            with open(model_path, 'rb') as f:
                models[name] = pickle.load(f)
            print(f"  已加载: {name}")
        else:
            print(f"  警告: 未找到 {name} 模型")

    return models


def load_data():
    """加载训练和测试数据"""
    # 这里需要重新加载数据并进行特征工程
    # 为了简化，我们假设数据已经准备好
    from utils.data import load_data as load_raw_data, build_week_panel
    from config import RAW_DATA

    df = load_raw_data(RAW_DATA)
    panel = build_week_panel(df)
    panel = panel[panel['has_scores']].copy()

    # 特征工程
    panel['judge_rank_in_week'] = panel.groupby('week')['judge_total'].rank(ascending=False)
    panel['relative_judge_score'] = panel.groupby('week')['judge_total'].transform(
        lambda x: (x - x.mean()) / x.std()
    )
    panel['cumulative_average'] = panel.groupby('celebrity_name')['judge_total'].cumsum() / \
                                   panel.groupby('celebrity_name').cumcount().add(1)

    # 准备特征和目标
    feature_cols = ['judge_rank_in_week', 'relative_judge_score', 'cumulative_average']
    X = panel[feature_cols].values
    y = panel['placement'].values

    # 划分训练集和测试集（按season）
    train_mask = panel['season'] <= 27
    test_mask = panel['season'] > 27

    X_train = X[train_mask]
    y_train = y[train_mask]
    X_test = X[test_mask]
    y_test = y[test_mask]

    return X_train, y_train, X_test, y_test, feature_cols


def gaussian_noise_sensitivity(models, X_train, y_train, X_test, y_test,
                                noise_levels=[0.01, 0.05, 0.1, 0.2, 0.3],
                                n_trials=30):
    """
    高斯噪声敏感性分析

    Args:
        models: 训练好的模型字典
        noise_levels: 噪声标准差占特征标准差的比例
        n_trials: 每个噪声水平的重复次数
    """
    print("\n" + "="*80)
    print("1. 高斯噪声注入实验")
    print("="*80)

    # 计算每个特征的标准差
    feature_stds = np.std(X_train, axis=0)

    # 基准性能（无噪声）
    baseline_performance = {}
    for name, model in models.items():
        y_pred = model.predict(X_test)
        baseline_performance[name] = {
            'R2': r2_score(y_test, y_pred),
            'RMSE': np.sqrt(mean_squared_error(y_test, y_pred)),
            'MAE': mean_absolute_error(y_test, y_pred)
        }

    results = []

    for noise_level in noise_levels:
        print(f"\n  噪声水平: σ = {noise_level:.2f} × feature_std")

        for name, model in models.items():
            trial_r2 = []
            trial_rmse = []
            trial_mae = []

            for trial in range(n_trials):
                # 向测试集注入高斯噪声
                noise = np.random.normal(0, noise_level, X_test.shape) * feature_stds
                X_test_noisy = X_test + noise

                # 预测
                y_pred = model.predict(X_test_noisy)

                trial_r2.append(r2_score(y_test, y_pred))
                trial_rmse.append(np.sqrt(mean_squared_error(y_test, y_pred)))
                trial_mae.append(mean_absolute_error(y_test, y_pred))

            # 计算统计量
            r2_mean = np.mean(trial_r2)
            r2_std = np.std(trial_r2)
            rmse_mean = np.mean(trial_rmse)
            mae_mean = np.mean(trial_mae)

            # 计算相对于基准的下降
            r2_drop = (baseline_performance[name]['R2'] - r2_mean) / baseline_performance[name]['R2'] * 100

            results.append({
                'Model': name.upper(),
                'Noise Level': noise_level,
                'R² Mean': r2_mean,
                'R² Std': r2_std,
                'RMSE Mean': rmse_mean,
                'MAE Mean': mae_mean,
                'R² Drop (%)': r2_drop,
                'Baseline R²': baseline_performance[name]['R2']
            })

            print(f"    {name.upper():12s}: R2 = {r2_mean:.4f} +/- {r2_std:.4f}, Drop = {r2_drop:.1f}%")

    return pd.DataFrame(results), baseline_performance


def missing_data_sensitivity(models, X_train, y_train, X_test, y_test,
                              missing_rates=[0.05, 0.1, 0.15, 0.2, 0.3],
                              imputation_methods=['mean', 'median', 'zero'],
                              n_trials=30):
    """
    数据缺失敏感性分析

    Args:
        missing_rates: 缺失比例
        imputation_methods: 填充方法
        n_trials: 每个配置的重复次数
    """
    print("\n" + "="*80)
    print("2. 数据缺失实验")
    print("="*80)

    results = []

    for missing_rate in missing_rates:
        print(f"\n  缺失率: {missing_rate*100:.0f}%")

        for method in imputation_methods:
            print(f"    填充方法: {method}")

            for name, model in models.items():
                trial_r2 = []
                trial_rmse = []

                for trial in range(n_trials):
                    # 随机创建缺失值
                    X_test_missing = X_test.copy()
                    mask = np.random.random(X_test.shape) < missing_rate
                    X_test_missing[mask] = np.nan

                    # 填充缺失值
                    if method == 'mean':
                        imputer = SimpleImputer(strategy='mean')
                    elif method == 'median':
                        imputer = SimpleImputer(strategy='median')
                    else:  # zero
                        imputer = SimpleImputer(strategy='constant', fill_value=0)

                    # 用训练集拟合imputer
                    imputer.fit(X_train)
                    X_test_imputed = imputer.transform(X_test_missing)

                    # 预测
                    y_pred = model.predict(X_test_imputed)

                    trial_r2.append(r2_score(y_test, y_pred))
                    trial_rmse.append(np.sqrt(mean_squared_error(y_test, y_pred)))

                results.append({
                    'Model': name.upper(),
                    'Missing Rate': missing_rate,
                    'Imputation': method,
                    'R² Mean': np.mean(trial_r2),
                    'R² Std': np.std(trial_r2),
                    'RMSE Mean': np.mean(trial_rmse),
                    'RMSE Std': np.std(trial_rmse)
                })

                print(f"      {name.upper():12s}: R2 = {np.mean(trial_r2):.4f} +/- {np.std(trial_r2):.4f}")

    return pd.DataFrame(results)


def outlier_injection_sensitivity(models, X_train, y_train, X_test, y_test,
                                   outlier_rates=[0.01, 0.02, 0.05, 0.1],
                                   outlier_magnitudes=[2, 3, 5],
                                   n_trials=30):
    """
    异常值注入敏感性分析

    Args:
        outlier_rates: 异常值比例
        outlier_magnitudes: 异常值幅度（倍数的标准差）
        n_trials: 每个配置的重复次数
    """
    print("\n" + "="*80)
    print("3. 异常值注入实验")
    print("="*80)

    feature_stds = np.std(X_train, axis=0)
    results = []

    for rate in outlier_rates:
        print(f"\n  异常值比例: {rate*100:.0f}%")

        for magnitude in outlier_magnitudes:
            print(f"    异常值幅度: {magnitude}σ")

            for name, model in models.items():
                trial_r2 = []
                trial_rmse = []

                for trial in range(n_trials):
                    X_test_outlier = X_test.copy()

                    # 随机选择样本和特征注入异常值
                    n_outliers = int(rate * X_test.shape[0] * X_test.shape[1])
                    outlier_rows = np.random.randint(0, X_test.shape[0], n_outliers)
                    outlier_cols = np.random.randint(0, X_test.shape[1], n_outliers)

                    for row, col in zip(outlier_rows, outlier_cols):
                        # 添加magnitude倍标准差的异常值
                        sign = np.random.choice([-1, 1])
                        X_test_outlier[row, col] += sign * magnitude * feature_stds[col]

                    # 预测
                    y_pred = model.predict(X_test_outlier)

                    trial_r2.append(r2_score(y_test, y_pred))
                    trial_rmse.append(np.sqrt(mean_squared_error(y_test, y_pred)))

                results.append({
                    'Model': name.upper(),
                    'Outlier Rate': rate,
                    'Magnitude (σ)': magnitude,
                    'R² Mean': np.mean(trial_r2),
                    'R² Std': np.std(trial_r2),
                    'RMSE Mean': np.mean(trial_rmse),
                    'RMSE Std': np.std(trial_rmse)
                })

                print(f"      {name.upper():12s}: R2 = {np.mean(trial_r2):.4f} +/- {np.std(trial_r2):.4f}")

    return pd.DataFrame(results)


def visualize_gaussian_noise(noise_results, baseline_performance, output_dir):
    """可视化高斯噪声实验结果"""
    print("\n  生成高斯噪声可视化...")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 子图1: R² vs 噪声水平
    ax1 = axes[0]

    for model_name in noise_results['Model'].unique():
        model_data = noise_results[noise_results['Model'] == model_name]

        noise_levels = model_data['Noise Level']
        r2_means = model_data['R² Mean']
        r2_stds = model_data['R² Std']

        ax1.errorbar(noise_levels, r2_means, yerr=r2_stds, fmt='o-', capsize=5,
                    label=model_name, linewidth=2, markersize=6)

        # 添加基准线
        baseline_r2 = model_data['Baseline R²'].iloc[0]
        ax1.axhline(y=baseline_r2, linestyle='--', alpha=0.3, linewidth=1)

    ax1.set_xlabel('Noise Level (σ ratio to feature std)', fontweight='bold')
    ax1.set_ylabel('R² Score', fontweight='bold')
    ax1.set_title('(A) Model Performance under Gaussian Noise', fontweight='bold', loc='left')
    ax1.legend(loc='best', framealpha=0.95)
    ax1.grid(True, alpha=0.3)

    # 子图2: R² Drop (%)
    ax2 = axes[1]

    for model_name in noise_results['Model'].unique():
        model_data = noise_results[noise_results['Model'] == model_name]

        noise_levels = model_data['Noise Level']
        r2_drops = model_data['R² Drop (%)']

        ax2.plot(noise_levels, r2_drops, 'o-', label=model_name, linewidth=2, markersize=6)

    ax2.set_xlabel('Noise Level (σ ratio to feature std)', fontweight='bold')
    ax2.set_ylabel('R² Drop (%)', fontweight='bold')
    ax2.set_title('(B) Performance Degradation', fontweight='bold', loc='left')
    ax2.legend(loc='best', framealpha=0.95)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.5)

    plt.tight_layout()

    for ext in ['png', 'pdf']:
        output_path = output_dir / f'noise_gaussian_robustness.{ext}'
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"    已保存: {output_path.name}")

    plt.close(fig)


def visualize_missing_data(missing_results, output_dir):
    """可视化数据缺失实验结果"""
    print("\n  生成数据缺失可视化...")

    # 为每个模型创建热力图
    models = missing_results['Model'].unique()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, model_name in enumerate(models):
        if idx >= len(axes):
            break

        ax = axes[idx]
        model_data = missing_results[missing_results['Model'] == model_name]

        # 创建透视表
        pivot_table = model_data.pivot(index='Missing Rate',
                                       columns='Imputation',
                                       values='R² Mean')

        # 绘制热力图
        sns.heatmap(pivot_table, annot=True, fmt='.3f', cmap='RdYlGn',
                   vmin=0.5, vmax=0.8, center=0.65, ax=ax,
                   cbar_kws={'label': 'R² Score'})

        ax.set_title(f'{model_name} Model', fontweight='bold')
        ax.set_xlabel('Imputation Method', fontweight='bold')
        ax.set_ylabel('Missing Rate', fontweight='bold')

    plt.suptitle('Model Robustness to Missing Data', fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()

    for ext in ['png', 'pdf']:
        output_path = output_dir / f'noise_missing_data_heatmap.{ext}'
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"    已保存: {output_path.name}")

    plt.close(fig)


def visualize_outlier_injection(outlier_results, output_dir):
    """可视化异常值注入实验结果"""
    print("\n  生成异常值注入可视化...")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 子图1: 热力图（固定一个模型，如Ridge）
    ax1 = axes[0]

    ridge_data = outlier_results[outlier_results['Model'] == 'RIDGE']
    pivot_table = ridge_data.pivot(index='Outlier Rate',
                                   columns='Magnitude (σ)',
                                   values='R² Mean')

    sns.heatmap(pivot_table, annot=True, fmt='.3f', cmap='RdYlGn',
               vmin=0.5, vmax=0.8, center=0.65, ax=ax1,
               cbar_kws={'label': 'R² Score'})

    ax1.set_title('(A) RIDGE: Outlier Rate × Magnitude', fontweight='bold', loc='left')
    ax1.set_xlabel('Outlier Magnitude (σ)', fontweight='bold')
    ax1.set_ylabel('Outlier Rate', fontweight='bold')

    # 子图2: 线图（所有模型，固定magnitude=3σ）
    ax2 = axes[1]

    magnitude_3 = outlier_results[outlier_results['Magnitude (σ)'] == 3]

    for model_name in magnitude_3['Model'].unique():
        model_data = magnitude_3[magnitude_3['Model'] == model_name]

        outlier_rates = model_data['Outlier Rate']
        r2_means = model_data['R² Mean']
        r2_stds = model_data['R² Std']

        ax2.errorbar(outlier_rates, r2_means, yerr=r2_stds, fmt='o-', capsize=5,
                    label=model_name, linewidth=2, markersize=6)

    ax2.set_xlabel('Outlier Rate', fontweight='bold')
    ax2.set_ylabel('R² Score', fontweight='bold')
    ax2.set_title('(B) All Models: Performance vs Outlier Rate (3σ)',
                 fontweight='bold', loc='left')
    ax2.legend(loc='best', framealpha=0.95)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    for ext in ['png', 'pdf']:
        output_path = output_dir / f'noise_outlier_injection.{ext}'
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"    已保存: {output_path.name}")

    plt.close(fig)


def generate_noise_robustness_table(noise_results, missing_results, outlier_results, output_dir):
    """生成噪声鲁棒性综合表格"""
    print("\n  生成噪声鲁棒性表格...")

    # 选择代表性结果
    table_data = []

    # 1. 高斯噪声（选择几个代表性水平）
    for noise_level in [0.01, 0.05, 0.1, 0.2]:
        noise_subset = noise_results[noise_results['Noise Level'] == noise_level]
        for _, row in noise_subset.iterrows():
            table_data.append({
                'Perturbation Type': f'Gaussian Noise (σ={noise_level:.2f})',
                'Model': row['Model'],
                'R² Mean': row['R² Mean'],
                'R² Std': row['R² Std'],
                'R² Drop (%)': row['R² Drop (%)']
            })

    # 2. 数据缺失（mean imputation）
    for missing_rate in [0.05, 0.1, 0.2, 0.3]:
        missing_subset = missing_results[
            (missing_results['Missing Rate'] == missing_rate) &
            (missing_results['Imputation'] == 'mean')
        ]
        for _, row in missing_subset.iterrows():
            table_data.append({
                'Perturbation Type': f'Missing Data ({int(missing_rate*100)}%, mean)',
                'Model': row['Model'],
                'R² Mean': row['R² Mean'],
                'R² Std': row['R² Std'],
                'R² Drop (%)': np.nan  # 需要计算
            })

    # 3. 异常值注入（3σ）
    for outlier_rate in [0.01, 0.05, 0.1]:
        outlier_subset = outlier_results[
            (outlier_results['Outlier Rate'] == outlier_rate) &
            (outlier_results['Magnitude (σ)'] == 3)
        ]
        for _, row in outlier_subset.iterrows():
            table_data.append({
                'Perturbation Type': f'Outlier ({int(outlier_rate*100)}%, 3σ)',
                'Model': row['Model'],
                'R² Mean': row['R² Mean'],
                'R² Std': row['R² Std'],
                'R² Drop (%)': np.nan  # 需要计算
            })

    table_df = pd.DataFrame(table_data)

    # 保存为CSV
    csv_path = output_dir / 'noise_robustness_table.csv'
    table_df.to_csv(csv_path, index=False)
    print(f"    已保存: {csv_path.name}")

    # 生成LaTeX表格
    latex_path = output_dir / 'noise_robustness_table.tex'
    with open(latex_path, 'w') as f:
        f.write("% Model Robustness to Data Perturbation\n")
        f.write("% 可直接复制到论文中\n\n")
        f.write("\\begin{table}[h]\n")
        f.write("\\centering\n")
        f.write("\\caption{Model Robustness to Data Perturbation}\n")
        f.write("\\label{tab:noise_robustness}\n")
        f.write("\\begin{tabular}{l l c c c}\n")
        f.write("\\toprule\n")
        f.write("\\textbf{Perturbation Type} & \\textbf{Model} & \\textbf{R2 Mean} & \\textbf{R2 Std} & \\textbf{R2 Drop (\\%)} \\\\\n")
        f.write("\\midrule\n")

        # 按扰动类型分组
        current_type = None
        for _, row in table_df.iterrows():
            if row['Perturbation Type'] != current_type:
                if current_type is not None:
                    f.write("\\midrule\n")
                current_type = row['Perturbation Type']

            drop_str = f"{row['R² Drop (%)']:.1f}" if not pd.isna(row['R² Drop (%)']) else "--"
            f.write(f"{row['Perturbation Type']} & {row['Model']} & {row['R² Mean']:.3f} & {row['R² Std']:.3f} & {drop_str} \\\\\n")

        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")

    print(f"    已保存: {latex_path.name}")

    return table_df


def main():
    """主函数"""
    print("="*80)
    print("噪声鲁棒性分析 - Noise Robustness Analysis")
    print("="*80)

    # 创建输出目录
    output_dir = ROOT / 'figures' / 'noise_robustness'
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 加载模型和数据
    print("\n1. 加载训练好的模型...")
    models = load_trained_models()

    if len(models) == 0:
        print("\n错误: 未找到训练好的模型！")
        print("请先运行 run_model_comparison.py")
        return

    print("\n2. 加载数据...")
    X_train, y_train, X_test, y_test, feature_cols = load_data()
    print(f"  训练集: {X_train.shape}")
    print(f"  测试集: {X_test.shape}")
    print(f"  特征: {feature_cols}")

    # 2. 高斯噪声实验
    noise_results, baseline_performance = gaussian_noise_sensitivity(
        models, X_train, y_train, X_test, y_test,
        noise_levels=[0.01, 0.05, 0.1, 0.2, 0.3],
        n_trials=30
    )

    # 3. 数据缺失实验
    missing_results = missing_data_sensitivity(
        models, X_train, y_train, X_test, y_test,
        missing_rates=[0.05, 0.1, 0.15, 0.2, 0.3],
        imputation_methods=['mean', 'median', 'zero'],
        n_trials=30
    )

    # 4. 异常值注入实验
    outlier_results = outlier_injection_sensitivity(
        models, X_train, y_train, X_test, y_test,
        outlier_rates=[0.01, 0.02, 0.05, 0.1],
        outlier_magnitudes=[2, 3, 5],
        n_trials=30
    )

    # 5. 可视化
    print("\n" + "="*80)
    print("生成可视化")
    print("="*80)

    visualize_gaussian_noise(noise_results, baseline_performance, output_dir)
    visualize_missing_data(missing_results, output_dir)
    visualize_outlier_injection(outlier_results, output_dir)

    # 6. 生成表格
    print("\n" + "="*80)
    print("生成表格")
    print("="*80)

    table_df = generate_noise_robustness_table(noise_results, missing_results,
                                               outlier_results, output_dir)

    # 7. 保存原始结果
    noise_results.to_csv(output_dir / 'gaussian_noise_results.csv', index=False)
    missing_results.to_csv(output_dir / 'missing_data_results.csv', index=False)
    outlier_results.to_csv(output_dir / 'outlier_injection_results.csv', index=False)

    print("\n" + "="*80)
    print("噪声鲁棒性分析完成！")
    print("="*80)
    print(f"\n输出目录: {output_dir}")
    print(f"生成文件:")
    print(f"  - noise_gaussian_robustness.png/pdf")
    print(f"  - noise_missing_data_heatmap.png/pdf")
    print(f"  - noise_outlier_injection.png/pdf")
    print(f"  - noise_robustness_table.csv/tex")
    print(f"  - gaussian_noise_results.csv")
    print(f"  - missing_data_results.csv")
    print(f"  - outlier_injection_results.csv")


if __name__ == '__main__':
    main()
