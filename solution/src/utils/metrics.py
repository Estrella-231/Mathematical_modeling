import numpy as np
import pandas as pd


def elimination_match_rate(actual_eliminated: pd.Series, predicted_eliminated: pd.Series) -> float:
    actual = actual_eliminated.astype(str)
    predicted = predicted_eliminated.astype(str)
    return np.mean(actual == predicted)
