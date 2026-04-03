# Source Comparison Report

- Total normalized rows: **180**
- Unique festivals: **26**
- Festivals with source disagreement: **20**

## Disagreements

| Festival ID | Dates | Sources |
|---|---|---|
| bs-new-year | 2021-04-13, 2022-04-13, 2023-04-14, 2024-04-13, 2025-04-14, 2026-04-14 | moha_pdf_2078, moha_pdf_2079, moha_pdf_2080, moha_pdf_2081, moha_pdf_2082, moha_pdf_2083 |
| janai-purnima | 2021-08-22, 2022-08-11, 2023-08-30, 2024-08-20, 2025-08-09, 2026-08-28 | moha_pdf_2078, moha_pdf_2079, moha_pdf_2080, moha_pdf_2081, moha_pdf_2082, moha_pdf_2083 |
| dashain | 2021-10-07, 2022-09-26, 2023-10-14, 2024-10-04, 2025-09-23, 2026-10-11 | moha_pdf_2078, moha_pdf_2079, moha_pdf_2080, moha_pdf_2081, moha_pdf_2082, moha_pdf_2083 |
| chhath | 2021-11-09, 2022-10-29, 2023-11-19, 2024-11-08, 2025-10-27, 2026-11-15 | moha_pdf_2078, moha_pdf_2079, moha_pdf_2080, moha_pdf_2081, moha_pdf_2082, moha_pdf_2083 |
| shivaratri | 2022-02-28, 2023-02-18, 2024-03-08, 2025-02-26, 2026-02-14, 2026-02-15, 2027-03-06 | moha_pdf_2078, moha_pdf_2079, moha_pdf_2080, moha_pdf_2081, moha_pdf_2082, moha_pdf_2083 |
| tamu-lhosar | 2021-12-30, 2022-12-30, 2023-12-30, 2024-12-30, 2025-12-30, 2026-12-30 | moha_pdf_2078, moha_pdf_2079, moha_pdf_2080, moha_pdf_2081, moha_pdf_2082, moha_pdf_2083 |
| sonam-lhosar | 2022-02-01, 2024-02-10, 2025-01-31, 2026-01-18, 2026-01-19, 2027-02-07 | moha_pdf_2078, moha_pdf_2080, moha_pdf_2081, moha_pdf_2082, moha_pdf_2083 |
| teej | 2021-09-09, 2022-08-30, 2023-09-17, 2025-08-27, 2026-09-14 | moha_pdf_2078, moha_pdf_2079, moha_pdf_2080, moha_pdf_2082, moha_pdf_2083 |
| gai-jatra | 2021-08-23, 2022-08-11, 2023-08-30, 2024-08-21, 2025-07-18, 2025-08-10, 2026-08-29 | moha_pdf_2078, moha_pdf_2079, moha_pdf_2080, moha_pdf_2081, moha_pdf_2082, moha_pdf_2083 |
| indra-jatra | 2021-09-19, 2022-09-09, 2023-09-27, 2024-09-18, 2025-09-07, 2026-09-25 | moha_pdf_2078, moha_pdf_2079, moha_pdf_2080, moha_pdf_2081, moha_pdf_2082, moha_pdf_2083 |
| ghode-jatra | 2022-03-31, 2023-03-20, 2024-04-08, 2025-03-30, 2026-03-17, 2026-03-18, 2027-04-06 | moha_pdf_2078, moha_pdf_2079, moha_pdf_2080, moha_pdf_2081, moha_pdf_2082, moha_pdf_2083 |
| buddha-jayanti | 2021-05-25, 2022-05-15, 2023-05-05, 2024-05-23, 2025-05-12, 2026-05-01 | moha_pdf_2078, moha_pdf_2079, moha_pdf_2080, moha_pdf_2081, moha_pdf_2082, moha_pdf_2083 |
| saraswati-puja | 2024-02-14, 2025-02-04, 2026-01-22, 2026-01-23, 2027-02-11 | moha_pdf_2080, moha_pdf_2081, moha_pdf_2082, moha_pdf_2083 |
| ram-navami | 2024-04-17, 2026-03-26, 2026-03-27 | moha_pdf_2081, moha_pdf_2082 |
| krishna-janmashtami | 2024-08-27, 2025-08-16, 2026-09-04 | moha_pdf_2081, moha_pdf_2082, moha_pdf_2083 |
| tihar | 2025-10-20, 2026-11-08 | moha_pdf_2082, moha_pdf_2083 |
| gyalpo-lhosar | 2026-02-17, 2026-02-18, 2027-03-09 | moha_pdf_2082, moha_pdf_2083 |
| yomari-punhi | 2025-12-04, 2026-12-25 | override, pradhanlaw_public_holidays_2082 |
| maghe-sankranti | 2026-01-14, 2027-01-14 | override, pradhanlaw_public_holidays_2082 |
| holi | 2026-03-03, 2027-03-22 | override, pradhanlaw_public_holidays_2082 |

## Artifacts

- Normalized data: `data/normalized_sources.json`
