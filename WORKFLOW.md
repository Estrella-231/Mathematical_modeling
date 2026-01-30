# 2026 MCM/ICM C 题协同工作流（Gemini CLI + Claude Code + Codex）

> 目标：充分利用 Gemini CLI 的长文本处理优势、Claude Code 的工程能力、Codex 的代码评审与调试能力，高效完成 2026 美赛 C 题（MCM/ICM）。

## 1. 总体分工

- **Gemini CLI（长文本）**
  - 任务：题目与资料的长文解析、要点提炼、文献/数据的结构化摘要。
  - 产出：问题定义、约束条件、关键指标、可行模型清单、数据需求清单。

- **Claude Code（工程能力）**
  - 任务：方案实现、代码骨架、实验脚手架、数据处理流水线。
  - 产出：可运行代码、实验脚本、配置文件、结果图表。

- **Codex（评审 + Debug）**
  - 任务：代码 review、边界情况检查、性能与可复现实验检查、补充与修复。
  - 产出：review 记录、修复补丁、测试补充与回归验证。

## 2. 工作目录与产物规范

建议目录结构（可在 `solution/` 内建立）：

```
solution/
  docs/
    00_problem_summary.md
    01_assumptions.md
    02_model_design.md
    03_experiments.md
    04_results.md
    05_paper_outline.md
    06_decision_log.md
  data/
    raw/
    processed/
  src/
    main.py
    models/
    utils/
  tests/
  figures/
  notes/
```

- **文档编号**：按流程编号，避免“最后一版”的混乱。
- **决策日志**：记录所有关键建模与假设变化，保证论文可追溯。

## 3. 端到端流程

### 阶段 A：题目理解与拆解（Gemini CLI）

1. 输入题目原文与相关材料。
2. 提取：目标函数/评价指标、约束、变量、可用数据。
3. 输出以下文件：
   - `docs/00_problem_summary.md`
   - `docs/01_assumptions.md`

**Gemini CLI 提示模板：**

```
你是建模竞赛助手。请从以下材料中提取：
1) 研究目标
2) 关键变量与指标
3) 约束与假设
4) 可用数据与缺失数据
5) 建模方向清单（最多 5 个）

材料：
{{PASTE_LONG_TEXT}}
```

### 阶段 B：模型设计（Gemini CLI -> Claude Code）

1. Gemini 生成候选模型并比较优劣。
2. Claude Code 根据模型方案搭建代码骨架。
3. 输出以下文件：
   - `docs/02_model_design.md`
   - `src/` 中的模型实现草稿

**Claude Code 任务模板：**

```
根据 docs/02_model_design.md 的方案，搭建可运行的实验脚手架：
- 数据加载与预处理
- 模型接口与训练/求解函数
- 输出指标与图表
- 配置参数集中化
```

### 阶段 C：实验与验证（Claude Code -> Codex）

1. Claude Code 编写实验脚本并产出初步结果。
2. Codex 对代码进行 review，检查：
   - 逻辑错误
   - 边界条件
   - 可复现性（随机种子）
   - 性能瓶颈
3. 输出以下文件：
   - `docs/03_experiments.md`
   - `docs/04_results.md`
   - Review 记录（可附在 `notes/`）

### 阶段 D：论文组织与最终润色（Gemini CLI + Codex）

1. Gemini 生成论文结构与段落要点。
2. Codex 检查论文一致性、结果解释与图表匹配。
3. 输出以下文件：
   - `docs/05_paper_outline.md`
   - 终稿 PDF/Word/LaTeX

## 4. 交接与同步规则

- **单一真相来源**：所有关键结论必须在 `docs/` 文档中有记录。
- **交接原则**：每次交接必须包含“输入-输出”摘要。
- **版本控制**：每次修改需记录在 `docs/06_decision_log.md`。

## 5. Codex Review Checklist

- 数据处理是否有缺失值/异常处理
- 模型求解是否考虑约束边界
- 随机性是否固定 seed
- 输出指标是否与题目一致
- 图表是否可复现

## 6. 最佳实践建议

- 每个阶段结束后生成一个“阶段小结”。
- 任何模型调整必须更新假设和决策日志。
- 论文写作与实验同步推进，避免最后阶段返工。

---

本文件建议作为统一工作流总纲，后续可在 `docs/` 下细化。
