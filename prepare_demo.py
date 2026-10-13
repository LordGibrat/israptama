"""Generate reproducible, explicitly synthetic deliverables from the engine."""
import json
from pathlib import Path

from engine import analyze, export_csv, sample_rows

folder = Path(__file__).parent / "data"
folder.mkdir(exist_ok=True)
rows = sample_rows()
(folder / "SYNTHETIC-sample.csv").write_text(export_csv(rows), encoding="utf-8-sig", newline="")
result = analyze(rows, synthetic=True)
(folder / "SYNTHETIC-evaluation.json").write_text(
    json.dumps({"notice": "SYNTHETIC SIMULATION, NOT REAL BUSINESS SAVINGS", **result},
               ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Generated {len(rows)} synthetic records and evaluation in {folder}")
