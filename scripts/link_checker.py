"""
Broken Link Checker — Thaura.ai
Task 02, Section 1.1: Verify internal/external links

Crawls all pages and checks for:
- Broken links (404, 5xx)
- Redirect chains
- Mixed content (HTTP links on HTTPS site)
- External links validation
"""

import requests
import re
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
from collections import defaultdict

BASE_URL = "https://thaura.ai"

PAGES = [
    "/",
    "/home",
    "/pricing",
    "/api-platform",
    "/faq",
    "/contact",
    "/story",
    "/constitution",
    "/careers",
]

bugs = []
checked_urls = {}
link_map = defaultdict(list)  # URL -> list of pages that link to it


def extract_links(html, page_url):
    """Extract all href and src links from HTML."""
    links = set()

    # href links
    for match in re.finditer(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE):
        url = match.group(1)
        if url.startswith("#") or url.startswith("javascript:") or url.startswith("mailto:") or url.startswith("tel:"):
            continue
        full_url = urljoin(page_url, url)
        links.add(full_url)

    return links


def check_link(url, source_page):
    """Check if a link is accessible."""
    if url in checked_urls:
        return checked_urls[url]

    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0 ThauraQABot/1.0"})

        # Some servers don't support HEAD, fallback to GET
        if r.status_code == 405:
            r = requests.get(url, timeout=10, allow_redirects=True,
                            headers={"User-Agent": "Mozilla/5.0 ThauraQABot/1.0"},
                            stream=True)

        result = {
            "url": url,
            "status": r.status_code,
            "final_url": r.url,
            "redirected": url != r.url,
        }

        # Check for mixed content
        parsed = urlparse(url)
        if parsed.scheme == "http" and urlparse(source_page).scheme == "https":
            result["mixed_content"] = True
            bugs.append({
                "page": source_page,
                "category": "Security",
                "severity": "Medium",
                "summary": f"Mixed content: HTTP link on HTTPS page",
                "detail": f"Link {url} uses HTTP instead of HTTPS, found on {source_page}",
            })

        # Check for broken links
        if r.status_code >= 400:
            result["broken"] = True
            severity = "High" if r.status_code == 404 else "Medium"
            bugs.append({
                "page": source_page,
                "category": "Functional",
                "severity": severity,
                "summary": f"Broken link: {r.status_code} - {url}",
                "detail": f"Link to {url} returns HTTP {r.status_code}. Found on {source_page}.",
            })

        checked_urls[url] = result
        return result

    except requests.exceptions.Timeout:
        result = {"url": url, "status": "TIMEOUT", "error": "Request timed out"}
        checked_urls[url] = result
        return result
    except requests.exceptions.ConnectionError as e:
        result = {"url": url, "status": "CONNECTION_ERROR", "error": str(e)[:200]}
        checked_urls[url] = result
        return result
    except Exception as e:
        result = {"url": url, "status": "ERROR", "error": str(e)[:200]}
        checked_urls[url] = result
        return result


def main():
    print("=" * 70)
    print("THAURA.AI -- BROKEN LINK CHECKER")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    all_links = {}
    total_links = 0
    broken_count = 0
    mixed_content_count = 0

    for path in PAGES:
        page_url = f"{BASE_URL}{path}"
        print(f"\n  Crawling: {page_url}")

        try:
            r = requests.get(page_url, timeout=15)
            links = extract_links(r.text, page_url)
            print(f"    Found {len(links)} links")

            # Filter to only check internal links + important external links
            internal_links = [l for l in links if urlparse(l).netloc in ("thaura.ai", "www.thaura.ai", "backend.thaura.ai", "")]
            external_links = [l for l in links if urlparse(l).netloc not in ("thaura.ai", "www.thaura.ai", "backend.thaura.ai", "")]

            print(f"    Internal: {len(internal_links)}, External: {len(external_links)}")

            # Check all internal links
            for link in internal_links:
                link_map[link].append(page_url)
                result = check_link(link, page_url)
                total_links += 1
                if result.get("broken"):
                    broken_count += 1
                    print(f"      [BROKEN] {result['status']} - {link}")
                if result.get("mixed_content"):
                    mixed_content_count += 1
                    print(f"      [MIXED] HTTP link: {link}")

            # Check external links (just the first 20 to avoid too many requests)
            checked_external = 0
            for link in external_links[:20]:
                link_map[link].append(page_url)
                result = check_link(link, page_url)
                total_links += 1
                checked_external += 1
                if result.get("broken"):
                    broken_count += 1
                    print(f"      [BROKEN EXT] {result['status']} - {link}")

            all_links[page_url] = {
                "internal": len(internal_links),
                "external": len(external_links),
                "checked_external": checked_external,
            }

        except Exception as e:
            print(f"    ERROR: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Pages crawled: {len(PAGES)}")
    print(f"  Total links checked: {total_links}")
    print(f"  Unique URLs checked: {len(checked_urls)}")
    print(f"  Broken links: {broken_count}")
    print(f"  Mixed content: {mixed_content_count}")
    print(f"  Bugs found: {len(bugs)}")

    if bugs:
        print("\n  BUGS:")
        for i, bug in enumerate(bugs, 1):
            print(f"    [{i}] [{bug['severity']}] {bug['summary']}")

    # Print all broken URLs
    broken_urls = {url: data for url, data in checked_urls.items()
                   if isinstance(data.get("status"), int) and data["status"] >= 400}
    if broken_urls:
        print(f"\n  BROKEN URLs ({len(broken_urls)}):")
        for url, data in broken_urls.items():
            pages = link_map.get(url, ["unknown"])
            print(f"    {data['status']} - {url}")
            print(f"          Found on: {', '.join(pages[:3])}")

    # Save
    output = {
        "audit_date": datetime.now().isoformat(),
        "pages_crawled": len(PAGES),
        "total_links_checked": total_links,
        "unique_urls": len(checked_urls),
        "broken_count": broken_count,
        "mixed_content_count": mixed_content_count,
        "bugs": bugs,
        "all_results": {url: data for url, data in checked_urls.items()},
    }
    output_path = "d:/Qtech-Tasks/test-artifacts/broken_links_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n  Full report saved to: {output_path}")


if __name__ == "__main__":
    main()
