"""
Model D: Twin Model Analysis - 双子模型对比分析
根据 docs/11_model_d_impact_analysis.md 实现

目标：
1. 构建双子模型：M_fan (粉丝偏好) 和 M_judge (评委偏好)
2. 对比分析两个模型的特征重要性差异
3. 识别粉丝和评委的偏好差异
4. 基于分析结果提出新的投票系统

Question 3: Propose a "fairer" or "better" voting system
"""
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import cross_val_score
from scipy.stats import spearmanr
import warnings
warnings.filterwarnings('ignore')


class ProDancerFeatureBuilder:
    """
    构建职业舞者特征
    注意：防止数据泄露，S_n 的舞伴特征只能用 S_1 到 S_{n-1} 计算
    """

    def __init__(self):
        self.partner_stats = {}

    def build_partner_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        为每个舞伴构建历史统计特征
        """
        # 按赛季排序
        seasons = sorted(data['season'].unique())

        partner_features = []

        for season in seasons:
            # 获取该赛季之前的所有数据
            historical_data = data[data['season'] < season]

            # 获取该赛季的选手-舞伴配对
            current_season = data[data['season'] == season]

            for _, row in current_season.drop_duplicates(['celebrity_name', 'ballroom_partner']).iterrows():
                partner = row['ballroom_partner']

                if len(historical_data) > 0:
                    # 计算该舞伴的历史统计
                    partner_history = historical_data[historical_data['ballroom_partner'] == partner]

                    if len(partner_history) > 0:
                        # 获取每个赛季的最终排名
                        partner_placements = partner_history.groupby('season')['placement'].first()

                        partner_avg_place = partner_placements.mean()
                        partner_experience = len(partner_placements)
                        partner_win_rate = (partner_placements <= 3).mean()  # 进入前三的比例
                        partner_best_place = partner_placements.min()
                    else:
                        # 新舞伴，无历史数据
                        partner_avg_place = 7.0  # 默认中等排名
                        partner_experience = 0
                        partner_win_rate = 0.0
                        partner_best_place = 12
                else:
                    # 第一季，所有舞伴都是新的
                    partner_avg_place = 7.0
                    partner_experience = 0
                    partner_win_rate = 0.0
                    partner_best_place = 12

                partner_features.append({
                    'season': season,
                    'celebrity_name': row['celebrity_name'],
                    'ballroom_partner': partner,
                    'partner_avg_place': partner_avg_place,
                    'partner_experience': partner_experience,
                    'partner_win_rate': partner_win_rate,
                    'partner_best_place': partner_best_place
                })

        return pd.DataFrame(partner_features)


class TwinModelAnalyzer:
    """
    双子模型分析器
    M_fan: 预测粉丝投票份额
    M_judge: 预测评委评分
    """

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.n_estimators = n_estimators
        self.random_state = random_state

        self.model_fan = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=10,
            min_samples_split=5,
            random_state=random_state,
            n_jobs=-1
        )

        self.model_judge = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=10,
            min_samples_split=5,
            random_state=random_state,
            n_jobs=-1
        )

        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_names = []

    def prepare_features(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        准备特征矩阵

        Returns:
        --------
        X : 特征矩阵
        y_fan : 粉丝投票份额
        y_judge : 标准化评委分数
        """
        # 选择特征列
        feature_cols = [
            'celebrity_age_during_season',
            'celebrity_industry',
            'partner_avg_place',
            'partner_experience',
            'partner_win_rate',
            'week',
            'relative_judge_score',
        ]

        # 检查可用列
        available_cols = [col for col in feature_cols if col in data.columns]

        # 复制数据
        df = data[available_cols + ['fan_vote_share', 'judge_total']].copy()
        df = df.dropna()

        # 编码分类变量
        categorical_cols = ['celebrity_industry']
        for col in categorical_cols:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    df[col] = self.label_encoders[col].transform(df[col].astype(str))

        # 准备特征矩阵
        X = df[[col for col in available_cols]].values
        y_fan = df['fan_vote_share'].values
        y_judge = df['judge_total'].values

        # 标准化评委分数
        y_judge = self.scaler.fit_transform(y_judge.reshape(-1, 1)).flatten()

        self.feature_names = [col for col in available_cols]

        return X, y_fan, y_judge

    def train(self, X: np.ndarray, y_fan: np.ndarray, y_judge: np.ndarray):
        """
        训练双子模型
        """
        print("Training M_fan (Fan Preference Model)...")
        self.model_fan.fit(X, y_fan)
        fan_cv_score = cross_val_score(self.model_fan, X, y_fan, cv=5, scoring='r2')
        print(f"  - CV R2 Score: {fan_cv_score.mean():.4f} (+/- {fan_cv_score.std():.4f})")

        print("\nTraining M_judge (Judge Preference Model)...")
        self.model_judge.fit(X, y_judge)
        judge_cv_score = cross_val_score(self.model_judge, X, y_judge, cv=5, scoring='r2')
        print(f"  - CV R2 Score: {judge_cv_score.mean():.4f} (+/- {judge_cv_score.std():.4f})")

        return {
            'fan_cv_r2': fan_cv_score.mean(),
            'fan_cv_std': fan_cv_score.std(),
            'judge_cv_r2': judge_cv_score.mean(),
            'judge_cv_std': judge_cv_score.std()
        }

    def get_feature_importance(self) -> pd.DataFrame:
        """
        获取两个模型的特征重要性对比
        """
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'fan_importance': self.model_fan.feature_importances_,
            'judge_importance': self.model_judge.feature_importances_
        })

        # 计算重要性差异
        importance_df['importance_diff'] = (
            importance_df['fan_importance'] - importance_df['judge_importance']
        )

        # 计算排名
        importance_df['fan_rank'] = importance_df['fan_importance'].rank(ascending=False)
        importance_df['judge_rank'] = importance_df['judge_importance'].rank(ascending=False)

        return importance_df.sort_values('fan_importance', ascending=False)

    def calculate_rank_correlation(self, importance_df: pd.DataFrame) -> Dict:
        """
        计算特征重要性排名的 Spearman 相关系数
        """
        corr, p_value = spearmanr(
            importance_df['fan_rank'],
            importance_df['judge_rank']
        )

        return {
            'spearman_correlation': corr,
            'p_value': p_value,
            'interpretation': self._interpret_correlation(corr)
        }

    def _interpret_correlation(self, corr: float) -> str:
        """解释相关系数"""
        if corr > 0.7:
            return "High correlation: Fans and judges value similar factors"
        elif corr > 0.4:
            return "Moderate correlation: Some overlap in preferences"
        elif corr > 0.0:
            return "Low correlation: Different preference patterns"
        else:
            return "Negative correlation: Opposing preferences"


