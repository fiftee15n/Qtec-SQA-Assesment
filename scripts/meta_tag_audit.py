"""
SEO / Meta Tag / Open Graph / Twitter Card Audit — Thaura.ai
Task 02, Section 1.4: Canonical URLs, meta tags, OG/Twitter data

Checks:
- <title> tag presence and uniqueness
- meta description
- canonical URL correctness
- Open Graph tags (og:title, og:description, og:image, og:url, og:type)
- Twitter Card tags (twitter:card, twitter:title, twitter:description, twitter:image)
- Duplicate detection across pages
- Heading structure (single <h1> per page)
"""

import requests
import re
import json
from datetime import datetime
from collections import defaultdict

PAGES = [
    "https://thaura.ai/",
    "https://thaura.ai/home",
    "https://thaura.ai/pricing",
    "https://thaura.ai/api-platform",
    "https://thaura.ai/faq",
    "https://thaura.ai/contact",
    "https://thaura.ai/story",
    "https://thaura.ai/constitution",
    "https://thaura.ai/careers",
    "https://thaura.ai/apps",
    "https://thaura.ai/privacy",
    "https://thaura.ai/terms",
]

bugs = []
page_data = []

def extract_meta(html, name_attr, name_val):
    """Extract content from <meta name='...' content='...'> or <meta property='...' content='...'>."""
    pattern = rf'<meta\s+(?:{name_attr}=["\']?{re.escape(name_val)}["\']?\s+content=["\']([^"\']*)["\']|content=["\']([^"\']*)["\']?\s+{name_attr}=["\']?{re.escape(name_val)}["\'])'
    match = re.search(pattern, html, re.IGNORECASE)
    if match:
        return match.group(1) or match.group(2)
    return None

def extract_title(html):
    """Extract <title> content."""
    match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None

def extract_canonical(html):
    """Extract canonical URL."""
    match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    return match.group(1) if match else None

def count_h1(html):
    """Count number of <h1> tags."""
    return len(re.findall(r'<h1[\s>]', html, re.IGNORECASE))

def extract_lang(html):
    """Extract html lang attribute."""
    match = re.search(r'<html[^>]*\slang=["\']([^"\']+)["\']', html, re.IGNORECASE)
    return match.group(1) if match else None

def audit_page(url):
    """Run full SEO audit on a single page."""
    try:
        r = requests.get(url, timeout=15, allow_redirects=True)
        html = r.text
        final_url = r.url

        data = {
            "url": url,
            "final_url": final_url,
            "status_code": r.status_code,
            "redirected": url != final_url,
            "title": extract_title(html),
            "meta_description": extract_meta(html, "name", "description"),
            "canonical": extract_canonical(html),
            "lang": extract_lang(html),
            "h1_count": count_h1(html),
            "robots": extract_meta(html, "name", "robots"),
            "og": {
                "og:title": extract_meta(html, "property", "og:title"),
                "og:description": extract_meta(html, "property", "og:description"),
                "og:url": extract_meta(html, "property", "og:url"),
                "og:image": extract_meta(html, "property", "og:image"),
                "og:type": extract_meta(html, "property", "og:type"),
                "og:site_name": extract_meta(html, "property", "og:site_name"),
                "og:locale": extract_meta(html, "property", "og:locale"),
            },
            "twitter": {
                "twitter:card": extract_meta(html, "name", "twitter:card"),
                "twitter:title": extract_meta(html, "name", "twitter:title"),
                "twitter:description": extract_meta(html, "name", "twitter:description"),
                "twitter:image": extract_meta(html, "name", "twitter:image"),
                "twitter:site": extract_meta(html, "name", "twitter:site"),
            },
        }

        # Validation checks
        if not data["title"]:
            bugs.append({"page": url, "category": "SEO", "severity": "High",
                          "summary": "Missing <title> tag", "detail": "Page has no <title> element."})

        if not data["meta_description"]:
            bugs.append({"page": url, "category": "SEO", "severity": "Medium",
                          "summary": "Missing meta description", "detail": "No <meta name='description'> found."})

        if not data["canonical"]:
            bugs.append({"page": url, "category": "SEO", "severity": "Medium",
                          "summary": "Missing canonical URL", "detail": "No <link rel='canonical'> found."})
        elif data["canonical"] != url and data["canonical"] != final_url:
            # Check if canonical points somewhere unexpected
            bugs.append({"page": url, "category": "SEO", "severity": "Low",
                          "summary": f"Canonical URL mismatch",
                          "detail": f"Page URL: {url}, Canonical: {data['canonical']}, Final URL: {final_url}"})

        if data["h1_count"] == 0:
            bugs.append({"page": url, "category": "SEO", "severity": "Medium",
                          "summary": "Missing <h1> tag", "detail": "Page has no <h1> heading."})
        elif data["h1_count"] > 1:
            bugs.append({"page": url, "category": "SEO", "severity": "Low",
                          "summary": f"Multiple <h1> tags ({data['h1_count']})",
                          "detail": f"SEO best practice is a single <h1> per page."})

        # OG tag checks
        for key, val in data["og"].items():
            if not val and key in ("og:title", "og:description", "og:image", "og:url"):
                bugs.append({"page": url, "category": "SEO", "severity": "Medium",
                              "summary": f"Missing Open Graph tag: {key}",
                              "detail": f"{key} not found in page source."})

        # Twitter card checks
        for key, val in data["twitter"].items():
            if not val and key in ("twitter:card", "twitter:title", "twitter:description"):
                bugs.append({"page": url, "category": "SEO", "severity": "Low",
                              "summary": f"Missing Twitter Card tag: {key}",
                              "detail": f"{key} not found in page source."})

        return data

    except Exception as e:
        bugs.append({"page": url, "category": "SEO", "severity": "High",
                      "summary": f"Page unreachable", "detail": str(e)})
        return {"url": url, "error": str(e)}


