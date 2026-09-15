# SQA Engineer Assessment 2026 — Thaura.ai

## Submission Overview

**Candidate:** Jahangir Alam Tamal 
**Date:** 2026-09-15  
**Position:** SQA Engineer  

---

## Deliverables

| # | File | Description |
|---|------|-------------|
| 1 | [**`SQA_Engineer_Assessment_Report_2026.pdf`**](SQA_Engineer_Assessment_Report_2026.pdf) | **Executive Master Report (PDF)** — 12-page comprehensive report covering Task 01, Task 02, Task 03 & Defect Register |
| 2 | [`Bug_Report.xlsx`](Bug_Report.xlsx) / [`Bug_Report_Updated.xlsx`](Bug_Report_Updated.xlsx) | **Standardized bug report** — 27 bugs documented with steps, evidence, severity |
| 3 | [`test-reports/Task01_Chat_App_Test_Report.md`](test-reports/Task01_Chat_App_Test_Report.md) | Task 01: Chat app test report (35 verified test cases + API contract tests) |
| 4 | [`test-reports/Task02_Website_Test_Report.md`](test-reports/Task02_Website_Test_Report.md) | Task 02: Website test report (Complete automated + manual execution results) |
| 5 | [`test-reports/Task03_Reflection_Answers.md`](test-reports/Task03_Reflection_Answers.md) | Task 03: AI & Testing reflection answers |
| 6 | [`scripts/`](scripts/) | All automated test scripts & PDF compiler (reproducible) |
| 7 | [`test-artifacts/`](test-artifacts/) | Raw test data — Lighthouse reports, JSON outputs |

---

## Quick Bug Summary

| Severity | Count | Key Examples |
|----------|-------|-------------|
| **High** | 4 | Missing /privacy (404), /terms (404), /apps (404), Google avatar preconnect broken link |
| **Medium** | 18 | Uncaught console TypeError, missing UI rate limit counter, duplicate API headers, missing H1 tags |
| **Low** | 5 | Extended 1.5-year JWT expiry, canonical mismatch (/home vs /), encryption claim verbosity |
| **Total** | **27** | Fully documented in Excel with reproduction steps & evidence |

---

## Automated Test Scripts

| Script | Purpose | Run Command |
|--------|---------|-------------|
| `security_header_check.py` | Security headers + cookie audit | `python scripts/security_header_check.py` |
| `meta_tag_audit.py` | SEO/meta/OG/Twitter card audit | `python scripts/meta_tag_audit.py` |
| `pricing_consistency.py` | Pricing math + cross-page consistency | `python scripts/pricing_consistency.py` |
| `link_checker.py` | Broken link crawler | `python scripts/link_checker.py` |
| `api_tests.py` | Developer API contract tests | `python scripts/api_tests.py --api-key KEY` |
| `generate_bug_report.py` | Aggregate bugs → Excel | `python scripts/generate_bug_report.py` |

### Requirements
- Python 3.10+ with `requests` and `openpyxl` packages
- Node.js 18+ (for Lighthouse)
- Set `PYTHONIOENCODING=utf-8` on Windows

---

## Test Environment

| Component | Version |
|-----------|---------|
| OS | Windows 11 |
| Browser | Chrome 128 |
| Python | 3.13.7 |
| Node.js | 24.13.0 |
| Lighthouse | 13.4.1 |

---

## Testing Execution Status
- [x] **Task 01: Chat App Manual Testing** — Completed (Account/session, Rate limit 429 verification, Multimodal PDF/Excel/Image uploads, Memory isolation, Injection security)
- [x] **Task 02: Website Technical Testing** — Completed (Automated link checks, SEO audit, Pricing consistency, Lighthouse audits, Load testing, Contact form validation, DevTools console inspection)
- [x] **Bug Report Compilation** — Completed (27 verified bugs compiled into Excel with summary dashboards)

