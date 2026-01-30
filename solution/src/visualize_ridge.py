"""
可视化 Ridge 模型结果
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def visualize_ridge_results(results_path: Path, output_dir: Path):
    """
    可视化 Ridge 回归结果
    """
    print("=" * 60)
    print("可视化 Ridge 模型结果")
    print("=" * 60)

    # 加载结果
    df = pd.read_csv(results_path)
    print(f"\n加载数据: {len(df)} 行")

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 残差分布直方图
    plt.figure(figsize=(10, 6))
    plt.hist(df['residual'], bins=50, edgecolor='black', alpha=0.7)
    plt.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero Residual')
    plt.xlabel('Residual (Actual Rank - Predicted Rank)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Distribution of Residuals (Fan Vote Effect)', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'residual_distribution.png', dpi=300)
    print(f"[保存] 残差分布图: {output_dir / 'residual_distribution.png'}")
    plt.close()

    # 2. 粉丝分数分布
    plt.figure(figsize=(10, 6))
    plt.hist(df['fan_score'], bins=50, edgecolor='black', alpha=0.7, color='green')
    plt.axvline(x=0.5, color='red', linestyle='--', linewidth=2, label='Neutral (0.5)')
    plt.xlabel('Fan Support Score', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Distribution of Fan Support Scores', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'fan_score_distribution.png', dpi=300)
    print(f"[保存] 粉丝分数分布图: {output_dir / 'fan_score_distribution.png'}")
    plt.close()

    # 3. 实际排名 vs 预测排名
    # 计算预测排名
    df['predicted_rank'] = df['placement'] - df['residual']

    plt.figure(figsize=(10, 10))
    plt.scatter(df['predicted_rank'], df['placement'], alpha=0.5, s=20)

    # 添加对角线（完美预测）
    min_rank = min(df['predicted_rank'].min(), df['placement'].min())
    max_rank = max(df['predicted_rank'].max(), df['placement'].max())
    plt.plot([min_rank, max_rank], [min_rank, max_rank], 'r--', linewidth=2, label='Perfect Prediction')

    plt.xlabel('Predicted Rank (Judge-based)', fontsize=12)
    plt.ylabel('Actual Rank', fontsize=12)
    plt.title('Actual vs Predicted Rank', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'actual_vs_predicted.png', dpi=300)
    print(f"[保存] 实际vs预测排名图: {output_dir / 'actual_vs_predicted.png'}")
    plt.close()

    # 4. 按赛季的平均粉丝分数
    season_fan_scores = df.groupby('season')['fan_score'].mean().sort_index()

    plt.figure(figsize=(12, 6))
    plt.bar(season_fan_scores.index, season_fan_scores.values, edgecolor='black', alpha=0.7)
    plt.axhline(y=0.5, color='red', linestyle='--', linewidth=2, label='Neutral (0.5)')
    plt.xlabel('Season', fontsize=12)
    plt.ylabel('Average Fan Support Score', fontsize=12)
    plt.title('Average Fan Support by Season', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_dir / 'fan_score_by_season.png', dpi=300)
    print(f"[保存] 按赛季的粉丝分数图: {output_dir / 'fan_score_by_season.png'}")
    plt.close()

    # 5. Top 20 粉丝支持最高的选手
    top_20 = df.nsmallest(20, 'residual')[['celebrity_name', 'season', 'week', 'placement', 'residual', 'fan_score']]

    plt.figure(figsize=(12, 8))
    y_pos = np.arange(len(top_20))
    plt.barh(y_pos, top_20['fan_score'].values, edgecolor='black', alpha=0.7, color='green')
    plt.yticks(y_pos, [f"{row['celebrity_name']} (S{row['season']}, W{row['week']})"
                       for _, row in top_20.iterrows()], fontsize=9)
    plt.xlabel('Fan Support Score', fontsize=12)
    plt.title('Top 20 Contestants with Highest Fan Support', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig(output_dir / 'top_20_fan_support.png', dpi=300)
    print(f"[保存] Top 20 粉丝支持图: {output_dir / 'top_20_fan_support.png'}")
    plt.close()

    # 6. 残差 vs 评委排名
    plt.figure(figsize=(10, 6))
    plt.scatter(df['judge_rank_in_week'], df['residual'], alpha=0.5, s=20)
    plt.axhline(y=0, color='red', linestyle='--', linewidth=2)
    plt.xlabel('Judge Rank in Week', fontsize=12)
    plt.ylabel('Residual (Fan Effect)', fontsize=12)
    plt.title('Residual vs Judge Rank', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'residual_vs_judge_rank.png', dpi=300)
    print(f"[保存] 残差vs评委排名图: {output_dir / 'residual_vs_judge_rank.png'}")
    plt.close()

    print("\n" + "=" * 60)
    print("可视化完成！")
    print("=" * 60)


if __name__ == "__main__":
    from config import DATA_DIR

    results_path = DATA_DIR / "models" / "ridge" / "ridge_fan_scores.csv"
    output_dir = DATA_DIR.parent / "figures" / "ridge"

    visualize_ridge_results(results_path, output_dir)
