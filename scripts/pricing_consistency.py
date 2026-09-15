"""
Pricing Consistency & Math Verification — Thaura.ai
Task 02, Section 1.3: Pricing toggle verification + cross-page consistency

Checks:
- Monthly vs Annual pricing math ($12/month vs annual with "Save 20%")
- Cross-page pricing figure consistency (Pricing, FAQ, Home, API)
- Factual claim consistency (parameter counts, energy figures, language counts)
"""

import requests
import re
import json
from datetime import datetime

PAGES_TO_CHECK = {
    "pricing": "https://thaura.ai/pricing",
    "faq": "https://thaura.ai/faq",
    "home": "https://thaura.ai/",
    "home_alt": "https://thaura.ai/home",
    "api": "https://thaura.ai/api-platform",
    "story": "https://thaura.ai/story",
    "constitution": "https://thaura.ai/constitution",
}

bugs = []
findings = {}


def fetch_page(url):
    """Fetch page source."""
    try:
        r = requests.get(url, timeout=15, allow_redirects=True)
        return r.text
    except Exception as e:
        return None


def extract_prices(html):
    """Extract all price mentions from HTML."""
    # Match patterns like $12, $12/month, $144/year, $9.60, etc.
    prices = re.findall(r'\$[\d,.]+(?:/(?:month|mo|year|yr))?', html, re.IGNORECASE)
    # Also match patterns like "12€", "12 USD", etc.
    prices += re.findall(r'[\d,.]+\s*(?:USD|EUR|€)', html, re.IGNORECASE)
    return prices


def extract_percentages(html):
    """Extract percentage mentions like 'Save 20%'."""
    return re.findall(r'(?:save|discount|off)\s*(\d+)%', html, re.IGNORECASE)


def extract_claims(html):
    """Extract factual/technical claims for consistency checking."""
    claims = {}

    # Parameter counts (e.g., "7B parameters", "70B parameters")
    param_matches = re.findall(r'(\d+\.?\d*)\s*(?:B|billion|M|million)\s*param(?:eter)?s?', html, re.IGNORECASE)
    if param_matches:
        claims["parameter_counts"] = param_matches

    # Language support counts
    lang_matches = re.findall(r'(\d+)\+?\s*languages?', html, re.IGNORECASE)
    if lang_matches:
        claims["language_count"] = lang_matches

    # Energy/token figures
    energy_matches = re.findall(r'([\d.]+)\s*(?:Wh|kWh|J|joules?)\s*(?:per|/)\s*(?:token|request|query)', html, re.IGNORECASE)
    if energy_matches:
        claims["energy_per_token"] = energy_matches

    # Encryption mentions
    encryption_matches = re.findall(r'(AES-\d+|TLS\s*[\d.]+|RSA-\d+|end-to-end\s*encrypt)', html, re.IGNORECASE)
    if encryption_matches:
        claims["encryption"] = encryption_matches

    # GDPR / data residency
    gdpr_matches = re.findall(r'(GDPR|data\s*residen(?:cy|t)|EU\s*(?:data|server|hosted))', html, re.IGNORECASE)
    if gdpr_matches:
        claims["gdpr_data_residency"] = gdpr_matches

    # Message/rate limits
    limit_matches = re.findall(r'(\d+)\s*messages?\s*(?:per|/|every)\s*(\d+)\s*(hour|minute|day)', html, re.IGNORECASE)
    if limit_matches:
        claims["rate_limits"] = [f"{m[0]} per {m[1]} {m[2]}" for m in limit_matches]

    return claims


