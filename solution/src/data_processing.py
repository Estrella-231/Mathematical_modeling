"""
数据处理流水线 (Data Processing Pipeline)
根据 docs/07_data_processing.md 的要求实现
"""
import re
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


def parse_elimination_week(results: str) -> int:
    """
    从 results 字段解析淘汰周数

    Examples:
        "Eliminated Week 3" -> 3
        "1st Place" -> 999 (决赛周，用大数表示)
        "2nd Place" -> 999
        "Quit" -> -1 (特殊标记)
    """
    if pd.isna(results):
        return -1

    results = str(results).strip()

    # 匹配 "Eliminated Week X"
    match = re.search(r"Eliminated Week (\d+)", results, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # 匹配 "1st Place", "2nd Place" 等
    if re.search(r"\d+(st|nd|rd|th) Place", results, re.IGNORECASE):
        return 999  # 决赛周

    # 匹配 "Quit", "Withdrew"
    if re.search(r"(Quit|Withdrew)", results, re.IGNORECASE):
        return -1

    return -1


def extract_week_judge_columns(df: pd.DataFrame) -> Dict[int, List[str]]:
    """
    提取所有 weekX_judgeY_score 列，按周分组

    Returns:
        {week_num: [col1, col2, ...]}
    """
    pattern = re.compile(r"^week(\d+)_judge(\d+)_score$", re.IGNORECASE)
    week_map: Dict[int, List[str]] = {}

    for col in df.columns:
        match = pattern.match(col)
        if match:
            week = int(match.group(1))
            week_map.setdefault(week, []).append(col)

    return week_map


def melt_to_long_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 1: Melt (宽转长)
    将 weekX_judgeY_score 转换为长格式

    Returns:
        DataFrame with columns: [season, celebrity_name, week, judge_id, score]
    """
    week_map = extract_week_judge_columns(df)

    records = []
    for week, cols in week_map.items():
        for col in cols:
            # 提取 judge_id
            match = re.search(r"judge(\d+)", col, re.IGNORECASE)
            judge_id = int(match.group(1)) if match else 0

            for idx, row in df.iterrows():
                score_val = row[col]
                records.append({
                    'season': row['season'],
                    'celebrity_name': row['celebrity_name'],
                    'week': week,
                    'judge_id': judge_id,
                    'score': score_val
                })

    long_df = pd.DataFrame(records)
    # 将 N/A 转换为 NaN
    long_df['score'] = pd.to_numeric(long_df['score'], errors='coerce')

    return long_df


def compute_standardized_score(scores: pd.Series) -> float:
    """
    计算标准化总分
    Score_std = (sum of valid scores / count of valid scores) × 30
    """
    valid_scores = scores.dropna()
    if len(valid_scores) == 0:
        return np.nan

    return (valid_scores.sum() / len(valid_scores)) * 30


def aggregate_weekly_scores(long_df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 2: Aggregation (周级聚合)
    计算每人每周的 judge_total, judge_rank_in_week
    """
    # 按 season, celebrity_name, week 分组
    grouped = long_df.groupby(['season', 'celebrity_name', 'week'])

    weekly_agg = grouped.agg({
        'score': lambda x: compute_standardized_score(x)
    }).reset_index()

    weekly_agg.rename(columns={'score': 'judge_total'}, inplace=True)

    # 计算每周的排名 (Dense Rank, 降序)
    weekly_agg['judge_rank_in_week'] = weekly_agg.groupby(['season', 'week'])['judge_total'].rank(
        ascending=False, method='dense'
    )

    # 标记是否有效分数 (非 NaN 且 > 0)
    weekly_agg['week_valid'] = (
        weekly_agg['judge_total'].notna() &
        (weekly_agg['judge_total'] > 0)
    )

    return weekly_agg


def join_metadata(weekly_df: pd.DataFrame, raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 3: Meta Join (合并元数据)
    合并选手的静态信息
    """
    meta_cols = [
        'celebrity_name', 'season', 'ballroom_partner',
        'celebrity_industry', 'celebrity_age_during_season',
        'celebrity_homestate', 'celebrity_homecountry/region',
        'results', 'placement'
    ]

    meta_df = raw_df[meta_cols].copy()

    # 解析淘汰周
    meta_df['elimination_week'] = meta_df['results'].apply(parse_elimination_week)

    # 合并
    merged = weekly_df.merge(
        meta_df,
        on=['celebrity_name', 'season'],
        how='left'
    )

    return merged


def generate_dynamic_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 4: Feature Generation (生成衍生特征)

    生成的特征：
    - relative_judge_score: Z-Score (当周分数相对于当周平均的标准化)
    - cumulative_average: 截止到上周的平均分
    - trend: 本周分 - 上周分
    - is_bottom_2_judge: 是否在评委分的倒数两名内
    """
    df = df.copy()

    # 按 season, celebrity_name 排序
    df = df.sort_values(['season', 'celebrity_name', 'week']).reset_index(drop=True)

    # 1. relative_judge_score (Z-Score)
    df['week_mean'] = df.groupby(['season', 'week'])['judge_total'].transform('mean')
    df['week_std'] = df.groupby(['season', 'week'])['judge_total'].transform('std').replace(0, np.nan)
    df['relative_judge_score'] = (df['judge_total'] - df['week_mean']) / df['week_std']
    df['relative_judge_score'] = (
        df['relative_judge_score']
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    # 2. cumulative_average (截止到上周的平均分)
    df['cumulative_average'] = df.groupby(['season', 'celebrity_name'])['judge_total'].apply(
        lambda x: x.shift(1).expanding().mean()
    ).reset_index(level=[0, 1], drop=True)

    # 3. trend (本周分 - 上周分)
    df['prev_week_score'] = df.groupby(['season', 'celebrity_name'])['judge_total'].shift(1)
    df['trend'] = df['judge_total'] - df['prev_week_score']

    # 4. is_bottom_2_judge (是否在倒数两名内)
    df['is_bottom_2_judge'] = df['judge_rank_in_week'] >= (
        df.groupby(['season', 'week'])['judge_rank_in_week'].transform('max') - 1
    )

    # 5. 处理淘汰后的分数：将淘汰后的周设为无效
    df['is_eliminated'] = (df['week'] > df['elimination_week']) & (df['elimination_week'] > 0)
    df.loc[df['is_eliminated'], 'week_valid'] = False
    df.loc[df['is_eliminated'], 'judge_total'] = np.nan

    # 清理临时列
    df = df.drop(columns=['week_mean', 'week_std', 'prev_week_score', 'is_eliminated'])

    return df


def create_age_groups(age: float) -> str:
    """将年龄分组"""
    if pd.isna(age):
        return 'Unknown'
    if age < 20:
        return '<20'
    elif age < 30:
        return '20-30'
    elif age < 40:
        return '30-40'
    elif age < 50:
        return '40-50'
    elif age < 60:
        return '50-60'
    else:
        return '60+'


def create_contestant_static(df: pd.DataFrame) -> pd.DataFrame:
    """
    创建选手级汇总数据
    Row = Contestant (每个选手一行)
    """
    static_df = df.groupby(['season', 'celebrity_name']).agg({
        'ballroom_partner': 'first',
        'celebrity_industry': 'first',
        'celebrity_age_during_season': 'first',
        'celebrity_homestate': 'first',
        'celebrity_homecountry/region': 'first',
        'placement': 'first',
        'results': 'first',
        'elimination_week': 'first',
        'judge_total': 'mean'  # 平均评委分
    }).reset_index()

    static_df.rename(columns={'judge_total': 'avg_judge_score'}, inplace=True)

    # 添加年龄分组
    static_df['age_group'] = static_df['celebrity_age_during_season'].apply(create_age_groups)

    return static_df


def create_season_meta(df: pd.DataFrame) -> pd.DataFrame:
    """
    创建赛季级元数据
    Row = Season
    """
    season_meta = df.groupby('season').agg({
        'week': 'max',  # 最大周数
        'celebrity_name': 'nunique'  # 选手数量
    }).reset_index()

    season_meta.rename(columns={
        'week': 'max_weeks',
        'celebrity_name': 'num_contestants'
    }, inplace=True)

    return season_meta


def split_train_test(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Step 5: Split (数据集切分)
    Train: S1-S27
    Test: S28-S34
    """
    train_df = df[df['season'] <= 27].copy()
    test_df = df[df['season'] >= 28].copy()

    return train_df, test_df


def run_pipeline(raw_data_path: Path, output_dir: Path) -> None:
    """
    运行完整的数据处理流水线
    """
    print("=" * 60)
    print("数据处理流水线 (Data Processing Pipeline)")
    print("=" * 60)

    # 加载原始数据
    print(f"\n[Step 0] 加载原始数据: {raw_data_path}")
    raw_df = pd.read_csv(raw_data_path)
    print(f"  - 原始数据形状: {raw_df.shape}")
    print(f"  - 赛季范围: {raw_df['season'].min()} - {raw_df['season'].max()}")
    print(f"  - 选手数量: {raw_df['celebrity_name'].nunique()}")

    # Step 1: Melt
    print("\n[Step 1] Melt (宽转长)")
    long_df = melt_to_long_format(raw_df)
    print(f"  - 长格式数据形状: {long_df.shape}")

    # Step 2: Aggregation
    print("\n[Step 2] Aggregation (周级聚合)")
    weekly_df = aggregate_weekly_scores(long_df)
    print(f"  - 周级数据形状: {weekly_df.shape}")
    print(f"  - 有效周数据: {weekly_df['week_valid'].sum()}")

    # Step 3: Meta Join
    print("\n[Step 3] Meta Join (合并元数据)")
    merged_df = join_metadata(weekly_df, raw_df)
    print(f"  - 合并后数据形状: {merged_df.shape}")

    # Step 4: Feature Generation
    print("\n[Step 4] Feature Generation (生成衍生特征)")
    featured_df = generate_dynamic_features(merged_df)
    print(f"  - 特征工程后数据形状: {featured_df.shape}")
    print(f"  - 生成的特征列: relative_judge_score, cumulative_average, trend, is_bottom_2_judge")

    # Step 5: Split
    print("\n[Step 5] Split (数据集切分)")
    train_df, test_df = split_train_test(featured_df)
    print(f"  - 训练集 (S1-S27): {train_df.shape}")
    print(f"  - 测试集 (S28-S34): {test_df.shape}")

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 保存 weekly_panel.csv
    weekly_panel_path = output_dir / "weekly_panel.csv"
    featured_df.to_csv(weekly_panel_path, index=False)
    print(f"\n[输出] 保存 weekly_panel.csv: {weekly_panel_path}")

    # 保存 contestant_static.csv
    static_df = create_contestant_static(featured_df)
    static_path = output_dir / "contestant_static.csv"
    static_df.to_csv(static_path, index=False)
    print(f"[输出] 保存 contestant_static.csv: {static_path}")
    print(f"  - 选手数量: {len(static_df)}")

    # 保存 season_meta.csv
    season_meta_df = create_season_meta(featured_df)
    season_path = output_dir / "season_meta.csv"
    season_meta_df.to_csv(season_path, index=False)
    print(f"[输出] 保存 season_meta.csv: {season_path}")
    print(f"  - 赛季数量: {len(season_meta_df)}")

    # 保存训练集和测试集
    train_path = output_dir / "train_panel.csv"
    test_path = output_dir / "test_panel.csv"
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    print(f"[输出] 保存 train_panel.csv: {train_path}")
    print(f"[输出] 保存 test_panel.csv: {test_path}")

    print("\n" + "=" * 60)
    print("数据处理完成！")
    print("=" * 60)


if __name__ == "__main__":
    from config import ROOT, DATA_DIR

    raw_data = DATA_DIR / "raw" / "2026_MCM_Problem_C_Data.csv"
    output_dir = DATA_DIR / "processed"

    run_pipeline(raw_data, output_dir)
