# Task 01 — Thaura Chat App (AI Chat Product) — Test Report

**Tester:** SQA Engineering Team  
**Date:** 2026-09-15  
**Environment:** Windows 11 (64-bit), Google Chrome 128 / 152, Microsoft Edge 128  
**App URL:** https://thaura.ai/ (Chat UI via "Talk to Thaura")  
**API Endpoint:** https://backend.thaura.ai/v1/chat/completions  
**Test Accounts:**
- Account A: `tamaljalam15@gmail.com` (UID: `cmu2e3vpi05nsjyr423b1r505`)
- Account B: `mail.jahangiralamtamal@gmail.com` (UID: `cmu2bj9ax07wdbqr4jq7ayeai`)

---

## Executive Summary

Task 01 involved comprehensive functional, security, session, rate-limiting, multimodal file upload, memory isolation, and negative input testing on the **Thaura Chat Application**. 

* **Overall Status:** Functionally Robust with Key UX & Rate Limit Nuances
* **Total Test Cases:** 57 (35 Executed & Verified, 22 API Automated Contracts)
* **Pass Rate:** 91.4% (32 Passed, 3 Defect/UX Observations)
* **Key Findings:**
  1. **Passwordless Authentication:** The platform uses a passwordless Email OTP verification architecture instead of traditional password credentials.
  2. **Rate Limit Policy Discrepancy:** The actual live enforcement is **5 messages per 5 hours** (`RateLimit-Policy: 200;w=900` API window / 5 msgs per 5 hrs chat quota), returning HTTP 429 with explicit `resetAt` payload.
  3. **UI Quota Blindspot:** The web chat UI provides **zero message counter** or warning indicator before hitting the rate limit wall.
  4. **Strict Multimodal Parsing:** Image OCR/vision (Cat photo), PDF calculation (`50000`), and `.xlsx` tabular extraction all returned 100% accurate responses.
  5. **Privacy & Incognito Isolation:** Zero data leakage observed between incognito and persistent chat history.
  6. **Prompt Injection & Safety Defenses:** Model actively identified and neutralized SQL injection (`'; DROP TABLE users; --`) and XSS script tags without execution.

---

## 1. Account & Session Testing

### 1.1 Sign Up / Login Flow

| Test Case | Steps | Expected Result | Actual Result | Status |
|-----------|-------|-----------------|---------------|--------|
| **TC-01: New Account Signup** | 1. Navigate to https://thaura.ai/<br>2. Click "Talk to Thaura"<br>3. Enter email (`tamaljalam15@gmail.com`) & name<br>4. Enter received OTP code | OTP received; account created; redirected to active chat | Email and name requested, OTP sent and accepted, immediately redirected to chat interface. | ✅ **PASS** |
| **TC-02: Passwordless Login Flow** | 1. Log out of account<br>2. Click "Try Thaura AI"<br>3. Enter registered email<br>4. Submit OTP | Re-authenticates without requiring password | System sent 6-digit verification code to email. Entering code restored session. Note: No traditional password field exists. | ✅ **PASS** (Observation) |
| **TC-03: Invalid Email Format** | 1. Enter `notanemail` in signup email field<br>2. Submit | Frontend validation blocks submission | Browser HTML5 validation displays: *"Please include an '@' in the email address. 'notanemail' is missing an '@'."* | ✅ **PASS** |
| **TC-04: Non-Existent Email Authentication** | 1. Enter unverified email in login flow<br>2. Request OTP | System treats as new signup or sends verification | OTP is dispatched regardless; seamless just-in-time account creation upon code verification. | ✅ **PASS** |

### 1.2 Session Handling & Security

| Test Case | Steps | Expected Result | Actual Result | Status |
|-----------|-------|-----------------|---------------|--------|
| **TC-05: Concurrent Browser Sessions** | 1. Login to `tamaljalam15@gmail.com` in Chrome<br>2. Open Microsoft Edge and login with same account<br>3. Send messages concurrently from both browsers | Both sessions remain active OR first is gracefully retired | Both sessions functioned concurrently without kicking user out or corrupting state. | ✅ **PASS** |
| **TC-06: Server-Side Logout Invalidation** | 1. Capture active session cookie `thaura_token`<br>2. Click "Log Out" in UI<br>3. Replay POST `/v1/chat/completions` using the captured token | Server rejects old token with HTTP 401 | **HTTP 401 Unauthorized** returned immediately: `{"error":{"message":"Authentication required...","code":"unauthorized"}}`. Server-side JWT revocation list works correctly. | ✅ **PASS** |
| **TC-07: Session Cookie Flags & Storage** | 1. Open DevTools Application tab -> Cookies<br>2. Inspect `thaura_token` attributes | Cookie protected with `HttpOnly`, `Secure`, and `SameSite` | Cookie configured as: `HttpOnly=True` (inaccessible to `document.cookie`), `Secure=True` (HTTPS only), `SameSite=Lax`. | ✅ **PASS** |

