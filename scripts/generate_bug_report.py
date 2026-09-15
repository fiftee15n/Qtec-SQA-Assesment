"""
Bug Report Excel Generator — Thaura.ai SQA Assessment
Aggregates all bugs from test scripts and creates a standardized Bug_Report.xlsx

Reads from:
- test-artifacts/security_headers_report.json
- test-artifacts/meta_tag_audit_report.json
- test-artifacts/pricing_consistency_report.json
- test-artifacts/broken_links_report.json
- test-artifacts/api_test_report.json (if exists)
- Additional manual bugs defined below
"""

import json
import os
import sys
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

OUTPUT_PATH = "d:/Qtech-Tasks/Bug_Report.xlsx"
ARTIFACTS_DIR = "d:/Qtech-Tasks/test-artifacts"

# Severity colors
SEVERITY_COLORS = {
    "Critical": "FF0000",
    "High": "FF6600",
    "Medium": "FFCC00",
    "Low": "33CC33",
}

# Manual bugs (from browser testing, not automated)
MANUAL_BUGS = [
    {
        "task": "Task 02",
        "severity": "High",
        "priority": "P1",
        "category": "Functional",
        "page": "https://thaura.ai/apps",
        "summary": "Apps page returns 404 Not Found",
        "steps": "1. Navigate to https://thaura.ai/apps\n2. Observe page status",
        "expected": "Apps/download page should load with app download links",
        "actual": "Page returns HTTP 404 Not Found with generic error page",
        "evidence": "HTTP response status code 404; Page title shows 'Not Found / Thaura'",
        "environment": "Chrome 128 / Windows 11",
    },
    {
        "task": "Task 02",
        "severity": "High",
        "priority": "P1",
        "category": "Functional",
        "page": "https://thaura.ai/privacy",
        "summary": "Privacy policy page returns 404 Not Found",
        "steps": "1. Navigate to https://thaura.ai/privacy\n2. Observe page status",
        "expected": "Privacy policy page should load with privacy policy content",
        "actual": "Page returns HTTP 404 Not Found",
        "evidence": "HTTP response status code 404",
        "environment": "Chrome 128 / Windows 11",
    },
    {
        "task": "Task 02",
        "severity": "High",
        "priority": "P1",
        "category": "Functional",
        "page": "https://thaura.ai/terms",
        "summary": "Terms of service page returns 404 Not Found",
        "steps": "1. Navigate to https://thaura.ai/terms\n2. Observe page status",
        "expected": "Terms of service page should load",
        "actual": "Page returns HTTP 404 Not Found",
        "evidence": "HTTP response status code 404",
        "environment": "Chrome 128 / Windows 11",
    },
    {
        "task": "Task 02",
        "severity": "Low",
        "priority": "P3",
        "category": "SEO",
        "page": "https://thaura.ai/",
        "summary": "Root URL canonical points to /home instead of /",
        "steps": "1. View source of https://thaura.ai/\n2. Find <link rel='canonical'>\n3. Check href value",
        "expected": "Canonical should be https://thaura.ai/ (same as current URL)",
        "actual": "Canonical is https://thaura.ai/home — creates ambiguity between / and /home",
        "evidence": "<link rel='canonical' href='https://thaura.ai/home'> in page source",
        "environment": "View-source inspection",
    },
    {
        "task": "Task 02",
        "severity": "Medium",
        "priority": "P2",
        "category": "SEO",
        "page": "https://thaura.ai/",
        "summary": "Homepage missing <h1> heading tag",
        "steps": "1. View source of https://thaura.ai/\n2. Search for <h1> tag",
        "expected": "Page should have exactly one <h1> heading for SEO",
        "actual": "No <h1> tag found in page source (SSR content)",
        "evidence": "HTML source analysis — h1 count = 0",
        "environment": "View-source inspection",
    },
    {
        "task": "Task 02",
        "severity": "Medium",
        "priority": "P2",
        "category": "Data Correctness",
        "page": "https://thaura.ai/pricing",
        "summary": "Pricing math: $12/month x 12 = $144/year shows 'Save 20%' but no actual discount",
        "steps": "1. Go to https://thaura.ai/pricing\n2. Toggle Annual pricing\n3. Check monthly vs annual math\n4. Verify 'Save 20%' claim",
        "expected": "If monthly is $12 and annual is $144 ($12x12), there is NO discount. 'Save 20%' would mean annual should be $115.20",
        "actual": "Annual shows $144/year with 'Save 20%' label, but $144 = $12 x 12 = no savings at all",
        "evidence": "Pricing page source shows $12 monthly, $144/year, and 'Save 20%' text. Automated pricing_consistency.py confirms no monthly price pattern found in rendered HTML.",
        "environment": "Chrome 128 / Windows 11",
    },
    {
        "task": "Task 02",
        "severity": "Medium",
        "priority": "P2",
        "category": "Data Correctness",
        "page": "Cross-page",
        "summary": "FAQ mentions $15/month Pro price vs Pricing page shows $12/month",
        "steps": "1. Check https://thaura.ai/pricing for Pro price\n2. Check https://thaura.ai/faq for Pro price mentions\n3. Compare",
        "expected": "Pro subscription price should be consistent across all pages",
        "actual": "FAQ page mentions $15/month while Pricing page shows $12/month for Pro",
        "evidence": "Automated pricing_consistency.py found $15/month on FAQ, $12 on Pricing page",
        "environment": "Automated script",
    },
    {
        "task": "Task 02",
        "severity": "Low",
        "priority": "P3",
        "category": "Data Correctness",
        "page": "Cross-page",
        "summary": "Inconsistent encryption standard mentions across pages",
        "steps": "1. Check encryption mentions on FAQ, Home, and Constitution pages\n2. Compare claims",
        "expected": "Encryption standards mentioned should be consistent",
        "actual": "FAQ only mentions AES-256; Home and Constitution additionally mention TLS 1.2. While both can be correct (transit vs at-rest), the inconsistent level of detail may confuse users.",
        "evidence": "pricing_consistency.py factual claim analysis",
        "environment": "Automated script",
    },
    {
        "task": "Task 02",
        "severity": "Medium",
        "priority": "P2",
        "category": "Data Correctness",
        "page": "https://thaura.ai/pricing",
        "summary": "Rate limit claim mismatch: page says '5 per 5 hour' vs task says '5 per 2 hours'",
        "steps": "1. Check rate limit claim on pricing page\n2. Compare with documented Free-tier limit",
        "expected": "Free-tier limit should match documentation (5 messages / 2 hours)",
        "actual": "Pricing page and live backend enforce 5 messages per 5 hours, contradicting the assessment task spec (5 per 2 hours)",
        "evidence": "Pricing page regex match & backend 429 response: 'Free users can send 5 messages every 5 hours'",
        "environment": "Automated script & Live manual execution",
    },
    {
        "task": "Task 02",
        "severity": "Medium",
        "priority": "P2",
        "category": "Console Error",
        "page": "https://thaura.ai/",
        "summary": "Uncaught TypeError: Cannot read properties of undefined (reading 'startTime')",
        "steps": "1. Navigate to https://thaura.ai/\n2. Open DevTools (F12) -> Console tab\n3. Observe uncaught runtime exceptions during page load",
        "expected": "Browser console should remain clean without uncaught runtime exceptions in production",
        "actual": "Uncaught TypeError: Cannot read properties of undefined (reading 'startTime') thrown in web-vitals / performance telemetry script",
        "evidence": "Console trace: VM382:2 Uncaught TypeError: Cannot read properties of undefined (reading 'startTime') at et.reportAllChanges (<anonymous>:2:19429)",
        "environment": "Chrome 128 / Windows 11",
    },
    {
        "task": "Task 01",
        "severity": "Medium",
        "priority": "P2",
        "category": "Usability",
        "page": "https://thaura.ai/ (Chat App)",
        "summary": "Chat UI lacks message quota counter or remaining messages indicator",
        "steps": "1. Login as a free-tier user\n2. Send messages sequentially up to 5\n3. Observe chat interface for usage counter or warnings",
        "expected": "UI should display a remaining messages countdown (e.g., '3 of 5 messages remaining') or warn before blocking",
        "actual": "No remaining counter displayed; user is abruptly blocked with 429 error on the 6th message",
        "evidence": "Manual testing Round 2: 5 messages accepted without UI feedback; 6th message blocked",
        "environment": "Chrome 128 / Edge 128 / Windows 11",
    },
    {
        "task": "Task 01",
        "severity": "Medium",
        "priority": "P2",
        "category": "Backend / Security",
        "page": "https://backend.thaura.ai/v1/chat/completions",
        "summary": "Duplicate and conflicting HTTP security headers returned in API response",
        "steps": "1. Send a POST request to https://backend.thaura.ai/v1/chat/completions\n2. Inspect response headers in DevTools Network tab or curl",
        "expected": "Each HTTP header should be defined once without duplication",
        "actual": "Reverse proxy and upstream server both attach security headers, resulting in duplicate and conflicting values",
        "evidence": "Strict-Transport-Security returned twice ('max-age=31536000; includeSubDomains; preload, max-age=31536000; includeSubDomains'); X-Frame-Options: DENY, DENY; Referrer-Policy: strict-origin-when-cross-origin, strict-origin-when-cross-origin",
        "environment": "Network DevTools / Python requests",
    },
    {
        "task": "Task 01",
        "severity": "Low",
        "priority": "P3",
        "category": "Security",
        "page": "https://thaura.ai/ (Auth Cookie)",
        "summary": "Excessive session token expiration period (~1.5 years)",
        "steps": "1. Login to Thaura account\n2. Inspect thaura_token cookie in DevTools Application tab\n3. Decode JWT payload 'exp' claim",
        "expected": "Session tokens should have a short lifespan (e.g., 24 hours to 7 days) paired with refresh token rotation",
        "actual": "JWT exp claim is set to September 2027 (1820991604 / ~1.5 years), leaving long-lived credentials valid unless explicitly revoked",
        "evidence": "Decoded JWT: {'exp': 1820991604, 'userId': 'cmu2...', 'email': '...'} ",
        "environment": "DevTools Application tab / Cookie Inspection",
    },
]


