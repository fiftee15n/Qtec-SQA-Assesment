import json
import sys

report_path = sys.argv[1] if len(sys.argv) > 1 else "d:/Qtech-Tasks/test-artifacts/lighthouse-home.report.json"

with open(report_path, "r", encoding="utf-8") as f:
    d = json.load(f)

cats = d.get("categories", {})
print("=== LIGHTHOUSE SCORES ===")
for k, v in cats.items():
    score = v.get("score", 0)
    score_pct = score * 100 if score else 0
    print(f"  {v.get('title', k)}: {score_pct:.0f}")

audits = d.get("audits", {})
print("\n=== CORE WEB VITALS ===")
for metric in ["largest-contentful-paint", "cumulative-layout-shift", "interactive", "total-blocking-time", "first-contentful-paint", "speed-index", "server-response-time"]:
    if metric in audits:
        a = audits[metric]
        display = a.get("displayValue", "N/A")
        score = a.get("score", 0)
        score_pct = score * 100 if score else 0
        print(f"  {a.get('title', metric)}: {display} (score: {score_pct:.0f})")