def verify_pricing_math():
    """Verify the Monthly/Annual pricing toggle math."""
    print("\n[1] PRICING MATH VERIFICATION")
    print("-" * 50)

    html = fetch_page(PAGES_TO_CHECK["pricing"])
    if not html:
        print("  ❌ Could not fetch pricing page")
        return

    prices = extract_prices(html)
    percentages = extract_percentages(html)

    print(f"  Prices found on pricing page: {prices}")
    print(f"  Discount percentages found: {percentages}")

    # Expected: $12/month, $X/year (with "Save 20%")
    monthly = None
    annual = None

    for p in prices:
        clean = p.replace("$", "").replace(",", "")
        if "/month" in p.lower() or "/mo" in p.lower():
            try:
                monthly = float(re.search(r'[\d.]+', clean).group())
            except:
                pass
        elif "/year" in p.lower() or "/yr" in p.lower():
            try:
                annual = float(re.search(r'[\d.]+', clean).group())
            except:
                pass

    if monthly:
        print(f"\n  Monthly price: ${monthly}")
        expected_annual_no_discount = monthly * 12
        print(f"  Expected annual (no discount): ${expected_annual_no_discount}")

        if annual:
            print(f"  Stated annual price: ${annual}")
            actual_discount = ((expected_annual_no_discount - annual) / expected_annual_no_discount) * 100
            print(f"  Actual discount: {actual_discount:.1f}%")

            if percentages:
                stated_discount = int(percentages[0])
                print(f"  Stated discount: {stated_discount}%")

                if abs(actual_discount - stated_discount) > 0.5:
                    msg = (f"Pricing math inconsistency: ${monthly}/month × 12 = ${expected_annual_no_discount}/year. "
                           f"Stated annual = ${annual} (actual discount = {actual_discount:.1f}%), "
                           f"but site claims 'Save {stated_discount}%'.")
                    bugs.append({
                        "page": PAGES_TO_CHECK["pricing"],
                        "category": "Data Correctness",
                        "severity": "High",
                        "summary": "Pricing math inconsistency — discount percentage is incorrect",
                        "detail": msg,
                    })
                    print(f"  ❌ BUG: {msg}")
                else:
                    print(f"  ✅ Discount math is consistent")
            else:
                # If annual equals monthly*12, there's no actual discount
                if annual == expected_annual_no_discount:
                    msg = f"Annual price ${annual} equals ${monthly}×12 — no actual discount, but might claim savings"
                    bugs.append({
                        "page": PAGES_TO_CHECK["pricing"],
                        "category": "Data Correctness",
                        "severity": "High",
                        "summary": "Annual price shows no actual discount over monthly",
                        "detail": msg,
                    })
                    print(f"  ❌ BUG: {msg}")
        else:
            print(f"  ⚠️ No annual price found — may be in JS-toggled content")
    else:
        print(f"  ⚠️ No monthly price pattern found — may be dynamically rendered")


def cross_page_pricing_check():
    """Check pricing consistency across all pages."""
    print("\n[2] CROSS-PAGE PRICING CONSISTENCY")
    print("-" * 50)

    all_prices = {}
    for name, url in PAGES_TO_CHECK.items():
        html = fetch_page(url)
        if html:
            prices = extract_prices(html)
            if prices:
                all_prices[name] = {"url": url, "prices": prices}
                print(f"  {name}: {prices}")

    if not all_prices:
        print("  ⚠️ No prices found on any page")
        return

    # Compare price lists for inconsistencies
    price_sets = {}
    for name, data in all_prices.items():
        for price in data["prices"]:
            if price not in price_sets:
                price_sets[price] = []
            price_sets[price].append(name)

    findings["cross_page_prices"] = all_prices
    print(f"\n  Unique price strings found: {list(price_sets.keys())}")


def factual_consistency_check():
    """Check factual/technical claim consistency across pages."""
    print("\n[3] FACTUAL CLAIM CONSISTENCY")
    print("-" * 50)

    all_claims = {}
    for name, url in PAGES_TO_CHECK.items():
        html = fetch_page(url)
        if html:
            claims = extract_claims(html)
            if claims:
                all_claims[name] = {"url": url, "claims": claims}

    for name, data in all_claims.items():
        print(f"\n  {name}:")
        for claim_type, values in data["claims"].items():
            print(f"    {claim_type}: {values}")

    # Cross-check specific claims
    claim_types = set()
    for data in all_claims.values():
        claim_types.update(data["claims"].keys())

    for claim_type in claim_types:
        values_by_page = {}
        for name, data in all_claims.items():
            if claim_type in data["claims"]:
                values_by_page[name] = data["claims"][claim_type]

        if len(values_by_page) > 1:
            # Compare values across pages
            unique_values = set()
            for vals in values_by_page.values():
                unique_values.update(str(v) for v in vals)

            if len(unique_values) > 1:
                msg = f"Inconsistent '{claim_type}' across pages: "
                for name, vals in values_by_page.items():
                    msg += f"{name}={vals}, "
                bugs.append({
                    "page": "Cross-page",
                    "category": "Data Correctness",
                    "severity": "Medium",
                    "summary": f"Inconsistent factual claim: {claim_type}",
                    "detail": msg,
                })
                print(f"\n  ❌ BUG: {msg}")

    findings["factual_claims"] = all_claims


def main():
    print("=" * 70)
    print("THAURA.AI — PRICING & FACTUAL CONSISTENCY AUDIT")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    verify_pricing_math()
    cross_page_pricing_check()
    factual_consistency_check()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Bugs found: {len(bugs)}")
    if bugs:
        for i, bug in enumerate(bugs, 1):
            print(f"    [{i}] [{bug['severity']}] {bug['summary']}")

    output = {
        "audit_date": datetime.now().isoformat(),
        "findings": {k: str(v) for k, v in findings.items()},
        "bugs": bugs,
    }
    output_path = "d:/Qtech-Tasks/test-artifacts/pricing_consistency_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n  Full report saved to: {output_path}")


if __name__ == "__main__":
    main()
