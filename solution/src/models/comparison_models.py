"""
Q1对比模型实现：Lasso, Elastic Net, SVR
用于与Ridge回归进行对比实验

根据论文改进计划，实现以下模型：
1. Lasso回归 - L1正则化，特征选择
2. Elastic Net - L1+L2混合正则化
3. SVR (Support Vector Regression) - 非线性回归
"""
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Lasso, LassoCV, ElasticNet, ElasticNetCV
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pickle
from typing import Tuple, Dict
import warnings
warnings.filterwarnings('ignore')


class BaseFanVoteModel:
    """
    基础粉丝投票模型类
    提供通用的数据处理和评估方法
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_fitted = False
        self.residual_std = None
        self.sensitivity = 1.0

    def construct_week_result_score(self, df: pd.DataFrame) -> pd.Series:
        """构建周级结果分数（与Ridge模型相同）"""
        max_rank = df.groupby(['season', 'week'])['placement'].transform('max')
        inverted_rank = max_rank - df['placement'] + 1
        epsilon = 0.1
        p = (inverted_rank + epsilon) / (max_rank + 2 * epsilon)
        week_result_score = np.log(p / (1 - p))
        return week_result_score

    def prepare_features(self, df: pd.DataFrame) -> Tuple:
        """准备特征和目标变量"""
        valid_df = df[df['week_valid'] == True].copy()

        # 排除决赛周和人数太少的周
        week_counts = valid_df.groupby(['season', 'week']).size()
        valid_weeks = week_counts[week_counts > 3].index

        valid_df = valid_df.set_index(['season', 'week'])
        valid_df = valid_df.loc[valid_df.index.isin(valid_weeks)].reset_index()

        # 构建周级结果分数
        valid_df['week_result_score'] = self.construct_week_result_score(valid_df)

        # 特征列
        feature_cols = [
            'relative_judge_score',
            'judge_rank_in_week',
            'cumulative_average'
        ]

        # 处理缺失值
        for col in feature_cols:
            if col in valid_df.columns:
                valid_df[col] = valid_df[col].fillna(0)

        X = valid_df[feature_cols].values
        y = valid_df['week_result_score'].values
        groups = valid_df['season'].values

        self.feature_names = feature_cols

        return X, y, groups, valid_df

    def predict(self, X):
        """预测周级结果分数"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def compute_residuals(self, X, y):
        """计算残差"""
        y_pred = self.predict(X)
        residuals = y - y_pred
        return residuals, y_pred

    def residuals_to_fan_vote_share(self, residuals: np.ndarray,
                                     week_groups: pd.Series) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """将残差转换为粉丝投票份额"""
        raw_logits = self.sensitivity * residuals

        fan_vote_share = np.zeros_like(residuals)
        uncertainty_lower = np.zeros_like(residuals)
        uncertainty_upper = np.zeros_like(residuals)

        for week_id in week_groups.unique():
            mask = (week_groups == week_id).values
            week_logits = raw_logits[mask]
            week_logits = week_logits - week_logits.max()
            week_raw_votes = np.exp(week_logits)
            week_sum = week_raw_votes.sum()

            fan_vote_share[mask] = week_raw_votes / (week_sum + 1e-12)

            # 计算不确定性
            residuals_lower = residuals[mask] - self.residual_std
            residuals_upper = residuals[mask] + self.residual_std

            raw_votes_lower = np.exp(self.sensitivity * (residuals_lower - residuals_lower.max()))
            raw_votes_upper = np.exp(self.sensitivity * (residuals_upper - residuals_upper.max()))

            week_sum_lower = raw_votes_lower.sum()
            week_sum_upper = raw_votes_upper.sum()

            uncertainty_lower[mask] = raw_votes_lower / (week_sum_lower + 1e-12)
            uncertainty_upper[mask] = raw_votes_upper / (week_sum_upper + 1e-12)

        return fan_vote_share, uncertainty_lower, uncertainty_upper

    def evaluate(self, X, y, groups=None):
        """评估模型性能"""
        y_pred = self.predict(X)

        metrics = {
            'r2': r2_score(y, y_pred),
            'rmse': np.sqrt(mean_squared_error(y, y_pred)),
            'mae': mean_absolute_error(y, y_pred),
            'mse': mean_squared_error(y, y_pred)
        }

        return metrics


