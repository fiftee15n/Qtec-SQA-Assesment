"""
Security Header & Cookie Audit — Thaura.ai
Task 02, Section 3: Security Testing (Non-Intrusive)

Checks:
- HTTPS enforcement (HTTP→HTTPS redirect)
- Security headers: CSP, X-Frame-Options, HSTS, X-Content-Type-Options
- Cookie attributes: Secure, HttpOnly, SameSite
- Mixed-content indicators
"""

import requests
import json
import sys
from datetime import datetime

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

REQUIRED_HEADERS = {
    "Strict-Transport-Security": "HSTS — enforces HTTPS",
    "X-Content-Type-Options": "Prevents MIME-type sniffing",
    "X-Frame-Options": "Prevents clickjacking",
    "Content-Security-Policy": "Controls resource loading",
}

RECOMMENDED_HEADERS = {
    "Referrer-Policy": "Controls referrer info leakage",
    "Permissions-Policy": "Controls browser feature access",
    "X-XSS-Protection": "Legacy XSS filter (deprecated but still checked)",
    "Cross-Origin-Opener-Policy": "Cross-origin isolation",
    "Cross-Origin-Resource-Policy": "Cross-origin resource control",
}

COOKIE_FLAGS = ["Secure", "HttpOnly", "SameSite"]

results = []
bugs = []

def check_https_redirect(url):
    """Check if HTTP automatically redirects to HTTPS."""
    http_url = url.replace("https://", "http://")
    try:
        r = requests.get(http_url, allow_redirects=False, timeout=10)
        if r.status_code in (301, 302, 307, 308):
            location = r.headers.get("Location", "")
            if location.startswith("https://"):
                return {"status": "PASS", "detail": f"{r.status_code} → {location}"}
            else:
                return {"status": "FAIL", "detail": f"Redirects to non-HTTPS: {location}"}
        else:
            return {"status": "FAIL", "detail": f"No redirect, status {r.status_code}"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}

def check_headers(url):
    """Check security headers for a given URL."""
    try:
        r = requests.get(url, timeout=15, allow_redirects=True)
        headers = r.headers
        result = {
            "url": url,
            "status_code": r.status_code,
            "required_headers": {},
            "recommended_headers": {},
            "cookies": [],
        }

        # Check required security headers
        for header, desc in REQUIRED_HEADERS.items():
            value = headers.get(header, None)
            if value:
                result["required_headers"][header] = {
                    "status": "PRESENT",
                    "value": value,
                    "description": desc,
                }
            else:
                result["required_headers"][header] = {
                    "status": "MISSING",
                    "value": None,
                    "description": desc,
                }
                bugs.append({
                    "page": url,
                    "category": "Security",
                    "severity": "Medium" if header != "Content-Security-Policy" else "High",
                    "summary": f"Missing security header: {header}",
                    "detail": f"{header} ({desc}) is not set in response headers.",
                })

        # Check recommended headers
        for header, desc in RECOMMENDED_HEADERS.items():
            value = headers.get(header, None)
            result["recommended_headers"][header] = {
                "status": "PRESENT" if value else "MISSING",
                "value": value,
                "description": desc,
            }

        # Check cookies
        if r.cookies:
            for cookie in r.cookies:
                cookie_info = {
                    "name": cookie.name,
                    "domain": cookie.domain,
                    "secure": cookie.secure,
                    "httponly": "HttpOnly" in (cookie._rest if hasattr(cookie, '_rest') else {}),
                    "samesite": None,
                    "path": cookie.path,
                }
                # Check for SameSite in the Set-Cookie header
                for set_cookie in r.headers.get("Set-Cookie", "").split(","):
                    if cookie.name in set_cookie:
                        if "SameSite=Strict" in set_cookie:
                            cookie_info["samesite"] = "Strict"
                        elif "SameSite=Lax" in set_cookie:
                            cookie_info["samesite"] = "Lax"
                        elif "SameSite=None" in set_cookie:
                            cookie_info["samesite"] = "None"

                        if "HttpOnly" in set_cookie:
                            cookie_info["httponly"] = True

                result["cookies"].append(cookie_info)

                # Flag missing cookie attributes
                if not cookie.secure:
                    bugs.append({
                        "page": url,
                        "category": "Security",
                        "severity": "High",
                        "summary": f"Cookie '{cookie.name}' missing Secure flag",
                        "detail": f"Cookie set without Secure attribute — can be sent over HTTP.",
                    })
                if not cookie_info["httponly"]:
                    bugs.append({
                        "page": url,
                        "category": "Security",
                        "severity": "Medium",
                        "summary": f"Cookie '{cookie.name}' missing HttpOnly flag",
                        "detail": f"Cookie accessible via JavaScript — XSS risk.",
                    })

        # Also check Set-Cookie in raw headers for cookies not parsed by requests
        set_cookie_headers = []
        for key, value in r.headers.items():
            if key.lower() == "set-cookie":
                set_cookie_headers.append(value)

        if set_cookie_headers:
            result["raw_set_cookie"] = set_cookie_headers

        return result

    except Exception as e:
        return {"url": url, "error": str(e)}


