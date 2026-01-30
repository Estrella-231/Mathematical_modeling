"""
Model B2: Random Forest for Fan Preference Drivers Analysis
根据 docs/09_model_b2_rf_impl.md 实现

目标：
1. 解释粉丝投票残差（识别驱动因素）
2. 为新选手构建基础人气先验
3. 验证 B1 提取的粉丝票是否具有统计规律
"""
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import pickle
from typing import Dict, Tuple


class RandomForestFanPreferenceModel:
    """
    Random Forest 模型用于分析粉丝偏好驱动因素

    核心思想：
    - 使用选手特征（年龄、行业、舞伴等）预测 Model B1 的残差
    - 残差代表粉丝投票效应
    - 如果 RF 能预测残差，说明粉丝投票有规律可循
    """

    def __init__(self, n_estimators=100, max_depth=10, random_state=42):
        """
        Parameters:
        -----------
        n_estimators : int
            树的数量
        max_depth : int
            树的最大深度
        random_state : int
            随机种子
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1
        )
        self.label_encoders = {}
        self.feature_names = None
        self.is_fitted = False

    def prepare_features(self, df: pd.DataFrame, residuals: pd.Series = None) -> Tuple:
        """
        准备特征和目标变量

        特征：
        - 静态特征：age, industry, homestate, ballroom_partner
        - 动态特征：relative_judge_score, cumulative_average, trend
        - 交互特征：age_group × industry

        目标：
        - residual（来自 Model B1）
        """
        feature_df = df.copy()

        # 1. 静态特征
        # 年龄
        if 'celebrity_age_during_season' in feature_df.columns:
            feature_df['age'] = feature_df['celebrity_age_during_season']
        else:
            feature_df['age'] = 0

        # 年龄分组
        feature_df['age_group'] = pd.cut(
            feature_df['age'],
            bins=[0, 25, 35, 45, 55, 100],
            labels=['<25', '25-35', '35-45', '45-55', '55+']
        )

        # 行业
        if 'celebrity_industry' in feature_df.columns:
            feature_df['industry'] = feature_df['celebrity_industry']
        else:
            feature_df['industry'] = 'Unknown'

        # 州
        if 'celebrity_homestate' in feature_df.columns:
            feature_df['homestate'] = feature_df['celebrity_homestate']
        else:
            feature_df['homestate'] = 'Unknown'

        # 舞伴
        if 'ballroom_partner' in feature_df.columns:
            feature_df['partner'] = feature_df['ballroom_partner']
        else:
            feature_df['partner'] = 'Unknown'

        # 2. 动态特征
        dynamic_features = [
            'relative_judge_score',
            'cumulative_average',
            'trend',
            'judge_rank_in_week',
            'week'
        ]

        for feat in dynamic_features:
            if feat not in feature_df.columns:
                feature_df[feat] = 0
            else:
                feature_df[feat] = feature_df[feat].fillna(0)

        # 3. 交互特征
        # age × industry (通过 one-hot 编码后自动产生交互)

        # 4. 选择特征列
        categorical_features = ['age_group', 'industry', 'homestate', 'partner']
        numerical_features = dynamic_features + ['age']

        # 编码分类特征
        for feat in categorical_features:
            if feat not in self.label_encoders:
                self.label_encoders[feat] = LabelEncoder()
                feature_df[f'{feat}_encoded'] = self.label_encoders[feat].fit_transform(
                    feature_df[feat].astype(str)
                )
            else:
                # 处理测试集中的新类别
                feature_df[f'{feat}_encoded'] = feature_df[feat].astype(str).apply(
                    lambda x: self.label_encoders[feat].transform([x])[0]
                    if x in self.label_encoders[feat].classes_
                    else -1
                )

        # 最终特征列
        encoded_categorical = [f'{feat}_encoded' for feat in categorical_features]
        self.feature_names = numerical_features + encoded_categorical

        X = feature_df[self.feature_names].values

        # 目标变量
        if residuals is not None:
            y = residuals.values
        else:
            y = None

        return X, y, feature_df

    def fit(self, X, y):
        """训练模型"""
        print("\n" + "=" * 60)
        print("训练 Random Forest 模型")
        print("=" * 60)

        print(f"\n[训练参数]")
        print(f"  - n_estimators: {self.n_estimators}")
        print(f"  - max_depth: {self.max_depth}")
        print(f"  - 特征数量: {X.shape[1]}")
        print(f"  - 样本数量: {X.shape[0]}")

        # 训练模型
        self.model.fit(X, y)

        # 计算训练集性能
        y_pred = self.model.predict(X)
        r2 = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        mae = mean_absolute_error(y, y_pred)

        print(f"\n[训练集性能]")
        print(f"  - R2 Score: {r2:.4f}")
        print(f"  - RMSE: {rmse:.4f}")
        print(f"  - MAE: {mae:.4f}")

        # 交叉验证
        print(f"\n[5-Fold 交叉验证]")
        cv_scores = cross_val_score(
            self.model, X, y,
            cv=5,
            scoring='r2',
            n_jobs=-1
        )
        print(f"  - CV R2 均值: {cv_scores.mean():.4f}")
        print(f"  - CV R2 标准差: {cv_scores.std():.4f}")

        self.is_fitted = True
        return self

    def predict(self, X):
        """预测"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")
        return self.model.predict(X)

    def get_feature_importance(self) -> pd.DataFrame:
        """获取特征重要性"""
        if not self.is_fitted:
            raise ValueError("模型尚未训练")

        importance = self.model.feature_importances_
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)

        return importance_df

    def analyze_feature_importance(self):
        """分析特征重要性"""
        print("\n" + "=" * 60)
        print("特征重要性分析")
        print("=" * 60)

        importance_df = self.get_feature_importance()

        print(f"\n[Top 10 最重要特征]")
        for idx, row in importance_df.head(10).iterrows():
            print(f"  {row['feature']}: {row['importance']:.4f}")

        # 按类别汇总
        print(f"\n[按特征类别汇总]")

        # 静态特征
        static_features = [f for f in self.feature_names if '_encoded' in f]
        static_importance = importance_df[
            importance_df['feature'].isin(static_features)
        ]['importance'].sum()
        print(f"  - 静态特征（年龄、行业、州、舞伴）: {static_importance:.4f}")

        # 动态特征
        dynamic_features = [f for f in self.feature_names if '_encoded' not in f]
        dynamic_importance = importance_df[
            importance_df['feature'].isin(dynamic_features)
        ]['importance'].sum()
        print(f"  - 动态特征（评委分、趋势等）: {dynamic_importance:.4f}")

        return importance_df

    def save_model(self, path: Path):
        """保存模型"""
        model_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth
        }
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"\n[保存] 模型已保存到: {path}")

    @classmethod
    def load_model(cls, path: Path):
        """加载模型"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)

        instance = cls(
            n_estimators=model_data['n_estimators'],
            max_depth=model_data['max_depth']
        )
        instance.model = model_data['model']
        instance.label_encoders = model_data['label_encoders']
        instance.feature_names = model_data['feature_names']
        instance.is_fitted = True

        return instance


def run_random_forest_model(ridge_results_path: Path, weekly_panel_path: Path, output_dir: Path):
    """
    运行完整的 Random Forest 流程
    """
    print("=" * 80)
    print("Model B2: Random Forest for Fan Preference Drivers Analysis")
    print("=" * 80)

    # 1. 加载 Model B1 的结果（残差）
    print("\n[Step 1] 加载 Model B1 的残差")
    ridge_results = pd.read_csv(ridge_results_path)
    print(f"  - Ridge 结果形状: {ridge_results.shape}")

    # 2. 加载完整的周级面板数据
    print("\n[Step 2] 加载周级面板数据")
    weekly_panel = pd.read_csv(weekly_panel_path)
    print(f"  - 周级面板形状: {weekly_panel.shape}")

    # 3. 合并数据（确保有残差的行）
    print("\n[Step 3] 合并数据")
    # Ridge 结果已经是筛选后的数据，直接使用
    merged_df = ridge_results.copy()
    print(f"  - 合并后形状: {merged_df.shape}")

    # 4. 准备训练集和测试集
    print("\n[Step 4] 准备训练集和测试集")
    train_df = merged_df[merged_df['season'] <= 27].copy()
    test_df = merged_df[merged_df['season'] >= 28].copy()

    print(f"  - 训练集: {len(train_df)} 行")
    print(f"  - 测试集: {len(test_df)} 行")

    # 5. 初始化模型
    model = RandomForestFanPreferenceModel(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )

    # 6. 准备特征
    print("\n[Step 5] 准备特征")
    X_train, y_train, train_featured = model.prepare_features(train_df, train_df['residual'])
    print(f"  - 训练集特征形状: {X_train.shape}")
    print(f"  - 特征列: {model.feature_names}")

    # 7. 训练模型
    print("\n[Step 6] 训练模型")
    model.fit(X_train, y_train)

    # 8. 特征重要性分析
    print("\n[Step 7] 特征重要性分析")
    importance_df = model.analyze_feature_importance()

    # 9. 测试集验证
    if len(test_df) > 0:
        print("\n" + "=" * 80)
        print("[Step 8] 测试集验证")
        print("=" * 80)

        X_test, y_test, test_featured = model.prepare_features(test_df, test_df['residual'])

        y_pred_test = model.predict(X_test)
        r2_test = r2_score(y_test, y_pred_test)
        rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
        mae_test = mean_absolute_error(y_test, y_pred_test)

        print(f"\n[测试集性能]")
        print(f"  - R2 Score: {r2_test:.4f}")
        print(f"  - RMSE: {rmse_test:.4f}")
        print(f"  - MAE: {mae_test:.4f}")

        # 解释 R2
        print(f"\n[结果解释]")
        if r2_test > 0.3:
            print(f"  ✓ R2 = {r2_test:.2f} > 0.3")
            print(f"    说明粉丝投票有明显的规律性，由选手特征驱动")
            print(f"    Model B1 提取的残差具有统计意义")
        elif r2_test > 0.1:
            print(f"  ~ R2 = {r2_test:.2f} (0.1-0.3)")
            print(f"    说明粉丝投票有一定规律，但也受其他因素影响")
        else:
            print(f"  ✗ R2 = {r2_test:.2f} < 0.1")
            print(f"    说明粉丝投票主要由数据中未包含的因素驱动")
            print(f"    （如个人魅力、绯闻、社交媒体影响等）")

    # 10. 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)

    # 保存模型
    model_path = output_dir / "random_forest_model.pkl"
    model.save_model(model_path)

    # 保存特征重要性
    importance_path = output_dir / "feature_importance.csv"
    importance_df.to_csv(importance_path, index=False)
    print(f"[保存] 特征重要性: {importance_path}")

    # 保存预测结果
    train_featured['rf_prediction'] = model.predict(X_train)
    train_featured['rf_residual'] = y_train - train_featured['rf_prediction']

    results_path = output_dir / "rf_predictions.csv"
    train_featured.to_csv(results_path, index=False)
    print(f"[保存] 预测结果: {results_path}")

    print("\n" + "=" * 80)
    print("Model B2 训练完成！")
    print("=" * 80)

    return model, importance_df


if __name__ == "__main__":
    from config import DATA_DIR

    ridge_results_path = DATA_DIR / "models" / "ridge_v2" / "ridge_fan_vote_shares_v2.csv"
    weekly_panel_path = DATA_DIR / "processed" / "weekly_panel.csv"
    output_dir = DATA_DIR / "models" / "random_forest"

    model, importance = run_random_forest_model(ridge_results_path, weekly_panel_path, output_dir)
