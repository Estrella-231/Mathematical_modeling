"""
交互式数据查看工具
使用方法：python interactive_view.py
"""
import pandas as pd
from pathlib import Path

def main():
    processed_dir = Path("F:/Mathematical_modeling/solution/Data/processed")

    # 加载数据
    weekly = pd.read_csv(processed_dir / "weekly_panel.csv")
    static = pd.read_csv(processed_dir / "contestant_static.csv")
    season = pd.read_csv(processed_dir / "season_meta.csv")

    print("=" * 80)
    print("交互式数据查看工具")
    print("=" * 80)
    print("\n可用的数据集：")
    print("1. weekly - 周级面板数据 (4,631 行)")
    print("2. static - 选手静态数据 (421 行)")
    print("3. season - 赛季元数据 (34 行)")
    print("\n示例查询：")
    print("-" * 80)

    # 示例 1：查看某个选手的所有数据
    print("\n[示例 1] Kelly Monaco (Season 1 冠军) 的周数据：")
    kelly = weekly[(weekly['celebrity_name'] == 'Kelly Monaco') & (weekly['season'] == 1)]
    print(kelly[['week', 'judge_total', 'judge_rank_in_week', 'relative_judge_score',
                 'cumulative_average', 'trend', 'week_valid']].to_string(index=False))

    # 示例 2：查看某一周的所有选手排名
    print("\n[示例 2] Season 1, Week 1 的所有选手排名：")
    week1 = weekly[(weekly['season'] == 1) & (weekly['week'] == 1) & (weekly['week_valid'] == True)]
    week1_sorted = week1.sort_values('judge_rank_in_week')
    print(week1_sorted[['celebrity_name', 'judge_total', 'judge_rank_in_week',
                        'relative_judge_score']].to_string(index=False))

    # 示例 3：查看某个赛季的元数据
    print("\n[示例 3] Season 1 的元数据：")
    s1_meta = season[season['season'] == 1]
    print(s1_meta.to_string(index=False))

    # 示例 4：查看行业分布
    print("\n[示例 4] 行业分布 (Top 5)：")
    industry_dist = static['celebrity_industry'].value_counts().head(5)
    for industry, count in industry_dist.items():
        print(f"  {industry}: {count} 人")

    # 示例 5：查看年龄分组
    print("\n[示例 5] 年龄分组分布：")
    age_dist = static['age_group'].value_counts().sort_index()
    for age_group, count in age_dist.items():
        print(f"  {age_group}: {count} 人 ({count/len(static)*100:.1f}%)")

    # 示例 6：查看评委分数统计
    print("\n[示例 6] 评委分数统计 (有效数据)：")
    valid_scores = weekly[weekly['week_valid']]['judge_total']
    print(f"  最小值: {valid_scores.min():.2f}")
    print(f"  最大值: {valid_scores.max():.2f}")
    print(f"  平均值: {valid_scores.mean():.2f}")
    print(f"  中位数: {valid_scores.median():.2f}")
    print(f"  标准差: {valid_scores.std():.2f}")

    # 示例 7：查看淘汰周分布
    print("\n[示例 7] 淘汰周分布：")
    elim_dist = static[static['elimination_week'] > 0]['elimination_week'].value_counts().sort_index()
    for week, count in elim_dist.head(10).items():
        print(f"  Week {int(week)}: {count} 人被淘汰")

    # 示例 8：查看训练集和测试集的分布
    print("\n[示例 8] 训练集 vs 测试集：")
    train_seasons = weekly[weekly['season'] <= 27]['season'].nunique()
    test_seasons = weekly[weekly['season'] >= 28]['season'].nunique()
    train_rows = len(weekly[weekly['season'] <= 27])
    test_rows = len(weekly[weekly['season'] >= 28])
    print(f"  训练集: {train_seasons} 个赛季, {train_rows} 行数据")
    print(f"  测试集: {test_seasons} 个赛季, {test_rows} 行数据")

    print("\n" + "=" * 80)
    print("提示：你可以修改这个脚本来查看其他数据")
    print("=" * 80)

if __name__ == "__main__":
    main()
