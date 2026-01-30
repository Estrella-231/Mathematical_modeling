# 模型 B2 实现方案：基于随机森林的粉丝偏好驱动力分析 (Model B2: Fan Preference Drivers via Random Forest)

## 1. 目标 (Objective)
**核心目标：解释和细化粉丝投票估算。**

在 Model B1 (Ridge) 中，我们将“残差”定义为粉丝投票。Model B2 (Random Forest) 的任务是：
1.  **解释 (Explainability):** 识别哪些选手特征（年龄、职业、舞伴）驱动了这些“粉丝投票残差”。
2.  **先验构建 (Prior Construction):** 为没有历史数据的新选手构建“基础人气先验” (Baseline Popularity Prior)。
3.  **验证 (Validation):** 验证 B1 提取的“粉丝票”是否具有统计规律（例如：如果不相关的特征能预测残差，说明提取成功；如果是纯噪，说明 B1 失败）。

## 2. 输入数据 (Input Data)
*   **Source:**
    *   `X` (Features): 选手静态特征 (`age`, `industry`, `gender`, `is_pro`) + 动态特征 (`trend`).
    *   **$Y$ (Target):** 来自 **Model B1 的输出残差 ($R_i$)** (即估算的粉丝效应代理变量)。
*   **Logic:** 我们试图用选手特征来预测“粉丝会比评委多给多少分”。

## 3. 模型架构 (Model Architecture)
*   **Algorithm:** `sklearn.ensemble.RandomForestRegressor`
*   **Task:** Regression ($X_{traits} 	o Y_{residual}$). 
*   **Rationale:** 粉丝偏好往往是非线性的（例如：太老或太小都可能受欢迎，中间年龄层可能被忽视），RF 适合捕捉这种关系。

## 4. 核心分析：SHAP 值驱动的洞察
题目要求分析“职业舞者和名人特征的影响”。
利用 **SHAP (SHapley Additive exPlanations)**：
1.  **全局重要性:** 哪些特征最能决定粉丝票的高低？（是 `Industry` 还是 `Age`？）
2.  **依赖图 (Dependence Plot):** 
    *   *Age vs. FanSupport:* 绘制年龄与 SHAP 值的关系，观察是否存在“U型曲线”（老少通吃）。
    *   *Industry Effect:* 哪个行业的名人天生自带高票仓（如 Reality TV vs. Politician）？

## 5. 增强估算的确定性 (Enhancing Certainty)
题目询问“确定性”。
*   如果 RF 模型在测试集上的 $R^2$ 较高，说明粉丝投票是有规律可循的（由人口统计学特征驱动），我们的估算**确定性较高**。
*   如果 RF 无法预测残差 ($R^2 
approx 0$)，说明粉丝投票可能是随机的或由数据中未包含的因素（如个人魅力、绯闻）驱动，估算的**不确定性高**。
*   **输出:** 将 RF 的预测误差作为“确定性指标”的一部分。

## 6. 实现步骤 (Implementation Steps)
1.  **Input:** Load residuals ($R$) from Model B1 results.
2.  **Train:** Fit RF Regressor on ($X_{traits}$, $Y=R$). 
3.  **Explain:** Compute SHAP values.
4.  **Visualize:** Generate summary plots and dependence plots for the final report.
5.  **Refine B1 (Optional Loop):** Use RF predictions as a "Prior" mean for the Ridge Regression in a Bayesian Ridge setup (Advanced/Optional).