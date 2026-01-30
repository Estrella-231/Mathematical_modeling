"""
Model C: Counterfactual Simulation - Voting Method Comparison
根据 docs/10_model_c_comparison.md 实现

目标：
1. 使用 Ridge V2 的粉丝投票份额模拟不同投票规则
2. 比较 Rank Sum vs Percent Sum vs Judge Save 的差异
3. 分析争议案例
4. 计算 Fan Favorability Index (FFI)
5. 推荐最佳投票机制
"""
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt


def calculate_fan_favorability_index(judge_scores: pd.Series, fan_votes: pd.Series) -> pd.Series:
    """
    计算 Fan Favorability Index (FFI)

    FFI = (粉丝投票排名 - 评委排名) / (N - 1)

    - 正值: 粉丝更喜欢该选手（粉丝排名比评委排名好）
    - 负值: 评委更喜欢该选手（评委排名比粉丝排名好）
    - 范围: [-1, 1]

    Parameters:
    -----------
    judge_scores : pd.Series
        评委分数（越高越好）
    fan_votes : pd.Series
        粉丝投票份额（越高越好）

    Returns:
    --------
    ffi : pd.Series
        每位选手的 FFI 值
    """
    n = len(judge_scores)
    if n <= 1:
        return pd.Series(0, index=judge_scores.index)

    # 计算排名（降序，1 = 最好）
    judge_rank = judge_scores.rank(ascending=False, method='average')
    fan_rank = fan_votes.rank(ascending=False, method='average')

    # FFI = (fan_rank - judge_rank) / (N - 1)
    # 注意：如果粉丝排名更好（数值更小），则 fan_rank - judge_rank < 0
    # 我们希望粉丝更喜欢时 FFI > 0，所以用 judge_rank - fan_rank
    ffi = (judge_rank - fan_rank) / (n - 1)

    return ffi


