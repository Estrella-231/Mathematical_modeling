# 如何查看数据处理输出

## 📂 输出文件位置

所有处理后的数据保存在：
```
F:\Mathematical_modeling\solution\Data\processed\
```

包含以下文件：
- `weekly_panel.csv` - 4,631 行，18 列（选手-周级面板数据）
- `contestant_static.csv` - 421 行，12 列（选手静态信息）
- `season_meta.csv` - 34 行，3 列（赛季元数据）
- `train_panel.csv` - 3,542 行（训练集，S1-S27）
- `test_panel.csv` - 1,089 行（测试集，S28-S34）

---

## 🔍 查看方法

### 方法 1：使用 Excel 或文本编辑器（最简单）

直接打开 CSV 文件：
```
solution/Data/processed/weekly_panel.csv
```

**优点**：直观、可以排序和筛选
**缺点**：大文件可能加载慢

---

### 方法 2：使用交互式查看脚本（推荐）

运行我创建的查看脚本：

```bash
cd solution/src
python interactive_view.py
```

**输出内容**：
- ✅ Kelly Monaco（冠军）的完整周数据
- ✅ Season 1, Week 1 的所有选手排名
- ✅ 赛季元数据
- ✅ 行业分布（Top 5）
- ✅ 年龄分组分布
- ✅ 评委分数统计
- ✅ 淘汰周分布
- ✅ 训练集 vs 测试集统计

---

### 方法 3：使用命令行快速查看

**查看文件大小**：
```bash
ls -lh solution/Data/processed/
```

**查看前 20 行**：
```bash
head -20 solution/Data/processed/weekly_panel.csv
```

**统计行数**：
```bash
wc -l solution/Data/processed/*.csv
```

**查看特定列**：
```bash
cut -d',' -f1-8 solution/Data/processed/weekly_panel.csv | head -20
```

---

### 方法 4：使用 Python 自定义查询

在 Python 中加载数据：

```python
import pandas as pd

# 加载数据
weekly = pd.read_csv("solution/Data/processed/weekly_panel.csv")
static = pd.read_csv("solution/Data/processed/contestant_static.csv")
season = pd.read_csv("solution/Data/processed/season_meta.csv")

# 查看基本信息
print(weekly.info())
print(weekly.head())

# 查看某个选手
kelly = weekly[weekly['celebrity_name'] == 'Kelly Monaco']
print(kelly)

# 查看某一周的排名
week1 = weekly[(weekly['season'] == 1) & (weekly['week'] == 1)]
print(week1.sort_values('judge_rank_in_week'))
```

---

## 📊 数据结构说明

### weekly_panel.csv（核心数据）

**18 个列**：

| 列名 | 说明 | 示例 |
|------|------|------|
| `season` | 赛季编号 | 1-34 |
| `celebrity_name` | 选手姓名 | Kelly Monaco |
| `week` | 周数 | 1-11 |
| `judge_total` | 标准化评委总分 | 130.0-390.0 |
| `judge_rank_in_week` | 周内排名 | 1, 2, 3... |
| `week_valid` | 是否有效周 | True/False |
| `ballroom_partner` | 舞伴 | Alec Mazo |
| `celebrity_industry` | 行业 | Actor/Actress |
| `celebrity_age_during_season` | 年龄 | 29 |
| `celebrity_homestate` | 州 | Pennsylvania |
| `celebrity_homecountry/region` | 国家/地区 | United States |
| `results` | 结果 | 1st Place |
| `placement` | 最终排名 | 1 |
| `elimination_week` | 淘汰周 | 999（决赛） |
| `relative_judge_score` | Z-Score | -1.90 |
| `cumulative_average` | 累积平均分 | 150.0 |
| `trend` | 趋势（本周-上周） | 40.0 |
| `is_bottom_2_judge` | 是否倒数两名 | False |

---

### contestant_static.csv（选手汇总）

**12 个列**：
- 选手基本信息（姓名、舞伴、行业、年龄、州、国家）
- `placement` - 最终排名
- `elimination_week` - 淘汰周
- `avg_judge_score` - 平均评委分
- `age_group` - 年龄分组（<20, 20-30, 30-40...）

---

### season_meta.csv（赛季元数据）

**3 个列**：
- `season` - 赛季编号
- `max_weeks` - 最大周数
- `num_contestants` - 选手数量

---

## 💡 常用查询示例

### 查询 1：查看某个选手的完整数据
```python
kelly = weekly[weekly['celebrity_name'] == 'Kelly Monaco']
print(kelly[['week', 'judge_total', 'judge_rank_in_week', 'week_valid']])
```

### 查询 2：查看某一周的排名
```python
week1 = weekly[(weekly['season'] == 1) & (weekly['week'] == 1) & (weekly['week_valid'] == True)]
print(week1.sort_values('judge_rank_in_week')[['celebrity_name', 'judge_total', 'judge_rank_in_week']])
```

### 查询 3：查看某个赛季的所有选手
```python
s1_contestants = static[static['season'] == 1]
print(s1_contestants[['celebrity_name', 'placement', 'avg_judge_score']])
```

### 查询 4：查看行业分布
```python
print(static['celebrity_industry'].value_counts())
```

### 查询 5：查看评委分数分布
```python
valid_scores = weekly[weekly['week_valid']]['judge_total']
print(valid_scores.describe())
```

---

## 🎯 关键数据点

从 `interactive_view.py` 的输出可以看到：

**Kelly Monaco（Season 1 冠军）的表现**：
- Week 1: 130.0 分，排名第 3
- Week 2: 170.0 分，排名第 5
- Week 3: 210.0 分，排名第 4
- Week 4: 260.0 分，排名第 1 ⭐
- Week 5: 235.0 分，排名第 2
- Week 6: 275.0 分，排名第 1 ⭐
- 趋势：持续进步，最后两周排名第一

**Season 1, Week 1 排名**：
1. Joey McIntyre, John O'Hurley, Rachel Hunter: 200.0 分（并列第一）
2. Evander Holyfield, Trista Sutter: 180.0 分（并列第二）
3. Kelly Monaco: 130.0 分（第三）

**数据质量**：
- 评委分数范围：80.00 - 390.00
- 平均分：236.92
- 中位数：240.00
- 标准差：43.91

---

## 📝 注意事项

1. **week_valid = False** 的数据是淘汰后的周，`judge_total` 为 NaN
2. **elimination_week = 999** 表示进入决赛（1st/2nd/3rd Place）
3. **relative_judge_score** 是 Z-Score，0 表示平均水平
4. **cumulative_average** 是截止上周的平均分，第一周为 NaN
5. **trend** 是本周分 - 上周分，第一周为 NaN

---

## 🚀 下一步

数据已准备就绪，可以开始：
1. 实现粉丝投票估计模型（Model A）
2. 实现特征影响分析（Model B1: Ridge, B2: Random Forest）
3. 进行反事实模拟（Model C）
4. 设计优化的投票系统（Model D）
