"""
数据质量验证脚本 (Data Quality Validation)
"""
import pandas as pd
from pathlib import Path
from config import DATA_DIR


def validate_data_quality():
    """验证处理后数据的质量"""
    print("=" * 60)
    print("数据质量验证 (Data Quality Validation)")
    print("=" * 60)

    processed_dir = DATA_DIR / "processed"

    # 1. 加载所有处理后的文件
    print("\n[1] 加载处理后的数据文件")
    weekly_panel = pd.read_csv(processed_dir / "weekly_panel.csv")
    contestant_static = pd.read_csv(processed_dir / "contestant_static.csv")
    season_meta = pd.read_csv(processed_dir / "season_meta.csv")
    train_panel = pd.read_csv(processed_dir / "train_panel.csv")
    test_panel = pd.read_csv(processed_dir / "test_panel.csv")

    print(f"  [OK] weekly_panel: {weekly_panel.shape}")
    print(f"  [OK] contestant_static: {contestant_static.shape}")
    print(f"  [OK] season_meta: {season_meta.shape}")
    print(f"  [OK] train_panel: {train_panel.shape}")
    print(f"  [OK] test_panel: {test_panel.shape}")

    # 2. 验证数据完整性
    print("\n[2] 验证数据完整性")

    # 检查训练集和测试集的分割
    train_seasons = train_panel['season'].unique()
    test_seasons = test_panel['season'].unique()
    print(f"  [OK] 训练集赛季: {train_seasons.min()}-{train_seasons.max()}")
    print(f"  [OK] 测试集赛季: {test_seasons.min()}-{test_seasons.max()}")

    # 检查是否有重叠
    overlap = set(train_seasons) & set(test_seasons)
    if overlap:
        print(f"  [WARN] 警告: 训练集和测试集有重叠赛季: {overlap}")
    else:
        print(f"  [OK] 训练集和测试集无重叠")

    # 3. 验证特征生成
    print("\n[3] 验证特征生成")
    required_features = [
        'judge_total', 'judge_rank_in_week', 'week_valid',
        'relative_judge_score', 'cumulative_average', 'trend',
        'is_bottom_2_judge', 'elimination_week'
    ]

    for feat in required_features:
        if feat in weekly_panel.columns:
            print(f"  [OK] {feat}")
        else:
            print(f"  [MISSING] 缺失特征: {feat}")

    # 4. 验证数据质量指标
    print("\n[4] 数据质量指标")

    # 有效周数据比例
    valid_ratio = weekly_panel['week_valid'].sum() / len(weekly_panel)
    print(f"  - 有效周数据比例: {valid_ratio:.2%}")

    # judge_total 的缺失率
    judge_total_missing = weekly_panel['judge_total'].isna().sum() / len(weekly_panel)
    print(f"  - judge_total 缺失率: {judge_total_missing:.2%}")

    # 淘汰周解析成功率
    valid_elimination = (contestant_static['elimination_week'] > 0).sum()
    total_contestants = len(contestant_static)
    print(f"  - 淘汰周解析成功: {valid_elimination}/{total_contestants} ({valid_elimination/total_contestants:.2%})")

    # 5. 验证标准化分数
    print("\n[5] 验证标准化分数 (judge_total)")
    valid_scores = weekly_panel[weekly_panel['week_valid']]['judge_total']
    print(f"  - 最小值: {valid_scores.min():.2f}")
    print(f"  - 最大值: {valid_scores.max():.2f}")
    print(f"  - 平均值: {valid_scores.mean():.2f}")
    print(f"  - 标准差: {valid_scores.std():.2f}")
    print(f"  - 理论范围: 30-300 (1-10分 × 3评委 × 标准化)")

    # 6. 验证年龄分组
    print("\n[6] 年龄分组分布")
    age_dist = contestant_static['age_group'].value_counts().sort_index()
    for age_group, count in age_dist.items():
        print(f"  - {age_group}: {count} ({count/len(contestant_static):.1%})")

    # 7. 验证行业分布
    print("\n[7] 行业分布 (Top 5)")
    industry_dist = contestant_static['celebrity_industry'].value_counts().head(5)
    for industry, count in industry_dist.items():
        print(f"  - {industry}: {count}")

    # 8. 验证赛季元数据
    print("\n[8] 赛季元数据统计")
    print(f"  - 平均选手数: {season_meta['num_contestants'].mean():.1f}")
    print(f"  - 平均周数: {season_meta['max_weeks'].mean():.1f}")
    print(f"  - 选手数范围: {season_meta['num_contestants'].min()}-{season_meta['num_contestants'].max()}")

    # 9. 检查异常值
    print("\n[9] 异常值检查")

    # 检查是否有负分
    negative_scores = (weekly_panel['judge_total'] < 0).sum()
    print(f"  - 负分数量: {negative_scores}")

    # 检查是否有超出范围的分数
    valid_panel = weekly_panel[weekly_panel['week_valid']]
    out_of_range = ((valid_panel['judge_total'] < 30) | (valid_panel['judge_total'] > 300)).sum()
    print(f"  - 超出理论范围的分数: {out_of_range}")

    # 检查 relative_judge_score 的极端值
    extreme_z = (weekly_panel['relative_judge_score'].abs() > 3).sum()
    print(f"  - |Z-Score| > 3 的数量: {extreme_z}")

    print("\n" + "=" * 60)
    print("数据质量验证完成！")
    print("=" * 60)


if __name__ == "__main__":
    validate_data_quality()