class LassoFanVoteModel(BaseFanVoteModel):
    """
    Lasso回归模型（L1正则化）

    特点：
    - L1正则化可以产生稀疏解（特征选择）
    - 自动识别重要特征
    - 适合高维数据
    """

    def __init__(self, alpha=1.0, sensitivity=1.0):
        super().__init__("Lasso")
        self.alpha = alpha
        self.sensitivity = sensitivity
        self.model = Lasso(alpha=alpha, max_iter=10000)

    def find_optimal_alpha(self, X, y, groups, alphas=None):
        """使用交叉验证找到最优的alpha"""
        if alphas is None:
            alphas = np.logspace(-4, 1, 50)

        print(f"\n[{self.model_name}] 交叉验证搜索最优 alpha...")
        print(f"  - 候选 alpha 范围: {alphas.min():.4f} - {alphas.max():.4f}")

        gkf = GroupKFold(n_splits=5)
        lasso_cv = LassoCV(
            alphas=alphas,
            cv=gkf.split(X, y, groups),
            max_iter=10000,
            n_jobs=-1
        )
        lasso_cv.fit(X, y)

        optimal_alpha = lasso_cv.alpha_
        print(f"  - 最优 alpha: {optimal_alpha:.4f}")

        return optimal_alpha

    def fit(self, X, y, groups=None, find_alpha=True):
        """训练Lasso模型"""
        print(f"\n{'='*60}")
        print(f"训练 {self.model_name} 回归模型")
        print(f"{'='*60}")

        # 标准化特征
        X_scaled = self.scaler.fit_transform(X)

        # 寻找最优alpha
        if find_alpha and groups is not None:
            self.alpha = self.find_optimal_alpha(X_scaled, y, groups)
            self.model = Lasso(alpha=self.alpha, max_iter=10000)

        # 训练模型
        print(f"\n[训练] 使用 alpha = {self.alpha:.4f}")
        self.model.fit(X_scaled, y)
        self.is_fitted = True

        # 计算训练集性能
        metrics = self.evaluate(X, y)

        print(f"\n[训练集性能]")
        print(f"  - R2 Score: {metrics['r2']:.4f}")
        print(f"  - RMSE: {metrics['rmse']:.4f}")
        print(f"  - MAE: {metrics['mae']:.4f}")

        # 计算残差标准差
        residuals = y - self.predict(X)
        self.residual_std = np.std(residuals)
        print(f"  - 残差标准差: {self.residual_std:.4f}")

        # 特征重要性（非零系数）
        print(f"\n[特征重要性] (系数)")
        non_zero_features = 0
        for name, coef in zip(self.feature_names, self.model.coef_):
            print(f"  - {name}: {coef:.4f}")
            if abs(coef) > 1e-6:
                non_zero_features += 1
        print(f"  - Intercept: {self.model.intercept_:.4f}")
        print(f"  - 非零特征数: {non_zero_features}/{len(self.feature_names)}")

        self.is_fitted = True
        return self


class ElasticNetFanVoteModel(BaseFanVoteModel):
    """
    Elastic Net回归模型（L1+L2混合正则化）

    特点：
    - 结合L1和L2正则化的优点
    - l1_ratio控制L1/L2的比例
    - 在相关特征存在时表现更稳定
    """

    def __init__(self, alpha=1.0, l1_ratio=0.5, sensitivity=1.0):
        super().__init__("ElasticNet")
        self.alpha = alpha
        self.l1_ratio = l1_ratio
        self.sensitivity = sensitivity
        self.model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, max_iter=10000)

    def find_optimal_params(self, X, y, groups, alphas=None, l1_ratios=None):
        """使用交叉验证找到最优的alpha和l1_ratio"""
        if alphas is None:
            alphas = np.logspace(-4, 1, 30)
        if l1_ratios is None:
            l1_ratios = [0.1, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]

        print(f"\n[{self.model_name}] 交叉验证搜索最优参数...")
        print(f"  - 候选 alpha 范围: {alphas.min():.4f} - {alphas.max():.4f}")
        print(f"  - 候选 l1_ratio: {l1_ratios}")

        gkf = GroupKFold(n_splits=5)
        enet_cv = ElasticNetCV(
            alphas=alphas,
            l1_ratio=l1_ratios,
            cv=gkf.split(X, y, groups),
            max_iter=10000,
            n_jobs=-1
        )
        enet_cv.fit(X, y)

        optimal_alpha = enet_cv.alpha_
        optimal_l1_ratio = enet_cv.l1_ratio_
        print(f"  - 最优 alpha: {optimal_alpha:.4f}")
        print(f"  - 最优 l1_ratio: {optimal_l1_ratio:.4f}")

        return optimal_alpha, optimal_l1_ratio

    def fit(self, X, y, groups=None, find_params=True):
        """训练Elastic Net模型"""
        print(f"\n{'='*60}")
        print(f"训练 {self.model_name} 回归模型")
        print(f"{'='*60}")

        # 标准化特征
        X_scaled = self.scaler.fit_transform(X)

        # 寻找最优参数
        if find_params and groups is not None:
            self.alpha, self.l1_ratio = self.find_optimal_params(X_scaled, y, groups)
            self.model = ElasticNet(alpha=self.alpha, l1_ratio=self.l1_ratio, max_iter=10000)

        # 训练模型
        print(f"\n[训练] 使用 alpha = {self.alpha:.4f}, l1_ratio = {self.l1_ratio:.4f}")
        self.model.fit(X_scaled, y)
        self.is_fitted = True

        # 计算训练集性能
        metrics = self.evaluate(X, y)

        print(f"\n[训练集性能]")
        print(f"  - R2 Score: {metrics['r2']:.4f}")
        print(f"  - RMSE: {metrics['rmse']:.4f}")
        print(f"  - MAE: {metrics['mae']:.4f}")

        # 计算残差标准差
        residuals = y - self.predict(X)
        self.residual_std = np.std(residuals)
        print(f"  - 残差标准差: {self.residual_std:.4f}")

        # 特征重要性
        print(f"\n[特征重要性] (系数)")
        non_zero_features = 0
        for name, coef in zip(self.feature_names, self.model.coef_):
            print(f"  - {name}: {coef:.4f}")
            if abs(coef) > 1e-6:
                non_zero_features += 1
        print(f"  - Intercept: {self.model.intercept_:.4f}")
        print(f"  - 非零特征数: {non_zero_features}/{len(self.feature_names)}")

        self.is_fitted = True
        return self


