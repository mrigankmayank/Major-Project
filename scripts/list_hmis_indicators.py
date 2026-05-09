"""Write unique HMIS indicator strings (filtered) to a UTF-8 text file."""
import pandas as pd

path = r"14277- Dataful/district-and-year-wise-data-related-to-all-health-indicators-under-health-management-information-system-hmis-for-bihar.xlsx"
df = pd.read_excel(path, usecols=["indicator"])
u = df["indicator"].dropna().astype(str).unique()
keys = ("child", "infant", "neonatal", "death", "diarr", "pneumo", "sam", "malnut", "stunt", "wast", "immun", "dpt", "measles", "diarrhoea", "ari", "lbw", "still")
sel = sorted({x for x in u if any(k in x.lower() for k in keys)})
open("data/raw_health/_hmis_indicator_subset.txt", "w", encoding="utf-8").write("\n".join(sel[:500]))
print("count", len(sel))
