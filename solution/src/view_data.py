"""
查看数据处理输出的快速脚本
"""
import pandas as pd
from pathlib import Path

# 设置显示选项
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)

def view_processed_data():
    processed_dir = Path("F:/Mathematical_modeling/solution/Data/processed")

    print("=" * 80)
    print("数据处理输出查看")
    print("=" * 80)

    # 1. weekly_panel.csv
    print("\n[1] weekly_panel.csv - 前10行")
    print("-" * 80)
    weekly = pd.read_csv(processed_dir / "weekly_panel.csv")
    print(weekly.head(10))
    print(f"\n形状: {weekly.shape}")
    print(f"列名: {list(weekly.columns)}")

    # 2. 查看某个具体选手的完整数据
    print("\n" + "=" * 80)
    print("[2] 示例：Kelly Monaco (Season 1 冠军) 的完整数据")
    print("-" * 80)
    kelly = weekly[(weekly['celebrity_name'] == 'Kelly Monaco') & (weekly['season'] == 1)]
    print(kelly[['week', 'judge_total', 'judge_rank_in_week', 'week_valid',
                 'relative_judge_score', 'cumulative_average', 'trend']].to_string())

    # 3. contestant_static.csv
    print("\n" + "=" * 80)
    print("[3] contestant_static.csv - 前10行")
    print("-" * 80)
    static = pd.read_csv(processed_dir / "contestant_static.csv")
    print(static.head(10))

    # 4. season_meta.csv
    print("\n" + "=" * 80)
    print("[4] season_meta.csv - 所有赛季")
    print("-" * 80)
    season = pd.read_csv(processed_dir / "season_meta.csv")
    print(season.to_string())

    # 5. 数据统计
    print("\n" + "=" * 80)
    print("[5] 关键统计信息")
    print("-" * 80)
    print(f"总选手数: {weekly['celebrity_name'].nunique()}")
    print(f"总赛季数: {weekly['season'].nunique()}")
    print(f"总周数据: {len(weekly)}")
    print(f"有效周数据: {weekly['week_valid'].sum()}")
    print(f"有效比例: {weekly['week_valid'].sum() / len(weekly):.2%}")

    print("\n评委分数统计 (有效数据):")
    valid_scores = weekly[weekly['week_valid']]['judge_total']
    print(valid_scores.describe())

    print("\n年龄分组分布:")
    print(static['age_group'].value_counts().sort_index())

    print("\n行业分布 (Top 10):")
    print(static['celebrity_industry'].value_counts().head(10))

if __name__ == "__main__":
    view_processed_data()