---

## 2. Free-Tier Rate Limit Testing

> **Policy Audit:** The assessment task specified "5 messages / 2 hours", while the website pricing states "5 per 5 hours". Our testing confirmed live enforcement follows **5 messages every 5 hours**.

| Test Case | Steps | Expected Result | Actual Result | Status |
|-----------|-------|-----------------|---------------|--------|
| **TC-08: Sequential Messages (1 to 5)** | Send 5 normal prompts sequentially in a fresh session | All 5 messages accepted and answered | Messages 1 through 5 processed normally with full AI completions. | ✅ **PASS** |
| **TC-09: 6th Message Enforcement** | Immediately attempt sending 6th prompt | Blocked by rate limiter with informative message | HTTP 429 returned. UI message: *"Free users can send 5 messages every 5 hours. Upgrade for unlimited messages."* with exact ISO `resetAt` timestamp. | ✅ **PASS** |
| **TC-10: UI Usage Counter Visibility** | Observe chat interface while sending messages 1 to 5 | Visible remaining quota (e.g. "X of 5 remaining") | **Defect (BUG-025):** Chat UI does not show any counter, countdown, or warning before the 429 block is triggered. | ❌ **FAIL (UX Bug)** |
| **TC-11: Cross-Tab Rate Limit Sync** | 1. Reach rate limit in Tab 1<br>2. Open Tab 2 for thaura.ai in same browser profile<br>3. Attempt sending prompt | Tab 2 blocked immediately | Rate limit enforced globally across all tabs on the server; prompt in Tab 2 immediately blocked. | ✅ **PASS** |
| **TC-12: Rate Limit Bypass via Cookie Manipulation** | 1. Reach rate limit<br>2. Attempt direct API invocation with token | Blocked at API level | Direct POST `/v1/chat/completions` returned `429 Too Many Requests`. Cannot bypass via headless API call. | ✅ **PASS** |
| **TC-13: Rate Limit Bypass via Page Reload** | Refresh browser or clear local storage while keeping session | Limit persists | Quota tracked server-side against `userId`; refresh does not restore quota. | ✅ **PASS** |
| **TC-14: Failed / Blocked Request Quota Accounting** | Send an invalid model name or empty payload | Failed request should not consume message credit | 400 Bad Request responses do not decrement the 5-message user quota. | ✅ **PASS** |

---

## 3. Multimodal File Upload & Data Integrity

| Test Case | File Type | Test Steps | Expected Result | Actual Result | Status |
|-----------|-----------|------------|-----------------|---------------|--------|
| **TC-15: PDF Document Analysis** | Standard `.pdf` | Upload numerical document; ask for calculation | Correct mathematical answer | Thaura analyzed document and returned exact calculated answer: `50000`. | ✅ **PASS** |
| **TC-16: Spreadsheet Ingestion** | Microsoft Excel (`.xlsx`) | Upload spreadsheet; query table content | Accurate tabular data parsing | Answer returned from `.xlsx` dataset was completely accurate. | ✅ **PASS** |
| **TC-17: Vision / Image Understanding** | Image (`.png` / `.jpg`) | Upload photo of a cat; prompt: "Describe this image" | Accurate visual description | Vision model recognized subject, breed features, and composition accurately. | ✅ **PASS** |
| **TC-18: 0-Byte Empty File** | Empty text/pdf (`0 bytes`) | Attempt uploading empty file | File rejected with error | Application blocked upload: *"Cannot upload empty file."* | ✅ **PASS** |
| **TC-19: Oversized File Upload** | Audio file (`>50MB`) | Attempt uploading >50MB media file | Blocked with clear size boundary notification | File rejected immediately: *"Audio file size exceeds the 50MB limit."* | ✅ **PASS** |
| **TC-20: Unsupported Executable File** | `.exe` / `.bat` | Attempt uploading binary executable | Blocked by MIME/extension filter | Upload picker filters unsupported binary files. | ✅ **PASS** |

---

## 4. Memory Persistence vs. Incognito Mode

| Test Case | Test Steps | Expected Result | Actual Result | Status |
|-----------|------------|-----------------|---------------|--------|
| **TC-21: Multi-Turn Conversational Memory** | 1. In standard chat, tell Thaura user's name<br>2. Ask follow-up questions several turns later | Thaura retains name in context window | Thaura recalled user name accurately throughout the conversation. | ✅ **PASS** |
| **TC-22: Incognito History Suppression** | 1. Enter Incognito Mode<br>2. Have a multi-turn conversation<br>3. Close incognito mode and inspect sidebar chat history | Incognito session does NOT persist in chat history list | Chat history sidebar has zero record of the incognito session. | ✅ **PASS** |
| **TC-23: Cross-Session Data Isolation** | 1. In Incognito chat, share a secret code<br>2. Switch to standard regular chat<br>3. Prompt: "What is my secret code?" | Normal chat has zero knowledge of incognito secret | Thaura answered that it has no record of the secret code. Complete memory isolation confirmed. | ✅ **PASS** |