class FairnessAnalyzer:
    """
    公平性分析器
    分析不同投票系统的公平性指标
    """

    def __init__(self):
        self.metrics = {}

    def calculate_fairness_metrics(self, data: pd.DataFrame,
                                   importance_df: pd.DataFrame) -> Dict:
        """
        计算公平性指标
        """
        metrics = {}

        # 1. 技术权重 (Technical Weight)
        # 评委更看重的因素应该与技术相关
        technical_features = ['relative_judge_score', 'partner_avg_place', 'partner_experience']
        popularity_features = ['celebrity_industry', 'celebrity_age_during_season']

        tech_importance_fan = importance_df[
            importance_df['feature'].isin(technical_features)
        ]['fan_importance'].sum()

        tech_importance_judge = importance_df[
            importance_df['feature'].isin(technical_features)
        ]['judge_importance'].sum()

        metrics['technical_weight_fan'] = tech_importance_fan
        metrics['technical_weight_judge'] = tech_importance_judge
        metrics['technical_bias'] = tech_importance_judge - tech_importance_fan

        # 2. 人气权重 (Popularity Weight)
        pop_importance_fan = importance_df[
            importance_df['feature'].isin(popularity_features)
        ]['fan_importance'].sum()

        pop_importance_judge = importance_df[
            importance_df['feature'].isin(popularity_features)
        ]['judge_importance'].sum()

        metrics['popularity_weight_fan'] = pop_importance_fan
        metrics['popularity_weight_judge'] = pop_importance_judge
        metrics['popularity_bias'] = pop_importance_fan - pop_importance_judge

        # 3. 行业公平性 (Industry Fairness)
        if 'celebrity_industry' in data.columns:
            industry_stats = data.groupby('celebrity_industry').agg({
                'fan_vote_share': 'mean',
                'judge_total': 'mean',
                'placement': 'mean'
            }).reset_index()

            # 计算行业间的标准差（越小越公平）
            metrics['industry_variance_fan'] = industry_stats['fan_vote_share'].std()
            metrics['industry_variance_judge'] = industry_stats['judge_total'].std()

        self.metrics = metrics
        return metrics

    def propose_optimal_weights(self, metrics: Dict) -> Dict:
        """
        基于分析结果提出最优权重

        目标：平衡技术和人气，确保公平性
        """
        # 计算最优权重
        # 原则：技术应该占主导，但人气也应该有一定影响

        tech_bias = metrics.get('technical_bias', 0)
        pop_bias = metrics.get('popularity_bias', 0)

        # 如果评委过于看重技术，增加粉丝权重
        # 如果粉丝过于看重人气，增加评委权重

        # 基础权重：50-50
        base_judge_weight = 0.5
        base_fan_weight = 0.5

        # 调整因子
        if tech_bias > 0.1:  # 评委过于技术导向
            adjustment = min(tech_bias * 0.5, 0.15)
            optimal_fan_weight = base_fan_weight + adjustment
            optimal_judge_weight = base_judge_weight - adjustment
        elif pop_bias > 0.1:  # 粉丝过于人气导向
            adjustment = min(pop_bias * 0.5, 0.15)
            optimal_judge_weight = base_judge_weight + adjustment
            optimal_fan_weight = base_fan_weight - adjustment
        else:
            optimal_judge_weight = base_judge_weight
            optimal_fan_weight = base_fan_weight

        return {
            'optimal_judge_weight': optimal_judge_weight,
            'optimal_fan_weight': optimal_fan_weight,
            'reasoning': self._generate_weight_reasoning(
                optimal_judge_weight, optimal_fan_weight, metrics
            )
        }

    def _generate_weight_reasoning(self, judge_w: float, fan_w: float,
                                   metrics: Dict) -> str:
        """生成权重推荐理由"""
        reasoning = f"Recommended weights: Judge {judge_w:.0%}, Fan {fan_w:.0%}\n\n"

        reasoning += "Rationale:\n"
        reasoning += f"1. Technical bias: {metrics.get('technical_bias', 0):.3f}\n"
        reasoning += f"   - Judges emphasize technical skills more than fans\n"
        reasoning += f"2. Popularity bias: {metrics.get('popularity_bias', 0):.3f}\n"
        reasoning += f"   - Fans favor popular industries more than judges\n"
        reasoning += f"3. The proposed weights balance these biases\n"

        return reasoning


