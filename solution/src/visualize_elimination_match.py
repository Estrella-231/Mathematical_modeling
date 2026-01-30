"""
淘汰匹配率可视化
Elimination Match Rate Visualization
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from collections import defaultdict


def compute_detailed_elimination_match_rate(df: pd.DataFrame):
    """
    计算详细的淘汰匹配率（按赛季、按周）

    Returns:
    --------
    match_by_season: 按赛季的匹配率
    match_by_week: 按周的匹配率
    overall_match_rate: 总体匹配率
    details: 详细的匹配信息
    """
    correct_eliminations = 0
    total_weeks = 0

    match_by_season = defaultdict(lambda: {'correct': 0, 'total': 0})
    match_by_week = defaultdict(lambda: {'correct': 0, 'total': 0})

    details = []

    for (season, week), group in df.groupby(['season', 'week']):
        if len(group) <= 3:  # 跳过人数太少的周
            continue

        # 使用 Rank Sum 方法
        judge_rank = group['judge_rank_in_week']
        fan_rank = group['fan_vote_share'].rank(ascending=False)

        combined_rank = judge_rank + fan_rank

        # 预测淘汰者（综合排名最差）
        predicted_eliminated_idx = combined_rank.idxmax()
        predicted_eliminated = group.loc[predicted_eliminated_idx, 'celebrity_name']

        # 实际淘汰者
        actual_eliminated_mask = (
            (group['week'] == group['elimination_week']) &
            (group['elimination_week'] > 0)
        )

        if actual_eliminated_mask.any():
            actual_eliminated_idx = group[actual_eliminated_mask].index[0]
            actual_eliminated = group.loc[actual_eliminated_idx, 'celebrity_name']

            is_match = (predicted_eliminated_idx == actual_eliminated_idx)

            if is_match:
                correct_eliminations += 1
                match_by_season[season]['correct'] += 1
                match_by_week[week]['correct'] += 1

            match_by_season[season]['total'] += 1
            match_by_week[week]['total'] += 1
            total_weeks += 1

            details.append({
                'season': season,
                'week': week,
                'predicted': predicted_eliminated,
                'actual': actual_eliminated,
                'match': is_match,
                'num_contestants': len(group)
            })

    overall_match_rate = correct_eliminations / total_weeks if total_weeks > 0 else 0

    return match_by_season, match_by_week, overall_match_rate, details


def visualize_elimination_match_rate(data_path: Path, output_dir: Path):
    """
    生成淘汰匹配率相关的可视化
    """
    print("=" * 80)
    print("淘汰匹配率可视化")
    print("=" * 80)

    # 加载数据
    df = pd.read_csv(data_path)
    print(f"\n加载数据: {len(df)} 行")

    # 计算详细匹配率
    print("\n计算淘汰匹配率...")
    match_by_season, match_by_week, overall_rate, details = compute_detailed_elimination_match_rate(df)

    print(f"\n总体淘汰匹配率: {overall_rate:.2%}")
    print(f"总周数: {len(details)}")
    print(f"正确预测: {sum(d['match'] for d in details)}")

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 按赛季的匹配率
    seasons = sorted(match_by_season.keys())
    season_rates = [match_by_season[s]['correct'] / match_by_season[s]['total']
                    if match_by_season[s]['total'] > 0 else 0
                    for s in seasons]

    plt.figure(figsize=(14, 6))
    bars = plt.bar(seasons, season_rates, edgecolor='black', alpha=0.7)

    # 颜色编码：高匹配率（绿色），低匹配率（红色）
    for i, (bar, rate) in enumerate(zip(bars, season_rates)):
        if rate >= 0.9:
            bar.set_color('green')
        elif rate >= 0.7:
            bar.set_color('orange')
        else:
            bar.set_color('red')

    plt.axhline(y=overall_rate, color='blue', linestyle='--', linewidth=2,
                label=f'Overall: {overall_rate:.1%}')
    plt.xlabel('Season', fontsize=12)
    plt.ylabel('Elimination Match Rate', fontsize=12)
    plt.title('Elimination Match Rate by Season', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.ylim(0, 1.05)

    # 添加数值标签
    for i, (s, rate) in enumerate(zip(seasons, season_rates)):
        plt.text(s, rate + 0.02, f'{rate:.0%}', ha='center', fontsize=8)

    plt.tight_layout()
    plt.savefig(output_dir / 'match_rate_by_season.png', dpi=300)
    print(f"\n[保存] 按赛季匹配率: {output_dir / 'match_rate_by_season.png'}")
    plt.close()

    # 2. 按周的匹配率
    weeks = sorted(match_by_week.keys())
    week_rates = [match_by_week[w]['correct'] / match_by_week[w]['total']
                  if match_by_week[w]['total'] > 0 else 0
                  for w in weeks]
    week_counts = [match_by_week[w]['total'] for w in weeks]

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 匹配率（柱状图）
    color = 'tab:blue'
    ax1.set_xlabel('Week', fontsize=12)
    ax1.set_ylabel('Match Rate', fontsize=12, color=color)
    bars = ax1.bar(weeks, week_rates, alpha=0.7, edgecolor='black', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.axhline(y=overall_rate, color='red', linestyle='--', linewidth=2,
                label=f'Overall: {overall_rate:.1%}')
    ax1.set_ylim(0, 1.05)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3, axis='y')

    # 样本数量（折线图）
    ax2 = ax1.twinx()
    color = 'tab:orange'
    ax2.set_ylabel('Number of Weeks', fontsize=12, color=color)
    ax2.plot(weeks, week_counts, color=color, marker='o', linewidth=2, label='Sample Size')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.legend(loc='upper right')

    plt.title('Elimination Match Rate by Week', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'match_rate_by_week.png', dpi=300)
    print(f"[保存] 按周匹配率: {output_dir / 'match_rate_by_week.png'}")
    plt.close()

    # 3. 混淆矩阵风格的可视化
    details_df = pd.DataFrame(details)

    plt.figure(figsize=(10, 6))

    # 统计匹配和不匹配的数量
    match_count = details_df['match'].sum()
    mismatch_count = len(details_df) - match_count

    categories = ['Correct\nPrediction', 'Incorrect\nPrediction']
    counts = [match_count, mismatch_count]
    colors = ['green', 'red']

    bars = plt.bar(categories, counts, color=colors, alpha=0.7, edgecolor='black')

    # 添加百分比标签
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        percentage = count / len(details_df) * 100
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{count}\n({percentage:.1f}%)',
                ha='center', va='bottom', fontsize=14, fontweight='bold')

    plt.ylabel('Number of Weeks', fontsize=12)
    plt.title(f'Elimination Prediction Accuracy\nOverall Match Rate: {overall_rate:.1%}',
              fontsize=14, fontweight='bold')
    plt.ylim(0, max(counts) * 1.15)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_dir / 'match_rate_summary.png', dpi=300)
    print(f"[保存] 匹配率总结: {output_dir / 'match_rate_summary.png'}")
    plt.close()

    # 4. 按选手数量的匹配率
    details_df['num_contestants_bin'] = pd.cut(details_df['num_contestants'],
                                                bins=[0, 6, 8, 10, 20],
                                                labels=['4-6', '7-8', '9-10', '11+'])

    match_by_size = details_df.groupby('num_contestants_bin').agg({
        'match': ['sum', 'count', 'mean']
    }).reset_index()
    match_by_size.columns = ['num_contestants', 'correct', 'total', 'rate']

    plt.figure(figsize=(10, 6))
    bars = plt.bar(match_by_size['num_contestants'], match_by_size['rate'],
                   edgecolor='black', alpha=0.7)

    # 颜色编码
    for bar, rate in zip(bars, match_by_size['rate']):
        if rate >= 0.9:
            bar.set_color('green')
        elif rate >= 0.7:
            bar.set_color('orange')
        else:
            bar.set_color('red')

    plt.axhline(y=overall_rate, color='blue', linestyle='--', linewidth=2,
                label=f'Overall: {overall_rate:.1%}')
    plt.xlabel('Number of Contestants in Week', fontsize=12)
    plt.ylabel('Match Rate', fontsize=12)
    plt.title('Elimination Match Rate by Number of Contestants', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.ylim(0, 1.05)

    # 添加标签
    for i, row in match_by_size.iterrows():
        plt.text(i, row['rate'] + 0.02,
                f"{row['rate']:.0%}\n(n={int(row['total'])})",
                ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_dir / 'match_rate_by_size.png', dpi=300)
    print(f"[保存] 按选手数量匹配率: {output_dir / 'match_rate_by_size.png'}")
    plt.close()

    # 5. 时间序列：累积匹配率
    details_df_sorted = details_df.sort_values(['season', 'week'])
    details_df_sorted['cumulative_correct'] = details_df_sorted['match'].cumsum()
    details_df_sorted['cumulative_total'] = range(1, len(details_df_sorted) + 1)
    details_df_sorted['cumulative_rate'] = (details_df_sorted['cumulative_correct'] /
                                             details_df_sorted['cumulative_total'])

    plt.figure(figsize=(14, 6))
    plt.plot(details_df_sorted['cumulative_total'],
             details_df_sorted['cumulative_rate'],
             linewidth=2, color='blue')
    plt.axhline(y=overall_rate, color='red', linestyle='--', linewidth=2,
                label=f'Final Rate: {overall_rate:.1%}')
    plt.xlabel('Cumulative Number of Weeks', fontsize=12)
    plt.ylabel('Cumulative Match Rate', fontsize=12)
    plt.title('Cumulative Elimination Match Rate Over Time', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1.05)
    plt.tight_layout()
    plt.savefig(output_dir / 'cumulative_match_rate.png', dpi=300)
    print(f"[保存] 累积匹配率: {output_dir / 'cumulative_match_rate.png'}")
    plt.close()

    # 6. 输出详细统计
    print("\n" + "=" * 80)
    print("详细统计")
    print("=" * 80)

    print("\n[按赛季匹配率] (Top 10 最高)")
    season_stats = [(s, match_by_season[s]['correct'] / match_by_season[s]['total'])
                    for s in seasons if match_by_season[s]['total'] > 0]
    season_stats.sort(key=lambda x: x[1], reverse=True)
    for s, rate in season_stats[:10]:
        print(f"  Season {s}: {rate:.1%} ({match_by_season[s]['correct']}/{match_by_season[s]['total']})")

    print("\n[按周匹配率]")
    for w in weeks:
        if match_by_week[w]['total'] > 0:
            rate = match_by_week[w]['correct'] / match_by_week[w]['total']
            print(f"  Week {w}: {rate:.1%} ({match_by_week[w]['correct']}/{match_by_week[w]['total']})")

    print("\n[按选手数量匹配率]")
    for _, row in match_by_size.iterrows():
        print(f"  {row['num_contestants']} contestants: {row['rate']:.1%} ({int(row['correct'])}/{int(row['total'])})")

    # 保存详细结果到 CSV
    details_df.to_csv(output_dir / 'elimination_match_details.csv', index=False)
    print(f"\n[保存] 详细匹配结果: {output_dir / 'elimination_match_details.csv'}")

    print("\n" + "=" * 80)
    print("可视化完成！")
    print("=" * 80)


if __name__ == "__main__":
    data_path = Path("F:/Mathematical_modeling/solution/Data/models/ridge_v2/ridge_fan_vote_shares_v2.csv")
    output_dir = Path("F:/Mathematical_modeling/solution/figures/elimination_match_rate")

    visualize_elimination_match_rate(data_path, output_dir)