---

## 5. Negative & Boundary Input Testing

| Test Case | Input Payload | Expected Result | Actual Result | Status |
|-----------|---------------|-----------------|---------------|--------|
| **TC-24: Blank / Whitespace Submission** | Empty input / multiple spaces | Send button disabled | Send button is disabled in UI; prevents submitting blank requests. | ✅ **PASS** |
| **TC-25: Very Long Input (>5,000 chars)** | Extended 5,000+ character text block | Handled gracefully without crash | Message accepted and processed without frontend freeze or buffer overflow. | ✅ **PASS** |
| **TC-26: SQL Injection & XSS Attack Payloads** | `'; DROP TABLE users; --`<br>`<script>alert('xss')</script>` | Neutralized safely; no code execution | Model recognized injection attempts: *"That's a classic pair of injection payloads — an XSS attempt and a SQL injection string... I'm not going to execute those..."* Input safely rendered as text. | ✅ **PASS** |
| **TC-27: Special Characters & Unicode Rendering** | RTL Arabic (`مرحبا بالعالم`), Emojis, Code syntax | Displayed cleanly with correct typography | Unicode, code blocks, and markdown rendered with correct directionality and zero layout breakage. | ✅ **PASS** |

---

## 6. Developer API Contract Testing (`POST /v1/chat/completions`)

**Automated Test Suite:** [`scripts/api_tests.py`](file:///d:/Qtech-Tasks/scripts/api_tests.py)  
**Live Endpoint:** `https://backend.thaura.ai/v1/chat/completions`

| Category | Test Scenario | Request Details | Expected | Actual Result | Status |
|----------|---------------|-----------------|----------|---------------|--------|
| **Auth** | Missing Auth Header | POST without credentials | 401 | `401 Unauthorized` | ✅ **PASS** |
| **Auth** | Malformed Bearer Key | `Bearer invalid-token-123` | 401 | `401 Unauthorized` | ✅ **PASS** |
| **Auth** | Fake API Key Format | `Bearer sk-thaura-fakekey99` | 401 | `401 Unauthorized` | ✅ **PASS** |
| **Model** | Invalid / Legacy Model Name | `{"model": "thaura-x", ...}` | 400 | `400 Bad Request` (`Only 'thaura' model is supported`) | ✅ **PASS** |
| **Model** | Valid Model Name | `{"model": "thaura", ...}` | 200 | `200 OK` (Valid chat completion returned) | ✅ **PASS** |
| **Params** | Missing `messages` | `{"model": "thaura"}` | 400 | `400 Bad Request` | ✅ **PASS** |
| **Streaming**| SSE Event Stream | `{"stream": true, ...}` | `text/event-stream` | Real-time chunks delivered with `choices[0].delta` | ✅ **PASS** |
| **Headers**| Response Security Headers | Response Inspection | Clean Headers | **BUG-026:** Duplicated HSTS, X-Frame-Options, Referrer-Policy | ❌ **FAIL (Config)** |

---

## Test Execution Summary

| Test Category | Total Test Cases | Passed | Failed / Bugs | Blocked | Pass Rate |
|---------------|------------------|--------|---------------|---------|-----------|
| **Account & Session** | 7 | 7 | 0 | 0 | 100% |
| **Rate Limiting** | 7 | 6 | 1 (UX) | 0 | 85.7% |
| **Multimodal Uploads** | 6 | 6 | 0 | 0 | 100% |
| **Memory & Privacy** | 3 | 3 | 0 | 0 | 100% |
| **Negative & Boundary** | 4 | 4 | 0 | 0 | 100% |
| **Developer API** | 8 | 7 | 1 (Headers) | 0 | 87.5% |
| **TOTAL** | **35** | **33** | **2** | **0** | **94.3%** |

### Verified Bugs Logged to [`Bug_Report.xlsx`](file:///d:/Qtech-Tasks/Bug_Report.xlsx):
1. **BUG-025:** Chat UI lacks remaining message quota counter or countdown indicator before 429 block.
2. **BUG-026:** Backend returns duplicate and conflicting HTTP security headers (`Strict-Transport-Security`, `X-Frame-Options`, `Referrer-Policy`).
3. **BUG-027:** Session token (`thaura_token`) expiration is set to 1.5+ years (September 2027) without rolling refresh rotation.
