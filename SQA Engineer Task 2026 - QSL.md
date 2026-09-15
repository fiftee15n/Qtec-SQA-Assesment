**SQA Hiring Assessment**

## **Task 01:  Comprehensive Technical Testing of the Thaura Web App (Chat Product)**

**Web Short Description:**

Thaura's core product is a web-based AI chat application offering text and voice conversation, file/document/image upload and analysis, live code execution and artifacts (charts, dashboards, diagrams), persistent cross-conversation memory, an Incognito Mode, and grouped "Projects" workspaces. Access is tier-based: a rate-limited Free plan and an unlimited Pro subscription, alongside a separately-billed developer API.

**Objective:**

Perform technical-focused functional, data-integrity, security, and performance testing of the Thaura Web App.

**App URL:** [https://thaura.ai/](https://thaura.ai/) (chat entry point via "Talk to Thaura")

**User:** No admin credentials provided — create a new Free-tier account using a test email during execution, and record the credentials used in the test report for reproducibility.

**Details:**

1\.    Sign up / log in using a newly created test account; verify session handling (token expiry, logout invalidation, concurrent-session behavior).

2\.    Test the Free-tier message limit (5 messages / 2 hours) at the logic level:

1\.    Confirm exact enforcement at message \#5 and \#6.

2\.    Determine whether the 2-hour window is rolling or fixed, and verify reset behavior.

3\.    Test whether a failed/errored assistant response still consumes a quota slot.

4\.    Test whether the limit can be bypassed (multiple tabs, session refresh, direct API calls with a Free-tier-linked key).

3\.    Test file/document upload at a data-integrity level:

1\.    Upload PDF, spreadsheet, and image files; verify the extracted/parsed content is accurate, not just that a response is returned.

2\.    Test corrupted, password-protected, empty, and oversized files; verify correct error handling (proper status/message, no silent failure).

3\.    Verify uploaded content does not leak across unrelated sessions/accounts (data isolation).

4\.    Test Memory persistence vs. Incognito Mode:

1\.    Confirm a fact/preference stored in normal mode is retrievable in a new, unrelated chat.

2\.    Confirm Incognito Mode chats do not persist to history and do not leak into the memory system.

3\.    Note explicitly which claims (e.g., full server-side deletion) cannot be verified from the client side alone.

5\.    Test the Developer API (POST /v1/chat/completions) against its documented contract at thaura.ai/api-platform:

1\.    Required vs. optional parameter validation; invalid data types; boundary values (temperature range, max\_completion\_tokens cap of 32000).

2\.    Precedence rule between max\_tokens and max\_completion\_tokens.

3\.    Parameters documented as "accepted but ignored" vs. parameters that should be rejected (functions, function\_call).

4\.    Authentication/authorization: missing, malformed, invalid, and zero-balance API keys (expect 401/402 as documented).

5\.    Rate limiting: 60 requests/minute and 8 concurrent requests per key — confirm 429 behavior.

6\.    Response schema validation for streaming and non-streaming calls, including usage-token accounting.

7\.    Note: this is a real, metered, billed API — keep all test calls to minimal token usage.

6\.    Negative/boundary testing across all forms and inputs: blank submissions, invalid email/password formats, max-length field overflow, invalid file types, and any other input field exposed in Settings/Account/Billing.

## **Task 02: Thaura.ai Website Technical Testing**

**Website short description:**

Thaura is an "ethical AI companion" website and product — a ChatGPT-style conversational AI platform positioned around privacy, no ad-tracking, and EU data residency. The public site showcases the product's story/mission, a public "Constitution" (ethics commitments), pricing plans (Free vs. Pro), a developer API platform, download/app pages, an FAQ, careers, and contact/community pages, alongside marketing content about its efficiency and sustainability claims.

**Objective:**

Perform technical-focused testing of https://thaura.ai/ covering functional correctness at a logic/data level, performance, security, and cross-browser/device technical compatibility. Prepare a detailed bug report.

**Tasks:**

**1\. Functional & Data Correctness Testing**

1\.    Verify every internal/external link resolves to the correct destination with the correct HTTP status (no 404s, no broken redirects, no mixed-content/HTTP links on an HTTPS site).

2\.    Validate the Contact form: required-field enforcement, input validation (email format, field length limits), correct success/error response codes, and confirm submitted data is actually received (not silently dropped).

3\.    Test the Pricing page's Monthly/Annual toggle for correct underlying calculation (confirm $12/month vs. "$144/year, Save 20%" is mathematically consistent) and cross-check pricing figures against every other page that mentions price (e.g., FAQ) for data consistency.

4\.    Verify canonical URLs, meta tags, and Open Graph/Twitter card data are correct and non-duplicated across pages (check via view-source, not visual inspection).

5\.    Verify all stated factual/technical claims are internally consistent across pages (parameter counts, energy-per-token figures, language-support counts, encryption standard references, GDPR/data-residency claims).

**2\. Performance Testing**

1\.    Run Lighthouse (or equivalent) audits on key pages (Home, Pricing, API, FAQ) — capture Performance, Best Practices, and SEO scores plus Core Web Vitals (LCP, CLS, INP/FID, TTFB).

2\.    Load-test key pages using JMeter or similar to check response time and stability under concurrent load.

3\.    Validate image/video optimization: correct formats (WebP/AVIF where applicable), appropriate compression, and lazy-loading behavior for below-the-fold assets (hero image, analyzing.mp4, illustrations).

4\.    Measure and report total page weight and number of network requests per page; flag unusually large payloads or unoptimized third-party scripts.

5\.    Monitor and log all JavaScript console errors/warnings and failed network requests (4xx/5xx) across every page in DevTools.

**3\. Security Testing (Basic, Non-Intrusive)**

1\.    Confirm HTTPS is enforced site-wide with no mixed-content warnings.

2\.    Check response headers for standard security headers (Content-Security-Policy, X-Frame-Options, Strict-Transport-Security, X-Content-Type-Options).

3\.    Verify the Contact form and any other public input fields handle unusual/special-character input (long strings, script-like input, unicode/RTL text) without server errors or reflected/unsanitized output.

4\.    Check that no sensitive information (API keys, internal endpoints, stack traces) is exposed in page source, console logs, or network responses.

5\.    Verify cookie attributes (Secure, HttpOnly, SameSite) on any cookies set by the site.

## **Task 03: AI & Testing — Reflection Questions**

Please answer the following questions in your own words as part of your submission. There are no "correct" answers — we are interested in your genuine perspective and how you actually work.

1\.    In your opinion, how do you think AI will impact software testing over the next 2–3 years?

2\.    Do you personally use AI? Does AI help you in testing? If yes, in what specific ways does it help?

3\.    Which AI tools do you currently use (for testing or otherwise)?

4\.    Which AI tool do you currently find most helpful for testing specifically, and why do you think that is?

***Note:** We know you will most likely use AI to help answer these questions and complete the tasks in this assessment — and that's fine, we appreciate it. We also know that the vast majority of candidates will use AI for both the questions and the practical tasks. What we're actually evaluating in this section is the quality of your thinking, not just the answer itself — and how comfortably and frequently you're able to work with AI tools day-to-day.*

**Bug Reporting**

•      Document any issues or defects found during testing using a standardized bug report format in an Excel file.

•      Include steps to reproduce, expected and actual results, request/response payloads or console/network evidence where applicable.

**Deadline**

ASAP

