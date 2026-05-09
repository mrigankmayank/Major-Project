# District susceptibility Yes / No report

This file lists **every district-year** with explicit **Yes/No** answers (see columns).
Generated from `results/models/district_susceptibility_profile.csv`.

## Definitions

- **Environmental high stress Y/N**: **Yes** = top tertile of cohort-relative groundwater/monitoring stress (`Environmental_stress_band` = High). Not a clinical diagnosis.
- **HMIS high burden Y/N**: **Yes** = observed composite HMIS burden in **top tertile** (`high`) by district-year in this dataset.
- **Top GW stress 1–3**: groundwater parameters most shifted vs cohort (see CSV for full text with z-scores).

## HMIS indicators in the composite burden

- Childhood Diseases - Severe Acute Malnutrition (SAM)
- Childhood Diseases - Diarrhoea
- Childhood Diseases - Pneumonia
- Childhood Diseases - Measles
- Number of Infant Deaths (1 -12 months) due to Diarrhoea
- Number of Infant Deaths (1 -12 months) due to Pneumonia
- Number of Child Deaths (1 -5 years) due to Diarrhoea
- Number of Child Deaths (1 -5 years) due to Pneumonia
- Number of cases of Infant deaths within 24 hrs of birth
- Number of still births

## Full table

| District | Year | Environmental_susceptibility_high_stress_YN | HMIS_observed_high_burden_YN | Environmental_stress_band | HMIS_observed_burden_tercile | HMIS_burden_per_100k | Environmental_exposure_index | Top_GW_stress_1 | Top_GW_stress_2 | Top_GW_stress_3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Araria | 2019 | No | Yes | Medium | high | 69.46 | 0.1887 | Fluoride (F) (z=+2.05) | Monitoring intensity (# wells sampled) (z=-0.80) | Sulphate (SO4) (z=-0.69) |
| Arwal | 2019 | No | Yes | Medium | high | 126.7 | -0.0821 | Fluoride (F) (z=+1.44) | Chloride (Cl) (z=-1.36) | Bicarbonate (HCO3) (z=+1.03) |
| Arwal | 2020 | No | Yes | Low | high | 55.08 | -0.5959 | Bicarbonate (HCO3) (z=-1.38) | Electrical conductivity (EC) (z=-1.11) | Fluoride (F) (z=-1.01) |
| Arwal | 2021 | No | No | Medium | mid | 42.52 | 0.0672 | Chloride (Cl) (z=+2.00) | Bicarbonate (HCO3) (z=-1.28) | Monitoring intensity (# wells sampled) (z=-0.80) |
| Aurangabad | 2019 | Yes | No | High | mid | 38.07 | 0.4907 | Bicarbonate (HCO3) (z=+1.52) | Total dissolved solids (TDS) (z=+1.36) | Electrical conductivity (EC) (z=+1.32) |
| Aurangabad | 2021 | Yes | No | High | low | 5.67 | 0.6689 | Electrical conductivity (EC) (z=+1.80) | Total dissolved solids (TDS) (z=+1.67) | Nitrate (NO3) (z=+0.86) |
| Banka | 2019 | No | No | Medium | mid | 31.99 | 0.1524 | Fluoride (F) (z=+2.10) | Bicarbonate (HCO3) (z=-0.64) | Total dissolved solids (TDS) (z=+0.57) |
| Begusarai | 2019 | Yes | No | High | mid | 40.36 | 0.2987 | Monitoring intensity (# wells sampled) (z=+1.65) | Nitrate (NO3) (z=-0.86) | pH (z=+0.78) |
| Begusarai | 2021 | No | No | Medium | low | 13.13 | 0.1032 | Sulphate (SO4) (z=+2.69) | Total dissolved solids (TDS) (z=-1.86) | Fluoride (F) (z=-0.99) |
| Bhagalpur | 2019 | No | No | Medium | mid | 47.14 | 0.1369 | Fluoride (F) (z=+1.48) | Sulphate (SO4) (z=+0.82) | Total dissolved solids (TDS) (z=+0.74) |
| Bhojpur | 2019 | Yes | Yes | High | high | 48.2 | 0.356 | Monitoring intensity (# wells sampled) (z=+1.58) | Total dissolved solids (TDS) (z=+0.80) | Sulphate (SO4) (z=+0.75) |
| Bhojpur | 2020 | No | No | Medium | mid | 44.93 | 0.1507 | pH (z=-3.03) | Nitrate (NO3) (z=+2.14) | Sulphate (SO4) (z=+1.88) |
| Bhojpur | 2021 | Yes | Yes | High | high | 61.9 | 0.653 | Electrical conductivity (EC) (z=+1.97) | Total dissolved solids (TDS) (z=-1.82) | Monitoring intensity (# wells sampled) (z=+1.70) |
| Buxar | 2019 | Yes | No | High | low | 7.09 | 0.4456 | Fluoride (F) (z=+2.05) | Bicarbonate (HCO3) (z=+1.34) | Monitoring intensity (# wells sampled) (z=+1.31) |
| Buxar | 2020 | No | No | Low | low | 0.41 | -0.6264 | pH (z=-2.87) | Bicarbonate (HCO3) (z=-1.94) | Sulphate (SO4) (z=+1.41) |
| Buxar | 2021 | No | No | Medium | low | 0.94 | 0.0 | Total dissolved solids (TDS) (z=-1.81) | Monitoring intensity (# wells sampled) (z=+1.31) | Bicarbonate (HCO3) (z=+1.23) |
| Darbhanga | 2019 | No | No | Low | low | 8.23 | -0.6094 | Sulphate (SO4) (z=-1.50) | Chloride (Cl) (z=-1.42) | Electrical conductivity (EC) (z=-1.25) |
| Darbhanga | 2021 | No | No | Low | mid | 25.07 | -0.7675 | Total dissolved solids (TDS) (z=-1.82) | Sulphate (SO4) (z=-1.64) | Chloride (Cl) (z=-1.25) |
| Gaya | 2019 | Yes | Yes | High | high | 51.87 | 0.6096 | Bicarbonate (HCO3) (z=+1.98) | Total dissolved solids (TDS) (z=+1.33) | Electrical conductivity (EC) (z=+1.27) |
| Gaya | 2020 | Yes | No | High | mid | 19.47 | 0.5616 | Nitrate (NO3) (z=+1.95) | Chloride (Cl) (z=+1.29) | Electrical conductivity (EC) (z=+1.13) |
| Gaya | 2021 | Yes | No | High | mid | 20.77 | 0.4844 | Chloride (Cl) (z=+2.61) | Electrical conductivity (EC) (z=+1.80) | Total dissolved solids (TDS) (z=-1.77) |
| Gopalganj | 2019 | No | Yes | Medium | high | 78.26 | -0.0634 | pH (z=-1.05) | Fluoride (F) (z=-0.96) | Sulphate (SO4) (z=+0.91) |
| Gopalganj | 2020 | No | No | Low | mid | 44.34 | -0.5579 | Monitoring intensity (# wells sampled) (z=-1.09) | Fluoride (F) (z=-1.01) | Chloride (Cl) (z=-0.88) |
| Jamui | 2019 | Yes | No | High | mid | 40.73 | 0.2127 | Fluoride (F) (z=+1.48) | Bicarbonate (HCO3) (z=-0.90) | Sulphate (SO4) (z=+0.82) |
| Jehanabad | 2020 | Yes | Yes | High | high | 65.4 | 0.48 | Sulphate (SO4) (z=+1.94) | Nitrate (NO3) (z=+1.44) | Fluoride (F) (z=-1.01) |
| Jehanabad | 2021 | Yes | No | High | mid | 45.68 | 0.738 | Chloride (Cl) (z=+2.00) | Total dissolved solids (TDS) (z=+1.24) | Fluoride (F) (z=+1.14) |
| Katihar | 2019 | No | No | Medium | low | 8.17 | 0.0009 | Chloride (Cl) (z=-0.64) | pH (z=+0.63) | Bicarbonate (HCO3) (z=+0.53) |
| Katihar | 2020 | Yes | No | High | low | 3.65 | 0.4352 | pH (z=-3.65) | Nitrate (NO3) (z=+3.60) | Electrical conductivity (EC) (z=+2.59) |
| Khagaria | 2019 | Yes | Yes | High | high | 965.69 | 0.2787 | Chloride (Cl) (z=+2.66) | Sulphate (SO4) (z=-1.40) | Nitrate (NO3) (z=-0.93) |
| Kishanganj | 2019 | No | Yes | Medium | high | 150.5 | -0.1255 | Fluoride (F) (z=+2.12) | Bicarbonate (HCO3) (z=-1.19) | Chloride (Cl) (z=-0.88) |
| Madhepura | 2019 | No | No | Medium | mid | 18.48 | 0.1387 | Fluoride (F) (z=+1.40) | Sulphate (SO4) (z=+1.11) | Bicarbonate (HCO3) (z=-0.98) |
| Madhubani | 2019 | No | No | Medium | mid | 38.95 | -0.0091 | Monitoring intensity (# wells sampled) (z=+1.31) | Sulphate (SO4) (z=-1.09) | Fluoride (F) (z=+1.02) |
| Munger | 2019 | Yes | Yes | High | high | 438.82 | 0.2448 | Total dissolved solids (TDS) (z=+0.95) | Chloride (Cl) (z=+0.78) | Electrical conductivity (EC) (z=+0.68) |
| Muzaffarpur | 2019 | No | No | Low | low | 13.83 | -0.2972 | Electrical conductivity (EC) (z=-0.88) | Sulphate (SO4) (z=-0.81) | Nitrate (NO3) (z=-0.54) |
| Muzaffarpur | 2020 | No | No | Low | low | 0.87 | -0.1692 | Monitoring intensity (# wells sampled) (z=-1.92) | Fluoride (F) (z=-1.01) | Bicarbonate (HCO3) (z=+0.98) |
| Muzaffarpur | 2021 | Yes | No | High | low | 0.29 | 0.3445 | Chloride (Cl) (z=+2.36) | Sulphate (SO4) (z=+1.97) | Total dissolved solids (TDS) (z=-1.83) |
| Nalanda | 2019 | No | Yes | Medium | high | 88.89 | 0.154 | Monitoring intensity (# wells sampled) (z=+1.97) | Chloride (Cl) (z=+0.44) | Bicarbonate (HCO3) (z=-0.42) |
| Nalanda | 2020 | Yes | No | High | low | 13.97 | 0.7367 | Nitrate (NO3) (z=+1.48) | Monitoring intensity (# wells sampled) (z=+1.24) | Electrical conductivity (EC) (z=+1.01) |
| Nalanda | 2021 | No | No | Medium | low | 10.7 | 0.144 | Bicarbonate (HCO3) (z=+1.89) | Total dissolved solids (TDS) (z=-1.79) | Monitoring intensity (# wells sampled) (z=+1.52) |
| Nawada | 2019 | No | No | Low | mid | 22.4 | -0.3777 | Sulphate (SO4) (z=-1.49) | Bicarbonate (HCO3) (z=-1.48) | Electrical conductivity (EC) (z=-1.02) |
| Nawada | 2020 | No | No | Low | low | 4.46 | -0.5654 | Electrical conductivity (EC) (z=-1.38) | Bicarbonate (HCO3) (z=-1.18) | Sulphate (SO4) (z=-1.13) |
| Nawada | 2021 | No | No | Low | low | 2.88 | -0.4774 | Total dissolved solids (TDS) (z=-1.78) | Sulphate (SO4) (z=-1.13) | Electrical conductivity (EC) (z=-0.71) |
| Patna | 2019 | No | Yes | Low | high | 52.58 | -0.5885 | Bicarbonate (HCO3) (z=-1.89) | Electrical conductivity (EC) (z=-1.69) | Monitoring intensity (# wells sampled) (z=+1.24) |
| Patna | 2020 | Yes | No | High | low | 3.05 | 0.3824 | Bicarbonate (HCO3) (z=+2.79) | Monitoring intensity (# wells sampled) (z=-1.92) | Electrical conductivity (EC) (z=+1.78) |
| Patna | 2021 | No | Yes | Low | high | 65.29 | -0.2707 | Monitoring intensity (# wells sampled) (z=+1.76) | Bicarbonate (HCO3) (z=-1.18) | Electrical conductivity (EC) (z=-1.08) |
| Purnia | 2020 | No | No | Low | mid | 30.91 | -0.7006 | pH (z=-4.12) | Nitrate (NO3) (z=+2.61) | Sulphate (SO4) (z=-1.48) |
| Rohtas | 2019 | Yes | No | High | low | 1.89 | 0.4999 | Bicarbonate (HCO3) (z=+2.10) | Fluoride (F) (z=+1.90) | Total dissolved solids (TDS) (z=+1.18) |
| Saharsa | 2019 | No | Yes | Medium | high | 485.83 | 0.1479 | Chloride (Cl) (z=+1.16) | Fluoride (F) (z=+1.03) | Nitrate (NO3) (z=-0.91) |
| Samastipur | 2019 | No | Yes | Medium | high | 193.07 | -0.0668 | Nitrate (NO3) (z=-0.65) | Bicarbonate (HCO3) (z=-0.53) | Chloride (Cl) (z=-0.46) |
| Samastipur | 2020 | No | Yes | Low | high | 90.72 | -0.1459 | Nitrate (NO3) (z=+1.74) | Bicarbonate (HCO3) (z=-1.18) | Fluoride (F) (z=-0.98) |
| Saran | 2019 | No | No | Medium | mid | 19.13 | -0.0122 | Monitoring intensity (# wells sampled) (z=+1.08) | Chloride (Cl) (z=+0.97) | pH (z=-0.93) |
| Saran | 2020 | No | No | Low | low | 6.45 | -0.2753 | Chloride (Cl) (z=-1.25) | Fluoride (F) (z=-1.01) | Bicarbonate (HCO3) (z=+0.63) |
| Saran | 2021 | Yes | No | High | low | 14.22 | 0.2128 | Nitrate (NO3) (z=+0.92) | Bicarbonate (HCO3) (z=-0.83) | Fluoride (F) (z=+0.65) |
| Sheohar | 2019 | No | Yes | Medium | high | 166.1 | -0.0368 | Monitoring intensity (# wells sampled) (z=-1.09) | Fluoride (F) (z=-0.79) | Bicarbonate (HCO3) (z=-0.76) |
| Sitamarhi | 2019 | No | Yes | Low | high | 106.91 | -0.7349 | Sulphate (SO4) (z=-1.71) | Electrical conductivity (EC) (z=-1.67) | Chloride (Cl) (z=-1.62) |
| Sitamarhi | 2021 | No | No | Low | low | 8.68 | -1.0018 | Electrical conductivity (EC) (z=-2.01) | Total dissolved solids (TDS) (z=-1.85) | Bicarbonate (HCO3) (z=-1.59) |
| Siwan | 2019 | No | Yes | Medium | high | 115.03 | -0.1448 | Fluoride (F) (z=-1.01) | Sulphate (SO4) (z=-0.90) | Chloride (Cl) (z=+0.80) |
| Siwan | 2020 | No | No | Low | mid | 33.03 | -0.5985 | Monitoring intensity (# wells sampled) (z=-1.92) | Fluoride (F) (z=-1.01) | Chloride (Cl) (z=-0.88) |
| Siwan | 2021 | Yes | No | High | mid | 36.18 | 0.2744 | Monitoring intensity (# wells sampled) (z=-1.46) | Fluoride (F) (z=+1.37) | Nitrate (NO3) (z=+0.86) |
| Supaul | 2019 | No | Yes | Low | high | 66.4 | -0.3814 | Monitoring intensity (# wells sampled) (z=+1.24) | Electrical conductivity (EC) (z=-1.14) | Chloride (Cl) (z=-0.97) |
| Vaishali | 2019 | No | No | Low | mid | 45.75 | -0.3246 | pH (z=-1.07) | Sulphate (SO4) (z=-1.00) | Fluoride (F) (z=-0.96) |
| Vaishali | 2020 | No | No | Low | low | 8.04 | -0.3085 | Chloride (Cl) (z=-1.25) | Fluoride (F) (z=-1.01) | Electrical conductivity (EC) (z=-0.91) |
| Vaishali | 2021 | No | No | Medium | mid | 14.33 | 0.1222 | Nitrate (NO3) (z=+1.79) | Fluoride (F) (z=-1.01) | Monitoring intensity (# wells sampled) (z=+0.89) |

---

*End of report.*