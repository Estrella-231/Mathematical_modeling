"""
Model C 可视化：反事实模拟结果分析
根据 docs/10_model_c_comparison.md 实现

包含：
1. 翻转率分析图
2. FFI (Fan Favorability Index) 分布图
3. 争议案例分析图
4. 推荐机制评分图
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def plot_ffi_distribution(results_df: pd.DataFrame, output_dir: Path):
    """
    绘制 FFI 分布图
    """
    print("\n[图表] FFI 分布分析")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 各规则的 FFI 列
    ffi_cols = {
        'Rank Sum': 'ffi_rank_sum',
        'Percent Sum': 'ffi_percent_sum',
        'Judge Save': 'ffi_judge_save',
        'Actual': 'ffi_actual'
    }

    colors = ['steelblue', 'coral', 'lightgreen', 'gold']

    for ax, (rule_name, col), color in zip(axes.flatten(), ffi_cols.items(), colors):
        if col in results_df.columns:
            data = results_df[col].dropna()
            ax.hist(data, bins=20, color=color, alpha=0.7, edgecolor='black')
            ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Neutral (FFI=0)')
            ax.axvline(x=data.mean(), color='darkblue', linestyle='-', linewidth=2,
                      label=f'Mean: {data.mean():.3f}')
            ax.set_xlabel('Fan Favorability Index (FFI)', fontsize=10)
            ax.set_ylabel('Frequency', fontsize=10)
            ax.set_title(f'{rule_name}\n(Positive = Fan Favorite Eliminated)', fontsize=11, fontweight='bold')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)

    plt.suptitle('FFI Distribution of Eliminated Contestants by Rule',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / 'ffi_distribution.png', dpi=300, bbox_inches='tight')
    print(f"  - 保存: {output_dir / 'ffi_distribution.png'}")
    plt.close()


def plot_ffi_comparison(results_df: pd.DataFrame, output_dir: Path):
    """
    绘制 FFI 规则对比图
    """
    print("\n[图表] FFI 规则对比")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 左图：各规则的平均 FFI
    ffi_cols = ['ffi_rank_sum', 'ffi_percent_sum', 'ffi_judge_save', 'ffi_actual']
    rule_names = ['Rank Sum', 'Percent Sum', 'Judge Save', 'Actual']
    colors = ['steelblue', 'coral', 'lightgreen', 'gold']

    means = []
    stds = []
    for col in ffi_cols:
        if col in results_df.columns:
            data = results_df[col].dropna()
            means.append(data.mean())
            stds.append(data.std())
        else:
            means.append(0)
            stds.append(0)

    x = np.arange(len(rule_names))
    bars = axes[0].bar(x, means, yerr=stds, color=colors, alpha=0.8,
                       edgecolor='black', capsize=5)
    axes[0].axhline(y=0, color='red', linestyle='--', linewidth=2)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(rule_names)
    axes[0].set_ylabel('Mean FFI', fontsize=11)
    axes[0].set_title('Average FFI by Rule\n(Error bars = Std Dev)', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='y')

    # 添加数值标签
    for bar, mean in zip(bars, means):
        height = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{mean:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # 右图：粉丝偏好 vs 评委偏好比例
    positive_rates = []
    negative_rates = []
    for col in ffi_cols:
        if col in results_df.columns:
            data = results_df[col].dropna()
            positive_rates.append((data > 0).mean())
            negative_rates.append((data < 0).mean())
        else:
            positive_rates.append(0)
            negative_rates.append(0)

    width = 0.35
    axes[1].bar(x - width/2, positive_rates, width, label='Fan Favorite (FFI > 0)',
                color='coral', alpha=0.8, edgecolor='black')
    axes[1].bar(x + width/2, negative_rates, width, label='Judge Favorite (FFI < 0)',
                color='steelblue', alpha=0.8, edgecolor='black')
    axes[1].axhline(y=0.5, color='gray', linestyle='--', linewidth=1, label='50% Balance')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(rule_names)
    axes[1].set_ylabel('Proportion of Eliminations', fontsize=11)
    axes[1].set_title('Who Gets Eliminated More Often?', fontsize=12, fontweight='bold')
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.3, axis='y')
    axes[1].set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(output_dir / 'ffi_comparison.png', dpi=300)
    print(f"  - 保存: {output_dir / 'ffi_comparison.png'}")
    plt.close()


def plot_recommendation_scores(results_df: pd.DataFrame, output_dir: Path):
    """
    绘制推荐机制评分图
    """
    print("\n[图表] 推荐机制评分")

    # 计算各规则的评分
    ffi_cols = {
        'rank_sum': 'ffi_rank_sum',
        'percent_sum': 'ffi_percent_sum',
        'judge_save': 'ffi_judge_save'
    }

    scores = {}
    for rule, col in ffi_cols.items():
        if col in results_df.columns:
            data = results_df[col].dropna()
            mean_ffi = data.mean()
            std_ffi = data.std()
            positive_rate = (data > 0).mean()

            fairness = 1 - abs(mean_ffi)
            balance = 1 - abs(positive_rate - 0.5) * 2
            stability = 1 - min(std_ffi, 1)
            total = fairness * 0.4 + balance * 0.3 + stability * 0.3

            scores[rule] = {
                'Fairness\n(40%)': fairness,
                'Balance\n(30%)': balance,
                'Stability\n(30%)': stability,
                'Total': total
            }

    # 绘制雷达图
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 左图：各维度评分对比
    metrics = ['Fairness\n(40%)', 'Balance\n(30%)', 'Stability\n(30%)']
    x = np.arange(len(metrics))
    width = 0.25
    colors = ['steelblue', 'coral', 'lightgreen']

    for i, (rule, score_dict) in enumerate(scores.items()):
        values = [score_dict[m] for m in metrics]
        axes[0].bar(x + i * width, values, width, label=rule.replace('_', ' ').title(),
                   color=colors[i], alpha=0.8, edgecolor='black')

    axes[0].set_xticks(x + width)
    axes[0].set_xticklabels(metrics)
    axes[0].set_ylabel('Score (0-1)', fontsize=11)
    axes[0].set_title('Rule Evaluation by Criteria', fontsize=12, fontweight='bold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3, axis='y')
    axes[0].set_ylim(0, 1.1)

    # 右图：总分对比
    rule_names = [r.replace('_', ' ').title() for r in scores.keys()]
    total_scores = [s['Total'] for s in scores.values()]

    bars = axes[1].bar(rule_names, total_scores, color=colors, alpha=0.8, edgecolor='black')

    # 标记最高分
    max_idx = np.argmax(total_scores)
    bars[max_idx].set_color('gold')
    bars[max_idx].set_edgecolor('darkgoldenrod')
    bars[max_idx].set_linewidth(2)

    for bar, score in zip(bars, total_scores):
        height = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{score:.3f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

    axes[1].set_ylabel('Total Score', fontsize=11)
    axes[1].set_title('Overall Recommendation Score\n(★ = Recommended)', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    axes[1].set_ylim(0, 1.1)

    # 添加推荐标记
    axes[1].annotate('★ Recommended', xy=(max_idx, total_scores[max_idx]),
                    xytext=(max_idx, total_scores[max_idx] + 0.1),
                    ha='center', fontsize=11, color='darkgoldenrod', fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_dir / 'recommendation_scores.png', dpi=300)
    print(f"  - 保存: {output_dir / 'recommendation_scores.png'}")
    plt.close()


def plot_ffi_by_season(results_df: pd.DataFrame, output_dir: Path):
    """
    绘制 FFI 按赛季变化图
    """
    print("\n[图表] FFI 按赛季变化")

    fig, ax = plt.subplots(figsize=(14, 6))

    ffi_cols = {
        'Rank Sum': 'ffi_rank_sum',
        'Percent Sum': 'ffi_percent_sum',
        'Judge Save': 'ffi_judge_save'
    }
    colors = ['steelblue', 'coral', 'lightgreen']
    markers = ['o', 's', '^']

    for (rule_name, col), color, marker in zip(ffi_cols.items(), colors, markers):
        if col in results_df.columns:
            season_ffi = results_df.groupby('season')[col].mean()
            ax.plot(season_ffi.index, season_ffi.values, marker=marker, color=color,
                   label=rule_name, linewidth=2, markersize=6, alpha=0.8)

    ax.axhline(y=0, color='red', linestyle='--', linewidth=2, label='Neutral (FFI=0)')
    ax.set_xlabel('Season', fontsize=12)
    ax.set_ylabel('Mean FFI', fontsize=12)
    ax.set_title('Average FFI by Season\n(Positive = More Fan Favorites Eliminated)',
                fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'ffi_by_season.png', dpi=300)
    print(f"  - 保存: {output_dir / 'ffi_by_season.png'}")
    plt.close()


def visualize_simulation_results(results_path: Path, case_path: Path, output_dir: Path):
    """
    可视化反事实模拟结果
    """
    print("=" * 80)
    print("Model C 可视化：投票规则对比分析")
    print("=" * 80)

    # 加载数据
    results_df = pd.read_csv(results_path)

    # 尝试加载争议案例数据
    case_df = None
    if case_path.exists():
        case_df = pd.read_csv(case_path)
        print(f"\n加载数据:")
        print(f"  - 模拟结果: {len(results_df)} 周")
        print(f"  - 争议案例: {len(case_df)} 条记录")
    else:
        print(f"\n加载数据:")
        print(f"  - 模拟结果: {len(results_df)} 周")
        print(f"  - 争议案例文件不存在，跳过案例分析")

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # ========== FFI 相关图表 ==========
    # 检查是否有 FFI 列
    if 'ffi_rank_sum' in results_df.columns:
        plot_ffi_distribution(results_df, output_dir)
        plot_ffi_comparison(results_df, output_dir)
        plot_ffi_by_season(results_df, output_dir)
        plot_recommendation_scores(results_df, output_dir)

    # ========== 翻转率图表 ==========
    # 1. 翻转率按赛季分析
    print("\n[图表 1] 翻转率按赛季分析")
    plt.figure(figsize=(14, 6))

    season_flip = results_df.groupby('season').agg({
        'rank_vs_percent_same': lambda x: 1 - x.mean(),
        'rank_vs_judge_save_same': lambda x: 1 - x.mean(),
        'percent_vs_judge_save_same': lambda x: 1 - x.mean()
    })

    x = season_flip.index
    width = 0.25

    plt.bar(x - width, season_flip['rank_vs_percent_same'], width,
            label='Rank vs Percent', alpha=0.8, edgecolor='black')
    plt.bar(x, season_flip['rank_vs_judge_save_same'], width,
            label='Rank vs Judge Save', alpha=0.8, edgecolor='black')
    plt.bar(x + width, season_flip['percent_vs_judge_save_same'], width,
            label='Percent vs Judge Save', alpha=0.8, edgecolor='black')

    plt.xlabel('Season', fontsize=12)
    plt.ylabel('Flip Rate (Different Elimination)', fontsize=12)
    plt.title('Flip Rate by Season: How Often Do Different Rules Produce Different Results?',
              fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_dir / 'flip_rate_by_season.png', dpi=300)
    print(f"  - 保存: {output_dir / 'flip_rate_by_season.png'}")
    plt.close()

    # 2. 总体翻转率对比
    print("\n[图表 2] 总体翻转率对比")
    plt.figure(figsize=(10, 6))

    flip_rates = {
        'Rank vs\nPercent': 1 - results_df['rank_vs_percent_same'].mean(),
        'Rank vs\nJudge Save': 1 - results_df['rank_vs_judge_save_same'].mean(),
        'Percent vs\nJudge Save': 1 - results_df['percent_vs_judge_save_same'].mean(),
        'All Three\nDifferent': 1 - results_df['all_same'].mean()
    }

    colors = ['steelblue', 'coral', 'lightgreen', 'gold']
    bars = plt.bar(flip_rates.keys(), flip_rates.values(), color=colors,
                   alpha=0.8, edgecolor='black')

    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{height:.1%}', ha='center', va='bottom', fontsize=12, fontweight='bold')

    plt.ylabel('Flip Rate', fontsize=12)
    plt.title('Overall Flip Rate: How Often Do Rules Disagree?',
              fontsize=14, fontweight='bold')
    plt.ylim(0, max(flip_rates.values()) * 1.15)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_dir / 'overall_flip_rate.png', dpi=300)
    print(f"  - 保存: {output_dir / 'overall_flip_rate.png'}")
    plt.close()

    # 3. 争议案例生存曲线
    if case_df is not None and len(case_df) > 0:
        print("\n[图表 3] 争议案例生存曲线")

        # 按选手分组
        for celebrity_name in case_df['celebrity_name'].unique():
            celebrity_cases = case_df[case_df['celebrity_name'] == celebrity_name]
            season = celebrity_cases['season'].iloc[0]

            plt.figure(figsize=(10, 6))

            # 绘制每种规则下的生存周数
            rules = celebrity_cases['rule'].unique()
            x_pos = np.arange(len(rules))

            weeks_survived = []
            colors_list = []

            for rule in rules:
                weeks = celebrity_cases[celebrity_cases['rule'] == rule]['weeks_survived'].iloc[0]
                weeks_survived.append(weeks)

                # 颜色编码
                if rule == 'rank_sum':
                    colors_list.append('steelblue')
                elif rule == 'percent_sum':
                    colors_list.append('coral')
                else:
                    colors_list.append('lightgreen')

            bars = plt.bar(x_pos, weeks_survived, color=colors_list, alpha=0.8, edgecolor='black')

            # 添加实际淘汰周的参考线
            actual_week = celebrity_cases['actual_elimination_week'].iloc[0]
            if actual_week < 900:  # 不是决赛
                plt.axhline(y=actual_week, color='red', linestyle='--', linewidth=2,
                           label=f'Actual Elimination (Week {actual_week})')

            # 添加数值标签
            for i, bar in enumerate(bars):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                        f'{int(height)}', ha='center', va='bottom', fontsize=11, fontweight='bold')

            plt.xticks(x_pos, [r.replace('_', ' ').title() for r in rules])
            plt.ylabel('Weeks Survived', fontsize=12)
            plt.title(f'{celebrity_name} (Season {season}): Survival Under Different Rules',
                      fontsize=14, fontweight='bold')
            plt.legend()
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()

            safe_name = celebrity_name.replace(' ', '_')
            plt.savefig(output_dir / f'case_study_{safe_name}_S{season}.png', dpi=300)
            print(f"  - 保存: {output_dir / f'case_study_{safe_name}_S{season}.png'}")
            plt.close()
    else:
        print("\n[图表 3] 争议案例生存曲线 - 跳过（无案例数据）")

    # 4. 规则一致性矩阵
    print("\n[图表 4] 规则一致性矩阵")
    plt.figure(figsize=(8, 6))

    # 计算一致性矩阵
    consistency_matrix = np.array([
        [1.0, results_df['rank_vs_percent_same'].mean(), results_df['rank_vs_judge_save_same'].mean()],
        [results_df['rank_vs_percent_same'].mean(), 1.0, results_df['percent_vs_judge_save_same'].mean()],
        [results_df['rank_vs_judge_save_same'].mean(), results_df['percent_vs_judge_save_same'].mean(), 1.0]
    ])

    labels = ['Rank Sum', 'Percent Sum', 'Judge Save']

    im = plt.imshow(consistency_matrix, cmap='RdYlGn', vmin=0, vmax=1)

    # 添加数值标签
    for i in range(3):
        for j in range(3):
            text = plt.text(j, i, f'{consistency_matrix[i, j]:.1%}',
                          ha="center", va="center", color="black", fontsize=14, fontweight='bold')

    plt.xticks(range(3), labels, rotation=45, ha='right')
    plt.yticks(range(3), labels)
    plt.title('Rule Consistency Matrix\n(% of Weeks with Same Elimination)',
              fontsize=14, fontweight='bold')
    plt.colorbar(im, label='Consistency Rate')
    plt.tight_layout()
    plt.savefig(output_dir / 'rule_consistency_matrix.png', dpi=300)
    print(f"  - 保存: {output_dir / 'rule_consistency_matrix.png'}")
    plt.close()

    # 5. 按选手数量的翻转率
    print("\n[图表 5] 按选手数量的翻转率")
    plt.figure(figsize=(10, 6))

    # 按选手数量分组
    results_df['contestant_bin'] = pd.cut(results_df['num_contestants'],
                                           bins=[0, 5, 7, 9, 20],
                                           labels=['3-5', '6-7', '8-9', '10+'])

    flip_by_size = results_df.groupby('contestant_bin').agg({
        'rank_vs_percent_same': lambda x: 1 - x.mean(),
        'rank_vs_judge_save_same': lambda x: 1 - x.mean(),
        'percent_vs_judge_save_same': lambda x: 1 - x.mean()
    })

    x = np.arange(len(flip_by_size))
    width = 0.25

    plt.bar(x - width, flip_by_size['rank_vs_percent_same'], width,
            label='Rank vs Percent', alpha=0.8, edgecolor='black')
    plt.bar(x, flip_by_size['rank_vs_judge_save_same'], width,
            label='Rank vs Judge Save', alpha=0.8, edgecolor='black')
    plt.bar(x + width, flip_by_size['percent_vs_judge_save_same'], width,
            label='Percent vs Judge Save', alpha=0.8, edgecolor='black')

    plt.xticks(x, flip_by_size.index)
    plt.xlabel('Number of Contestants', fontsize=12)
    plt.ylabel('Flip Rate', fontsize=12)
    plt.title('Flip Rate by Number of Contestants',
              fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_dir / 'flip_rate_by_size.png', dpi=300)
    print(f"  - 保存: {output_dir / 'flip_rate_by_size.png'}")
    plt.close()

    print("\n" + "=" * 80)
    print("可视化完成！")
    print("=" * 80)


if __name__ == "__main__":
    results_path = Path("F:/Mathematical_modeling/solution/Data/simulation/simulation_results.csv")
    case_path = Path("F:/Mathematical_modeling/solution/Data/simulation/controversy_case_analysis.csv")
    output_dir = Path("F:/Mathematical_modeling/solution/figures/simulation")

    visualize_simulation_results(results_path, case_path, output_dir)