def check_duplicates(all_data):
    """Check for duplicate titles, descriptions, canonicals across pages."""
    titles = defaultdict(list)
    descriptions = defaultdict(list)
    canonicals = defaultdict(list)

    for d in all_data:
        if "error" in d:
            continue
        if d["title"]:
            titles[d["title"]].append(d["url"])
        if d["meta_description"]:
            descriptions[d["meta_description"]].append(d["url"])
        if d["canonical"]:
            canonicals[d["canonical"]].append(d["url"])

    for title, urls in titles.items():
        if len(urls) > 1:
            bugs.append({"page": ", ".join(urls), "category": "SEO", "severity": "Medium",
                          "summary": f"Duplicate title: '{title[:60]}...'",
                          "detail": f"Same <title> on {len(urls)} pages: {', '.join(urls)}"})

    for desc, urls in descriptions.items():
        if len(urls) > 1:
            bugs.append({"page": ", ".join(urls), "category": "SEO", "severity": "Medium",
                          "summary": f"Duplicate meta description",
                          "detail": f"Same meta description on {len(urls)} pages: {', '.join(urls)}"})

    for canon, urls in canonicals.items():
        if len(urls) > 1:
            # Multiple URLs pointing to same canonical is expected (e.g., / and /home)
            # Only flag if they're truly different pages
            pass  # Intentionally not flagging — canonical dedup is valid SEO


def main():
    print("=" * 70)
    print("THAURA.AI — SEO / META TAG / OG / TWITTER CARD AUDIT")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    for url in PAGES:
        print(f"\n  Auditing: {url}")
        data = audit_page(url)
        page_data.append(data)

        if "error" in data:
            print(f"    ❌ ERROR: {data['error']}")
            continue

        print(f"    Status: {data['status_code']}")
        if data["redirected"]:
            print(f"    ↳ Redirected to: {data['final_url']}")
        print(f"    Title: {data['title']}")
        print(f"    Description: {(data['meta_description'] or 'MISSING')[:80]}...")
        print(f"    Canonical: {data['canonical']}")
        print(f"    H1 count: {data['h1_count']}")
        print(f"    Lang: {data['lang']}")

        print("    OG Tags:")
        for k, v in data["og"].items():
            icon = "✅" if v else "❌"
            print(f"      {icon} {k}: {(v or 'MISSING')[:60]}")

        print("    Twitter Tags:")
        for k, v in data["twitter"].items():
            icon = "✅" if v else "❌"
            print(f"      {icon} {k}: {(v or 'MISSING')[:60]}")

    # Cross-page duplicate checks
    print("\n" + "-" * 70)
    print("CROSS-PAGE DUPLICATE CHECK")
    print("-" * 70)
    check_duplicates(page_data)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Pages audited: {len(PAGES)}")
    print(f"  Bugs found: {len(bugs)}")

    if bugs:
        print("\n  BUGS:")
        for i, bug in enumerate(bugs, 1):
            print(f"    [{i}] [{bug['severity']}] {bug['summary']}")
            print(f"        Page: {bug['page']}")

    # Save
    output = {
        "audit_date": datetime.now().isoformat(),
        "page_data": page_data,
        "bugs": bugs,
    }
    output_path = "d:/Qtech-Tasks/test-artifacts/meta_tag_audit_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n  Full report saved to: {output_path}")


if __name__ == "__main__":
    main()
