#!/usr/bin/env python3
"""Profile a CSV or Excel (.xlsx) research dataset: row/col counts, missingness, numeric summaries."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
from typing import Any, Dict, List
import numpy as np
import openpyxl


def load_tabular(path: pathlib.Path) -> List[Dict[str, str]]:
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        headers = [str(h).strip() for h in rows[0]]
        return [{headers[i]: ("" if v is None else str(v).strip()) for i, v in enumerate(r)} for r in rows[1:] if any(x is not None for x in r)]
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def profile_file(path: pathlib.Path) -> Dict[str, Any]:
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    records = load_tabular(path)
    cols = list(records[0].keys()) if records else []
    col_stats: Dict[str, Any] = {}
    for c in cols:
        raw = [r.get(c, "") for r in records]
        non_empty = [x for x in raw if x != "" and x.lower() not in ("na", "nan", "null")]
        nums = []
        for x in non_empty:
            try:
                nums.append(float(x))
            except ValueError:
                pass
        if non_empty and len(nums) == len(non_empty):
            arr = np.array(nums, dtype=float)
            col_stats[c] = {
                "type": "numeric",
                "n": int(len(arr)),
                "missing": int(len(raw) - len(arr)),
                "mean": round(float(np.mean(arr)), 4),
                "sd": round(float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0, 4),
                "median": round(float(np.median(arr)), 4),
                "iqr": [round(float(np.percentile(arr, 25)), 4), round(float(np.percentile(arr, 75)), 4)],
            }
        else:
            counts: Dict[str, int] = {}
            for x in non_empty:
                counts[x] = counts.get(x, 0) + 1
            col_stats[c] = {"type": "categorical", "n": len(non_empty), "missing": len(raw) - len(non_empty), "levels": counts}
    return {"file": str(path), "sha256": sha, "row_count": len(records), "columns": col_stats}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    prof = profile_file(pathlib.Path(args.data))
    pathlib.Path(args.out).write_text(json.dumps(prof, indent=2), encoding="utf-8")
    print(json.dumps(prof, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
