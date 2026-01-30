"""
Model B1 (Updated): Ridge Regression for Weekly Fan Vote Share Estimation
根据更新后的 docs/08_model_b1_ridge_impl.md 实现

核心改进：
1. 预测周级结果（而非最终排名）
2. 输出粉丝投票份额（归一化到 100%）
3. 提供不确定性估计（置信区间）
4. 验证淘汰匹配率
"""
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import pickle
from typing import Tuple, Dict


class RidgeFanVoteModelV2:
    """
    Ridge 回归模型用于估计周级粉丝投票份额（更新版）

    核心改进：
    - 预测周级结果（week_result_score）
    - 输出归一化的粉丝投票份额（每周总和 = 100%）
    - 提供不确定性估计
    - 验证淘汰匹配率
    """

    def __init__(self, alpha=1.0, sensitivity=1.0):
        """
        Parameters:
        -----------
        alpha : float
            Ridge 正则化强度
        sensitivity : float
            残差到投票的敏感度系数（α in the document）
        """
        self.alpha = alpha
        self.sensitivity = sensitivity
        self.model = Ridge(alpha=alpha)
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_fitted = False
        self.residual_std = None  # 用于计算不确定性

    def construct_week_result_score(self, df: pd.DataFrame) -> pd.Series:
        """
        构建周级结果分数（Y）

        策略：使用 logits 形式的排名
        - 排名越好（数字越小），分数越高
        - 使用 log 变换使分布更接近正态
        """
        # 计算每周的最大排名
        max_rank = df.groupby(['season', 'week'])['placement'].transform('max')

        # 反转排名：1 -> 最高分，max_rank -> 最低分
        inverted_rank = max_rank - df['placement'] + 1

        # Logits 变换：log(p / (1-p))
        # 避免除零：添加小的平滑项
        epsilon = 0.1
        p = (inverted_rank + epsilon) / (max_rank + 2 * epsilon)
        week_result_score = np.log(p / (1 - p))

        return week_result_score

    def prepare_features(self, df: pd.DataFrame) -> Tuple:
        """
        准备特征和目标变量

        特征（X）：
        - relative_judge_score: Z-Score
        - judge_rank_in_week: 评委排名
        - cumulative_average: 累积平均分

        目标（Y）：
        - week_result_score: 周级结果分数（logits 形式）
        """
        # 只使用有效周的数据
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

    def find_optimal_alpha(self, X, y, groups, alphas=None):
        """使用交叉验证找到最优的 alpha"""
        if alphas is None:
            alphas = np.logspace(-3, 3, 50)

        print(f"\n[交叉验证] 搜索最优 alpha...")
        print(f"  - 候选 alpha 范围: {alphas.min():.4f} - {alphas.max():.4f}")

        gkf = GroupKFold(n_splits=5)
        ridge_cv = RidgeCV(
            alphas=alphas,
            cv=gkf.split(X, y, groups),
            scoring='neg_mean_squared_error'
        )
        ridge_cv.fit(X, y)

        optimal_alpha = ridge_cv.alpha_
        print(f"  - 最优 alpha: {optimal_alpha:.4f}")

        return optimal_alpha

    def fit(self, X, y, groups=None, find_alpha=True):
        """训练模型"""
        print("\n" + "=" * 60)
        print("训练 Ridge 回归模型（更新版）")
        print("=" * 60)

        # 标准化特征
        X_scaled = self.scaler.fit_transform(X)

        # 寻找最优 alpha
        if find_alpha and groups is not None:
            self.alpha = self.find_optimal_alpha(X_scaled, y, groups)
            self.model = Ridge(alpha=self.alpha)

        # 训练模型
        print(f"\n[训练] 使用 alpha = {self.alpha:.4f}")
        self.model.fit(X_scaled, y)

        # 计算训练集性能
        y_pred = self.model.predict(X_scaled)
        r2 = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        mae = mean_absolute_error(y, y_pred)

        print(f"\n[训练集性能]")
        print(f"  - R2 Score: {r2:.4f}")
        print(f"  - RMSE: {rmse:.4f}")
        print(f"  - MAE: {mae:.4f}")

        # 计算残差标准差（用于不确定性估计）
        residuals = y - y_pred
        self.residual_std = np.std(residuals)
        print(f"  - 残差标准差: {self.residual_std:.4f}")

        # 特征重要性
        print(f"\n[特征重要性] (系数)")
        for name, coef in zip(self.feature_names, self.model.coef_):
            print(f"  - {name}: {coef:.4f}")
        print(f"  - Intercept: {self.model.intercept_:.4f}")

        self.is_fitted = True
        return self

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
        """
        将残差转换为粉丝投票份额（归一化到 100%）

        使用 Softmax：
        RawVote_i = exp(sensitivity × residual_i)
        FanVoteShare_i = RawVote_i / Σ(RawVote_j) for j in same week

        Returns:
        --------
        fan_vote_share : 粉丝投票份额 [0, 1]
        uncertainty_lower : 不确定性下界
        uncertainty_upper : 不确定性上界
        """
        # 计算原始投票（未归一化）——使用数值稳定化
        raw_logits = self.sensitivity * residuals

        # 按周归一化
        fan_vote_share = np.zeros_like(raw_votes)
        uncertainty_lower = np.zeros_like(raw_votes)
        uncertainty_upper = np.zeros_like(raw_votes)

        for week_id in week_groups.unique():
            mask = (week_groups == week_id).values
            week_logits = raw_logits[mask]
            week_logits = week_logits - week_logits.max()
            week_raw_votes = np.exp(week_logits)
            week_sum = week_raw_votes.sum()

            # 归一化到 [0, 1]
            fan_vote_share[mask] = week_raw_votes / (week_sum + 1e-12)

            # 计算不确定性（基于残差的标准差）
            # 使用 ±1 std 作为置信区间
            residuals_lower = residuals[mask] - self.residual_std
            residuals_upper = residuals[mask] + self.residual_std

            raw_votes_lower = np.exp(self.sensitivity * (residuals_lower - residuals_lower.max()))
            raw_votes_upper = np.exp(self.sensitivity * (residuals_upper - residuals_upper.max()))

            # 重新归一化
            week_sum_lower = raw_votes_lower.sum()
            week_sum_upper = raw_votes_upper.sum()

            uncertainty_lower[mask] = raw_votes_lower / (week_sum_lower + 1e-12)
            uncertainty_upper[mask] = raw_votes_upper / (week_sum_upper + 1e-12)

        return fan_vote_share, uncertainty_lower, uncertainty_upper

    def calibrate_sensitivity(self, X, y, df, sensitivity_range=None):
        """
        校准敏感度系数（α），使淘汰匹配率最大化

        策略：
        1. 尝试不同的 sensitivity 值
        2. 对每个值，计算估算的粉丝投票份额
        3. 使用投票规则重建淘汰结果
        4. 计算淘汰匹配率
        5. 选择匹配率最高的 sensitivity
        """
        if sensitivity_range is None:
            sensitivity_range = np.linspace(0.1, 2.0, 20)

        print("\n" + "=" * 60)
        print("校准敏感度系数（Sensitivity Calibration）")
        print("=" * 60)

        residuals, _ = self.compute_residuals(X, y)
        week_groups = df.groupby(['season', 'week']).ngroup()

        best_sensitivity = self.sensitivity
        best_match_rate = 0

        print(f"\n尝试 {len(sensitivity_range)} 个 sensitivity 值...")

        for sens in sensitivity_range:
            self.sensitivity = sens

            # 计算粉丝投票份额
            fan_shares, _, _ = self.residuals_to_fan_vote_share(residuals, week_groups)
            df_temp = df.copy()
            df_temp['est_fan_vote_share'] = fan_shares

            # 计算淘汰匹配率
            match_rate = self.compute_elimination_match_rate(df_temp)

            if match_rate > best_match_rate:
                best_match_rate = match_rate
                best_sensitivity = sens

        self.sensitivity = best_sensitivity

        print(f"\n[最优 Sensitivity]: {best_sensitivity:.4f}")
        print(f"[最高淘汰匹配率]: {best_match_rate:.2%}")

        return best_sensitivity

    def compute_elimination_match_rate(self, df: pd.DataFrame) -> float:
        """
        计算淘汰匹配率

        对每周：
        1. 使用评委分 + 估算的粉丝投票重建综合排名
        2. 找出预测的淘汰者
        3. 与实际淘汰者比较
        """
        correct_eliminations = 0
        total_weeks = 0

        for (season, week), group in df.groupby(['season', 'week']):
            if len(group) <= 3:  # 跳过人数太少的周
                continue

            # 使用 Rank Sum 方法（简化）
            judge_rank = group['judge_rank_in_week']
            fan_rank = group['est_fan_vote_share'].rank(ascending=False)

            combined_rank = judge_rank + fan_rank

            # 预测淘汰者（综合排名最差）
            predicted_eliminated = combined_rank.idxmax()

            # 实际淘汰者（当周被淘汰的人）
            # 简化：假设 placement 最差且 week == elimination_week 的人
            actual_eliminated_mask = (
                (group['week'] == group['elimination_week']) &
                (group['elimination_week'] > 0)
            )

            if actual_eliminated_mask.any():
                actual_eliminated = group[actual_eliminated_mask].index[0]

                if predicted_eliminated == actual_eliminated:
                    correct_eliminations += 1

                total_weeks += 1

        if total_weeks == 0:
            return 0.0

        return correct_eliminations / total_weeks

    def save_model(self, path: Path):
        """保存模型"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'alpha': self.alpha,
            'sensitivity': self.sensitivity,
            'feature_names': self.feature_names,
            'residual_std': self.residual_std
        }
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"\n[保存] 模型已保存到: {path}")


def run_ridge_model_v2(data_path: Path, output_dir: Path):
    """
    运行更新后的 Ridge 回归流程
    """
    print("=" * 80)
    print("Model B1 V2: Ridge Regression for Weekly Fan Vote Share Estimation")
    print("=" * 80)

    # 1. 加载数据
    print("\n[Step 1] 加载处理后的数据")
    df = pd.read_csv(data_path)
    print(f"  - 数据形状: {df.shape}")

    # 2. 准备训练集
    print("\n[Step 2] 准备训练集（S1-S27）")
    train_df = df[df['season'] <= 27].copy()

    # 3. 初始化模型
    model = RidgeFanVoteModelV2(alpha=1.0, sensitivity=1.0)

    # 4. 准备特征
    print("\n[Step 3] 准备特征和目标变量")
    X_train, y_train, groups_train, train_valid_df = model.prepare_features(train_df)
    print(f"  - 特征矩阵形状: {X_train.shape}")
    print(f"  - 目标变量形状: {y_train.shape}")

    # 5. 训练模型
    print("\n[Step 4] 训练模型")
    model.fit(X_train, y_train, groups_train, find_alpha=True)

    # 6. 计算残差
    print("\n[Step 5] 计算残差")
    residuals, y_pred = model.compute_residuals(X_train, y_train)

    # 7. 校准敏感度
    print("\n[Step 6] 校准敏感度系数")
    model.calibrate_sensitivity(X_train, y_train, train_valid_df)

    # 8. 计算粉丝投票份额
    print("\n[Step 7] 计算粉丝投票份额")
    week_groups = train_valid_df.groupby(['season', 'week']).ngroup()
    fan_shares, uncertainty_lower, uncertainty_upper = model.residuals_to_fan_vote_share(
        residuals, week_groups
    )

    train_valid_df['residual'] = residuals
    train_valid_df['fan_vote_share'] = fan_shares
    train_valid_df['uncertainty_lower'] = uncertainty_lower
    train_valid_df['uncertainty_upper'] = uncertainty_upper
    train_valid_df['uncertainty_range'] = uncertainty_upper - uncertainty_lower

    print(f"\n[粉丝投票份额统计]")
    print(f"  - 均值: {fan_shares.mean():.4f}")
    print(f"  - 标准差: {fan_shares.std():.4f}")
    print(f"  - 范围: [{fan_shares.min():.4f}, {fan_shares.max():.4f}]")
    print(f"  - 平均不确定性范围: {train_valid_df['uncertainty_range'].mean():.4f}")

    # 9. 验证每周总和是否为 1
    print(f"\n[验证] 每周粉丝投票份额总和:")
    week_sums = train_valid_df.groupby(['season', 'week'])['fan_vote_share'].sum()
    print(f"  - 均值: {week_sums.mean():.6f} (应该接近 1.0)")
    print(f"  - 标准差: {week_sums.std():.6f}")

    # 10. 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)

    model_path = output_dir / "ridge_model_v2.pkl"
    model.save_model(model_path)

    results_path = output_dir / "ridge_fan_vote_shares_v2.csv"
    train_valid_df.to_csv(results_path, index=False)
    print(f"[保存] 结果已保存到: {results_path}")

    # 11. 测试集验证
    print("\n" + "=" * 80)
    print("[Step 8] 在测试集上验证（S28-S34）")
    print("=" * 80)

    test_df = df[df['season'] >= 28].copy()
    if len(test_df) > 0:
        X_test, y_test, groups_test, test_valid_df = model.prepare_features(test_df)

        y_pred_test = model.predict(X_test)
        r2_test = r2_score(y_test, y_pred_test)
        rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))

        print(f"\n[测试集性能]")
        print(f"  - R2 Score: {r2_test:.4f}")
        print(f"  - RMSE: {rmse_test:.4f}")

        # 计算测试集的残差和粉丝投票份额
        residuals_test, _ = model.compute_residuals(X_test, y_test)
        week_groups_test = test_valid_df.groupby(['season', 'week']).ngroup()
        fan_shares_test, uncertainty_lower_test, uncertainty_upper_test = model.residuals_to_fan_vote_share(
            residuals_test, week_groups_test
        )

        test_valid_df['residual'] = residuals_test
        test_valid_df['fan_vote_share'] = fan_shares_test
        test_valid_df['uncertainty_lower'] = uncertainty_lower_test
        test_valid_df['uncertainty_upper'] = uncertainty_upper_test
        test_valid_df['uncertainty_range'] = uncertainty_upper_test - uncertainty_lower_test

        # 保存测试集结果
        test_results_path = output_dir / "ridge_fan_vote_shares_v2_test.csv"
        test_valid_df.to_csv(test_results_path, index=False)
        print(f"[保存] 测试集结果已保存到: {test_results_path}")

    print("\n" + "=" * 80)
    print("Model B1 V2 训练完成！")
    print("=" * 80)

    return model, train_valid_df


if __name__ == "__main__":
    from config import DATA_DIR

    data_path = DATA_DIR / "processed" / "weekly_panel.csv"
    output_dir = DATA_DIR / "models" / "ridge_v2"

    model, results = run_ridge_model_v2(data_path, output_dir)
