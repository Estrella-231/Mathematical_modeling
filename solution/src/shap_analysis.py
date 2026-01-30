"""
SHAP 分析脚本
使用 SHAP 值深度分析 Random Forest 模型的特征影响
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
from pathlib import Path
import pickle


def run_shap_analysis(model_path: Path, predictions_path: Path, output_dir: Path):
    """
    运行 SHAP 分析
    """
    print("=" * 80)
    print("SHAP 分析：Random Forest 特征影响深度解析")
    print("=" * 80)

    # 1. 加载模型
    print("\n[Step 1] 加载模型")
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)

    model = model_data['model']
    feature_names = model_data['feature_names']
    print(f"  - 模型加载成功")
    print(f"  - 特征数量: {len(feature_names)}")

    # 2. 加载预测数据
    print("\n[Step 2] 加载预测数据")
    predictions_df = pd.read_csv(predictions_path)
    print(f"  - 数据形状: {predictions_df.shape}")

    # 准备特征矩阵（与训练时相同的特征）
    X = predictions_df[feature_names].values
    print(f"  - 特征矩阵形状: {X.shape}")

    # 3. 创建 SHAP Explainer
    print("\n[Step 3] 创建 SHAP Explainer")
    print("  - 使用 TreeExplainer（针对树模型优化）")

    # 使用 TreeExplainer（针对树模型，速度快）
    explainer = shap.TreeExplainer(model)

    # 计算 SHAP 值（使用子集以加快速度）
    sample_size = min(500, len(X))
    X_sample = X[:sample_size]
    print(f"  - 计算 SHAP 值（样本数: {sample_size}）...")

    shap_values = explainer.shap_values(X_sample)
    print(f"  - SHAP 值形状: {shap_values.shape}")

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 4. SHAP Summary Plot（最重要的图）
    print("\n[Step 4] 生成 SHAP Summary Plot")
    plt.figure(figsize=(12, 8))
    shap.summary_plot(shap_values, X_sample, feature_names=feature_names, show=False)
    plt.tight_layout()
    plt.savefig(output_dir / 'shap_summary_plot.png', dpi=300, bbox_inches='tight')
    print(f"  - 保存: {output_dir / 'shap_summary_plot.png'}")
    plt.close()

    # 5. SHAP Bar Plot（特征重要性）
    print("\n[Step 5] 生成 SHAP Bar Plot")
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_sample, feature_names=feature_names,
                      plot_type="bar", show=False)
    plt.tight_layout()
    plt.savefig(output_dir / 'shap_bar_plot.png', dpi=300, bbox_inches='tight')
    print(f"  - 保存: {output_dir / 'shap_bar_plot.png'}")
    plt.close()

    # 6. SHAP Dependence Plots（关键特征）
    print("\n[Step 6] 生成 SHAP Dependence Plots")

    # 找出最重要的特征
    feature_importance = np.abs(shap_values).mean(axis=0)
    top_features_idx = np.argsort(feature_importance)[-5:][::-1]  # Top 5

    for idx in top_features_idx:
        feat_name = feature_names[idx]
        print(f"  - 生成 {feat_name} 的 dependence plot...")

        plt.figure(figsize=(10, 6))
        shap.dependence_plot(idx, shap_values, X_sample,
                            feature_names=feature_names, show=False)
        plt.tight_layout()

        # 清理文件名
        safe_name = feat_name.replace('_encoded', '').replace('/', '_')
        plt.savefig(output_dir / f'shap_dependence_{safe_name}.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

    # 7. SHAP Force Plot（单个样本解释）
    print("\n[Step 7] 生成 SHAP Force Plot（示例）")

    # 选择几个有代表性的样本
    # 找出残差最大和最小的样本
    residuals_sample = predictions_df['residual'].values[:sample_size]
    max_idx = np.argmax(residuals_sample)
    min_idx = np.argmin(residuals_sample)
    median_idx = np.argsort(residuals_sample)[len(residuals_sample)//2]

    for idx, label in [(max_idx, 'highest_fan_support'),
                       (min_idx, 'lowest_fan_support'),
                       (median_idx, 'median_fan_support')]:

        print(f"  - 生成 {label} 的 force plot...")

        # 创建 force plot
        shap.force_plot(
            explainer.expected_value,
            shap_values[idx],
            X_sample[idx],
            feature_names=feature_names,
            matplotlib=True,
            show=False
        )

        plt.tight_layout()
        plt.savefig(output_dir / f'shap_force_{label}.png',
                   dpi=300, bbox_inches='tight')
        plt.close()

    # 8. 生成 SHAP 值统计报告
    print("\n[Step 8] 生成 SHAP 值统计报告")

    shap_df = pd.DataFrame(shap_values, columns=feature_names)

    # 计算每个特征的平均绝对 SHAP 值
    mean_abs_shap = shap_df.abs().mean().sort_values(ascending=False)

    print(f"\n[SHAP 特征重要性排序]")
    for feat, val in mean_abs_shap.head(10).items():
        print(f"  {feat}: {val:.4f}")

    # 保存 SHAP 值
    shap_df['residual'] = residuals_sample
    shap_df['celebrity_name'] = predictions_df['celebrity_name'].values[:sample_size]
    shap_df['season'] = predictions_df['season'].values[:sample_size]
    shap_df['week'] = predictions_df['week'].values[:sample_size]

    shap_output_path = output_dir / 'shap_values.csv'
    shap_df.to_csv(shap_output_path, index=False)
    print(f"\n[保存] SHAP 值已保存到: {shap_output_path}")

    # 9. 分析关键发现
    print("\n" + "=" * 80)
    print("SHAP 分析关键发现")
    print("=" * 80)

    # 年龄的影响
    if 'age' in feature_names:
        age_idx = feature_names.index('age')
        age_shap = shap_values[:, age_idx]
        age_values = X_sample[:, age_idx]

        print(f"\n[年龄的影响]")
        print(f"  - 平均绝对 SHAP 值: {np.abs(age_shap).mean():.4f}")

        # 按年龄分组分析
        age_bins = [0, 30, 40, 50, 100]
        age_labels = ['<30', '30-40', '40-50', '50+']
        age_groups = pd.cut(age_values, bins=age_bins, labels=age_labels)

        for label in age_labels:
            mask = (age_groups == label)
            if mask.sum() > 0:
                mean_shap = age_shap[mask].mean()
                print(f"  - {label} 岁: 平均 SHAP = {mean_shap:.4f}")

    # 舞伴的影响
    if 'partner_encoded' in feature_names:
        partner_idx = feature_names.index('partner_encoded')
        partner_shap = shap_values[:, partner_idx]

        print(f"\n[舞伴的影响]")
        print(f"  - 平均绝对 SHAP 值: {np.abs(partner_shap).mean():.4f}")
        print(f"  - SHAP 值范围: [{partner_shap.min():.4f}, {partner_shap.max():.4f}]")

    print("\n" + "=" * 80)
    print("SHAP 分析完成！")
    print("=" * 80)

    print(f"\n生成的图表:")
    print(f"  1. shap_summary_plot.png - SHAP 值总览（最重要）")
    print(f"  2. shap_bar_plot.png - 特征重要性条形图")
    print(f"  3. shap_dependence_*.png - Top 5 特征的依赖图")
    print(f"  4. shap_force_*.png - 3 个代表性样本的解释")


if __name__ == "__main__":
    model_path = Path("F:/Mathematical_modeling/solution/Data/models/random_forest/random_forest_model.pkl")
    predictions_path = Path("F:/Mathematical_modeling/solution/Data/models/random_forest/rf_predictions.csv")
    output_dir = Path("F:/Mathematical_modeling/solution/figures/shap_analysis")

    run_shap_analysis(model_path, predictions_path, output_dir)