def main():
    print("=" * 70)
    print("THAURA.AI — SECURITY HEADER & COOKIE AUDIT")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 1. HTTPS redirect check
    print("\n[1] HTTPS REDIRECT CHECK")
    print("-" * 40)
    redirect_result = check_https_redirect("https://thaura.ai/")
    print(f"  HTTP→HTTPS redirect: {redirect_result['status']} — {redirect_result['detail']}")
    if redirect_result["status"] != "PASS":
        bugs.append({
            "page": "http://thaura.ai/",
            "category": "Security",
            "severity": "Critical",
            "summary": "HTTP does not redirect to HTTPS",
            "detail": redirect_result["detail"],
        })

    # 2. Security headers per page
    print("\n[2] SECURITY HEADERS PER PAGE")
    print("-" * 40)
    for url in PAGES:
        print(f"\n  Checking: {url}")
        result = check_headers(url)
        results.append(result)

        if "error" in result:
            print(f"    ❌ ERROR: {result['error']}")
            continue

        print(f"    Status: {result['status_code']}")

        print("    Required Headers:")
        for header, info in result["required_headers"].items():
            status_icon = "✅" if info["status"] == "PRESENT" else "❌"
            value_display = f" = {info['value'][:80]}..." if info["value"] and len(info["value"]) > 80 else (f" = {info['value']}" if info["value"] else "")
            print(f"      {status_icon} {header}{value_display}")

        print("    Recommended Headers:")
        for header, info in result["recommended_headers"].items():
            status_icon = "✅" if info["status"] == "PRESENT" else "⚠️"
            print(f"      {status_icon} {header}: {info['status']}")

        if result["cookies"]:
            print("    Cookies:")
            for c in result["cookies"]:
                flags = []
                if c["secure"]: flags.append("Secure")
                if c["httponly"]: flags.append("HttpOnly")
                if c["samesite"]: flags.append(f"SameSite={c['samesite']}")
                print(f"      🍪 {c['name']} [{', '.join(flags) if flags else 'NO FLAGS'}]")
        else:
            print("    Cookies: None set")

    # 3. Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    total_missing = 0
    for r in results:
        if "error" not in r:
            missing = sum(1 for h in r["required_headers"].values() if h["status"] == "MISSING")
            total_missing += missing

    print(f"  Pages checked: {len(PAGES)}")
    print(f"  Total missing required headers: {total_missing}")
    print(f"  Bugs found: {len(bugs)}")

    if bugs:
        print("\n  BUGS:")
        for i, bug in enumerate(bugs, 1):
            print(f"    [{i}] [{bug['severity']}] {bug['summary']}")
            print(f"        Page: {bug['page']}")
            print(f"        Detail: {bug['detail']}")

    # Save results to JSON
    output = {
        "audit_date": datetime.now().isoformat(),
        "results": results,
        "bugs": bugs,
    }
    output_path = "d:/Qtech-Tasks/test-artifacts/security_headers_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n  Full report saved to: {output_path}")


if __name__ == "__main__":
    main()
