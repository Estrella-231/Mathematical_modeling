from pathlib import Path
# 配置文件 | Configuration file
ROOT = Path(__file__).resolve().parents[1]
# Prefer existing Data/ if present; fallback to data/ for portability.
DATA_DIR = ROOT / ("Data" if (ROOT / "Data").exists() else "data")
RAW_DATA = DATA_DIR / "raw" / "2026_MCM_Problem_C_Data.csv"
