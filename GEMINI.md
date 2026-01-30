# 2026 MCM Problem C Workspace

## Project Overview
This workspace is dedicated to solving the **2026 MCM Problem C**. The project involves analyzing data from a dance competition (likely "Dancing with the Stars"), including celebrity demographics, judge scores across multiple weeks, and final placements.

The goal is typically to model voting patterns, judge bias, or predict outcomes based on the provided dataset.

## Directory Structure

### `problem/`
Contains the problem statement and original datasets.
*   **`2026_MCM_Problem_C.pdf`**: The official problem description.
*   **`primitive_data/2026_MCM_Problem_C_Data.csv`**: The primary dataset.
    *   **Key Columns**: `celebrity_name`, `ballroom_partner`, `celebrity_industry`, `season`, `results`, `placement`, and weekly judge scores (e.g., `week1_judge1_score`).

### `solution/`
The main working directory for the solution.
*   **`Code/`**: Directory for analysis and modeling scripts (currently empty).
    *   *Recommended*: Use Python (pandas, numpy, scikit-learn) or MATLAB for analysis.
*   **`Data/`**: Directory for storing processed or intermediate datasets.
*   **`Draw_picture/`**: Destination for generated plots and visualizations to be included in the paper.
*   **`paper/`**: Directory for the final submission paper (LaTeX or Word).

## Getting Started

1.  **Data Loading**:
    The raw data is located at `problem/primitive_data/2026_MCM_Problem_C_Data.csv`.
    Start by creating a script in `solution/Code` to load and inspect this data.

    ```python
    import pandas as pd
    
    # Path relative to solution/Code/
    data_path = "../../problem/primitive_data/2026_MCM_Problem_C_Data.csv"
    df = pd.read_csv(data_path)
    print(df.head())
    ```

2.  **Analysis Workflow**:
    *   **Preprocessing**: Handle missing values (e.g., `N/A` in scores) and format column names.
    *   **Exploratory Data Analysis (EDA)**: Visualize score distributions and correlations in `solution/Draw_picture`.
    *   **Modeling**: Develop mathematical models as required by the problem statement.

## Conventions
*   **Paths**: Use relative paths when referencing data files to ensure portability.
*   **Outputs**: Save all generated figures to `solution/Draw_picture` for easy inclusion in the final paper.
