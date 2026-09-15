# Task 02 — Thaura.ai Website Technical Testing — Test Report

**Tester:** SQA Engineering Team  
**Date:** 2026-09-15  
**Environment:** Windows 11 (64-bit), Google Chrome 128 / 152  
**Website URL:** https://thaura.ai/  
**Tools Used:** Python test scripts (`requests`), Google Lighthouse 13.4.1, Node `autocannon` (load testing), Chrome DevTools

---

## Executive Summary

Task 02 comprised rigorous functional verification, link checking, contact form validation, pricing consistency audits, SEO/meta-tag inspection, client performance auditing (Core Web Vitals), backend load testing, and security header evaluations across all public routes of **thaura.ai**.

* **Automated Scripts Executed:** 6 test runners (Links, Meta tags, Pricing, Security Headers, Lighthouse, Load test)
* **Manual Tests Executed:** 15 test cases (Forms, Pricing Toggle, Console Exceptions, Cookie Inspection, Input Sanitization)
* **Total Defects / Findings Logged:** 24 issues categorized in `Bug_Report.xlsx`
* **Performance Summary:** Strong desktop Lighthouse performance (Desktop Performance: 99 on `/pricing`, 91 on `/`, 88 on `/faq`). Homepage LCP requires improvement (~3.1s).
* **Load Test Baseline:** 54.4 req/sec sustained with 0 non-2xx responses and 106ms average latency under 10 concurrent connections.

---

## 1. Functional & Data Correctness Testing

### 1.1 Link Verification (Automated)

