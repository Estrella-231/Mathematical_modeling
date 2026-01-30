"""
选秀节目淘汰机制模型 - 核心流程处理模块

功能：
- 综合评委打分和粉丝投票
- 根据综合评分确定淘汰选手
- 支持评委拯救权机制
"""

import pandas as pd


def combine_rank(judge_total: pd.Series, fan_votes: pd.Series) -> pd.Series:
    """
    排名法综合评分
    
    将评委总分和粉丝票数转换为排名，然后相加求和
    排名越低代表越优秀
    
    Args:
        judge_total: 评委总分序列
        fan_votes: 粉丝投票数序列
    
    Returns:
        综合排名分数序列（分数越低越优秀）
    """
    # 分别对评委分数和粉丝投票进行排名（降序，即分数/票数越高排名越靠前）
    judge_rank = judge_total.rank(ascending=False, method="min")
    fan_rank = fan_votes.rank(ascending=False, method="min")
    # 两个排名相加，得到综合排名分数（分数越低越优秀）
    return judge_rank + fan_rank


def combine_percent(judge_total: pd.Series, fan_votes: pd.Series) -> pd.Series:
    """
    百分比法综合评分
    
    将评委总分和粉丝票数分别转换为百分比占比，然后相加
    
    Args:
        judge_total: 评委总分序列
        fan_votes: 粉丝投票数序列
    
    Returns:
        综合百分比序列（分数越高越优秀）
    """
    judge_percent = judge_total / judge_total.sum()
    fan_percent = fan_votes / fan_votes.sum()
    return judge_percent + fan_percent


    # 计算各自的百分比占比
    judge_percent = judge_total / judge_total.sum()
    fan_percent = fan_votes / fan_votes.sum()
    # 两个百分比相加，得到综合评分
    return judge_percent + fan_percent


def select_eliminated(
    week_df: pd.DataFrame,
    fan_votes: pd.Series,
    method: str,
    n_eliminate: int = 1,
    judge_save: bool = False,
):
    """
    确定本周被淘汰的选手
    
    Args:
        week_df: 本周数据框，包含'judge_total'列（评委总分）
        fan_votes: 粉丝投票数据（Series）
        method: 综合评分方法，"rank"或"percent"
        n_eliminate: 淘汰人数，默认为1
        judge_save: 是否启用评委拯救权，默认False
                   当启用且只淘汰1人时：
                   - 从综合得分最低的2人中
                   - 评委分数最低的被淘汰
    
    Returns:
        被淘汰选手的索引列表
    
    Raises:
        ValueError: 当method参数无效时
    """
    # 参数校验：淘汰人数必须大于0
    if n_eliminate < 1:
        return []

    # 根据指定方法计算综合评分
    if method == "rank":
        combined = combine_rank(week_df["judge_total"], fan_votes)
    elif method == "percent":
        combined = combine_percent(week_df["judge_total"], fan_votes)
    else:
        raise ValueError(f"Unknown method: {method}")

    # 评委拯救机制：只淘汰1人且启用拯救权时
    if judge_save and n_eliminate == 1:
        # 获取综合排名最后的2人
        bottom_two = combined.nsmallest(2).index
        # 在这2人中，选择评委分数最低的被淘汰
        eliminated = week_df.loc[bottom_two, "judge_total"].idxmin()
        return [eliminated]

    # 常规方式：直接返回综合排名最后n_eliminate的选手
    return list(combined.nsmallest(n_eliminate).index)


def estimate_fan_votes(panel, config=None):
    """
    估算粉丝投票数
    
    根据给定的面板数据和配置参数，估算每个选手获得的粉丝投票数
    
    Args:
        panel: 选手面板数据
        config: 模型配置参数，默认为None
    
    Returns:
        粉丝投票数序列
    
    Note:
        具体实现详见 docs/02_model_design.md 中的模型设计说明
    """
    raise NotImplementedError("Implement in docs/02_model_design.md")
