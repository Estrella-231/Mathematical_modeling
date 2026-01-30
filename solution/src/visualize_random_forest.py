"""
Random Forest 模型可视化
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns


def visualize_random_forest_results(importance_path: Path, predictions_path: Path, output_dir: Path):
    """
    可视化 Random Forest 结果
    """
    print("=" * 80)
    print("Random Forest 模型可视化")
    print("=" * 80)

    # 加载数据
    importance_df = pd.read_csv(importance_path)
    predictions_df = pd.read_csv(predictions_path)

    print(f"\n加载数据:")
    print(f"  - 特征重要性: {len(importance_df)} 个特征")
    print(f"  - 预测结果: {len(predictions_df)} 行")

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 特征重要性条形图
    plt.figure(figsize=(12, 8))
    top_n = 15
    top_features = importance_df.head(top_n)

    # 颜色编码：静态特征 vs 动态特征
    colors = []
    for feat in top_features['feature']:
        if '_encoded' in feat:
            colors.append('steelblue')  # 静态特征
        else:
            colors.append('coral')  # 动态特征

    plt.barh(range(len(top_features)), top_features['importance'], color=colors, edgecolor='black')
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Feature Importance', fontsize=12)
    plt.title(f'Top {top_n} Feature Importance (Random Forest)', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()

    # 添加图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='coral', edgecolor='black', label='Dynamic Features'),
        Patch(facecolor='steelblue', edgecolor='black', label='Static Features')
    ]
    plt.legend(handles=legend_elements, loc='lower right')

    plt.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig(output_dir / 'feature_importance.png', dpi=300)
    print(f"\n[保存] 特征重要性图: {output_dir / 'feature_importance.png'}")
    plt.close()

    # 2. 实际 vs 预测残差
    plt.figure(figsize=(10, 10))
    plt.scatter(predictions_df['residual'], predictions_df['rf_prediction'],
                alpha=0.5, s=20, edgecolor='black', linewidth=0.5)

    # 添加对角线
    min_val = min(predictions_df['residual'].min(), predictions_df['rf_prediction'].min())
    max_val = max(predictions_df['residual'].max(), predictions_df['rf_prediction'].max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')

    plt.xlabel('Actual Residual (from Ridge)', fontsize=12)
    plt.ylabel('Predicted Residual (from RF)', fontsize=12)
    plt.title('Actual vs Predicted Fan Effect Residual', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'actual_vs_predicted.png', dpi=300)
    print(f"[保存] 实际vs预测图: {output_dir / 'actual_vs_predicted.png'}")
    plt.close()

    # 3. 残差分布对比
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(predictions_df['residual'], bins=50, alpha=0.7, edgecolor='black', label='Actual')
    axes[0].axvline(x=0, color='red', linestyle='--', linewidth=2)
    axes[0].set_xlabel('Residual Value', fontsize=12)
    axes[0].set_ylabel('Frequency', fontsize=12)
    axes[0].set_title('Actual Residual Distribution', fontsize=13, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].hist(predictions_df['rf_prediction'], bins=50, alpha=0.7, edgecolor='black',
                 color='green', label='Predicted')
    axes[1].axvline(x=0, color='red', linestyle='--', linewidth=2)
    axes[1].set_xlabel('Residual Value', fontsize=12)
    axes[1].set_ylabel('Frequency', fontsize=12)
    axes[1].set_title('Predicted Residual Distribution', fontsize=13, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'residual_distributions.png', dpi=300)
    print(f"[保存] 残差分布对比图: {output_dir / 'residual_distributions.png'}")
    plt.close()

    # 4. 按年龄的粉丝效应
    if 'age' in predictions_df.columns:
        plt.figure(figsize=(12, 6))

        # 按年龄分组
        age_bins = [0, 25, 35, 45, 55, 100]
        age_labels = ['<25', '25-35', '35-45', '45-55', '55+']
        predictions_df['age_bin'] = pd.cut(predictions_df['age'], bins=age_bins, labels=age_labels)

        # 计算每个年龄组的平均残差
        age_effect = predictions_df.groupby('age_bin').agg({
            'residual': ['mean', 'std', 'count']
        }).reset_index()
        age_effect.columns = ['age_group', 'mean_residual', 'std_residual', 'count']

        # 绘制条形图
        x_pos = np.arange(len(age_effect))
        plt.bar(x_pos, age_effect['mean_residual'], yerr=age_effect['std_residual'],
                alpha=0.7, edgecolor='black', capsize=5)
        plt.xticks(x_pos, age_effect['age_group'])
        plt.axhline(y=0, color='red', linestyle='--', linewidth=2)
        plt.xlabel('Age Group', fontsize=12)
        plt.ylabel('Average Fan Effect (Residual)', fontsize=12)
        plt.title('Fan Effect by Age Group', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='y')

        # 添加样本数量标签
        for i, row in age_effect.iterrows():
            plt.text(i, row['mean_residual'] + 0.1, f"n={int(row['count'])}",
                    ha='center', fontsize=9)

        plt.tight_layout()
        plt.savefig(output_dir / 'fan_effect_by_age.png', dpi=300)
        print(f"[保存] 按年龄的粉丝效应图: {output_dir / 'fan_effect_by_age.png'}")
        plt.close()

    # 5. 按行业的粉丝效应
    if 'celebrity_industry' in predictions_df.columns:
        plt.figure(figsize=(14, 8))

        # 计算每个行业的平均残差
        industry_effect = predictions_df.groupby('celebrity_industry').agg({
            'residual': ['mean', 'count']
        }).reset_index()
        industry_effect.columns = ['industry', 'mean_residual', 'count']

        # 只显示样本数 >= 20 的行业
        industry_effect = industry_effect[industry_effect['count'] >= 20].sort_values('mean_residual')

        # 绘制条形图
        colors = ['green' if x > 0 else 'red' for x in industry_effect['mean_residual']]
        plt.barh(range(len(industry_effect)), industry_effect['mean_residual'],
                color=colors, alpha=0.7, edgecolor='black')
        plt.yticks(range(len(industry_effect)), industry_effect['industry'])
        plt.axvline(x=0, color='black', linestyle='--', linewidth=2)
        plt.xlabel('Average Fan Effect (Residual)', fontsize=12)
        plt.title('Fan Effect by Industry (n >= 20)', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='x')

        # 添加样本数量标签
        for i, row in industry_effect.iterrows():
            x_pos = row['mean_residual'] + (0.05 if row['mean_residual'] > 0 else -0.05)
            ha = 'left' if row['mean_residual'] > 0 else 'right'
            plt.text(x_pos, i, f"n={int(row['count'])}", ha=ha, va='center', fontsize=8)

        plt.tight_layout()
        plt.savefig(output_dir / 'fan_effect_by_industry.png', dpi=300)
        print(f"[保存] 按行业的粉丝效应图: {output_dir / 'fan_effect_by_industry.png'}")
        plt.close()

    # 6. 特征重要性饼图（静态 vs 动态）
    plt.figure(figsize=(10, 8))

    static_importance = importance_df[importance_df['feature'].str.contains('_encoded')]['importance'].sum()
    dynamic_importance = importance_df[~importance_df['feature'].str.contains('_encoded')]['importance'].sum()

    sizes = [static_importance, dynamic_importance]
    labels = [f'Static Features\n(Age, Industry, etc.)\n{static_importance:.2%}',
              f'Dynamic Features\n(Judge Score, Trend, etc.)\n{dynamic_importance:.2%}']
    colors = ['steelblue', 'coral']
    explode = (0.05, 0.05)

    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90,
            textprops={'fontsize': 12, 'weight': 'bold'})
    plt.title('Feature Importance: Static vs Dynamic', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'feature_importance_pie.png', dpi=300)
    print(f"[保存] 特征重要性饼图: {output_dir / 'feature_importance_pie.png'}")
    plt.close()

    print("\n" + "=" * 80)
    print("可视化完成！")
    print("=" * 80)


if __name__ == "__main__":
    importance_path = Path("F:/Mathematical_modeling/solution/Data/models/random_forest/feature_importance.csv")
    predictions_path = Path("F:/Mathematical_modeling/solution/Data/models/random_forest/rf_predictions.csv")
    output_dir = Path("F:/Mathematical_modeling/solution/figures/random_forest")

    visualize_random_forest_results(importance_path, predictions_path, output_dir)