**Tool:** [`scripts/link_checker.py`](file:///d:/Qtech-Tasks/scripts/link_checker.py)  
**Artifact:** [`test-artifacts/broken_links_report.json`](file:///d:/Qtech-Tasks/test-artifacts/broken_links_report.json)

| Metric | Result | SQA Assessment |
|--------|--------|----------------|
| Pages crawled | 9 routes | Complete public navigation crawl |
| Total links checked | 282 links | Full DOM anchor and `<link>` scan |
| Unique URLs checked | 42 unique targets | Internal & external URLs |
| Broken links | 2 unique (18 occurrences) | Preconnect tags returning 401/404 |
| Mixed content (HTTP on HTTPS) | 0 instances | ✅ Fully secure HTTPS asset delivery |

**404 Pages Discovered (P1 Functional Bugs):**

| URL | HTTP Status | Impact | Bug ID |
|-----|-------------|--------|--------|
| `https://thaura.ai/apps` | 404 Not Found | Broken navigation to app downloads | BUG-015 |
| `https://thaura.ai/privacy` | 404 Not Found | Missing Privacy Policy (Critical GDPR compliance violation) | BUG-016 |
| `https://thaura.ai/terms` | 404 Not Found | Missing Terms of Service | BUG-017 |

---

### 1.2 Contact Form Testing (Manual)

| Test Case | Test Steps & Input | Expected Result | Actual Result | Status |
|-----------|--------------------|-----------------|---------------|--------|
| **TC-W01: Empty Submission** | Click "Submit" with all fields blank | Validation errors on required inputs | Required fields are Name, Email, and Message. Browser highlights empty field: *"Please fill out this field."* | ✅ **PASS** |
| **TC-W02: Missing Email** | Fill Name and Message; leave Email blank | Email required validation triggers | Submission blocked; focus set to Email input with *"Please fill out this field."* | ✅ **PASS** |
| **TC-W03: Invalid Email Format** | Enter `notanemail` in email field | Email format validation error | Browser validation triggers: *"Please include an '@' in the email address. 'notanemail' is missing an '@'."* | ✅ **PASS** |
| **TC-W04: Very Long Message** | Input 5,000+ characters in Message field | Handled without UI or layout freeze | Form accepts long message without clipping or overflowing layout. | ✅ **PASS** |
| **TC-W05: Valid Submission** | Submit valid Name, Email, and Message | Success notification / toast displayed | Success banner displayed: *"Message sent successfully! We'll get back to you soon."* | ✅ **PASS** |
| **TC-W06: Script / XSS Input** | Enter `<script>alert('xss')</script>` | Sanitized as plain text; no script run | Text treated literally and submitted without script injection or DOM execution. | ✅ **PASS** |
| **TC-W07: Unicode / RTL Text** | Enter Arabic / multilingual text | Rendered with correct typography | Arabic script rendered correctly without alignment or layout distortion. | ✅ **PASS** |

---

### 1.3 Pricing Consistency (Automated + Live Manual Toggle)

**Tool:** [`scripts/pricing_consistency.py`](file:///d:/Qtech-Tasks/scripts/pricing_consistency.py)  
**Report:** [`test-artifacts/pricing_consistency_report.json`](file:///d:/Qtech-Tasks/test-artifacts/pricing_consistency_report.json)

#### Live Interactive Pricing Toggle Verification

| Toggle State | Displayed Pro Price | Billed Subtext | Math Check | SQA Analysis |
|--------------|---------------------|----------------|------------|--------------|
| **Monthly** | **$15/month** | Standard monthly billing | $15 × 12 = $180/year | Matches the Pro price stated on `/faq` ($15/mo). |
| **Annually** | **$12/month** | "Billed $144/year" | $12 × 12 = $144/year | Exactly 20% discount on $180 ($180 × 0.80 = $144). |

#### Critical Finding (BUG-020 & BUG-021 Resolution):
1. **Interactive Client UI:** The pricing math is mathematically valid ($15/mo base vs $12/mo annual billed at $144/yr).
2. **SSR / Static Crawler Bug:** In initial SSR HTML, only `$12` and `$144/year` were visible without the `$15` base monthly context, causing static crawlers and search engine snippets to see an apparent math inconsistency ($12 × 12 = $144 with "Save 20%").
3. **Cross-Page Consistency:** The `/faq` page explicitly mentions `$15/month`, which aligns with the active Monthly toggle state.

---

### 1.4 SEO & Meta Tag Audit (Automated)

**Tool:** [`scripts/meta_tag_audit.py`](file:///d:/Qtech-Tasks/scripts/meta_tag_audit.py)  
**Report:** [`test-artifacts/meta_tag_audit_report.json`](file:///d:/Qtech-Tasks/test-artifacts/meta_tag_audit_report.json)

| Page Route | Title Tag | Meta Description | Canonical URL | H1 Heading | OpenGraph / Twitter | Overall Status |
|------------|-----------|------------------|---------------|------------|---------------------|----------------|
| **`/` (Home)** | ✅ Present | ✅ Present | ⚠️ Points to `/home` | ❌ **0 H1 Tags** | ✅ Complete | Issues Found |
| **`/home`** | ✅ Present | ✅ Present | ✅ Valid | ✅ 1 H1 Tag | ✅ Complete | ✅ Clean |
| **`/pricing`** | ✅ Present | ✅ Present | ✅ Valid | ✅ 1 H1 Tag | ✅ Complete | ✅ Clean |
| **`/api-platform`** | ✅ Present | ✅ Present | ✅ Valid | ✅ 1 H1 Tag | ✅ Complete | ✅ Clean |
| **`/faq`** | ✅ Present | ✅ Present | ✅ Valid | ✅ 1 H1 Tag | ✅ Complete | ✅ Clean |
| **`/contact`** | ✅ Present | ✅ Present | ✅ Valid | ✅ 1 H1 Tag | ✅ Complete | ✅ Clean |
| **`/story`** | ✅ Present | ✅ Present | ✅ Valid | ✅ 1 H1 Tag | ✅ Complete | ✅ Clean |
| **`/constitution`** | ✅ Present | ✅ Present | ✅ Valid | ✅ 1 H1 Tag | ✅ Complete | ✅ Clean |
| **`/careers`** | ✅ Present | ✅ Present | ✅ Valid | ✅ 1 H1 Tag | ✅ Complete | ✅ Clean |
| **`/apps`** | ❌ Generic 404 | ❌ Missing | ❌ Missing | ❌ 0 H1 Tags | ⚠️ Generic | ❌ Broken Route |
| **`/privacy`** | ❌ Generic 404 | ❌ Missing | ❌ Missing | ❌ 0 H1 Tags | ⚠️ Generic | ❌ Broken Route |
| **`/terms`** | ❌ Generic 404 | ❌ Missing | ❌ Missing | ❌ 0 H1 Tags | ⚠️ Generic | ❌ Broken Route |

---

## 2. Performance & Reliability Testing

### 2.1 Lighthouse Core Web Vitals Audits

| Page | Performance Score | Accessibility | Best Practices | SEO | LCP (s) | CLS |
|------|-------------------|---------------|----------------|-----|---------|-----|
| **Homepage (`/`)** | **91 / 100** | **95** | **96** | **92** | 3.1s ⚠️ | 0.00 ✅ |
| **Pricing (`/pricing`)** | **99 / 100** | **95** | **96** | **92** | 1.3s ✅ | 0.00 ✅ |
| **FAQ (`/faq`)** | **88 / 100** | **92** | **96** | **92** | 3.2s ⚠️ | 0.00 ✅ |
| **API Platform (`/api-platform`)** | **96 / 100** | **95** | **96** | **92** | 2.1s ✅ | 0.00 ✅ |

### 2.2 Console Runtime Errors (BUG-024)
During homepage loading and performance metrics reporting in Chrome DevTools:
```text
VM382:2 Uncaught TypeError: Cannot read properties of undefined (reading 'startTime')
    at et.reportAllChanges (<anonymous>:2:19429)
    at <anonymous>:2:13070
    at <anonymous>:2:331
    at d (<anonymous>:2:6141)
    at <anonymous>:2:6326
    at <anonymous>:2:2895
    at n.timeout (<anonymous>:2:5652)
```
* **Severity:** Medium (P2)
* **Root Cause:** Web Vitals / performance telemetry script attempts to read `startTime` from an undefined performance entry object.

### 2.3 Load Testing (Autocannon)
* **Configuration:** 10 concurrent connections, 10-second duration, 2 pipelined requests
* **Target:** `https://thaura.ai/`
* **Throughput:** 54.40 requests/sec | 544 total requests in 10.05s
* **Data Transfer:** 4.79 MB
* **Latency Profile:**
  - 50th percentile (Median): 91 ms
  - 97.5th percentile: 211 ms
  - 99th percentile: 235 ms
  - Max Latency: 257 ms
* **Error Rate:** **0%** (0 non-2xx responses, 0 socket timeouts)

---

## 3. Security Testing

### 3.1 Security Headers Audit (Automated)

**Tool:** [`scripts/security_header_check.py`](file:///d:/Qtech-Tasks/scripts/security_header_check.py)  
**Report:** [`test-artifacts/security_headers_report.json`](file:///d:/Qtech-Tasks/test-artifacts/security_headers_report.json)

| Header Name | Required Standard | Observed Configuration | Compliance |
|-------------|-------------------|------------------------|------------|
| **Strict-Transport-Security** | `max-age=31536000; includeSubDomains` | `max-age=31536000; includeSubDomains` | ✅ PASS |
| **X-Content-Type-Options** | `nosniff` | `nosniff` | ✅ PASS |
| **X-Frame-Options** | `DENY` | `DENY` | ✅ PASS |
| **Content-Security-Policy** | Restrictive script/style origins | Configured across all pages | ✅ PASS |
| **Referrer-Policy** | `strict-origin-when-cross-origin` | Present | ✅ PASS |
| **Permissions-Policy** | Hardware restrictions | `microphone=(self), camera=(), geolocation=()` | ✅ PASS |

### 3.2 Session Cookie Security Inspection

| Cookie Name | Scope / Domain | Flags Configured | Security Assessment |
|-------------|----------------|------------------|---------------------|
| **`thaura_token`** | `.thaura.ai` / Same-Site | `HttpOnly=True`, `Secure=True`, `SameSite=Lax` | ✅ **PASS:** JavaScript cannot read token; protected against XSS theft and cross-site request forgery. |

---

## Final Assessment & Recommendations

1. **Restore Critical 404 Pages:** Deploy live pages for `/privacy`, `/terms`, and `/apps`. Missing `/privacy` is a legal risk for GDPR marketing claims.
2. **Resolve Console Exception:** Fix null-check on performance entry `startTime` inside `et.reportAllChanges`.
3. **Deduplicate Reverse Proxy Headers:** Remove redundant `add_header` directives in Nginx configuration to avoid duplicate HSTS and X-Frame-Options in API responses.
4. **Optimize Homepage LCP:** Reduce 3.1s LCP on root `/` by preloading hero assets and fixing canonical mismatch with `/home`.
