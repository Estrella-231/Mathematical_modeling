# Assumptions and Decisions

# 假设和决策 | Assumptions and Decisions

## 基础假设（检查和修订）| Base Assumptions (check and revise)
- [ ] 季节方法划分：第1-2季排名法、第3-27季百分比法、第28-34季排名法+评委拯救权
      Season method split: seasons 1-2 rank, seasons 3-27 percent, seasons 28-34 rank + judge save.
- [ ] 粉丝投票建模为周内份额；绝对总数不可识别
      Fan votes are modeled as weekly shares; absolute totals are not identifiable.
- [ ] 粉丝投票份额非负且每周总和为1
      Fan vote shares are nonnegative and sum to 1 each week.
- [ ] 粉丝投票份额对同一选手的周变化平滑（需要正则化）
      Fan vote shares vary smoothly week-to-week for the same contestant (regularization).
- [ ] 无淘汰的周次仍提供有效的评分数据
      Weeks with no elimination still provide valid scoring data.
- [ ] 多人淘汰的周次移除最低k个综合评分的选手
      Weeks with multiple eliminations remove the lowest k combined scores.
- [ ] 评委拯救：从综合评分最低的2人中识别；评委选择评委总分较低者淘汰
      Judges save: bottom two identified by combined scores; judges eliminate lower judge_total.
- [ ] 淘汰后的零分表示不参与（在退出后排除出建模）
      Zero scores after elimination indicate non-participation (exclude from modeling after exit).
- [ ] N/A评分条目视为缺失，不是零
      N/A score entries are treated as missing, not zeros.

## 待测试的替代方案 | Alternatives to Test
- [ ] 评委拯救规则：评委选择更高总分拯救 vs 独立评委投票模型
      Judge save rule: judges choose higher total to save vs separate judge vote model.
- [ ] 评委和粉丝影响权重（50/50 vs 校准权重）
      Weighting of judge vs fan influence (50/50 vs calibrated).
- [ ] 包含流行度协变量（年龄、行业、地区、职业舞者）
      Include popularity covariates (age, industry, home region, pro dancer).

## 待解决的问题 | Open Questions
- 排名法何时重新使用（未有证据前假设第28季）
  Exact season when rank method returned (assume season 28 unless evidence).
- 评委拯救在第28季后是否每周使用
  Whether judge save was used every week after season 28.
- 团队舞蹈和加分处理（使用提供的评分原样）
  Treatment of team dances and bonus points (use provided scores as-is).

## 决策日志格式（追加新条目）| Logging Format (append new entries)
```
YYYY-MM-DD
决策 / Decision:
原因 / Reason:
影响 / Impact:
考虑的替代方案 / Alternatives considered:
```
