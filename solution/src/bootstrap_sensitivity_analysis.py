"""
Bootstrap预测区间和敏感性分析
根据论文改进计划实现：
1. Bootstrap方法构建95%置信区间
2. 超参数敏感性分析
3. 特征扰动敏感性分析
"""

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.utils import resample
from sklearn.base import clone, BaseEstimator
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import copy
from scipy import stats
import pickle
import warnings
warnings.filterwarnings('ignore')

# 配置matplotlib
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['figure.titlesize'] = 14


class BootstrapAnalyzer:
    """
    Bootstrap预测区间分析器

    功能：
    1. 构建Bootstrap预测区间
    2. 计算覆盖率
    3. 可视化不确定性
    """

    def __init__(self, n_iterations=1000, confidence=0.95, random_state=42):
        """
        Parameters:
        -----------
        n_iterations : int
            Bootstrap重采样次数
        confidence : float
            置信水平（默认95%）
        random_state : int
            随机种子
        """
        self.n_iterations = n_iterations
        self.confidence = confidence
        self.random_state = random_state
        self.predictions_history = None

    def compute_prediction_interval(self, model, X_train, y_train, X_test):
        """
        使用Bootstrap方法构建预测区间

        Returns:
        --------
        median_pred : array
            中位数预测
        lower_bound : array
            下界
        upper_bound : array
            上界
        predictions_history : array
            所有Bootstrap预测的历史（用于进一步分析）
        """
        print(f"\n[Bootstrap] 开始 {self.n_iterations} 次重采样...")

        predictions = []

        for i in range(self.n_iterations):
            if (i + 1) % 100 == 0:
                print(f"  进度: {i+1}/{self.n_iterations}")

            # 重采样训练集
            X_resampled, y_resampled = resample(
                X_train, y_train,
                random_state=self.random_state + i
            )

            # 克隆并训练模型
            # 使用深拷贝代替sklearn的clone（因为我们的模型不是标准sklearn估计器）
            try:
                model_boot = clone(model)
            except TypeError:
                # 如果clone失败，使用深拷贝
                model_boot = copy.deepcopy(model)
                # 重置fitted状态
                model_boot.is_fitted = False

            model_boot.fit(X_resampled, y_resampled)

            # 预测
            y_pred = model_boot.predict(X_test)
            predictions.append(y_pred)

        predictions = np.array(predictions)
        self.predictions_history = predictions

        # 计算置信区间
        alpha = (1 - self.confidence) / 2
        lower_bound = np.percentile(predictions, alpha * 100, axis=0)
        upper_bound = np.percentile(predictions, (1 - alpha) * 100, axis=0)
        median_pred = np.percentile(predictions, 50, axis=0)
        mean_pred = np.mean(predictions, axis=0)

        print(f"[Bootstrap] 完成！")

        return median_pred, lower_bound, upper_bound, mean_pred

    def evaluate_coverage(self, y_test, lower_bound, upper_bound):
        """
        评估预测区间的覆盖率
        """
        coverage = np.mean((y_test >= lower_bound) & (y_test <= upper_bound))

        # 计算区间宽度统计
        interval_widths = upper_bound - lower_bound

        stats_dict = {
            'coverage_rate': coverage,
            'mean_width': np.mean(interval_widths),
            'median_width': np.median(interval_widths),
            'std_width': np.std(interval_widths),
            'min_width': np.min(interval_widths),
            'max_width': np.max(interval_widths)
        }

        return stats_dict

    def plot_prediction_intervals(self, y_test, median_pred, lower_bound, upper_bound,
                                   output_path, title="Bootstrap Prediction Intervals"):
        """
        可视化预测区间
        """
        fig, axes = plt.subplots(2, 1, figsize=(14, 10), dpi=300)

        # 图1: 预测值 vs 实际值（带区间）
        ax1 = axes[0]

        # 排序以便更好地可视化
        sort_idx = np.argsort(y_test)
        y_test_sorted = y_test[sort_idx]
        median_sorted = median_pred[sort_idx]
        lower_sorted = lower_bound[sort_idx]
        upper_sorted = upper_bound[sort_idx]

        x_axis = np.arange(len(y_test))

        ax1.scatter(x_axis, y_test_sorted, alpha=0.6, s=30, color='black',
                   label='Actual Values', zorder=3)
        ax1.plot(x_axis, median_sorted, 'r-', linewidth=2,
                label='Median Prediction', zorder=2)
        ax1.fill_between(x_axis, lower_sorted, upper_sorted,
                        alpha=0.3, color='blue',
                        label=f'{int(self.confidence*100)}% Bootstrap CI', zorder=1)

        ax1.set_xlabel('Sample Index (sorted by actual value)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Value', fontsize=12, fontweight='bold')
        ax1.set_title(f'{title} - Prediction with Confidence Intervals',
                     fontsize=13, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)

        # 图2: 区间宽度分布
        ax2 = axes[1]

        interval_widths = upper_bound - lower_bound

        ax2.hist(interval_widths, bins=50, color='steelblue', alpha=0.7, edgecolor='black')
        ax2.axvline(np.mean(interval_widths), color='red', linestyle='--',
                   linewidth=2, label=f'Mean: {np.mean(interval_widths):.4f}')
        ax2.axvline(np.median(interval_widths), color='green', linestyle='--',
                   linewidth=2, label=f'Median: {np.median(interval_widths):.4f}')

        ax2.set_xlabel('Interval Width', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax2.set_title('Distribution of Prediction Interval Widths',
                     fontsize=13, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"[OK] 预测区间图已保存: {output_path}")


class SensitivityAnalyzer:
    """
    敏感性分析器

    功能：
    1. 超参数敏感性分析
    2. 特征扰动敏感性分析
    3. 样本量敏感性分析
    """

    def __init__(self, base_model, X_train, y_train, X_test, y_test):
        """
        Parameters:
        -----------
        base_model : sklearn model
            基准模型
        X_train, y_train : array
            训练数据
        X_test, y_test : array
            测试数据
        """
        self.base_model = base_model
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

    def hyperparameter_sensitivity(self, param_name, param_values, model_class):
        """
        超参数敏感性分析

        Parameters:
        -----------
        param_name : str
            超参数名称（如'alpha', 'C'）
        param_values : array
            要测试的参数值范围
        model_class : class
            模型类（如Ridge, Lasso）

        Returns:
        --------
        results_df : DataFrame
            包含不同参数值下的性能指标
        """
        print(f"\n[敏感性分析] 测试超参数: {param_name}")
        print(f"  参数范围: {param_values.min():.4f} - {param_values.max():.4f}")

        results = []

        for param_value in param_values:
            # 创建模型
            model = model_class(**{param_name: param_value})

            # 训练
            model.fit(self.X_train, self.y_train)

            # 评估
            y_pred_train = model.predict(self.X_train)
            y_pred_test = model.predict(self.X_test)

            train_r2 = r2_score(self.y_train, y_pred_train)
            test_r2 = r2_score(self.y_test, y_pred_test)
            test_rmse = np.sqrt(mean_squared_error(self.y_test, y_pred_test))
            test_mae = mean_absolute_error(self.y_test, y_pred_test)

            results.append({
                param_name: param_value,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'test_rmse': test_rmse,
                'test_mae': test_mae,
                'overfitting': train_r2 - test_r2
            })

        results_df = pd.DataFrame(results)

        print(f"[OK] 完成 {len(param_values)} 个参数值的测试")

        return results_df

    def feature_perturbation_sensitivity(self, feature_names, perturbation_levels=[0.1, 0.2, 0.5]):
        """
        特征扰动敏感性分析

        测试每个特征在不同扰动水平下对预测的影响

        Parameters:
        -----------
        feature_names : list
            特征名称列表
        perturbation_levels : list
            扰动水平（相对标准差的倍数）

        Returns:
        --------
        results_df : DataFrame
            每个特征在不同扰动水平下的性能变化
        """
        print(f"\n[敏感性分析] 特征扰动测试")
        print(f"  特征数: {len(feature_names)}")
        print(f"  扰动水平: {perturbation_levels}")

        # 基准性能
        y_pred_base = self.base_model.predict(self.X_test)
        base_r2 = r2_score(self.y_test, y_pred_base)
        base_rmse = np.sqrt(mean_squared_error(self.y_test, y_pred_base))

        results = []

        for feat_idx, feat_name in enumerate(feature_names):
            for perturb_level in perturbation_levels:
                # 扰动特征
                X_test_perturbed = self.X_test.copy()
                feat_std = np.std(X_test_perturbed[:, feat_idx])
                noise = np.random.normal(0, perturb_level * feat_std, size=len(X_test_perturbed))
                X_test_perturbed[:, feat_idx] += noise

                # 预测
                y_pred_perturbed = self.base_model.predict(X_test_perturbed)

                # 评估
                perturbed_r2 = r2_score(self.y_test, y_pred_perturbed)
                perturbed_rmse = np.sqrt(mean_squared_error(self.y_test, y_pred_perturbed))

                # 计算性能下降
                r2_drop = base_r2 - perturbed_r2
                rmse_increase = perturbed_rmse - base_rmse

                results.append({
                    'feature': feat_name,
                    'perturbation_level': perturb_level,
                    'r2': perturbed_r2,
                    'r2_drop': r2_drop,
                    'rmse': perturbed_rmse,
                    'rmse_increase': rmse_increase
                })

        results_df = pd.DataFrame(results)

        print(f"[OK] 完成特征扰动测试")

        return results_df

    def sample_size_sensitivity(self, sample_fractions=[0.2, 0.4, 0.6, 0.8, 1.0], n_repeats=10):
        """
        样本量敏感性分析

        测试不同训练集大小对模型性能的影响

        Parameters:
        -----------
        sample_fractions : list
            训练集比例
        n_repeats : int
            每个比例重复次数

        Returns:
        --------
        results_df : DataFrame
            不同样本量下的性能统计
        """
        print(f"\n[敏感性分析] 样本量测试")
        print(f"  样本比例: {sample_fractions}")
        print(f"  每个比例重复: {n_repeats} 次")

        results = []

        for frac in sample_fractions:
            n_samples = int(len(self.X_train) * frac)

            for repeat in range(n_repeats):
                # 随机采样
                indices = np.random.choice(len(self.X_train), size=n_samples, replace=False)
                X_train_subset = self.X_train[indices]
                y_train_subset = self.y_train[indices]

                # 训练
                try:
                    model = clone(self.base_model)
                except TypeError:
                    model = copy.deepcopy(self.base_model)
                    model.is_fitted = False
                model.fit(X_train_subset, y_train_subset)

                # 评估
                y_pred = model.predict(self.X_test)
                test_r2 = r2_score(self.y_test, y_pred)
                test_rmse = np.sqrt(mean_squared_error(self.y_test, y_pred))
                test_mae = mean_absolute_error(self.y_test, y_pred)

                results.append({
                    'sample_fraction': frac,
                    'n_samples': n_samples,
                    'repeat': repeat,
                    'test_r2': test_r2,
                    'test_rmse': test_rmse,
                    'test_mae': test_mae
                })

        results_df = pd.DataFrame(results)

        print(f"[OK] 完成样本量测试")

        return results_df


def plot_hyperparameter_sensitivity(results_df, param_name, output_path):
    """可视化超参数敏感性"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=300)

    param_values = results_df[param_name].values

    # R2 Score
    ax1 = axes[0, 0]
    ax1.plot(param_values, results_df['train_r2'], 'o-', label='Train R²', linewidth=2)
    ax1.plot(param_values, results_df['test_r2'], 's-', label='Test R²', linewidth=2)
    ax1.set_xlabel(param_name, fontsize=12, fontweight='bold')
    ax1.set_ylabel('R² Score', fontsize=12, fontweight='bold')
    ax1.set_title(f'R² vs {param_name}', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')

    # RMSE
    ax2 = axes[0, 1]
    ax2.plot(param_values, results_df['test_rmse'], 'o-', color='red', linewidth=2)
    ax2.set_xlabel(param_name, fontsize=12, fontweight='bold')
    ax2.set_ylabel('RMSE', fontsize=12, fontweight='bold')
    ax2.set_title(f'RMSE vs {param_name}', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')

    # MAE
    ax3 = axes[1, 0]
    ax3.plot(param_values, results_df['test_mae'], 'o-', color='green', linewidth=2)
    ax3.set_xlabel(param_name, fontsize=12, fontweight='bold')
    ax3.set_ylabel('MAE', fontsize=12, fontweight='bold')
    ax3.set_title(f'MAE vs {param_name}', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.set_xscale('log')

    # Overfitting
    ax4 = axes[1, 1]
    ax4.plot(param_values, results_df['overfitting'], 'o-', color='purple', linewidth=2)
    ax4.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax4.set_xlabel(param_name, fontsize=12, fontweight='bold')
    ax4.set_ylabel('Overfitting (Train R² - Test R²)', fontsize=12, fontweight='bold')
    ax4.set_title(f'Overfitting vs {param_name}', fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.set_xscale('log')

    plt.suptitle(f'Hyperparameter Sensitivity Analysis: {param_name}',
                fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"[OK] 超参数敏感性图已保存: {output_path}")


def plot_feature_perturbation_sensitivity(results_df, output_path):
    """可视化特征扰动敏感性"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

    # R2 drop
    ax1 = axes[0]
    pivot_r2 = results_df.pivot(index='feature', columns='perturbation_level', values='r2_drop')
    pivot_r2.plot(kind='bar', ax=ax1, width=0.8)
    ax1.set_xlabel('Feature', fontsize=12, fontweight='bold')
    ax1.set_ylabel('R² Drop', fontsize=12, fontweight='bold')
    ax1.set_title('Feature Sensitivity: R² Drop under Perturbation',
                 fontsize=13, fontweight='bold')
    ax1.legend(title='Perturbation Level', fontsize=9)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')

    # RMSE increase
    ax2 = axes[1]
    pivot_rmse = results_df.pivot(index='feature', columns='perturbation_level', values='rmse_increase')
    pivot_rmse.plot(kind='bar', ax=ax2, width=0.8, color=['#e74c3c', '#f39c12', '#9b59b6'])
    ax2.set_xlabel('Feature', fontsize=12, fontweight='bold')
    ax2.set_ylabel('RMSE Increase', fontsize=12, fontweight='bold')
    ax2.set_title('Feature Sensitivity: RMSE Increase under Perturbation',
                 fontsize=13, fontweight='bold')
    ax2.legend(title='Perturbation Level', fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"[OK] 特征扰动敏感性图已保存: {output_path}")


def plot_sample_size_sensitivity(results_df, output_path):
    """可视化样本量敏感性"""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), dpi=300)

    # 计算统计量
    stats_df = results_df.groupby('sample_fraction').agg({
        'test_r2': ['mean', 'std'],
        'test_rmse': ['mean', 'std'],
        'test_mae': ['mean', 'std']
    }).reset_index()

    sample_fractions = stats_df['sample_fraction'].values

    # R2
    ax1 = axes[0]
    r2_mean = stats_df[('test_r2', 'mean')].values
    r2_std = stats_df[('test_r2', 'std')].values
    ax1.errorbar(sample_fractions, r2_mean, yerr=r2_std,
                marker='o', linewidth=2, capsize=5, capthick=2)
    ax1.set_xlabel('Training Sample Fraction', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Test R² Score', fontsize=12, fontweight='bold')
    ax1.set_title('R² vs Sample Size', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # RMSE
    ax2 = axes[1]
    rmse_mean = stats_df[('test_rmse', 'mean')].values
    rmse_std = stats_df[('test_rmse', 'std')].values
    ax2.errorbar(sample_fractions, rmse_mean, yerr=rmse_std,
                marker='s', linewidth=2, capsize=5, capthick=2, color='red')
    ax2.set_xlabel('Training Sample Fraction', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Test RMSE', fontsize=12, fontweight='bold')
    ax2.set_title('RMSE vs Sample Size', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # MAE
    ax3 = axes[2]
    mae_mean = stats_df[('test_mae', 'mean')].values
    mae_std = stats_df[('test_mae', 'std')].values
    ax3.errorbar(sample_fractions, mae_mean, yerr=mae_std,
                marker='^', linewidth=2, capsize=5, capthick=2, color='green')
    ax3.set_xlabel('Training Sample Fraction', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Test MAE', fontsize=12, fontweight='bold')
    ax3.set_title('MAE vs Sample Size', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)

    plt.suptitle('Sample Size Sensitivity Analysis', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"[OK] 样本量敏感性图已保存: {output_path}")