class VotingSimulator:
    """
    投票规则模拟器

    支持三种规则：
    - Rule A (Rank Sum): 评委排名 + 粉丝排名，总和最大者淘汰
    - Rule B (Percent Sum): 评委百分比 + 粉丝百分比，总和最小者淘汰
    - Rule C (Judge Save): Rank Sum 确定倒数两名，评委淘汰评分低者
    """

    def __init__(self):
        self.simulation_results = []

    def rank_sum_rule(self, judge_scores: pd.Series, fan_votes: pd.Series) -> str:
        """
        Rule A: Rank Sum
        评委排名 + 粉丝排名，总和最大者淘汰（排名越大越差）
        """
        # 计算排名（降序，1 = 最好）
        judge_rank = judge_scores.rank(ascending=False, method='min')
        fan_rank = fan_votes.rank(ascending=False, method='min')

        # 总和最大者淘汰
        combined_rank = judge_rank + fan_rank
        eliminated = combined_rank.idxmax()

        return eliminated

    def percent_sum_rule(self, judge_scores: pd.Series, fan_votes: pd.Series) -> str:
        """
        Rule B: Percent Sum
        评委百分比 + 粉丝百分比，总和最小者淘汰
        """
        # 计算百分比
        judge_percent = judge_scores / judge_scores.sum()
        fan_percent = fan_votes / fan_votes.sum()

        # 总和最小者淘汰
        combined_percent = judge_percent + fan_percent
        eliminated = combined_percent.idxmin()

        return eliminated

    def judge_save_rule(self, judge_scores: pd.Series, fan_votes: pd.Series) -> str:
        """
        Rule C: Judge Save
        Rank Sum 确定倒数两名，评委淘汰评分低者
        """
        # 使用 Rank Sum 找出倒数两名
        judge_rank = judge_scores.rank(ascending=False, method='min')
        fan_rank = fan_votes.rank(ascending=False, method='min')
        combined_rank = judge_rank + fan_rank

        # 找出倒数两名
        bottom_two = combined_rank.nlargest(2).index

        # 评委淘汰评分低者
        eliminated = judge_scores.loc[bottom_two].idxmin()

        return eliminated

    def simulate_week(self, week_df: pd.DataFrame, rule: str) -> str:
        """
        模拟单周的淘汰结果

        Parameters:
        -----------
        week_df : DataFrame
            当周的数据，包含 judge_total 和 fan_vote_share
        rule : str
            规则名称：'rank_sum', 'percent_sum', 'judge_save'

        Returns:
        --------
        eliminated : str
            被淘汰的选手名字
        """
        if len(week_df) <= 2:
            # 人数太少，不模拟
            return None

        judge_scores = week_df['judge_total']
        fan_votes = week_df['fan_vote_share']

        # 设置 index 为选手名字
        judge_scores.index = week_df['celebrity_name']
        fan_votes.index = week_df['celebrity_name']

        if rule == 'rank_sum':
            return self.rank_sum_rule(judge_scores, fan_votes)
        elif rule == 'percent_sum':
            return self.percent_sum_rule(judge_scores, fan_votes)
        elif rule == 'judge_save':
            if len(week_df) >= 3:
                return self.judge_save_rule(judge_scores, fan_votes)
            else:
                return None
        else:
            raise ValueError(f"Unknown rule: {rule}")

    def simulate_all_weeks(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        模拟所有周次的淘汰结果

        Returns:
        --------
        results_df : DataFrame
            包含每周三种规则下的淘汰结果
        """
        results = []

        for (season, week), group in data.groupby(['season', 'week']):
            # 只模拟有效周（有评委分和粉丝投票）
            valid_group = group[group['week_valid'] == True].copy()

            if len(valid_group) <= 2:
                continue

            # 模拟三种规则
            eliminated_rank_sum = self.simulate_week(valid_group, 'rank_sum')
            eliminated_percent_sum = self.simulate_week(valid_group, 'percent_sum')
            eliminated_judge_save = self.simulate_week(valid_group, 'judge_save')

            # 实际淘汰者
            actual_eliminated_mask = (
                (group['week'] == group['elimination_week']) &
                (group['elimination_week'] > 0)
            )
            actual_eliminated = group[actual_eliminated_mask]['celebrity_name'].values
            actual_eliminated = actual_eliminated[0] if len(actual_eliminated) > 0 else None

            # 计算 FFI
            judge_scores = valid_group.set_index('celebrity_name')['judge_total']
            fan_votes = valid_group.set_index('celebrity_name')['fan_vote_share']
            ffi_values = calculate_fan_favorability_index(judge_scores, fan_votes)

            # 获取被淘汰者的 FFI
            ffi_rank_sum = ffi_values.get(eliminated_rank_sum, np.nan) if eliminated_rank_sum else np.nan
            ffi_percent_sum = ffi_values.get(eliminated_percent_sum, np.nan) if eliminated_percent_sum else np.nan
            ffi_judge_save = ffi_values.get(eliminated_judge_save, np.nan) if eliminated_judge_save else np.nan
            ffi_actual = ffi_values.get(actual_eliminated, np.nan) if actual_eliminated else np.nan

            # 计算该周的平均 FFI 和标准差
            mean_ffi = ffi_values.mean()
            std_ffi = ffi_values.std()

            results.append({
                'season': season,
                'week': week,
                'num_contestants': len(valid_group),
                'actual_eliminated': actual_eliminated,
                'rank_sum_eliminated': eliminated_rank_sum,
                'percent_sum_eliminated': eliminated_percent_sum,
                'judge_save_eliminated': eliminated_judge_save,
                'ffi_actual': ffi_actual,
                'ffi_rank_sum': ffi_rank_sum,
                'ffi_percent_sum': ffi_percent_sum,
                'ffi_judge_save': ffi_judge_save,
                'mean_ffi': mean_ffi,
                'std_ffi': std_ffi,
                'rank_vs_percent_same': (eliminated_rank_sum == eliminated_percent_sum),
                'rank_vs_judge_save_same': (eliminated_rank_sum == eliminated_judge_save),
                'percent_vs_judge_save_same': (eliminated_percent_sum == eliminated_judge_save),
                'all_same': (eliminated_rank_sum == eliminated_percent_sum == eliminated_judge_save)
            })

        results_df = pd.DataFrame(results)
        self.simulation_results = results_df

        return results_df

    def calculate_flip_rate(self, results_df: pd.DataFrame) -> Dict[str, float]:
        """
        计算翻转率（不同规则产生不同结果的频率）
        """
        total_weeks = len(results_df)

        flip_rates = {
            'rank_vs_percent': (1 - results_df['rank_vs_percent_same'].mean()),
            'rank_vs_judge_save': (1 - results_df['rank_vs_judge_save_same'].mean()),
            'percent_vs_judge_save': (1 - results_df['percent_vs_judge_save_same'].mean()),
            'all_different': (1 - results_df['all_same'].mean())
        }

        return flip_rates

    def analyze_controversy_cases(self, data: pd.DataFrame, results_df: pd.DataFrame,
                                   cases: List[Tuple[str, int]]) -> pd.DataFrame:
        """
        分析争议案例

        Parameters:
        -----------
        data : DataFrame
            原始数据
        results_df : DataFrame
            模拟结果
        cases : List[Tuple[str, int]]
            争议案例列表，格式：[(选手名, 赛季), ...]

        Returns:
        --------
        case_analysis : DataFrame
            争议案例分析结果
        """
        case_results = []

        for celebrity_name, season in cases:
            # 获取该选手的所有周数据
            celebrity_data = data[
                (data['celebrity_name'] == celebrity_name) &
                (data['season'] == season) &
                (data['week_valid'] == True)
            ].copy()

            if len(celebrity_data) == 0:
                print(f"  警告: 未找到 {celebrity_name} (S{season}) 的数据")
                continue

            # 获取该选手的实际淘汰周
            actual_elim_week = celebrity_data['elimination_week'].iloc[0]

            # 在模拟结果中查找该选手被淘汰的周次
            for rule in ['rank_sum', 'percent_sum', 'judge_save']:
                rule_col = f'{rule}_eliminated'

                # 找出该选手在该规则下被淘汰的周次
                eliminated_weeks = results_df[
                    (results_df['season'] == season) &
                    (results_df[rule_col] == celebrity_name)
                ]['week'].values

                simulated_elim_week = eliminated_weeks[0] if len(eliminated_weeks) > 0 else None

                case_results.append({
                    'celebrity_name': celebrity_name,
                    'season': season,
                    'rule': rule,
                    'actual_elimination_week': actual_elim_week,
                    'simulated_elimination_week': simulated_elim_week,
                    'weeks_survived': simulated_elim_week if simulated_elim_week else len(celebrity_data),
                    'saved_by_rule': (simulated_elim_week is None or simulated_elim_week > actual_elim_week)
                })

        case_analysis_df = pd.DataFrame(case_results)

        return case_analysis_df

    def analyze_ffi_by_rule(self, results_df: pd.DataFrame) -> Dict[str, Dict]:
        """
        分析各规则下被淘汰者的 FFI 分布

        Returns:
        --------
        ffi_stats : Dict
            各规则的 FFI 统计信息
        """
        ffi_stats = {}

        for rule in ['rank_sum', 'percent_sum', 'judge_save', 'actual']:
            col = f'ffi_{rule}'
            if col in results_df.columns:
                valid_ffi = results_df[col].dropna()
                ffi_stats[rule] = {
                    'mean': valid_ffi.mean(),
                    'std': valid_ffi.std(),
                    'median': valid_ffi.median(),
                    'min': valid_ffi.min(),
                    'max': valid_ffi.max(),
                    'count': len(valid_ffi),
                    'positive_rate': (valid_ffi > 0).mean(),  # 粉丝更喜欢的比例
                    'negative_rate': (valid_ffi < 0).mean(),  # 评委更喜欢的比例
                }

        return ffi_stats

    def recommend_voting_mechanism(self, results_df: pd.DataFrame) -> Dict:
        """
        基于模拟结果推荐最佳投票机制

        评估标准：
        1. 公平性：FFI 接近 0（平衡粉丝和评委意见）
        2. 一致性：与其他规则的翻转率低
        3. 争议性：避免淘汰高人气选手

        Returns:
        --------
        recommendation : Dict
            推荐结果和理由
        """
        ffi_stats = self.analyze_ffi_by_rule(results_df)
        flip_rates = self.calculate_flip_rate(results_df)

        # 计算各规则的评分
        scores = {}

        for rule in ['rank_sum', 'percent_sum', 'judge_save']:
            if rule not in ffi_stats:
                continue

            stats = ffi_stats[rule]

            # 公平性评分：FFI 均值越接近 0 越好
            fairness_score = 1 - abs(stats['mean'])

            # 平衡性评分：正负比例越接近 50% 越好
            balance_score = 1 - abs(stats['positive_rate'] - 0.5) * 2

            # 稳定性评分：标准差越小越好
            stability_score = 1 - min(stats['std'], 1)

            # 综合评分
            total_score = (fairness_score * 0.4 + balance_score * 0.3 + stability_score * 0.3)

            scores[rule] = {
                'fairness': fairness_score,
                'balance': balance_score,
                'stability': stability_score,
                'total': total_score
            }

        # 找出最佳规则
        best_rule = max(scores.keys(), key=lambda x: scores[x]['total'])

        recommendation = {
            'recommended_rule': best_rule,
            'scores': scores,
            'ffi_stats': ffi_stats,
            'flip_rates': flip_rates,
            'reasoning': self._generate_recommendation_reasoning(best_rule, scores, ffi_stats)
        }

        return recommendation

    def _generate_recommendation_reasoning(self, best_rule: str, scores: Dict,
                                            ffi_stats: Dict) -> str:
        """生成推荐理由"""
        rule_names = {
            'rank_sum': 'Rank Sum (排名相加)',
            'percent_sum': 'Percent Sum (百分比相加)',
            'judge_save': 'Judge Save (评委拯救)'
        }

        reasoning = f"推荐使用 {rule_names[best_rule]} 规则，原因如下：\n"

        stats = ffi_stats[best_rule]
        score = scores[best_rule]

        reasoning += f"\n1. 公平性 (权重 40%): {score['fairness']:.2f}\n"
        reasoning += f"   - 被淘汰者的平均 FFI: {stats['mean']:.3f}\n"
        reasoning += f"   - FFI 接近 0 表示粉丝和评委意见平衡\n"

        reasoning += f"\n2. 平衡性 (权重 30%): {score['balance']:.2f}\n"
        reasoning += f"   - 粉丝更喜欢的淘汰者比例: {stats['positive_rate']:.1%}\n"
        reasoning += f"   - 评委更喜欢的淘汰者比例: {stats['negative_rate']:.1%}\n"

        reasoning += f"\n3. 稳定性 (权重 30%): {score['stability']:.2f}\n"
        reasoning += f"   - FFI 标准差: {stats['std']:.3f}\n"
        reasoning += f"   - 标准差越小表示结果越稳定\n"

        reasoning += f"\n综合评分: {score['total']:.2f}"

        return reasoning


def run_counterfactual_simulation(data_path: Path, output_dir: Path):
    """
    运行完整的反事实模拟
    """
    print("=" * 80)
    print("Model C: Counterfactual Simulation - Voting Method Comparison")
    print("=" * 80)

    # 1. 加载数据
    print("\n[Step 1] 加载 Ridge V2 的粉丝投票份额")
    data = pd.read_csv(data_path)
    print(f"  - 数据形状: {data.shape}")
    print(f"  - 赛季范围: {data['season'].min()} - {data['season'].max()}")

    # 2. 初始化模拟器
    print("\n[Step 2] 初始化投票规则模拟器")
    simulator = VotingSimulator()

    # 3. 模拟所有周次
    print("\n[Step 3] 模拟所有周次的淘汰结果")
    print("  - 规则 A: Rank Sum（评委排名 + 粉丝排名）")
    print("  - 规则 B: Percent Sum（评委百分比 + 粉丝百分比）")
    print("  - 规则 C: Judge Save（倒数两名，评委淘汰评分低者）")

    results_df = simulator.simulate_all_weeks(data)
    print(f"\n  - 模拟了 {len(results_df)} 周")

    # 4. 计算翻转率
    print("\n[Step 4] 计算翻转率")
    flip_rates = simulator.calculate_flip_rate(results_df)

    print(f"\n[翻转率统计]")
    print(f"  - Rank Sum vs Percent Sum: {flip_rates['rank_vs_percent']:.2%}")
    print(f"  - Rank Sum vs Judge Save: {flip_rates['rank_vs_judge_save']:.2%}")
    print(f"  - Percent Sum vs Judge Save: {flip_rates['percent_vs_judge_save']:.2%}")
    print(f"  - 三种规则都不同: {flip_rates['all_different']:.2%}")

    # 5. 分析 FFI
    print("\n[Step 5] 分析 Fan Favorability Index (FFI)")
    ffi_stats = simulator.analyze_ffi_by_rule(results_df)

    print(f"\n[FFI 统计 - 被淘汰者]")
    for rule, stats in ffi_stats.items():
        rule_name = {
            'rank_sum': 'Rank Sum',
            'percent_sum': 'Percent Sum',
            'judge_save': 'Judge Save',
            'actual': 'Actual'
        }.get(rule, rule)
        print(f"  {rule_name}:")
        print(f"    - 平均 FFI: {stats['mean']:.3f}")
        print(f"    - 粉丝更喜欢比例: {stats['positive_rate']:.1%}")
        print(f"    - 评委更喜欢比例: {stats['negative_rate']:.1%}")

    # 6. 推荐投票机制
    print("\n[Step 6] 推荐投票机制")
    recommendation = simulator.recommend_voting_mechanism(results_df)
    print(f"\n{recommendation['reasoning']}")

    # 7. 分析争议案例
    print("\n[Step 7] 分析争议案例")
    # 扩展的争议案例列表（根据文档和历史数据）
    controversy_cases = [
        ('Bobby Bones', 27),      # 著名争议：评委分低但粉丝投票高
        ('Billy Ray Cyrus', 4),   # 早期争议案例
        ('Bristol Palin', 11),    # 政治争议
        ('Bristol Palin', 15),    # 第二次参赛
        ('Sabrina Bryan', 5),     # 意外淘汰
        ('Jerry Rice', 2),        # 运动员争议
        ('Kim Kardashian', 7),    # 名人效应
        ('Master P', 2),          # 早期争议
        ('Kate Gosselin', 10),    # 真人秀明星争议
    ]

    # 过滤出数据中存在的案例
    available_cases = []
    for name, season in controversy_cases:
        if ((data['celebrity_name'] == name) & (data['season'] == season)).any():
            available_cases.append((name, season))

    case_analysis = simulator.analyze_controversy_cases(data, results_df, available_cases)

    if len(case_analysis) > 0:
        print(f"\n[争议案例分析]")
        for name in case_analysis['celebrity_name'].unique():
            case_data = case_analysis[case_analysis['celebrity_name'] == name]
            season = case_data['season'].iloc[0]
            actual_week = case_data['actual_elimination_week'].iloc[0]
            print(f"\n  {name} (Season {season}):")
            print(f"    实际淘汰周: {actual_week if actual_week < 999 else '未淘汰(进入决赛)'}")
            for _, row in case_data.iterrows():
                sim_week = row['simulated_elimination_week']
                saved = "[+] Survived longer" if row['saved_by_rule'] else "[-] Eliminated earlier"
                print(f"    - {row['rule']}: Week {sim_week} {saved if sim_week else '(Not eliminated)'}")

    # 8. 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)

    results_path = output_dir / "simulation_results.csv"
    results_df.to_csv(results_path, index=False)
    print(f"\n[保存] 模拟结果: {results_path}")

    if len(case_analysis) > 0:
        case_path = output_dir / "controversy_case_analysis.csv"
        case_analysis.to_csv(case_path, index=False)
        print(f"[保存] 争议案例分析: {case_path}")

    # 保存推荐结果
    recommendation_path = output_dir / "recommendation.txt"
    with open(recommendation_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("Model C: 投票机制推荐报告\n")
        f.write("=" * 60 + "\n\n")
        f.write(recommendation['reasoning'])
        f.write("\n\n")
        f.write("=" * 60 + "\n")
        f.write("各规则评分详情\n")
        f.write("=" * 60 + "\n")
        for rule, scores in recommendation['scores'].items():
            f.write(f"\n{rule}:\n")
            for metric, value in scores.items():
                f.write(f"  - {metric}: {value:.3f}\n")
    print(f"[保存] 推荐报告: {recommendation_path}")

    print("\n" + "=" * 80)
    print("Model C 模拟完成！")
    print("=" * 80)

    return simulator, results_df, case_analysis, recommendation


if __name__ == "__main__":
    import sys
    from pathlib import Path
    # 添加 src 目录到路径
    src_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(src_dir))
    from config import DATA_DIR

    data_path = DATA_DIR / "models" / "ridge_v2" / "ridge_fan_vote_shares_v2.csv"
    output_dir = DATA_DIR / "simulation"

    simulator, results, cases, recommendation = run_counterfactual_simulation(data_path, output_dir)