class NewVotingSystem:
    """
    新投票系统提案
    基于双子模型分析结果设计
    """

    def __init__(self):
        self.system_name = "Adaptive Weighted Voting System (AWVS)"
        self.description = """
        A dynamic voting system that adapts weights based on:
        1. Competition stage (early vs late season)
        2. Performance trajectory (improving vs declining)
        3. Balanced consideration of technical skill and audience engagement
        """

    def calculate_score(self, judge_score: float, fan_vote: float,
                       week: int, total_weeks: int,
                       trend: float = 0) -> float:
        """
        计算新系统下的综合得分

        Parameters:
        -----------
        judge_score : float
            标准化评委分数 (0-1)
        fan_vote : float
            粉丝投票份额 (0-1)
        week : int
            当前周次
        total_weeks : int
            总周数
        trend : float
            表现趋势 (正=进步, 负=退步)

        Returns:
        --------
        combined_score : float
            综合得分
        """
        # 动态权重：随着赛季进展，技术权重增加
        progress = week / total_weeks

        # 基础权重
        base_judge_weight = 0.5
        base_fan_weight = 0.5

        # 阶段调整：后期更看重技术
        stage_adjustment = progress * 0.15  # 最多调整 15%

        # 趋势奖励：进步的选手获得额外加分
        trend_bonus = max(0, trend * 0.05)  # 最多 5% 奖励

        # 最终权重
        judge_weight = base_judge_weight + stage_adjustment
        fan_weight = base_fan_weight - stage_adjustment

        # 综合得分
        combined_score = (
            judge_weight * judge_score +
            fan_weight * fan_vote +
            trend_bonus
        )

        return combined_score

    def simulate_elimination(self, week_data: pd.DataFrame) -> str:
        """
        模拟新系统下的淘汰结果
        """
        scores = []

        for _, row in week_data.iterrows():
            # 标准化评委分数
            judge_norm = row['judge_total'] / week_data['judge_total'].max()
            fan_norm = row['fan_vote_share']

            # 获取趋势
            trend = row.get('trend', 0)
            if pd.isna(trend):
                trend = 0

            # 计算综合得分
            score = self.calculate_score(
                judge_norm, fan_norm,
                row['week'], 12,  # 假设总共 12 周
                trend
            )

            scores.append({
                'celebrity_name': row['celebrity_name'],
                'combined_score': score
            })

        scores_df = pd.DataFrame(scores)
        eliminated = scores_df.loc[scores_df['combined_score'].idxmin(), 'celebrity_name']

        return eliminated

    def get_system_description(self) -> Dict:
        """
        获取系统完整描述
        """
        return {
            'name': self.system_name,
            'description': self.description,
            'key_features': [
                "Dynamic weight adjustment based on competition stage",
                "Trend bonus rewards improvement over time",
                "Balanced consideration of skill and popularity",
                "Transparent and predictable scoring formula"
            ],
            'formula': """
            Combined Score = W_judge × Judge_Score + W_fan × Fan_Vote + Trend_Bonus

            Where:
            - W_judge = 0.50 + 0.15 × (week / total_weeks)
            - W_fan = 0.50 - 0.15 × (week / total_weeks)
            - Trend_Bonus = max(0, trend × 0.05)
            """,
            'benefits': [
                "Early weeks: Equal weight (50-50) encourages diverse contestants",
                "Late weeks: Higher judge weight (65-35) rewards technical excellence",
                "Trend bonus: Rewards contestants who show improvement",
                "Reduces controversy: Clear, objective formula"
            ]
        }


