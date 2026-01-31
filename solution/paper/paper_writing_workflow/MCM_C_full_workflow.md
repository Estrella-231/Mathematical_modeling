# 论文习作完整工作流（基于 MCM_C_outline.md）

> 目标：把 `MCM_C_outline.md` 转化为可执行的写作与产出流程，确保每一节都有输入、输出、图表与核查。

## 0. 初始化与约定
- **输入**：`paper/paper_writing_workflow/MCM_C_outline.md`、`solution/docs/` 中的建模文档与实验结果。
- **输出目录**：
  - 过程稿：`paper/drafts/`
  - 图表：`figures/`
  - 公式/符号：`paper/notes/`
- **记录**：
  - 运行日志：`docs/07_run_log.md`
  - 交接日志：`notes/handoff_log.md`

## 1. 材料清点（一次性）
- **动作**：核对所有模型结果文件、图表、指标表是否齐全。
- **产出**：`paper/notes/materials_index.md`（列出可用表/图/数据）

## 2. 写作拆解（按大纲逐节拆）
- **动作**：把大纲每节拆成“2–4条要点 + 1张图/表 + 1个结论”。
- **产出**：`paper/notes/section_checklist.md`

## 3. 先写 Summary Sheet（倒逼结论）
- **动作**：完成 0.1–0.5，锁定核心结论与推荐。
- **产出**：`paper/drafts/00_summary_sheet.md`

## 4. 数据与EDA（Section 5）
- **动作**：写数据来源、清洗、缺失处理、分布与相关性。
- **图表**：分布图、缺失热力图、外部信号相关性。
- **产出**：`paper/drafts/05_data_eda.md`

## 5. 模型章节（Section 6）
- **动作**：按 Model 0→1→2→3 顺序写，每个模型固定结构：
  - 动机 → 数学定义 → 求解方法 → 输出 → 约束一致性
- **产出**：
  - `paper/drafts/06_model0.md`
  - `paper/drafts/06_model1.md`
  - `paper/drafts/06_model2.md`
  - `paper/drafts/06_model3.md`

## 6. 评估与结果（Section 7–8）
- **动作**：统一指标口径（回归/分类/规则一致性/公平性）。
- **图表**：主结果表、跨季对比、案例周可视化。
- **产出**：`paper/drafts/07_evaluation.md`、`paper/drafts/08_results.md`

## 7. 机制设计与建议（Section 9）
- **动作**：对比现行规则与新机制，给出反事实模拟结论。
- **产出**：`paper/drafts/09_mechanism_design.md`

## 8. Memo（Section 1）
- **动作**：将核心发现与建议压缩为 1–2 页。
- **产出**：`paper/drafts/01_memo.md`

## 9. 结论与局限（Section 10）
- **动作**：回扣核心发现 + 局限 + 未来改进。
- **产出**：`paper/drafts/10_conclusion.md`

## 10. 汇编与排版
- **动作**：按顺序合并草稿；统一术语、符号、图表编号。
- **输出**：`paper/final/mcm_c_report.pdf`

## 11. 质量检查清单
- 规则一致性：每个季节按正确规则评估
- 图表可复现：脚本 + 路径一致
- 结论可追溯：每条结论指向结果表/图
- AI 使用说明完整

## 12. 建议节奏（3–5天）
- **Day1**：Summary + Data/EDA + Model 0/1
- **Day2**：Model 2/3 + Evaluation
- **Day3**：Results + Mechanism + Memo
- **Day4**：总装/排版/检查

---

> 每完成一节，更新 `docs/07_run_log.md`（本节数据与输出路径），并在 `notes/handoff_log.md` 记录交接输入输出。
