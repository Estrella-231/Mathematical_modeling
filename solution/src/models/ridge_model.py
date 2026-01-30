"""
Model B1: Ridge Regression for Fan Vote Estimation
根据 docs/08_model_b1_ridge_impl.md 实现

目标：通过残差分析分离"评委效应"与"粉丝效应"
"""
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import pickle


class RidgeFanVoteModel:
    """
    Ridge 回归模型用于估计粉丝投票影响

    核心思想：
    - 使用评委分数预测选手的理论排名
    - 实际排名与预测排名的差异（残差）代表粉丝投票的影响
    - 残差 < 0：表现优于预期 -> 粉丝支持高
    - 残差 > 0：表现差于预期 -> 粉丝支持低
    """

    def __init__(self, alpha=1.0, gamma=1.0):
        """
        Parameters:
        -----------
        alpha : float
            Ridge 正则化强度
        gamma : float
            残差到粉丝分数的缩放因子
        """
        self.alpha = alpha
        self.gamma = gamma
        self.model = Ridge(alpha=alpha)
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_fitted = False

    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """
        准备特征和目标变量

        特征：
        - relative_judge_score: Z-Score（标准化评委分）
        - cumulative_average: 累积平均分
        - is_bottom_2_judge: 是否在倒数两名
        - judge_rank_in_week: 周内排名

        目标：
        - placement: 最终赛季排名（1 = 冠军）
        """
        # 只使用有效周的数据
        valid_df = df[df['week_valid'] == True].copy()

        # 排除决赛周（只有少数人）和人数太少的周
        # 统计每周的人数
        week_counts = valid_df.groupby(['season', 'week']).size()
        valid_weeks = week_counts[week_counts > 3].index

        # 过滤数据
        valid_df = valid_df.set_index(['season', 'week'])
        valid_df = valid_df.loc[valid_df.index.isin(valid_weeks)].reset_index()

        # 特征列
        feature_cols = [
            'relative_judge_score',
            'cumulative_average',
            'is_bottom_2_judge',
            'judge_rank_in_week'
        ]

        # 处理缺失值
        for col in feature_cols:
            if col in valid_df.columns:
                valid_df[col] = valid_df[col].fillna(0)

        # 转换布尔值为整数
        valid_df['is_bottom_2_judge'] = valid_df['is_bottom_2_judge'].astype(int)

        X = valid_df[feature_cols].values
        y = valid_df['placement'].values  # 最终排名（1 = 最好）
        groups = valid_df['season'].values  # 用于 GroupKFold

        self.feature_names = feature_cols

        return X, y, groups, valid_df

    def find_optimal_alpha(self, X, y, groups, alphas=None):
        """
        使用交叉验证找到最优的 alpha

        使用 GroupKFold 确保同一赛季的数据不会同时出现在训练集和验证集
        """
        if alphas is None:
            alphas = np.logspace(-3, 3, 50)

        print(f"\n[交叉验证] 搜索最优 alpha...")
        print(f"  - 候选 alpha 范围: {alphas.min():.4f} - {alphas.max():.4f}")
        print(f"  - 候选数量: {len(alphas)}")

        # 使用 RidgeCV 进行交叉验证
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
        """
        训练模型

        Parameters:
        -----------
        X : array-like
            特征矩阵
        y : array-like
            目标变量（placement）
        groups : array-like
            分组标签（season），用于 GroupKFold
        find_alpha : bool
            是否自动寻找最优 alpha
        """
        print("\n" + "=" * 60)
        print("训练 Ridge 回归模型")
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

        # 特征重要性（系数）
        print(f"\n[特征重要性] (系数)")
        for name, coef in zip(self.feature_names, self.model.coef_):
            print(f"  - {name}: {coef:.4f}")
        print(f"  - Intercept: {self.model.intercept_:.4f}")

        self.is_fitted = True

        return self

    def predict(self, X):
        """预测排名"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练，请先调用 fit()")

        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def compute_residuals(self, X, y):
        """
        计算残差

        残差 = 实际排名 - 预测排名
        - 残差 < 0: 实际排名更好（数字更小）-> 粉丝支持高
        - 残差 > 0: 实际排名更差（数字更大）-> 粉丝支持低
        """
        y_pred = self.predict(X)
        residuals = y - y_pred
        return residuals, y_pred

    def residuals_to_fan_scores(self, residuals):
        """
        将残差转换为粉丝支持分数

        使用 Sigmoid 函数：
        FanScore = 1 / (1 + exp(residual * gamma))

        - 残差 < 0 (表现好) -> FanScore > 0.5
        - 残差 > 0 (表现差) -> FanScore < 0.5
        """
        fan_scores = 1 / (1 + np.exp(residuals * self.gamma))
        return fan_scores

    def analyze_residuals(self, residuals, df):
        """
        分析残差分布
        """
        print("\n" + "=" * 60)
        print("残差分析")
        print("=" * 60)

        print(f"\n[残差统计]")
        print(f"  - 均值: {residuals.mean():.4f}")
        print(f"  - 标准差: {residuals.std():.4f}")
        print(f"  - 最小值: {residuals.min():.4f}")
        print(f"  - 最大值: {residuals.max():.4f}")
        print(f"  - 中位数: {np.median(residuals):.4f}")

        # 残差 < 0 的比例（表现优于预期）
        better_than_expected = (residuals < 0).sum() / len(residuals)
        print(f"\n[表现优于预期的比例]: {better_than_expected:.2%}")

        # 找出残差最大和最小的选手
        df_with_residuals = df.copy()
        df_with_residuals['residual'] = residuals

        print(f"\n[Top 10 粉丝支持最高] (残差最负)")
        top_fan_support = df_with_residuals.nsmallest(10, 'residual')
        for idx, row in top_fan_support.iterrows():
            print(f"  - {row['celebrity_name']} (S{row['season']}, W{row['week']}): "
                  f"实际排名={row['placement']}, 残差={row['residual']:.2f}")

        print(f"\n[Top 10 粉丝支持最低] (残差最正)")
        low_fan_support = df_with_residuals.nlargest(10, 'residual')
        for idx, row in low_fan_support.iterrows():
            print(f"  - {row['celebrity_name']} (S{row['season']}, W{row['week']}): "
                  f"实际排名={row['placement']}, 残差={row['residual']:.2f}")

        return df_with_residuals

    def save_model(self, path: Path):
        """保存模型"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'alpha': self.alpha,
            'gamma': self.gamma,
            'feature_names': self.feature_names
        }
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"\n[保存] 模型已保存到: {path}")

    @classmethod
    def load_model(cls, path: Path):
        """加载模型"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)

        instance = cls(alpha=model_data['alpha'], gamma=model_data['gamma'])
        instance.model = model_data['model']
        instance.scaler = model_data['scaler']
        instance.feature_names = model_data['feature_names']
        instance.is_fitted = True

        return instance


def run_ridge_model(data_path: Path, output_dir: Path):
    """
    运行完整的 Ridge 回归流程
    """
    print("=" * 80)
    print("Model B1: Ridge Regression for Fan Vote Estimation")
    print("=" * 80)

    # 1. 加载数据
    print("\n[Step 1] 加载处理后的数据")
    df = pd.read_csv(data_path)
    print(f"  - 数据形状: {df.shape}")
    print(f"  - 赛季范围: {df['season'].min()} - {df['season'].max()}")

    # 2. 准备训练集（S1-S27）
    print("\n[Step 2] 准备训练集（S1-S27）")
    train_df = df[df['season'] <= 27].copy()
    print(f"  - 训练集形状: {train_df.shape}")

    # 3. 初始化模型
    model = RidgeFanVoteModel(alpha=1.0, gamma=0.5)

    # 4. 准备特征
    print("\n[Step 3] 准备特征和目标变量")
    X_train, y_train, groups_train, train_valid_df = model.prepare_features(train_df)
    print(f"  - 特征矩阵形状: {X_train.shape}")
    print(f"  - 目标变量形状: {y_train.shape}")
    print(f"  - 特征列: {model.feature_names}")

    # 5. 训练模型
    print("\n[Step 4] 训练模型")
    model.fit(X_train, y_train, groups_train, find_alpha=True)

    # 6. 计算残差
    print("\n[Step 5] 计算残差")
    residuals, y_pred = model.compute_residuals(X_train, y_train)

    # 7. 残差分析
    print("\n[Step 6] 残差分析")
    df_with_residuals = model.analyze_residuals(residuals, train_valid_df)

    # 8. 转换为粉丝分数
    print("\n[Step 7] 转换为粉丝支持分数")
    fan_scores = model.residuals_to_fan_scores(residuals)
    df_with_residuals['fan_score'] = fan_scores

    print(f"\n[粉丝分数统计]")
    print(f"  - 均值: {fan_scores.mean():.4f}")
    print(f"  - 标准差: {fan_scores.std():.4f}")
    print(f"  - 范围: [{fan_scores.min():.4f}, {fan_scores.max():.4f}]")

    # 9. 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)

    # 保存模型
    model_path = output_dir / "ridge_model.pkl"
    model.save_model(model_path)

    # 保存残差和粉丝分数
    results_path = output_dir / "ridge_fan_scores.csv"
    df_with_residuals.to_csv(results_path, index=False)
    print(f"[保存] 残差和粉丝分数已保存到: {results_path}")

    # 10. 在测试集上验证（S28-S34）
    print("\n" + "=" * 80)
    print("[Step 8] 在测试集上验证（S28-S34）")
    print("=" * 80)

    test_df = df[df['season'] >= 28].copy()
    X_test, y_test, groups_test, test_valid_df = model.prepare_features(test_df)

    if len(X_test) > 0:
        y_pred_test = model.predict(X_test)
        r2_test = r2_score(y_test, y_pred_test)
        rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
        mae_test = mean_absolute_error(y_test, y_pred_test)

        print(f"\n[测试集性能]")
        print(f"  - R2 Score: {r2_test:.4f}")
        print(f"  - RMSE: {rmse_test:.4f}")
        print(f"  - MAE: {mae_test:.4f}")

        # 测试集残差分析
        residuals_test, _ = model.compute_residuals(X_test, y_test)
        test_valid_df['residual'] = residuals_test
        test_valid_df['fan_score'] = model.residuals_to_fan_scores(residuals_test)

        # 保存测试集结果
        test_results_path = output_dir / "ridge_fan_scores_test.csv"
        test_valid_df.to_csv(test_results_path, index=False)
        print(f"[保存] 测试集结果已保存到: {test_results_path}")

    print("\n" + "=" * 80)
    print("Model B1 训练完成！")
    print("=" * 80)

    return model, df_with_residuals


if __name__ == "__main__":
    from config import DATA_DIR

    data_path = DATA_DIR / "processed" / "weekly_panel.csv"
    output_dir = DATA_DIR / "models" / "ridge"

    model, results = run_ridge_model(data_path, output_dir)
