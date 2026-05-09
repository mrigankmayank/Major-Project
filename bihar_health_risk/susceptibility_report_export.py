"""Human-readable Yes/No susceptibility reports (PDF + Markdown) from district_susceptibility_profile.csv."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from fpdf import FPDF

from bihar_health_risk.config import RESULTS_DIR
from bihar_health_risk.etl_hmis_vulnerability import HMIS_VULNERABILITY_INDICATORS

REPORTS_DIR = RESULTS_DIR / "reports"


def _T(text: str) -> str:
    return (
        str(text)
        .replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u00b2", "^2")
        .replace("\u2019", "'")
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def _truncate(s: str, n: int) -> str:
    s = str(s)
    return s if len(s) <= n else s[: n - 3] + "..."


class _SusPDF(FPDF):
    def __init__(self) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=14)
        self.set_margins(left=14, top=14, right=14)


def export_district_yesno_pdf(csv_path: Path, out_pdf: Path | None = None) -> Path:
    """Multi-page PDF: cover + definitions + full landscape table with Env Y/N and HMIS Y/N per row."""
    csv_path = Path(csv_path)
    out_pdf = Path(out_pdf or REPORTS_DIR / "District_Susceptibility_YesNo_Report.pdf")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    df = df.sort_values(["District", "Year"])

    pdf = _SusPDF()

    # ----- Cover -----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.ln(36)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(
        pdf.epw,
        10,
        _T("District susceptibility: Yes / No answers"),
        align="C",
    )
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(
        pdf.epw,
        6,
        _T(
            "Every row is one District + Year. Two independent answers:\n"
            "(1) Environmental high stress Y/N - from CGWB cohort tertiles.\n"
            "(2) HMIS observed high burden Y/N - top tertile of official composite burden per 100k."
        ),
        align="C",
    )
    pdf.ln(16)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(pdf.epw, 5, _T(f"Source data file: {csv_path.name}"))
    pdf.multi_cell(pdf.epw, 5, _T(f"Total rows listed below: {len(df)}"))

    # ----- Definitions -----
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.multi_cell(pdf.epw, 8, _T("Definitions"))
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    defs = [
        "Environmental_susceptibility_high_stress_YN = Yes only if Environmental_stress_band is High "
        "(top tertile of Environmental_exposure_index vs all district-years in this table).",
        "HMIS_observed_high_burden_YN = Yes if HMIS composite burden per 100k is in the top tertile (high) for this dataset.",
        "Top_GW_stress columns = the three groundwater/monitoring metrics most shifted from cohort average (|z|), with signed z in brackets.",
        "This is not a medical diagnosis and not from regression predictions.",
    ]
    for d in defs:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(pdf.epw, 5, _T("- " + d))
        pdf.ln(1)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.multi_cell(pdf.epw, 6, _T("HMIS indicators summed into composite burden"))
    pdf.set_font("Helvetica", "", 8)
    for ind in HMIS_VULNERABILITY_INDICATORS:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(pdf.epw, 4, _T("- " + ind))

    # ----- Full table (landscape) -----
    col_labels = [
        "District",
        "Year",
        "Env Y/N",
        "HMIS Y/N",
        "Env band",
        "HMIS tert",
        "Bur/100k",
        "Exp idx",
        "Top GW 1",
        "Top GW 2",
        "Top GW 3",
    ]
    wds = [28, 12, 12, 12, 14, 14, 14, 13, 50, 50, 50]

    def draw_header() -> None:
        pdf.set_font("Helvetica", "B", 7)
        x = pdf.l_margin
        y = pdf.get_y()
        h = 9
        for label, w in zip(col_labels, wds):
            pdf.rect(x, y, w, h)
            pdf.set_xy(x + 0.4, y + 2)
            pdf.cell(w - 0.8, 5, _T(label), align="C")
            x += w
        pdf.set_y(y + h)

    pdf.add_page(orientation="landscape")
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 8, _T("Full district-year Yes / No table"), ln=True)
    pdf.ln(2)
    draw_header()

    pdf.set_font("Helvetica", "", 6)
    row_h = 10
    y_limit = 188
    trunc = [22, 4, 5, 5, 10, 8, 10, 8, 42, 42, 42]

    for _, r in df.iterrows():
        if pdf.get_y() > y_limit:
            pdf.add_page(orientation="landscape")
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_x(pdf.l_margin)
            pdf.cell(0, 8, _T("Full district-year Yes / No table (continued)"), ln=True)
            pdf.ln(2)
            draw_header()
            pdf.set_font("Helvetica", "", 6)

        raw_cells = [
            str(r.get("District", "")),
            str(int(r["Year"])) if pd.notna(r.get("Year")) else "",
            str(r.get("Environmental_susceptibility_high_stress_YN", "")),
            str(r.get("HMIS_observed_high_burden_YN", "")),
            str(r.get("Environmental_stress_band", "")),
            str(r.get("HMIS_observed_burden_tercile", "")),
            str(r.get("HMIS_burden_per_100k", "")),
            str(r.get("Environmental_exposure_index", "")),
            str(r.get("Top_GW_stress_1", "")),
            str(r.get("Top_GW_stress_2", "")),
            str(r.get("Top_GW_stress_3", "")),
        ]
        cells = [_truncate(c, t) for c, t in zip(raw_cells, trunc)]
        x0 = pdf.l_margin
        y0 = pdf.get_y()
        for ci, (txt, w) in enumerate(zip(cells, wds)):
            pdf.rect(x0 + sum(wds[:ci]), y0, w, row_h)
            pdf.set_xy(x0 + sum(wds[:ci]) + 0.4, y0 + 2)
            pdf.cell(w - 0.8, row_h - 2, _T(txt), align="L")
        pdf.set_y(y0 + row_h)

    pdf.output(str(out_pdf))
    return out_pdf


def export_district_yesno_markdown(csv_path: Path, out_md: Path | None = None) -> Path:
    """Markdown report with full pipe table for easy viewing in GitHub / VS Code."""
    csv_path = Path(csv_path)
    out_md = Path(out_md or REPORTS_DIR / "District_Susceptibility_YesNo_Report.md")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    df = df.sort_values(["District", "Year"])

    lines: list[str] = [
        "# District susceptibility Yes / No report",
        "",
        "This file lists **every district-year** with explicit **Yes/No** answers (see columns).",
        "Generated from `results/models/district_susceptibility_profile.csv`.",
        "",
        "## Definitions",
        "",
        "- **Environmental high stress Y/N**: **Yes** = top tertile of cohort-relative groundwater/monitoring stress (`Environmental_stress_band` = High). Not a clinical diagnosis.",
        "- **HMIS high burden Y/N**: **Yes** = observed composite HMIS burden in **top tertile** (`high`) by district-year in this dataset.",
        "- **Top GW stress 1–3**: groundwater parameters most shifted vs cohort (see CSV for full text with z-scores).",
        "",
        "## HMIS indicators in the composite burden",
        "",
    ]
    for ind in HMIS_VULNERABILITY_INDICATORS:
        lines.append(f"- {ind}")
    lines.extend(["", "## Full table", ""])

    cols = [
        "District",
        "Year",
        "Environmental_susceptibility_high_stress_YN",
        "HMIS_observed_high_burden_YN",
        "Environmental_stress_band",
        "HMIS_observed_burden_tercile",
        "HMIS_burden_per_100k",
        "Environmental_exposure_index",
        "Top_GW_stress_1",
        "Top_GW_stress_2",
        "Top_GW_stress_3",
    ]
    sub = df[[c for c in cols if c in df.columns]].copy()
    header = "| " + " | ".join(sub.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(sub.columns)) + " |"
    lines.append(header)
    lines.append(sep)
    for _, row in sub.iterrows():
        cells = []
        for c in sub.columns:
            v = row.get(c, "")
            if pd.isna(v):
                cells.append("")
            else:
                s = str(v).replace("|", "/").replace("\n", " ")
                cells.append(s)
        lines.append("| " + " | ".join(cells) + " |")

    lines.extend(["", "---", "", "*End of report.*"])
    out_md.write_text("\n".join(lines), encoding="utf-8")
    return out_md


def export_all_yesno_reports(csv_path: Path) -> tuple[Path, Path]:
    """Write PDF + Markdown Yes/No reports next to other reports."""
    pdf_p = export_district_yesno_pdf(csv_path)
    md_p = export_district_yesno_markdown(csv_path)
    return pdf_p, md_p
