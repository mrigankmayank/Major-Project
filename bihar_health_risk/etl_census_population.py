"""Census 2011 district population (Bihar) for rate denominators."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from bihar_health_risk.etl_merge import standardize_district_names


def load_bihar_district_population_2011(xlsx_path: Path) -> pd.DataFrame:
    """
    Return columns District, Population_2011 from Census A-1 table.
    Rows: state code 10, level DISTRICT, urban/rural Total only.
    """
    path = Path(xlsx_path)
    df = pd.read_excel(path, sheet_name=0, header=None)
    rows: list[tuple[str, float]] = []
    for _, r in df.iterrows():
        cells = [r[i] if i < len(r) else None for i in range(12)]
        if cells[0] is None or cells[3] is None or cells[5] is None:
            continue
        if str(cells[0]).strip() != "10":
            continue
        if str(cells[3]).strip() != "DISTRICT":
            continue
        if str(cells[5]).strip() != "Total":
            continue
        name = str(cells[4]).strip()
        pop = pd.to_numeric(cells[10], errors="coerce")
        if pd.isna(pop) or pop <= 0:
            continue
        rows.append((name, float(pop)))
    out = pd.DataFrame(rows, columns=["District", "Population_2011"])
    out["District"] = standardize_district_names(out["District"])
    out = out.drop_duplicates(subset=["District"], keep="first")
    return out