class SVRFanVoteModel(BaseFanVoteModel):
    """
    支持向量回归模型（SVR）

    特点：
    - 非线性回归能力（使用RBF核）
    - 对异常值鲁棒
    - 可以捕捉复杂的非线性关系
    """

    def __init__(self, C=1.0, epsilon=0.1, kernel='rbf', sensitivity=1.0):
        super().__init__("SVR")
        self.C = C
        self.epsilon = epsilon
        self.kernel = kernel
        self.sensitivity = sensitivity
        self.model = SVR(C=C, epsilon=epsilon, kernel=kernel)

    def find_optimal_params(self, X, y, groups):
        """使用网格搜索找到最优参数"""
        print(f"\n[{self.model_name}] 网格搜索最优参数...")

        param_grid = {
            'C': [0.1, 1.0, 10.0, 100.0],
            'epsilon': [0.01, 0.1, 0.2],
            'gamma': ['scale', 'auto', 0.001, 0.01, 0.1]
        }

        gkf = GroupKFold(n_splits=5)
        grid_search = GridSearchCV(
            SVR(kernel=self.kernel),
            param_grid,
            cv=gkf.split(X, y, groups),
            scoring='neg_mean_squared_error',
            n_jobs=-1,
            verbose=0
        )
        grid_search.fit(X, y)

        best_params = grid_search.best_params_
        print(f"  - 最优参数: {best_params}")

        return best_params

    def fit(self, X, y, groups=None, find_params=True):
        """训练SVR模型"""
        print(f"\n{'='*60}")
        print(f"训练 {self.model_name} 回归模型")
        print(f"{'='*60}")

        # 标准化特征
        X_scaled = self.scaler.fit_transform(X)

        # 寻找最优参数
        if find_params and groups is not None:
            best_params = self.find_optimal_params(X_scaled, y, groups)
            self.C = best_params['C']
            self.epsilon = best_params['epsilon']
            gamma = best_params['gamma']
            self.model = SVR(C=self.C, epsilon=self.epsilon, kernel=self.kernel, gamma=gamma)

        # 训练模型
        print(f"\n[训练] 使用 C = {self.C:.4f}, epsilon = {self.epsilon:.4f}")
        self.model.fit(X_scaled, y)
        self.is_fitted = True

        # 计算训练集性能
        metrics = self.evaluate(X, y)

        print(f"\n[训练集性能]")
        print(f"  - R2 Score: {metrics['r2']:.4f}")
        print(f"  - RMSE: {metrics['rmse']:.4f}")
        print(f"  - MAE: {metrics['mae']:.4f}")

        # 计算残差标准差
        residuals = y - self.predict(X)
        self.residual_std = np.std(residuals)
        print(f"  - 残差标准差: {self.residual_std:.4f}")

        # SVR没有显式的特征重要性，但可以报告支持向量数量
        print(f"\n[模型信息]")
        print(f"  - 支持向量数: {len(self.model.support_)}")
        print(f"  - 支持向量比例: {len(self.model.support_)/len(X):.2%}")

        self.is_fitted = True
        return self