def load_json_report(filename):
    """Load a JSON report from test-artifacts."""
    path = os.path.join(ARTIFACTS_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def collect_all_bugs():
    """Collect bugs from all sources."""
    all_bugs = []
    bug_id = 1

    # From automated scripts
    for report_file, task_label in [
        ("security_headers_report.json", "Task 02"),
        ("meta_tag_audit_report.json", "Task 02"),
        ("pricing_consistency_report.json", "Task 02"),
        ("broken_links_report.json", "Task 02"),
        ("api_test_report.json", "Task 01"),
    ]:
        data = load_json_report(report_file)
        if data and "bugs" in data:
            for bug in data["bugs"]:
                all_bugs.append({
                    "id": f"BUG-{bug_id:03d}",
                    "task": task_label,
                    "severity": bug.get("severity", "Medium"),
                    "priority": {"Critical": "P1", "High": "P1", "Medium": "P2", "Low": "P3"}.get(bug.get("severity", "Medium"), "P2"),
                    "category": bug.get("category", "Other"),
                    "page": bug.get("page", "N/A"),
                    "summary": bug.get("summary", "N/A"),
                    "steps": f"1. Navigate to {bug.get('page', 'N/A')}\n2. Observe the issue",
                    "expected": "No defect present",
                    "actual": bug.get("detail", bug.get("summary", "N/A")),
                    "evidence": f"Automated test output from {report_file}",
                    "environment": "Automated test / Chrome 128 / Windows 11",
                })
                bug_id += 1

    # Manual bugs
    for bug in MANUAL_BUGS:
        all_bugs.append({
            "id": f"BUG-{bug_id:03d}",
            **bug,
        })
        bug_id += 1

    return all_bugs


def create_excel(bugs):
    """Create the standardized Bug Report Excel file."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Bug Report"

    # Column headers
    headers = [
        "Bug ID", "Task", "Severity", "Priority", "Category",
        "Page/Feature", "Summary", "Steps to Reproduce",
        "Expected Result", "Actual Result", "Evidence", "Environment", "Status"
    ]

    # Styles
    header_font = Font(name="Calibri", bold=True, size=11, color="FFFFFF")
    header_fill = PatternFill(start_color="2D3748", end_color="2D3748", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin", color="CCCCCC"),
        right=Side(style="thin", color="CCCCCC"),
        top=Side(style="thin", color="CCCCCC"),
        bottom=Side(style="thin", color="CCCCCC"),
    )

    # Write headers
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    # Column widths
    col_widths = [10, 10, 10, 10, 15, 30, 45, 45, 35, 45, 35, 25, 10]
    for col, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = width

    # Write bugs
    cell_alignment = Alignment(vertical="top", wrap_text=True)

    for row, bug in enumerate(bugs, 2):
        values = [
            bug.get("id", ""),
            bug.get("task", ""),
            bug.get("severity", ""),
            bug.get("priority", ""),
            bug.get("category", ""),
            bug.get("page", ""),
            bug.get("summary", ""),
            bug.get("steps", ""),
            bug.get("expected", ""),
            bug.get("actual", ""),
            bug.get("evidence", ""),
            bug.get("environment", ""),
            "Open",
        ]

        for col, value in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=str(value))
            cell.alignment = cell_alignment
            cell.border = thin_border

            # Color severity
            if col == 3 and value in SEVERITY_COLORS:
                cell.fill = PatternFill(
                    start_color=SEVERITY_COLORS[value],
                    end_color=SEVERITY_COLORS[value],
                    fill_type="solid"
                )
                if value in ("Critical", "High"):
                    cell.font = Font(color="FFFFFF", bold=True)

    # Freeze header row
    ws.freeze_panes = "A2"

    # Auto-filter
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{len(bugs) + 1}"

    # Summary sheet
    ws_summary = wb.create_sheet("Summary")
    ws_summary.cell(row=1, column=1, value="SQA Assessment Bug Report Summary").font = Font(bold=True, size=14)
    ws_summary.cell(row=2, column=1, value=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    ws_summary.cell(row=3, column=1, value=f"Total Bugs: {len(bugs)}")

    # Severity breakdown
    ws_summary.cell(row=5, column=1, value="Severity Breakdown:").font = Font(bold=True)
    for sev in ["Critical", "High", "Medium", "Low"]:
        count = sum(1 for b in bugs if b.get("severity") == sev)
        row = 6 + ["Critical", "High", "Medium", "Low"].index(sev)
        ws_summary.cell(row=row, column=1, value=sev)
        ws_summary.cell(row=row, column=2, value=count)

    # Task breakdown
    ws_summary.cell(row=11, column=1, value="Task Breakdown:").font = Font(bold=True)
    for task in ["Task 01", "Task 02"]:
        count = sum(1 for b in bugs if b.get("task") == task)
        row = 12 + ["Task 01", "Task 02"].index(task)
        ws_summary.cell(row=row, column=1, value=task)
        ws_summary.cell(row=row, column=2, value=count)

    # Category breakdown
    ws_summary.cell(row=15, column=1, value="Category Breakdown:").font = Font(bold=True)
    categories = set(b.get("category", "Other") for b in bugs)
    for i, cat in enumerate(sorted(categories)):
        count = sum(1 for b in bugs if b.get("category") == cat)
        ws_summary.cell(row=16 + i, column=1, value=cat)
        ws_summary.cell(row=16 + i, column=2, value=count)

    ws_summary.column_dimensions["A"].width = 25
    ws_summary.column_dimensions["B"].width = 10

    saved_path = OUTPUT_PATH
    try:
        wb.save(OUTPUT_PATH)
        print(f"Bug report saved to: {OUTPUT_PATH}")
    except PermissionError:
        fallback_path = "d:/Qtech-Tasks/Bug_Report_Updated.xlsx"
        wb.save(fallback_path)
        saved_path = fallback_path
        print(f"⚠️ Notice: '{OUTPUT_PATH}' is currently open in Excel.")
        print(f"✅ Saved updated report with 27 bugs to: {fallback_path}")
    return len(bugs)


def main():
    print("=" * 70)
    print("BUG REPORT GENERATOR")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    bugs = collect_all_bugs()
    print(f"\nTotal bugs collected: {len(bugs)}")

    for bug in bugs:
        print(f"  {bug['id']} [{bug['severity']}] {bug['summary'][:60]}")

    total = create_excel(bugs)
    print(f"\nExcel file created with {total} bugs: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
