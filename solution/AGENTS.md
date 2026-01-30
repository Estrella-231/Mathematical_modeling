# Repository Guidelines

## Project Structure & Module Organization
- `src/`: Python source code (entry point in `src/main.py`, helpers in `src/utils/`, models in `src/models/`).
- `Data/`: datasets and outputs (`Data/raw/` for the provided CSV; `Data/processed/` for derived tables).
- `docs/`: workflow artifacts and modeling notes (numbered docs like `00_problem_summary.md`).
- `figures/`: generated plots and tables for the report.
- `paper/`: report drafts and final write‑ups.
- `tests/`: test files (currently empty, reserved for pytest).

## Build, Test, and Development Commands
- `python src/main.py` — sanity check that the dataset loads and panel construction runs.
- `python -m pytest` — run tests once you add them under `tests/`.

If you add dependencies, document them and prefer a `requirements.txt` at repo root.

## Coding Style & Naming Conventions
- Python, 4‑space indentation, `snake_case` for functions/variables, `PascalCase` for classes.
- Keep data paths centralized in `src/config.py`.
- For docs, follow the numbered pattern: `docs/NN_short_topic.md`.
- Prefer small, composable functions with clear inputs/outputs; avoid hidden global state.

## Testing Guidelines
- Use pytest; name files `test_*.py` and functions `test_*`.
- Cover: data loading, week panel construction, voting scheme logic, and edge cases (N/A scores, zero scores after elimination, no‑elimination weeks).
- Add at least one “smoke test” that runs `src/main.py` without errors.

## Commit & Pull Request Guidelines
- No git history is present in this folder; if you initialize git, use concise conventional messages (e.g., `feat: add fan vote optimizer`, `fix: handle N/A judge scores`).
- PRs should include: a short summary, data source notes (if added), and updated results/figures when relevant.
- Log modeling decisions and assumption changes in `docs/06_decision_log.md`.

## Data & Reporting Notes
- Do not edit raw files in `Data/raw/`. Place derived outputs in `Data/processed/`.
- Any external data must be cited in the report and documented in `docs/`.
- Keep report figures reproducible from code and store outputs in `figures/`.
