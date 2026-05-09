"""Extract Bihar-only groundwater quality well rows from CGWB 'all states' yearbooks (PDF)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    import fitz  # PyMuPDF
except ImportError as e:  # pragma: no cover
    raise ImportError("Install pymupdf: pip install pymupdf") from e

WELL_RE = re.compile(r"^W\d{10,}$")
STATE_BIHAR_RE = re.compile(r"^(\d+)\s+Bihar\s*$")
SERIAL_ONLY_RE = re.compile(r"^(\d+)\s*$")
BIHAR_ONLY_RE = re.compile(r"^Bihar\s*$", re.I)
YEAR_PH_RE = re.compile(r"^(\d{4})\s+([\d.]+)\s*$")
YEAR_ONLY_RE = re.compile(r"^(\d{4})\s*$")

NUMERIC_FIELDS = [
    "EC_uScm",
    "CO3",
    "HCO3",
    "Cl",
    "SO4",
    "NO3",
    "PO4",
    "TH",
    "Ca",
    "Mg",
    "Na",
    "K",
    "F",
    "TDS",
    "SiO2",
]


def _clean_num(token: str) -> float | None:
    t = str(token).strip().replace(",", "")
    if not t or t.upper() in {"BDL", "N A", "NA", "#N/A", "NS", "NAN", "NIL", "ND"}:
        return None
    if t.startswith("<"):
        try:
            return float(t.replace("<", "")) / 2.0
        except ValueError:
            return None
    try:
        return float(t)
    except ValueError:
        return None


def _parse_one_record(lines: list[str]) -> dict[str, Any] | None:
    """Parse a single well block (lines starting with Well_ID)."""
    if not lines or not WELL_RE.match(lines[0]):
        return None
    if len(lines) < 9:
        return None
    well_id = lines[0]
    idx = 1
    if STATE_BIHAR_RE.match(lines[idx]):
        serial = int(STATE_BIHAR_RE.match(lines[idx]).group(1))
        idx += 1
    elif SERIAL_ONLY_RE.match(lines[idx]) and idx + 1 < len(lines) and BIHAR_ONLY_RE.match(lines[idx + 1]):
        serial = int(SERIAL_ONLY_RE.match(lines[idx]).group(1))
        idx += 2
    else:
        return None
    if idx + 4 >= len(lines):
        return None
    district_raw = lines[idx]
    block = lines[idx + 1]
    village = lines[idx + 2]
    lat_s, lon_s = lines[idx + 3], lines[idx + 4]
    idx += 5
    try:
        lat = float(lat_s)
        lon = float(lon_s)
    except ValueError:
        return None
    # Some yearbooks list longitude before latitude (first value > ~40 for Bihar).
    if lat > 45.0:
        lat, lon = lon, lat
    year: int | None = None
    ph: float | None = None
    if idx >= len(lines):
        return None
    m_yp = YEAR_PH_RE.match(lines[idx])
    m_y = YEAR_ONLY_RE.match(lines[idx])
    if m_yp:
        year = int(m_yp.group(1))
        ph = float(m_yp.group(2))
        idx += 1
    elif m_y:
        year = int(m_y.group(1))
        idx += 1
        if idx < len(lines):
            try:
                ph = float(lines[idx])
            except ValueError:
                ph = None
            idx += 1
    else:
        return None
    vals: list[float | None] = []
    while idx < len(lines) and len(vals) < len(NUMERIC_FIELDS):
        if WELL_RE.match(lines[idx]):
            break
        vals.append(_clean_num(lines[idx]))
        idx += 1
    if len(vals) < 10:
        return None
    while len(vals) < len(NUMERIC_FIELDS):
        vals.append(None)
    row: dict[str, Any] = {
        "Well_ID": well_id,
        "Serial": serial,
        "State": "Bihar",
        "District": district_raw.strip().title(),
        "Block": block.strip(),
        "Village": village.strip(),
        "Latitude": lat,
        "Longitude": lon,
        "Year": year,
        "pH": ph,
    }
    for name, v in zip(NUMERIC_FIELDS, vals):
        row[name] = v
    return row


def _normalize_cgwb_text(raw: str) -> str:
    """Fix some yearbook layouts where serial + '(' + Well_ID + 'Bihar' share one line."""
    raw = re.sub(r"(\d+)\s*\(\s*(W\d+)\s+Bihar", r"\2\n\1\nBihar", raw, flags=re.I)
    return raw


def _parse_modern_serial_bihar_records(lines: list[str]) -> list[dict[str, Any]]:
    """
    2023+ style: lines like ``758``, ``Bihar``, District, Location, lon, lat, year, pH, then 16 chemistry tokens.
    """
    records: list[dict[str, Any]] = []
    n = len(lines)
    i = 0
    while i < n - 22:
        if SERIAL_ONLY_RE.match(lines[i]) and i + 1 < n and BIHAR_ONLY_RE.match(lines[i + 1]):
            serial = int(lines[i])
            district_raw = lines[i + 2]
            village = lines[i + 3]
            lon_s, lat_s = lines[i + 4], lines[i + 5]
            try:
                lat = float(lat_s)
                lon = float(lon_s)
            except ValueError:
                i += 1
                continue
            if lat > 45.0:
                lat, lon = lon, lat
            try:
                year = int(lines[i + 6])
                ph = float(lines[i + 7])
            except ValueError:
                i += 1
                continue
            chem: list[float | None] = []
            for k in range(16):
                if i + 8 + k >= n:
                    break
                if WELL_RE.match(lines[i + 8 + k]):
                    break
                chem.append(_clean_num(lines[i + 8 + k]))
            if len(chem) < 12:
                i += 1
                continue
            while len(chem) < 16:
                chem.append(None)
            ec, co3, hco3, cl, f, so4, no3, po4, th, ca, mg, na, k, _fe, _as, _u = chem[:16]
            well_id = f"CGWB_{year}_{serial}_{district_raw[:8]}"
            row: dict[str, Any] = {
                "Well_ID": well_id,
                "Serial": serial,
                "State": "Bihar",
                "District": district_raw.strip().title(),
                "Block": "",
                "Village": village.strip(),
                "Latitude": lat,
                "Longitude": lon,
                "Year": year,
                "pH": ph,
                "EC_uScm": ec,
                "CO3": co3,
                "HCO3": hco3,
                "Cl": cl,
                "SO4": so4,
                "NO3": no3,
                "PO4": po4,
                "TH": th,
                "Ca": ca,
                "Mg": mg,
                "Na": na,
                "K": k,
                "F": f,
                "TDS": None,
                "SiO2": None,
            }
            records.append(row)
            i += 8 + len(chem)
            continue
        i += 1
    return records


def extract_bihar_wells_from_pdf(pdf_path: Path) -> pd.DataFrame:
    """Return one row per well for State == Bihar only."""
    pdf_path = Path(pdf_path)
    doc = fitz.open(str(pdf_path))
    all_lines: list[str] = []
    for page in doc:
        text = _normalize_cgwb_text(page.get_text() or "")
        for ln in text.splitlines():
            s = ln.strip()
            if s:
                all_lines.append(s)
    doc.close()
    records: list[dict[str, Any]] = []
    i = 0
    n = len(all_lines)
    while i < n:
        if WELL_RE.match(all_lines[i]):
            j = i + 1
            while j < n and not WELL_RE.match(all_lines[j]):
                j += 1
            block = all_lines[i:j]
            rec = _parse_one_record(block)
            if rec is not None:
                records.append(rec)
            i = j
        else:
            i += 1
    if not records:
        records = _parse_modern_serial_bihar_records(all_lines)
    return pd.DataFrame.from_records(records)


def aggregate_cgwb_by_district_year(wells: pd.DataFrame) -> pd.DataFrame:
    """District–year medians/means for modeling (robust to outliers)."""
    if wells.empty:
        return pd.DataFrame()
    g = wells.groupby(["District", "Year"], as_index=False)
    agg = g.agg(
        n_wells=("Well_ID", "count"),
        pH_mean=("pH", "median"),
        EC_median=("EC_uScm", "median"),
        HCO3_median=("HCO3", "median"),
        Cl_median=("Cl", "median"),
        SO4_median=("SO4", "median"),
        NO3_median=("NO3", "median"),
        F_median=("F", "median"),
        TDS_median=("TDS", "median"),
    )
    return agg
