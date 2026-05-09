"""
Extract Bihar-only rows from each CGWB 'all states' yearbook PDF under `official data/`.

Writes one CSV per PDF to `data/raw_groundwater/`:
  cgwb_bihar_wells_<YEAR>.csv
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bihar_health_risk.config import RAW_GW, ensure_directories  # noqa: E402
from bihar_health_risk.etl_cgwb import extract_bihar_wells_from_pdf  # noqa: E402

OFFICIAL = ROOT / "official data"
EXTRACTED = OFFICIAL / "extracted"
YEAR_RE = re.compile(r"all states (\d{4})\.pdf$", re.I)


def main() -> None:
    ensure_directories()
    EXTRACTED.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(OFFICIAL.glob("cgwb ground water quality data all states *.pdf"))
    if not pdfs:
        raise SystemExit(f"No CGWB PDFs found in {OFFICIAL}")
    for pdf in pdfs:
        m = YEAR_RE.search(pdf.name)
        year = m.group(1) if m else "unknown"
        df = extract_bihar_wells_from_pdf(pdf)
        out = RAW_GW / f"cgwb_bihar_wells_{year}.csv"
        df.to_csv(out, index=False)
        df.to_csv(EXTRACTED / f"cgwb_bihar_wells_{year}.csv", index=False)
        print(f"{pdf.name} -> {out} (+ {EXTRACTED}) ({len(df)} wells)")


if __name__ == "__main__":
    main()
