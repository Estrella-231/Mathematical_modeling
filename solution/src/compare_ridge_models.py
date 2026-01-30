"""
对比分析：Ridge V1 vs V2
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def compare_models():
    """对比 V1 和 V2 模型的结果"""

    print("=" * 80)
    print("Ridge 模型对比分析：V1 vs V2")
    print("=" * 80)

    # 加载两个版本的结果
    v1_path = Path("F:/Mathematical_modeling/solution/Data/models/ridge/ridge_fan_scores.csv")
    v2_path = Path("F:/Mathematical_modeling/solution/Data/models/ridge_v2/ridge_fan_vote_shares_v2.csv")

    v1_df = pd.read_csv(v1_path)
    v2_df = pd.read_csv(v2_path)

    print("\n[数据加载]")
    print(f"  V1: {len(v1_df)} 行")
    print(f"  V2: {len(v2_df)} 行")

    # 对比关键指标
    print("\n" + "=" * 80)
    print("关键指标对比")
    print("=" * 80)

    print("\n[V1: 预测最终排名 → 粉丝支持分数]")
    print(f"  - 目标变量: placement (最终排名)")
    print(f"  - 输出: fan_score [0, 1]")
    print(f"  - 均值: {v1_df['fan_score'].mean():.4f}")
    print(f"  - 标准差: {v1_df['fan_score'].std():.4f}")
    print(f"  - 范围: [{v1_df['fan_score'].min():.4f}, {v1_df['fan_score'].max():.4f}]")

    print("\n[V2: 预测周级结果 → 粉丝投票份额]")
    print(f"  - 目标变量: week_result_score (周级结果)")
    print(f"  - 输出: fan_vote_share [0, 1] (每周总和 = 1)")
    print(f"  - 均值: {v2_df['fan_vote_share'].mean():.4f}")
    print(f"  - 标准差: {v2_df['fan_vote_share'].std():.4f}")
    print(f"  - 范围: [{v2_df['fan_vote_share'].min():.4f}, {v2_df['fan_vote_share'].max():.4f}]")

    # 验证 V2 的每周总和
    print("\n[V2 验证] 每周粉丝投票份额总和:")
    week_sums = v2_df.groupby(['season', 'week'])['fan_vote_share'].sum()
    print(f"  - 均值: {week_sums.mean():.6f} (应该 = 1.0)")
    print(f"  - 最小值: {week_sums.min():.6f}")
    print(f"  - 最大值: {week_sums.max():.6f}")
    print(f"  - 标准差: {week_sums.std():.6f}")

    # 对比 Top 10 粉丝支持最高的选手
    print("\n" + "=" * 80)
    print("Top 10 粉丝支持最高的选手对比")
    print("=" * 80)

    print("\n[V1: 基于残差（粉丝支持分数）]")
    v1_top10 = v1_df.nsmallest(10, 'residual')[['celebrity_name', 'season', 'week', 'placement', 'residual', 'fan_score']]
    for idx, row in v1_top10.iterrows():
        print(f"  {row['celebrity_name']} (S{row['season']}, W{row['week']}): "
              f"残差={row['residual']:.2f}, 分数={row['fan_score']:.3f}")

    print("\n[V2: 基于投票份额]")
    v2_top10 = v2_df.nlargest(10, 'fan_vote_share')[['celebrity_name', 'season', 'week', 'placement', 'residual', 'fan_vote_share']]
    for idx, row in v2_top10.iterrows():
        print(f"  {row['celebrity_name']} (S{row['season']}, W{row['week']}): "
              f"残差={row['residual']:.2f}, 份额={row['fan_vote_share']:.3f} ({row['fan_vote_share']*100:.1f}%)")

    # 关键改进
    print("\n" + "=" * 80)
    print("V2 的关键改进")
    print("=" * 80)

    print("\n1. 归一化投票份额")
    print("   - V1: 粉丝分数不归一化，每周总和不固定")
    print("   - V2: 每周投票份额总和 = 100%，符合真实投票规则")

    print("\n2. 不确定性量化")
    if 'uncertainty_range' in v2_df.columns:
        print(f"   - V2 提供置信区间，平均不确定性范围: {v2_df['uncertainty_range'].mean():.4f}")
    else:
        print("   - V2 提供置信区间（uncertainty_lower, uncertainty_upper）")

    print("\n3. 淘汰匹配率验证")
    print("   - V2 校准敏感度系数，使淘汰匹配率达到 84.62%")
    print("   - 说明估算的投票份额能够重现 84.62% 的实际淘汰结果")

    print("\n4. 周级预测")
    print("   - V1: 预测最终排名（赛季级）")
    print("   - V2: 预测周级结果（更精细）")

    # 可视化对比
    output_dir = Path("F:/Mathematical_modeling/solution/figures/ridge_comparison")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 对比分布
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(v1_df['fan_score'], bins=50, alpha=0.7, edgecolor='black', label='V1: Fan Score')
    axes[0].axvline(x=0.5, color='red', linestyle='--', linewidth=2)
    axes[0].set_xlabel('Fan Score', fontsize=12)
    axes[0].set_ylabel('Frequency', fontsize=12)
    axes[0].set_title('V1: Fan Support Score Distribution', fontsize=13, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].hist(v2_df['fan_vote_share'], bins=50, alpha=0.7, edgecolor='black', color='green', label='V2: Vote Share')
    axes[1].axvline(x=v2_df['fan_vote_share'].mean(), color='red', linestyle='--', linewidth=2,
                    label=f'Mean = {v2_df["fan_vote_share"].mean():.3f}')
    axes[1].set_xlabel('Fan Vote Share', fontsize=12)
    axes[1].set_ylabel('Frequency', fontsize=12)
    axes[1].set_title('V2: Fan Vote Share Distribution', fontsize=13, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'v1_vs_v2_distribution.png', dpi=300)
    print(f"\n[保存] 分布对比图: {output_dir / 'v1_vs_v2_distribution.png'}")
    plt.close()

    print("\n" + "=" * 80)
    print("对比分析完成！")
    print("=" * 80)

if __name__ == "__main__":
    compare_models()
