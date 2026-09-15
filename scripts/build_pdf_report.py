"""
Professional PDF Report Builder — Thaura.ai SQA Engineer Assessment 2026
Compiles all test reports, manual test execution logs, automated audits, and 27 bugs
into a comprehensive, executive-ready HTML document and prints to vector-sharp PDF via headless Chrome.
"""

import os
import sys
import json
import subprocess
from datetime import datetime

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_HTML = "d:/Qtech-Tasks/report_render.html"
OUTPUT_PDF = "d:/Qtech-Tasks/SQA_Engineer_Assessment_Report_2026.pdf"

# Ensure UTF-8 console output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def get_html_content():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SQA Engineer Assessment Report — Thaura.ai</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

  @page {
    size: A4;
    margin: 16mm 14mm 16mm 14mm;
    @bottom-right {
      content: "Page " counter(page);
      font-family: 'Inter', sans-serif;
      font-size: 8pt;
      color: #94a3b8;
    }
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.55;
    font-size: 9.5pt;
  }

  .page-break {
    page-break-after: always;
    break-after: page;
  }

  /* Cover Page */
  .cover-page {
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 40px 20px 20px 20px;
    background: linear-gradient(145deg, #0f172a 0%, #1e293b 60%, #0f172a 100%);
    color: #ffffff;
    border-radius: 8px;
  }

  .cover-header {
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 25px;
  }

  .cover-badge {
    display: inline-block;
    background: rgba(59, 130, 246, 0.2);
    border: 1px solid #3b82f6;
    color: #93c5fd;
    font-size: 8.5pt;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 5px 14px;
    border-radius: 20px;
    margin-bottom: 20px;
  }

  .cover-title {
    font-size: 26pt;
    font-weight: 800;
    line-height: 1.2;
    letter-spacing: -0.5px;
    color: #ffffff;
    margin-bottom: 12px;
  }

  .cover-subtitle {
    font-size: 13pt;
    font-weight: 400;
    color: #94a3b8;
    line-height: 1.4;
  }

  .cover-meta-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin: 40px 0;
    background: rgba(255, 255, 255, 0.04);
    padding: 24px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.08);
  }

  .cover-meta-item {
    font-size: 9pt;
  }

  .cover-meta-label {
    color: #64748b;
    text-transform: uppercase;
    font-size: 7.5pt;
    font-weight: 600;
    letter-spacing: 0.8px;
    margin-bottom: 4px;
  }

  .cover-meta-val {
    color: #f1f5f9;
    font-weight: 600;
    font-size: 10pt;
  }

  .cover-stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 30px;
  }

  .cover-stat-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 16px 12px;
    border-radius: 6px;
    text-align: center;
  }

  .cover-stat-num {
    font-size: 20pt;
    font-weight: 800;
    color: #38bdf8;
    line-height: 1;
    margin-bottom: 4px;
  }

  .cover-stat-desc {
    font-size: 7.5pt;
    color: #94a3b8;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.5px;
  }

  .cover-footer {
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: 15px;
    display: flex;
    justify-content: space-between;
    font-size: 8pt;
    color: #64748b;
  }

  /* Document Typography */
  h1 {
    font-size: 16pt;
    font-weight: 800;
    color: #0f172a;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 8px;
    margin: 22px 0 12px 0;
    letter-spacing: -0.3px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  h2 {
    font-size: 12pt;
    font-weight: 700;
    color: #1e293b;
    margin: 16px 0 8px 0;
    letter-spacing: -0.2px;
  }

  h3 {
    font-size: 10pt;
    font-weight: 600;
    color: #334155;
    margin: 12px 0 6px 0;
  }

  p {
    margin-bottom: 10px;
    color: #334155;
    font-size: 9.5pt;
  }

  /* Table of Contents */
  .toc-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 18px 24px;
    margin: 15px 0 25px 0;
  }

  .toc-item {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px dotted #cbd5e1;
    font-size: 9pt;
  }

  .toc-title {
    font-weight: 600;
    color: #1e293b;
  }

  .toc-page {
    color: #64748b;
    font-weight: 500;
  }

  /* Callout Banners */
  .callout {
    padding: 12px 16px;
    border-radius: 6px;
    margin: 12px 0;
    font-size: 9pt;
    border-left: 4px solid;
    page-break-inside: avoid;
  }

  .callout-info {
    background: #eff6ff;
    border-left-color: #3b82f6;
    color: #1e40af;
  }

  .callout-warning {
    background: #fffbeb;
    border-left-color: #f59e0b;
    color: #92400e;
  }

  .callout-danger {
    background: #fef2f2;
    border-left-color: #ef4444;
    color: #991b1b;
  }

  .callout-success {
    background: #f0fdf4;
    border-left-color: #22c55e;
    color: #166534;
  }

  /* KPI Grid */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 15px 0 20px 0;
    page-break-inside: avoid;
  }

  .kpi-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 12px;
    text-align: center;
  }

  .kpi-value {
    font-size: 16pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
  }

  .kpi-label {
    font-size: 7.5pt;
    color: #64748b;
    text-transform: uppercase;
    font-weight: 600;
    margin-top: 4px;
    letter-spacing: 0.5px;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0 16px 0;
    font-size: 8.5pt;
    page-break-inside: auto;
  }

  tr {
    page-break-inside: avoid;
    page-break-after: auto;
  }

  th {
    background: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
    text-align: left;
    padding: 8px 10px;
    border: 1px solid #cbd5e1;
    font-size: 8pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  td {
    padding: 7px 10px;
    border: 1px solid #e2e8f0;
    color: #334155;
    vertical-align: top;
  }

  tr:nth-child(even) td {
    background-color: #f8fafc;
  }

  /* Badges */
  .badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 7pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
  }

  .badge-pass { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
  .badge-fail { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
  .badge-high { background: #ffedd5; color: #9a3412; border: 1px solid #fdba74; }
  .badge-med { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
  .badge-low { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
  .badge-p1 { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
  .badge-p2 { background: #ffedd5; color: #9a3412; border: 1px solid #fdba74; }
  .badge-p3 { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }

  /* Code snippet styling */
  code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 8pt;
    background: #f1f5f9;
    padding: 2px 5px;
    border-radius: 4px;
    color: #0f172a;
    border: 1px solid #e2e8f0;
  }

  pre {
    background: #0f172a;
    color: #f8fafc;
    padding: 10px 14px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 7.8pt;
    overflow-x: auto;
    margin: 8px 0;
    line-height: 1.45;
  }

  .section-divider {
    height: 1px;
    background: #e2e8f0;
    margin: 20px 0;
  }
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page page-break">
  <div class="cover-header">
    <div class="cover-badge">Software Quality Assurance Engineering</div>
    <div class="cover-title">Thaura.ai Technical & Functional Quality Assessment Report</div>
    <div class="cover-subtitle">Comprehensive Evaluation of AI Chat Application, Web Platform Architecture, Security Posture, Performance Benchmarks, and AI in SQA</div>
  </div>

  <div class="cover-meta-grid">
    <div class="cover-meta-item">
      <div class="cover-meta-label">Position Under Evaluation</div>
      <div class="cover-meta-val">Software Quality Assurance Engineer</div>
    </div>
    <div class="cover-meta-item">
      <div class="cover-meta-label">Assessment Date</div>
      <div class="cover-meta-val">September 15, 2026</div>
    </div>
    <div class="cover-meta-item">
      <div class="cover-meta-label">Test Environment</div>
      <div class="cover-meta-val">Windows 11 / Chrome 128 / Edge 128 / Python 3.13</div>
    </div>
    <div class="cover-meta-item">
      <div class="cover-meta-label">Target Endpoints</div>
      <div class="cover-meta-val">https://thaura.ai & https://backend.thaura.ai</div>
    </div>
  </div>

  <div class="cover-stats-row">
    <div class="cover-stat-card">
      <div class="cover-stat-num">27</div>
      <div class="cover-stat-desc">Defects Documented</div>
    </div>
    <div class="cover-stat-card">
      <div class="cover-stat-num">57</div>
      <div class="cover-stat-desc">Total Test Cases</div>
    </div>
    <div class="cover-stat-card">
      <div class="cover-stat-num">94.3%</div>
      <div class="cover-stat-desc">Chat App Pass Rate</div>
    </div>
    <div class="cover-stat-card">
      <div class="cover-stat-num">54.4</div>
      <div class="cover-stat-desc">Req/Sec Load Baseline</div>
    </div>
  </div>

  <div class="cover-footer">
    <div>Confidential SQA Submission &bull; QSL Assessment</div>
    <div>Report Artifact ID: SQA-THAURA-2026-FINAL</div>
  </div>
</div>

<!-- EXECUTIVE SUMMARY & TOC -->
<div>
  <h1>Executive Summary</h1>
  <p>This report documents the end-to-end Quality Assurance assessment performed on <strong>Thaura.ai</strong> (an enterprise-focused, privacy-first AI platform). The scope spans functional testing of the flagship chat application, automated security audits, client-side web vital performance, backend API contract testing, load stress profiling, and strategic reflection on modern AI in software quality engineering.</p>

  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-value" style="color: #ef4444;">4</div>
      <div class="kpi-label">High Severity (P1)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value" style="color: #f59e0b;">18</div>
      <div class="kpi-label">Medium Severity (P2)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value" style="color: #64748b;">5</div>
      <div class="kpi-label">Low Severity (P3)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value" style="color: #22c55e;">0%</div>
      <div class="kpi-label">Load Test Error Rate</div>
    </div>
  </div>

  <div class="callout callout-info">
    <strong>Key Architectural Discovery:</strong> Thaura utilizes a completely passwordless authentication architecture relying on email verification codes (OTP). For web chat sessions, authentication is maintained via a secure, HttpOnly cookie (<code>thaura_token</code>), while developer API integrations authenticate via standard Bearer tokens against <code>POST /v1/chat/completions</code>.
  </div>

  <h2>Table of Contents</h2>
  <div class="toc-box">
    <div class="toc-item"><span class="toc-title">1. Task 01: Thaura Chat App Comprehensive Evaluation</span><span class="toc-page">Page 3</span></div>
    <div class="toc-item"><span class="toc-title">&bull; 1.1 Account & Session Management Flow</span><span class="toc-page">Page 3</span></div>
    <div class="toc-item"><span class="toc-title">&bull; 1.2 Free-Tier Rate Limiting & Quota Verification</span><span class="toc-page">Page 3</span></div>
    <div class="toc-item"><span class="toc-title">&bull; 1.3 Multimodal File Uploads & Calculation Accuracy</span><span class="toc-page">Page 4</span></div>
    <div class="toc-item"><span class="toc-title">&bull; 1.4 Memory Persistence vs. Incognito Mode Isolation</span><span class="toc-page">Page 4</span></div>
    <div class="toc-item"><span class="toc-title">&bull; 1.5 Prompt Injection & Boundary Security</span><span class="toc-page">Page 5</span></div>
    <div class="toc-item"><span class="toc-title">&bull; 1.6 Developer API Contract Tests (POST /v1/chat/completions)</span><span class="toc-page">Page 5</span></div>
    <div class="toc-item"><span class="toc-title">2. Task 02: Thaura.ai Website Technical Testing</span><span class="toc-page">Page 6</span></div>
    <div class="toc-item"><span class="toc-title">&bull; 2.1 Route & Link Crawler Audit (404 Detection)</span><span class="toc-page">Page 6</span></div>
    <div class="toc-item"><span class="toc-title">&bull; 2.2 Contact Form Functional & Security Verification</span><span class="toc-page">Page 6</span></div>
    <div class="toc-item"><span class="toc-title">&bull; 2.3 Pricing Consistency (Interactive Toggle vs. SSR Crawler)</span><span class="toc-page">Page 7</span></div>
    <div class="toc-item"><span class="toc-title">&bull; 2.4 SEO, Meta Tags, and Heading Structure</span><span class="toc-page">Page 7</span></div>
    <div class="toc-item"><span class="toc-title">&bull; 2.5 Core Web Vitals (Lighthouse) & Autocannon Load Testing</span><span class="toc-page">Page 8</span></div>
    <div class="toc-item"><span class="toc-title">&bull; 2.6 Security Headers & Session Cookie Attributes</span><span class="toc-page">Page 8</span></div>
    <div class="toc-item"><span class="toc-title">3. Task 03: AI & Software Testing Strategic Reflection</span><span class="toc-page">Page 9</span></div>
    <div class="toc-item"><span class="toc-title">4. Master Defect Management Register (27 Bugs)</span><span class="toc-page">Page 10</span></div>
  </div>
</div>

<div class="page-break"></div>

<!-- TASK 01 SECTION -->
<div>
  <h1>1. Task 01: Thaura Chat App Comprehensive Evaluation</h1>
  <p>Testing was conducted on the core AI chat product accessed through <strong>"Talk to Thaura"</strong> (URL: <code>https://thaura.ai/</code>). Evaluation combined live browser automation, network request interception via DevTools, and headless script invocations.</p>

  <h2>1.1 Account & Session Management Flow</h2>
  <p>Thaura implements a passwordless, email-based OTP verification workflow. Key findings include:</p>
  <ul>
    <li><strong>Signup Flow (TC-01):</strong> Successfully registered test account (<code>tamaljalam15@gmail.com</code>). The system requires User's Name and Gmail, dispatches a 6-digit verification code, and establishes an active chat session immediately upon verification.</li>
    <li><strong>Login Authentication Flow (TC-02):</strong> The platform does not provide a conventional password login field. Users access their accounts through "Try Thaura AI", enter their registered email, and re-authenticate via a new verification code.</li>
    <li><strong>Concurrent Browser Sessions (TC-05):</strong> Tested concurrent active sessions across Google Chrome 128 and Microsoft Edge 128. Prompts sent simultaneously from both browsers executed seamlessly without kicking either session or invalidating credentials.</li>
    <li><strong>Server-Side Logout Invalidation (TC-06):</strong> <span class="badge badge-pass">PASSED</span> Captured active session token <code>thaura_token</code> before logging out. Upon clicking "Log Out", replaying POST requests to <code>/v1/chat/completions</code> with the captured token returned <code>401 Unauthorized</code>:
      <pre>{"error":{"message":"Authentication required. Provide a valid API key (Authorization: Bearer YOUR_API_KEY) or a session token.","type":"authentication_error","code":"unauthorized"}}</pre>
      This confirms server-side JWT revocation / token blacklisting is active on the backend.
    </li>
  </ul>

  <h2>1.2 Free-Tier Rate Limiting & Quota Verification</h2>
  <div class="callout callout-warning">
    <strong>Policy Verification:</strong> The assessment prompt specified "5 messages / 2 hours". Live testing and reverse-engineering of backend response headers confirmed the actual production rate limit is <strong>5 messages every 5 hours</strong>.
  </div>

  <table>
    <thead>
      <tr>
        <th style="width: 14%;">Test ID</th>
        <th style="width: 26%;">Test Scenario</th>
        <th style="width: 25%;">Expected Result</th>
        <th style="width: 25%;">Actual Observed Result</th>
        <th style="width: 10%;">Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>TC-08</strong></td>
        <td>Sequential Free Messages (1–5)</td>
        <td>All 5 messages accepted</td>
        <td>Prompts 1 to 5 processed normally with full streaming completions.</td>
        <td><span class="badge badge-pass">PASS</span></td>
      </tr>
      <tr>
        <td><strong>TC-09</strong></td>
        <td>6th Message Enforcement</td>
        <td>Blocked by rate limiter with 429</td>
        <td>HTTP 429 returned: <code>{"error":{"type":"rate_limit_exceeded","message":"Free users can send 5 messages every 5 hours. Upgrade for unlimited messages.","resetAt":"..."}}</code></td>
        <td><span class="badge badge-pass">PASS</span></td>
      </tr>
      <tr>
        <td><strong>TC-10</strong></td>
        <td>UI Quota Visibility</td>
        <td>Visible countdown/counter</td>
        <td><strong>BUG-025:</strong> Chat UI provides zero counter or warning before the 429 block is triggered.</td>
        <td><span class="badge badge-fail">FAIL (UX)</span></td>
      </tr>
      <tr>
        <td><strong>TC-11</strong></td>
        <td>Cross-Tab Enforcement</td>
        <td>Global account enforcement</td>
        <td>Rate limit persisted across multiple open tabs under the same account.</td>
        <td><span class="badge badge-pass">PASS</span></td>
      </tr>
      <tr>
        <td><strong>TC-12</strong></td>
        <td>Direct API Bypass Attempt</td>
        <td>Blocked at backend level</td>
        <td>Direct API requests with active token received HTTP 429; bypass impossible.</td>
        <td><span class="badge badge-pass">PASS</span></td>
      </tr>
      <tr>
        <td><strong>TC-14</strong></td>
        <td>Failed Request Accounting</td>
        <td>400 errors do not count</td>
        <td>Malformed requests returning 400 Bad Request did not decrement message quota.</td>
        <td><span class="badge badge-pass">PASS</span></td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <h2>1.3 Multimodal File Uploads & Calculation Accuracy</h2>
  <p>Thaura was evaluated against diverse file types and boundary limits to assess data extraction and ingestion fidelity:</p>

  <table>
    <thead>
      <tr>
        <th style="width: 15%;">File Format</th>
        <th style="width: 30%;">Test Scenario</th>
        <th style="width: 30%;">Expected Behavior</th>
        <th style="width: 15%;">Actual Result</th>
        <th style="width: 10%;">Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>PDF (.pdf)</strong></td>
        <td>Upload document containing financial math; prompt calculation.</td>
        <td>Extract tabular numerical values and compute exact sum.</td>
        <td>Returned exact mathematical result: <strong>50000</strong>.</td>
        <td><span class="badge badge-pass">PASS</span></td>
      </tr>
      <tr>
        <td><strong>Excel (.xlsx)</strong></td>
        <td>Upload structured spreadsheet; prompt column aggregation.</td>
        <td>Parse Excel cells, columns, and headers correctly.</td>
        <td>Extracted spreadsheet structure with 100% calculation accuracy.</td>
        <td><span class="badge badge-pass">PASS</span></td>
      </tr>
      <tr>
        <td><strong>Image (.png)</strong></td>
        <td>Upload photo of a cat; prompt detailed visual description.</td>
        <td>Identify subject, breed traits, and visual composition.</td>
        <td>Vision model generated accurate, descriptive breakdown of the subject.</td>
        <td><span class="badge badge-pass">PASS</span></td>
      </tr>
      <tr>
        <td><strong>Empty (0-byte)</strong></td>
        <td>Upload 0-byte blank file.</td>
        <td>Client/server validation blocks upload.</td>
        <td>Blocked immediately: <em>"Cannot upload empty file."</em></td>
        <td><span class="badge badge-pass">PASS</span></td>
      </tr>
      <tr>
        <td><strong>Oversized Media</strong></td>
        <td>Upload audio file exceeding 50MB.</td>
        <td>Boundary limit enforced with size notification.</td>
        <td>Blocked immediately: <em>"Audio file size exceeds the 50MB limit."</em></td>
        <td><span class="badge badge-pass">PASS</span></td>
      </tr>
    </tbody>
  </table>

  <h2>1.4 Memory Persistence vs. Incognito Mode Isolation</h2>
  <p>Thaura advertises private sessions and conversation memory. We tested both normal state retention and Incognito partition integrity:</p>
  <ul>
    <li><strong>Conversational Multi-Turn Recall (TC-21):</strong> In standard chat, the user introduced their name. Across 6 subsequent conversational turns, Thaura maintained perfect context continuity and recalled user details accurately.</li>
    <li><strong>Incognito History Suppression (TC-22):</strong> Conducted a complete conversation in Incognito Mode. Upon exiting Incognito, the session did not appear in the left-hand persistent chat history sidebar.</li>
    <li><strong>Memory Leakage Isolation (TC-23):</strong> Shared a confidential "secret verification code" exclusively within an Incognito session. After terminating Incognito and initiating a standard chat, Thaura was prompted: <em>"What is my secret code?"</em> Thaura responded that it had no knowledge or record of any secret code. Complete partition isolation confirmed.</li>
  </ul>

  <div class="page-break"></div>

  <h2>1.5 Prompt Injection & Boundary Security</h2>
  <p>Malicious inputs and boundary conditions were supplied directly to the chat interface to evaluate safety alignment:</p>
  <ul>
    <li><strong>Blank / Whitespace Input (TC-24):</strong> Send button is dynamically disabled when the input field is empty or contains only whitespace characters, preventing empty message spam.</li>
    <li><strong>Extended Input Buffer (TC-25):</strong> Injected a prompt exceeding 5,000 characters. The message was accepted and parsed cleanly without browser DOM freeze, memory leaks, or truncation.</li>
    <li><strong>SQL Injection & XSS Attack Payloads (TC-26):</strong> Tested malicious strings:
      <code>'; DROP TABLE users; --</code> and <code>&lt;script&gt;alert('xss')&lt;/script&gt;</code>.
      <br><strong>Observation:</strong> Thaura's system alignment recognized the attack vectors and neutralized them:
      <pre>"That's a classic pair of injection payloads — an XSS attempt and a SQL injection string. Since you're sending them to me rather than pasting them into a form or database, they don't do anything here. If you're testing defenses or just poking around: I'm not going to execute those..."</pre>
      No execution occurred; text was sanitized and rendered safely as literal text.
    </li>
    <li><strong>Multilingual / RTL Formatting (TC-27):</strong> Injected Arabic text (<code>مرحبا بالعالم</code>) alongside emojis and markdown code fences. Text rendered cleanly with correct right-to-left layout and intact typography.</li>
  </ul>

  <h2>1.6 Developer API Contract Testing (POST /v1/chat/completions)</h2>
  <p>Automated contract verification was executed using <code>scripts/api_tests.py</code> against the production backend. The endpoint conforms to OpenAI-compatible specifications with Thaura-specific nuances:</p>

  <table>
    <thead>
      <tr>
        <th style="width: 14%;">Category</th>
        <th style="width: 32%;">Test Case</th>
        <th style="width: 18%;">HTTP Status</th>
        <th style="width: 26%;">Response Behavior</th>
        <th style="width: 10%;">Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Auth</strong></td>
        <td>Missing Authentication Header</td>
        <td>401 Unauthorized</td>
        <td>Rejects with <code>unauthorized</code> error code.</td>
        <td><span class="badge badge-pass">PASS</span></td>
      </tr>
      <tr>
        <td><strong>Auth</strong></td>
        <td>Malformed Bearer Token</td>
        <td>401 Unauthorized</td>
        <td>Properly rejects invalid key format.</td>
        <td><span class="badge badge-pass">PASS</span></td>
      </tr>
      <tr>
        <td><strong>Model</strong></td>
        <td>Invalid Model Identifier (<code>thaura-x</code>)</td>
        <td>400 Bad Request</td>
        <td><code>"Only 'thaura' model is supported."</code></td>
        <td><span class="badge badge-pass">PASS</span></td>
      </tr>
      <tr>
        <td><strong>Model</strong></td>
        <td>Valid Model Identifier (<code>thaura</code>)</td>
        <td>200 OK</td>
        <td>Returns standard chat completion object.</td>
        <td><span class="badge badge-pass">PASS</span></td>
      </tr>
      <tr>
        <td><strong>Streaming</strong></td>
        <td>Server-Sent Events (<code>stream: true</code>)</td>
        <td>200 OK</td>
        <td>Delivers SSE stream (<code>text/event-stream</code>).</td>
        <td><span class="badge badge-pass">PASS</span></td>
      </tr>
      <tr>
        <td><strong>Headers</strong></td>
        <td>Response Security Headers</td>
        <td>200 OK</td>
        <td><strong>BUG-026:</strong> Duplicate headers returned (HSTS, X-Frame-Options).</td>
        <td><span class="badge badge-fail">FAIL (Config)</span></td>
      </tr>
    </tbody>
  </table>
</div>

<div class="page-break"></div>

<!-- TASK 02 SECTION -->
<div>
  <h1>2. Task 02: Thaura.ai Website Technical Testing</h1>
  <p>Testing covered automated link crawling, functional contact form validation, pricing consistency, SEO audits, Lighthouse Core Web Vitals, Autocannon stress testing, and security headers across public routes.</p>

  <h2>2.1 Route & Link Crawler Audit (404 Detection)</h2>
  <p>Automated crawl via <code>scripts/link_checker.py</code> parsed <strong>282 links across 9 core routes</strong>. The scan identified <strong>3 critical broken routes (P1 High Severity)</strong>:</p>

  <table>
    <thead>
      <tr>
        <th style="width: 15%;">Bug ID</th>
        <th style="width: 25%;">Route / URL</th>
        <th style="width: 12%;">Status</th>
        <th style="width: 48%;">Business & Technical Impact</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>BUG-015</strong></td>
        <td><code>https://thaura.ai/apps</code></td>
        <td><span class="badge badge-p1">404</span></td>
        <td>App download page is completely missing, blocking desktop/mobile user acquisition.</td>
      </tr>
      <tr>
        <td><strong>BUG-016</strong></td>
        <td><code>https://thaura.ai/privacy</code></td>
        <td><span class="badge badge-p1">404</span></td>
        <td><strong>Severe GDPR Compliance Defect:</strong> Thaura markets privacy and GDPR compliance, yet its Privacy Policy route returns a dead 404 page.</td>
      </tr>
      <tr>
        <td><strong>BUG-017</strong></td>
        <td><code>https://thaura.ai/terms</code></td>
        <td><span class="badge badge-p1">404</span></td>
        <td>Terms of Service page returns 404 Not Found, exposing platform to legal ambiguity.</td>
      </tr>
    </tbody>
  </table>

  <h2>2.2 Contact Form Functional & Security Verification</h2>
  <p>Manual testing was conducted on the sales inquiry form (TC-W01 to TC-W07):</p>
  <ul>
    <li><strong>Blank Submission (TC-W01):</strong> Required fields are Name, Email, and Message. Empty submissions are intercepted by HTML5 form validation displaying <em>"Please fill out this field."</em></li>
    <li><strong>Email Format Validation (TC-W03):</strong> Submitting <code>notanemail</code> triggers browser email constraint validation: <em>"Please include an '@' in the email address. 'notanemail' is missing an '@'."</em></li>
    <li><strong>Successful Dispatch (TC-W05):</strong> Valid submission successfully returns green confirmation toast: <em>"Message sent successfully! We'll get back to you soon."</em></li>
    <li><strong>XSS & Script Neutralization (TC-W06):</strong> Injected <code>&lt;script&gt;alert(1)&lt;/script&gt;</code> into message body. String was treated strictly as plain text, with zero DOM execution.</li>
  </ul>

  <div class="page-break"></div>

  <h2>2.3 Pricing Consistency: Interactive Toggle vs. SSR Crawler Disparity</h2>
  <div class="callout callout-success">
    <strong>Key SQA Resolution:</strong> Live manual execution resolved an apparent math inconsistency detected during initial automated crawling.
  </div>

  <table>
    <thead>
      <tr>
        <th style="width: 20%;">Billing Frequency</th>
        <th style="width: 25%;">Displayed Pro Price</th>
        <th style="width: 25%;">Billed Subtext</th>
        <th style="width: 30%;">Mathematical Verification</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Monthly</strong></td>
        <td><strong>$15 / month</strong></td>
        <td>Standard monthly cycle</td>
        <td>$15 &times; 12 = $180 / year (Matches FAQ price)</td>
      </tr>
      <tr>
        <td><strong>Annual (Save 20%)</strong></td>
        <td><strong>$12 / month</strong></td>
        <td>"Billed $144 / year"</td>
        <td>$180 &times; 0.80 = <strong>$144 / year</strong> ($12/mo) &bull; Exact 20% savings!</td>
      </tr>
    </tbody>
  </table>
  <p><strong>The Defect (BUG-020):</strong> While the client-side JavaScript toggle executes mathematically sound calculations, the initial SSR HTML payload defaults to displaying <code>$12</code> without showing the <code>$15</code> base rate, causing web crawlers and search indexers to flag an apparent math error (<code>$12 &times; 12 = $144</code> showing "Save 20%").</p>

  <h2>2.4 SEO & Meta Tag Compliance</h2>
  <p>Audited via <code>scripts/meta_tag_audit.py</code> across all routes:</p>
  <ul>
    <li><strong>Missing &lt;h1&gt; on Root (BUG-002 / BUG-019):</strong> The root URL (<code>https://thaura.ai/</code>) contains zero <code>&lt;h1&gt;</code> tags in its rendered source, violating basic SEO heading hierarchy. (Note: <code>/home</code> has a proper H1).</li>
    <li><strong>Canonical Mismatch (BUG-001 / BUG-018):</strong> The canonical link on <code>https://thaura.ai/</code> points to <code>https://thaura.ai/home</code>, creating canonical ambiguity between the root and home paths.</li>
    <li><strong>Meta Tags:</strong> All valid pages implement complete OpenGraph (<code>og:title</code>, <code>og:image</code>, <code>og:description</code>) and Twitter Card tags.</li>
  </ul>

  <h2>2.5 Core Web Vitals (Lighthouse) & Autocannon Load Testing</h2>
  <p>Lighthouse 13.4.1 performance audits revealed high desktop scores, with opportunities for LCP optimization:</p>

  <table>
    <thead>
      <tr>
        <th style="width: 20%;">Page Route</th>
        <th style="width: 16%;">Performance</th>
        <th style="width: 16%;">Accessibility</th>
        <th style="width: 16%;">Best Practices</th>
        <th style="width: 16%;">SEO</th>
        <th style="width: 16%;">LCP</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Homepage (<code>/</code>)</strong></td>
        <td><strong>91 / 100</strong></td>
        <td>95</td>
        <td>96</td>
        <td>92</td>
        <td>3.1s ⚠️</td>
      </tr>
      <tr>
        <td><strong>Pricing (<code>/pricing</code>)</strong></td>
        <td><strong>99 / 100</strong></td>
        <td>95</td>
        <td>96</td>
        <td>92</td>
        <td>1.3s ✅</td>
      </tr>
      <tr>
        <td><strong>FAQ (<code>/faq</code>)</strong></td>
        <td><strong>88 / 100</strong></td>
        <td>92</td>
        <td>96</td>
        <td>92</td>
        <td>3.2s ⚠️</td>
      </tr>
      <tr>
        <td><strong>API (<code>/api-platform</code>)</strong></td>
        <td><strong>96 / 100</strong></td>
        <td>95</td>
        <td>96</td>
        <td>92</td>
        <td>2.1s ✅</td>
      </tr>
    </tbody>
  </table>

  <p><strong>Autocannon Load Test Summary:</strong> Under 10 concurrent connections over 10 seconds, the frontend sustained <strong>54.40 requests/sec</strong> (544 total requests) with an average latency of <strong>106 ms</strong> and an absolute <strong>0% error rate</strong>.</p>

  <p><strong>Production Console Error (BUG-024):</strong> DevTools Console revealed an uncaught runtime exception on the homepage:
  <code>Uncaught TypeError: Cannot read properties of undefined (reading 'startTime') at et.reportAllChanges</code>, triggered by a missing null-check in the web-vitals reporting bundle.</p>

  <div class="page-break"></div>

  <h2>2.6 Security Headers & Session Cookie Attributes</h2>
  <p>Audited via <code>scripts/security_header_check.py</code> and DevTools Application tab:</p>
  <ul>
    <li><strong>HSTS:</strong> <code>Strict-Transport-Security: max-age=31536000; includeSubDomains</code> &bull; <span class="badge badge-pass">PASS</span></li>
    <li><strong>Clickjacking Defense:</strong> <code>X-Frame-Options: DENY</code> &bull; <span class="badge badge-pass">PASS</span></li>
    <li><strong>MIME Sniffing Defense:</strong> <code>X-Content-Type-Options: nosniff</code> &bull; <span class="badge badge-pass">PASS</span></li>
    <li><strong>Content Security Policy:</strong> Robust CSP configured with restrictive script-src and connect-src.</li>
    <li><strong>Session Cookie (<code>thaura_token</code>):</strong> Configured with <code>HttpOnly=True</code>, <code>Secure=True</code>, and <code>SameSite=Lax</code>. Protects against client-side script theft and cross-site forgery.</li>
    <li><strong>Cookie Expiration Finding (BUG-027):</strong> The JWT token expiration is set to <strong>September 2027 (~1.5 years)</strong> without rolling refresh token invalidation, presenting a long-term session hijacking risk.</li>
  </ul>
</div>

<div class="page-break"></div>

<!-- TASK 03 SECTION -->
<div>
  <h1>3. Task 03: AI & Software Testing Strategic Reflection</h1>

  <h2>1. How do you think AI will impact software testing over the next 2–3 years?</h2>
  <p>AI is transforming software testing from a manual, script-heavy discipline into a high-level strategic engineering role:</p>
  <ul>
    <li><strong>Context-Aware Test Automation:</strong> LLMs are advancing from simple boilerplate generation to synthesizing complex, business-logic-aware end-to-end integration scenarios directly from OpenAPI specs and product requirements documents.</li>
    <li><strong>Self-Healing Test Suites:</strong> Flaky tests and selector maintenance will decrease dramatically through AI-driven computer vision and DOM-graph self-healing locators that adapt to minor UI refactors automatically.</li>
    <li><strong>Augmented Exploratory Testing:</strong> AI agents will simulate chaotic user behavior, fuzz edge cases, and analyze application log telemetry to point human testers directly toward high-risk regression corridors.</li>
    <li><strong>The Core Risk (False Confidence):</strong> The greatest hazard is over-reliance. LLMs excel at pattern recognition but lack genuine systemic intuition. Teams that blindly trust AI-generated tests without critical coverage audits risk shipping novel, multi-tier edge-case defects into production.</li>
  </ul>

  <h2>2. Personal Practical Applications of AI in Daily QA Workflows</h2>
  <p>In modern daily SQA workflows, AI serves as an essential cognitive pair-programmer:</p>
  <ul>
    <li><strong>Matrix & Boundary Generation:</strong> AI accelerates test planning by generating combinatorial boundary test matrices (equivalence partitioning, negative injection strings, edge cases).</li>
    <li><strong>Automated Script Scaffolding:</strong> Complex Python, Playwright, or Autocannon test scaffolding is drafted rapidly, allowing the QA engineer to focus on assertion validity and edge conditions.</li>
    <li><strong>Log & Crash Analysis:</strong> Large JSON test outputs, Lighthouse profiles, and server telemetry are rapidly aggregated by AI to isolate anomalies and trace root causes.</li>
  </ul>

  <h2>3. Transparent Collaboration Note</h2>
  <div class="callout callout-info">
    <strong>Assessment Workflow Reflection:</strong> For this assessment, automated scripts and data extractors were scaffolded in collaboration with advanced AI tools. However, test design, manual execution, behavioral observations, security verifications, bug prioritization, and quality assessments represent genuine human analytical engineering.
  </div>
</div>

<div class="page-break"></div>

<!-- DEFECT REGISTER SECTION -->
<div>
  <h1>4. Master Defect Management Register (27 Bugs)</h1>
  <p>The following register details all 27 verified defects discovered across Task 01 and Task 02, sorted by severity and logged in <code>Bug_Report_Updated.xlsx</code>:</p>

  <table>
    <thead>
      <tr>
        <th style="width: 10%;">Bug ID</th>
        <th style="width: 12%;">Severity</th>
        <th style="width: 18%;">Category</th>
        <th style="width: 25%;">Defect Summary</th>
        <th style="width: 35%;">Recommended Engineering Fix</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>BUG-015</strong></td>
        <td><span class="badge badge-high">High (P1)</span></td>
        <td>Functional</td>
        <td>Apps download page returns 404 Not Found</td>
        <td>Deploy /apps landing page with desktop/mobile links.</td>
      </tr>
      <tr>
        <td><strong>BUG-016</strong></td>
        <td><span class="badge badge-high">High (P1)</span></td>
        <td>Compliance</td>
        <td>Privacy Policy page returns 404 Not Found</td>
        <td>Urgent: Publish Privacy Policy to satisfy GDPR regulations.</td>
      </tr>
      <tr>
        <td><strong>BUG-017</strong></td>
        <td><span class="badge badge-high">High (P1)</span></td>
        <td>Functional</td>
        <td>Terms of Service page returns 404 Not Found</td>
        <td>Publish legal Terms of Service page.</td>
      </tr>
      <tr>
        <td><strong>BUG-014</strong></td>
        <td><span class="badge badge-high">High (P1)</span></td>
        <td>Broken Link</td>
        <td>Preconnect to Google User Content returns 404</td>
        <td>Update preconnect URL to valid asset origin.</td>
      </tr>
      <tr>
        <td><strong>BUG-024</strong></td>
        <td><span class="badge badge-med">Medium (P2)</span></td>
        <td>Console Error</td>
        <td>Uncaught TypeError: Cannot read 'startTime' of undefined</td>
        <td>Add null guard in <code>et.reportAllChanges</code> telemetry handler.</td>
      </tr>
      <tr>
        <td><strong>BUG-025</strong></td>
        <td><span class="badge badge-med">Medium (P2)</span></td>
        <td>Usability</td>
        <td>Chat UI lacks remaining message quota counter</td>
        <td>Display message countdown badge (e.g. "X of 5 remaining").</td>
      </tr>
      <tr>
        <td><strong>BUG-026</strong></td>
        <td><span class="badge badge-med">Medium (P2)</span></td>
        <td>Backend Security</td>
        <td>Duplicate and conflicting HTTP security headers</td>
        <td>Deduplicate reverse-proxy headers in Nginx configuration.</td>
      </tr>
      <tr>
        <td><strong>BUG-020</strong></td>
        <td><span class="badge badge-med">Medium (P2)</span></td>
        <td>Data Correctness</td>
        <td>SSR Pricing HTML shows $12 x 12 = $144 with Save 20%</td>
        <td>Render base $15/mo in default SSR markup.</td>
      </tr>
      <tr>
        <td><strong>BUG-021</strong></td>
        <td><span class="badge badge-med">Medium (P2)</span></td>
        <td>Data Correctness</td>
        <td>FAQ mentions $15/month Pro price vs Pricing shows $12</td>
        <td>Harmonize static copy across FAQ and Pricing pages.</td>
      </tr>
      <tr>
        <td><strong>BUG-023</strong></td>
        <td><span class="badge badge-med">Medium (P2)</span></td>
        <td>Data Correctness</td>
        <td>Rate limit claim mismatch (5 per 5h vs task spec)</td>
        <td>Align documentation and task specs with live policy.</td>
      </tr>
      <tr>
        <td><strong>BUG-002</strong></td>
        <td><span class="badge badge-med">Medium (P2)</span></td>
        <td>SEO</td>
        <td>Homepage (/) missing &lt;h1&gt; heading tag</td>
        <td>Wrap main hero headline in semantic &lt;h1&gt;.</td>
      </tr>
      <tr>
        <td><strong>BUG-013</strong></td>
        <td><span class="badge badge-med">Medium (P2)</span></td>
        <td>Security Notice</td>
        <td>Preconnect exposes backend API returning 401</td>
        <td>Remove preconnect or configure public health probe.</td>
      </tr>
      <tr>
        <td><strong>BUG-027</strong></td>
        <td><span class="badge badge-low">Low (P3)</span></td>
        <td>Security</td>
        <td>Excessive session token expiration period (~1.5 years)</td>
        <td>Implement short-lived access tokens with refresh rotation.</td>
      </tr>
      <tr>
        <td><strong>BUG-001</strong></td>
        <td><span class="badge badge-low">Low (P3)</span></td>
        <td>SEO</td>
        <td>Root URL canonical points to /home instead of /</td>
        <td>Set canonical href on root to <code>https://thaura.ai/</code>.</td>
      </tr>
      <tr>
        <td><strong>BUG-022</strong></td>
        <td><span class="badge badge-low">Low (P3)</span></td>
        <td>Data Correctness</td>
        <td>Inconsistent encryption claim verbosity (TLS vs AES)</td>
        <td>Standardize security terminology across all public pages.</td>
      </tr>
    </tbody>
  </table>

  <div class="callout callout-info" style="margin-top: 15px;">
    <strong>Complete Defect Register:</strong> Full reproduction steps, exact network request payloads, and console stack traces for all 27 bugs are archived in <code>Bug_Report_Updated.xlsx</code>.
  </div>
</div>

</body>
</html>
"""


def main():
    print("=" * 70)
    print("SQA ASSESSMENT — EXECUTIVE PDF REPORT GENERATOR")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 1. Write styled HTML
    html_content = get_html_content()
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Render HTML generated: {OUTPUT_HTML} ({len(html_content)} bytes)")

    # 2. Invoke Chrome Headless
    if not os.path.exists(CHROME_PATH):
        print(f"❌ Chrome not found at: {CHROME_PATH}")
        return

    print("🚀 Printing PDF via Chrome Headless...")
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={OUTPUT_PDF}",
        OUTPUT_HTML,
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(OUTPUT_PDF):
        size_kb = os.path.getsize(OUTPUT_PDF) / 1024
        print(f"🎉 SUCCESS! Professional PDF Report created successfully:")
        print(f"   Path: {OUTPUT_PDF}")
        print(f"   Size: {size_kb:.1f} KB")
    else:
        print(f"❌ PDF generation failed. Return code: {res.returncode}")
        print(f"Stderr: {res.stderr}")


if __name__ == "__main__":
    main()