def run_twin_model_analysis(data_path: Path, output_dir: Path):
    """
    运行完整的双子模型分析
    """
    print("=" * 80)
    print("Model D: Twin Model Analysis - Fan vs Judge Preference Comparison")
    print("=" * 80)

    # 1. 加载数据
    print("\n[Step 1] Loading data...")
    data = pd.read_csv(data_path)
    print(f"  - Data shape: {data.shape}")
    print(f"  - Seasons: {data['season'].min()} - {data['season'].max()}")

    # 2. 构建舞伴特征
    print("\n[Step 2] Building professional dancer features...")
    partner_builder = ProDancerFeatureBuilder()
    partner_features = partner_builder.build_partner_features(data)

    # 合并特征
    data = data.merge(
        partner_features,
        on=['season', 'celebrity_name', 'ballroom_partner'],
        how='left'
    )

    # 填充缺失值
    data['partner_avg_place'] = data['partner_avg_place'].fillna(7.0)
    data['partner_experience'] = data['partner_experience'].fillna(0)
    data['partner_win_rate'] = data['partner_win_rate'].fillna(0)

    print(f"  - Partner features added: {len(partner_features)} records")

    # 3. 训练双子模型
    print("\n[Step 3] Training Twin Models...")
    analyzer = TwinModelAnalyzer(n_estimators=100, random_state=42)

    X, y_fan, y_judge = analyzer.prepare_features(data)
    print(f"  - Feature matrix shape: {X.shape}")
    print(f"  - Features: {analyzer.feature_names}")

    cv_scores = analyzer.train(X, y_fan, y_judge)

    # 4. 特征重要性对比
    print("\n[Step 4] Comparing Feature Importance...")
    importance_df = analyzer.get_feature_importance()

    print("\n[Feature Importance Comparison]")
    print(importance_df.to_string(index=False))

    # 5. 计算排名相关性
    print("\n[Step 5] Calculating Rank Correlation...")
    correlation = analyzer.calculate_rank_correlation(importance_df)

    print(f"\n[Spearman Correlation]")
    print(f"  - Correlation: {correlation['spearman_correlation']:.4f}")
    print(f"  - P-value: {correlation['p_value']:.4f}")
    print(f"  - Interpretation: {correlation['interpretation']}")

    # 6. 公平性分析
    print("\n[Step 6] Analyzing Fairness Metrics...")
    fairness_analyzer = FairnessAnalyzer()
    fairness_metrics = fairness_analyzer.calculate_fairness_metrics(data, importance_df)

    print("\n[Fairness Metrics]")
    for key, value in fairness_metrics.items():
        print(f"  - {key}: {value:.4f}")

    # 7. 提出最优权重
    print("\n[Step 7] Proposing Optimal Weights...")
    optimal_weights = fairness_analyzer.propose_optimal_weights(fairness_metrics)

    print(f"\n{optimal_weights['reasoning']}")

    # 8. 新投票系统
    print("\n[Step 8] Proposing New Voting System...")
    new_system = NewVotingSystem()
    system_desc = new_system.get_system_description()

    print(f"\n[{system_desc['name']}]")
    print(f"Description: {system_desc['description']}")
    print(f"\nKey Features:")
    for feature in system_desc['key_features']:
        print(f"  - {feature}")
    print(f"\nFormula:{system_desc['formula']}")
    print(f"\nBenefits:")
    for benefit in system_desc['benefits']:
        print(f"  - {benefit}")

    # 9. 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)

    # 保存特征重要性
    importance_path = output_dir / "feature_importance_comparison.csv"
    importance_df.to_csv(importance_path, index=False)
    print(f"\n[Saved] Feature importance: {importance_path}")

    # 保存分析结果
    results = {
        'cv_scores': cv_scores,
        'correlation': correlation,
        'fairness_metrics': fairness_metrics,
        'optimal_weights': optimal_weights,
        'system_description': system_desc
    }

    print("\n" + "=" * 80)
    print("Model D Analysis Complete!")
    print("=" * 80)

    return analyzer, importance_df, results, new_system


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # 添加 src 目录到路径
    src_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(src_dir))
    from config import DATA_DIR

    data_path = DATA_DIR / "models" / "ridge_v2" / "ridge_fan_vote_shares_v2.csv"
    output_dir = DATA_DIR / "twin_model"

    analyzer, importance_df, results, new_system = run_twin_model_analysis(
        data_path, output_dir
    )
