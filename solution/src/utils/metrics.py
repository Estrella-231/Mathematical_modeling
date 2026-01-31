import numpy as np
import pandas as pd
# 这个模块用于评估指标 | This module is used for evaluation metrics

def elimination_match_rate(actual_eliminated: pd.Series, predicted_eliminated: pd.Series) -> float:
    actual = actual_eliminated.astype(str)
    predicted = predicted_eliminated.astype(str)
    return np.mean(actual == predicted)
# 计算淘汰匹配率 | Calculate elimination match rate
