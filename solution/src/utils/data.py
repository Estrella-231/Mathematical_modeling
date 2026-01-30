import re
from typing import Dict, List

import pandas as pd


def load_data(path):
    return pd.read_csv(path)


def _week_columns(df: pd.DataFrame) -> Dict[int, List[str]]: #提取每周评委评分列
    pattern = re.compile(r"^week(\d+)_judge(\d+)_score$", re.I)
    week_map: Dict[int, List[str]] = {}
    for col in df.columns:
        match = pattern.match(col)
        if match:
            week = int(match.group(1))
            week_map.setdefault(week, []).append(col)
    return week_map


def build_week_panel(df: pd.DataFrame) -> pd.DataFrame: #构建每周数据面板
    week_map = _week_columns(df)
    base_cols = [
        c
        for c in [
            "celebrity_name",
            "ballroom_partner",
            "celebrity_industry",
            "celebrity_age_during_season",
            "celebrity_homestate",
            "celebrity_homecountry/region",
            "season",
            "placement",
            "results",
        ]
        if c in df.columns
    ]

    panels = []
    for week, cols in sorted(week_map.items()):
        temp = df[base_cols].copy()
        scores = df[cols].apply(pd.to_numeric, errors="coerce")
        temp["week"] = week
        temp["judge_total"] = scores.sum(axis=1, skipna=True)
        temp["has_scores"] = scores.notna().any(axis=1)
        panels.append(temp)

    return pd.concat(panels, ignore_index=True)
