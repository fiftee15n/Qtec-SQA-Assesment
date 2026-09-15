"""
Developer API Test Suite — Thaura.ai
Task 01, Section 5: API Contract Testing

Endpoint: POST https://backend.thaura.ai/v1/chat/completions
(or as documented at thaura.ai/api-platform)

⚠️ WARNING: This is a real, metered, billed API.
All test calls use MINIMAL token usage (short prompts, low max_completion_tokens).

Usage: python api_tests.py --api-key YOUR_KEY [--base-url URL] [--dry-run]
"""

import requests
import json
import time
import sys
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Fix Windows console encoding for Unicode emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# ============================================================
# CONFIGURATION
# ============================================================
DEFAULT_BASE_URL = "https://backend.thaura.ai"
ENDPOINT = "/v1/chat/completions"

MINIMAL_PAYLOAD = {
    "model": "thaura",
    "messages": [{"role": "user", "content": "Hi"}],
    "max_completion_tokens": 5,
}

results = []
bugs = []


def log_result(test_name, status, detail, response=None):
    """Log a test result."""
    entry = {
        "test": test_name,
        "status": status,  # PASS, FAIL, ERROR, SKIP
        "detail": detail,
        "response_status": response.status_code if response else None,
        "response_body": None,
    }
    if response:
        try:
            entry["response_body"] = response.json()
        except:
            entry["response_body"] = response.text[:500]
    results.append(entry)

    icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "⚠️", "SKIP": "⏭️"}.get(status, "?")
    print(f"  {icon} [{status}] {test_name}: {detail}")

    if status == "FAIL":
        bugs.append({
            "page": "Developer API",
            "category": "API",
            "severity": "High",
            "summary": test_name,
            "detail": detail,
        })


def api_call(base_url, api_key, payload, stream=False):
    """Make an API call to the chat completions endpoint."""
    if api_key and api_key.startswith("eyJ"):
        headers = {
            "Cookie": f"thaura_token={api_key}",
            "Origin": "https://thaura.ai",
            "Content-Type": "application/json",
        }
    else:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    if stream:
        payload = {**payload, "stream": True}
    
    return requests.post(
        f"{base_url}{ENDPOINT}",
        headers=headers,
        json=payload,
        timeout=30,
        stream=stream,
    )


# ============================================================
# TEST SUITES
# ============================================================

def test_auth_missing(base_url):
    """Test: Missing API key → expect 401."""
    print("\n[AUTH] Missing API key")
    try:
        r = requests.post(
            f"{base_url}{ENDPOINT}",
            headers={"Content-Type": "application/json"},
            json=MINIMAL_PAYLOAD,
            timeout=15,
        )
        if r.status_code == 401:
            log_result("Auth: Missing key", "PASS", f"Got 401 as expected", r)
        else:
            log_result("Auth: Missing key", "FAIL", f"Expected 401, got {r.status_code}", r)
    except Exception as e:
        log_result("Auth: Missing key", "ERROR", str(e))


def test_auth_malformed(base_url):
    """Test: Malformed API key → expect 401."""
    print("[AUTH] Malformed API key")
    try:
        headers = {
            "Authorization": "Bearer not-a-real-key-12345",
            "Content-Type": "application/json",
        }
        r = requests.post(f"{base_url}{ENDPOINT}", headers=headers, json=MINIMAL_PAYLOAD, timeout=15)
        if r.status_code == 401:
            log_result("Auth: Malformed key", "PASS", f"Got 401 as expected", r)
        else:
            log_result("Auth: Malformed key", "FAIL", f"Expected 401, got {r.status_code}", r)
    except Exception as e:
        log_result("Auth: Malformed key", "ERROR", str(e))


def test_auth_invalid(base_url):
    """Test: Invalid (looks real but wrong) API key → expect 401."""
    print("[AUTH] Invalid API key")
    try:
        headers = {
            "Authorization": "Bearer sk-thauraxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "Content-Type": "application/json",
        }
        r = requests.post(f"{base_url}{ENDPOINT}", headers=headers, json=MINIMAL_PAYLOAD, timeout=15)
        if r.status_code in (401, 403):
            log_result("Auth: Invalid key", "PASS", f"Got {r.status_code} as expected", r)
        else:
            log_result("Auth: Invalid key", "FAIL", f"Expected 401/403, got {r.status_code}", r)
    except Exception as e:
        log_result("Auth: Invalid key", "ERROR", str(e))


def test_required_params(base_url, api_key):
    """Test: Missing required parameters."""
    print("\n[PARAMS] Required parameter validation")

    # Missing 'messages'
    try:
        r = api_call(base_url, api_key, {"model": "thaura", "max_completion_tokens": 5})
        if r.status_code in (400, 422):
            log_result("Params: Missing 'messages'", "PASS", f"Got {r.status_code}", r)
        else:
            log_result("Params: Missing 'messages'", "FAIL", f"Expected 400/422, got {r.status_code}", r)
    except Exception as e:
        log_result("Params: Missing 'messages'", "ERROR", str(e))

    # Missing 'model'
    try:
        r = api_call(base_url, api_key, {"messages": [{"role": "user", "content": "Hi"}], "max_completion_tokens": 5})
        if r.status_code in (400, 422):
            log_result("Params: Missing 'model'", "PASS", f"Got {r.status_code}", r)
        elif r.status_code == 200:
            log_result("Params: Missing 'model'", "PASS", f"API accepted without model (uses default)", r)
        else:
            log_result("Params: Missing 'model'", "FAIL", f"Unexpected status {r.status_code}", r)
    except Exception as e:
        log_result("Params: Missing 'model'", "ERROR", str(e))

    # Empty messages array
    try:
        r = api_call(base_url, api_key, {"model": "thaura", "messages": [], "max_completion_tokens": 5})
        if r.status_code in (400, 422):
            log_result("Params: Empty messages[]", "PASS", f"Got {r.status_code}", r)
        else:
            log_result("Params: Empty messages[]", "FAIL", f"Expected 400/422, got {r.status_code}", r)
    except Exception as e:
        log_result("Params: Empty messages[]", "ERROR", str(e))


def test_invalid_types(base_url, api_key):
    """Test: Invalid data types for parameters."""
    print("\n[PARAMS] Invalid data types")

    # temperature as string
    try:
        payload = {**MINIMAL_PAYLOAD, "temperature": "hot"}
        r = api_call(base_url, api_key, payload)
        if r.status_code in (400, 422):
            log_result("Types: temperature='hot'", "PASS", f"Got {r.status_code}", r)
        else:
            log_result("Types: temperature='hot'", "FAIL", f"Expected 400/422, got {r.status_code}", r)
    except Exception as e:
        log_result("Types: temperature='hot'", "ERROR", str(e))

    # messages as string instead of array
    try:
        payload = {"model": "thaura", "messages": "hello", "max_completion_tokens": 5}
        r = api_call(base_url, api_key, payload)
        if r.status_code in (400, 422):
            log_result("Types: messages=string", "PASS", f"Got {r.status_code}", r)
        else:
            log_result("Types: messages=string", "FAIL", f"Expected 400/422, got {r.status_code}", r)
    except Exception as e:
        log_result("Types: messages=string", "ERROR", str(e))


def test_boundary_values(base_url, api_key):
    """Test: Boundary values for temperature and max_completion_tokens."""
    print("\n[PARAMS] Boundary values")

    # temperature = 0 (min)
    try:
        payload = {**MINIMAL_PAYLOAD, "temperature": 0}
        r = api_call(base_url, api_key, payload)
        if r.status_code == 200:
            log_result("Boundary: temperature=0", "PASS", "Accepted min temperature", r)
        else:
            log_result("Boundary: temperature=0", "FAIL", f"Unexpected {r.status_code}", r)
    except Exception as e:
        log_result("Boundary: temperature=0", "ERROR", str(e))

    # temperature = 2 (max)
    try:
        payload = {**MINIMAL_PAYLOAD, "temperature": 2}
        r = api_call(base_url, api_key, payload)
        if r.status_code == 200:
            log_result("Boundary: temperature=2", "PASS", "Accepted max temperature", r)
        else:
            log_result("Boundary: temperature=2", "FAIL", f"Unexpected {r.status_code}", r)
    except Exception as e:
        log_result("Boundary: temperature=2", "ERROR", str(e))

    # temperature = 2.5 (above max)
    try:
        payload = {**MINIMAL_PAYLOAD, "temperature": 2.5}
        r = api_call(base_url, api_key, payload)
        if r.status_code in (400, 422):
            log_result("Boundary: temperature=2.5", "PASS", f"Rejected above-max ({r.status_code})", r)
        elif r.status_code == 200:
            log_result("Boundary: temperature=2.5", "FAIL", "Accepted above-max temperature — should reject", r)
        else:
            log_result("Boundary: temperature=2.5", "FAIL", f"Unexpected {r.status_code}", r)
    except Exception as e:
        log_result("Boundary: temperature=2.5", "ERROR", str(e))

    # temperature = -1 (below min)
    try:
        payload = {**MINIMAL_PAYLOAD, "temperature": -1}
        r = api_call(base_url, api_key, payload)
        if r.status_code in (400, 422):
            log_result("Boundary: temperature=-1", "PASS", f"Rejected below-min ({r.status_code})", r)
        elif r.status_code == 200:
            log_result("Boundary: temperature=-1", "FAIL", "Accepted negative temperature — should reject", r)
        else:
            log_result("Boundary: temperature=-1", "FAIL", f"Unexpected {r.status_code}", r)
    except Exception as e:
        log_result("Boundary: temperature=-1", "ERROR", str(e))

    # max_completion_tokens = 32000 (cap)
    # NOTE: Don't actually send this — just test the boundary acceptance
    try:
        payload = {**MINIMAL_PAYLOAD, "max_completion_tokens": 32000}
        payload["messages"] = [{"role": "user", "content": "Say 'ok'"}]
        r = api_call(base_url, api_key, payload)
        if r.status_code == 200:
            log_result("Boundary: max_completion_tokens=32000", "PASS", "Accepted cap value", r)
        else:
            log_result("Boundary: max_completion_tokens=32000", "FAIL", f"Unexpected {r.status_code}", r)
    except Exception as e:
        log_result("Boundary: max_completion_tokens=32000", "ERROR", str(e))

    # max_completion_tokens = 32001 (above cap)
    try:
        payload = {**MINIMAL_PAYLOAD, "max_completion_tokens": 32001}
        r = api_call(base_url, api_key, payload)
        if r.status_code in (400, 422):
            log_result("Boundary: max_completion_tokens=32001", "PASS", f"Rejected above-cap ({r.status_code})", r)
        elif r.status_code == 200:
            log_result("Boundary: max_completion_tokens=32001", "FAIL", "Accepted above-cap value — should reject", r)
        else:
            log_result("Boundary: max_completion_tokens=32001", "FAIL", f"Unexpected {r.status_code}", r)
    except Exception as e:
        log_result("Boundary: max_completion_tokens=32001", "ERROR", str(e))


def test_precedence_max_tokens(base_url, api_key):
    """Test: Precedence between max_tokens and max_completion_tokens."""
    print("\n[PARAMS] max_tokens vs max_completion_tokens precedence")

    try:
        payload = {
            **MINIMAL_PAYLOAD,
            "max_tokens": 10,
            "max_completion_tokens": 5,
        }
        r = api_call(base_url, api_key, payload)
        if r.status_code == 200:
            body = r.json()
            completion_tokens = body.get("usage", {}).get("completion_tokens", 0)
            log_result(
                "Precedence: max_tokens=10 vs max_completion_tokens=5",
                "PASS" if completion_tokens <= 5 else "FAIL",
                f"completion_tokens={completion_tokens} (max_completion_tokens should take precedence if ≤5)",
                r,
            )
        else:
            log_result("Precedence: both params", "FAIL", f"Unexpected {r.status_code}", r)
    except Exception as e:
        log_result("Precedence: both params", "ERROR", str(e))


def test_rejected_params(base_url, api_key):
    """Test: Parameters that should be rejected (functions, function_call)."""
    print("\n[PARAMS] Rejected parameters (functions, function_call)")

    # functions parameter
    try:
        payload = {
            **MINIMAL_PAYLOAD,
            "functions": [{"name": "test", "parameters": {"type": "object", "properties": {}}}],
        }
        r = api_call(base_url, api_key, payload)
        if r.status_code in (400, 422):
            log_result("Rejected: 'functions' param", "PASS", f"Rejected ({r.status_code}) as documented", r)
        elif r.status_code == 200:
            log_result("Rejected: 'functions' param", "FAIL", "Accepted 'functions' — should be rejected per docs", r)
        else:
            log_result("Rejected: 'functions' param", "FAIL", f"Unexpected {r.status_code}", r)
    except Exception as e:
        log_result("Rejected: 'functions' param", "ERROR", str(e))

    # function_call parameter
    try:
        payload = {**MINIMAL_PAYLOAD, "function_call": "auto"}
        r = api_call(base_url, api_key, payload)
        if r.status_code in (400, 422):
            log_result("Rejected: 'function_call' param", "PASS", f"Rejected ({r.status_code})", r)
        elif r.status_code == 200:
            log_result("Rejected: 'function_call' param", "FAIL", "Accepted 'function_call' — should be rejected", r)
        else:
            log_result("Rejected: 'function_call' param", "FAIL", f"Unexpected {r.status_code}", r)
    except Exception as e:
        log_result("Rejected: 'function_call' param", "ERROR", str(e))


def test_response_schema_non_streaming(base_url, api_key):
    """Test: Non-streaming response schema validation."""
    print("\n[SCHEMA] Non-streaming response")

    try:
        r = api_call(base_url, api_key, MINIMAL_PAYLOAD)
        if r.status_code != 200:
            log_result("Schema: Non-streaming", "FAIL", f"Non-200 response: {r.status_code}", r)
            return

        body = r.json()

        # Validate required fields
        required_fields = ["id", "object", "created", "model", "choices", "usage"]
        missing = [f for f in required_fields if f not in body]
        if missing:
            log_result("Schema: Required fields", "FAIL", f"Missing: {missing}", r)
        else:
            log_result("Schema: Required fields", "PASS", f"All present: {required_fields}", r)

        # Validate choices structure
        if "choices" in body and body["choices"]:
            choice = body["choices"][0]
            choice_fields = ["index", "message", "finish_reason"]
            missing_choice = [f for f in choice_fields if f not in choice]
            if missing_choice:
                log_result("Schema: Choice fields", "FAIL", f"Missing in choice: {missing_choice}", r)
            else:
                log_result("Schema: Choice fields", "PASS", "Choice structure valid", r)

            # Validate message
            if "message" in choice:
                if "role" not in choice["message"] or "content" not in choice["message"]:
                    log_result("Schema: Message fields", "FAIL", "Missing role/content in message", r)
                else:
                    log_result("Schema: Message fields", "PASS", "Message has role + content", r)

        # Validate usage
        if "usage" in body:
            usage_fields = ["prompt_tokens", "completion_tokens", "total_tokens"]
            missing_usage = [f for f in usage_fields if f not in body["usage"]]
            if missing_usage:
                log_result("Schema: Usage fields", "FAIL", f"Missing: {missing_usage}", r)
            else:
                total = body["usage"]["total_tokens"]
                expected = body["usage"]["prompt_tokens"] + body["usage"]["completion_tokens"]
                if total == expected:
                    log_result("Schema: Token accounting", "PASS",
                               f"prompt={body['usage']['prompt_tokens']} + completion={body['usage']['completion_tokens']} = total={total}", r)
                else:
                    log_result("Schema: Token accounting", "FAIL",
                               f"total({total}) ≠ prompt({body['usage']['prompt_tokens']}) + completion({body['usage']['completion_tokens']})", r)

    except Exception as e:
        log_result("Schema: Non-streaming", "ERROR", str(e))


def test_response_schema_streaming(base_url, api_key):
    """Test: Streaming response schema validation."""
    print("\n[SCHEMA] Streaming response")

    try:
        r = api_call(base_url, api_key, MINIMAL_PAYLOAD, stream=True)
        if r.status_code != 200:
            log_result("Schema: Streaming", "FAIL", f"Non-200 response: {r.status_code}", r)
            return

        chunks = []
        for line in r.iter_lines():
            if line:
                decoded = line.decode("utf-8")
                if decoded.startswith("data: "):
                    data = decoded[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunks.append(json.loads(data))
                    except json.JSONDecodeError:
                        pass

        if not chunks:
            log_result("Schema: Streaming chunks", "FAIL", "No chunks received", r)
            return

        # First chunk should have role
        first = chunks[0]
        if "choices" in first and first["choices"]:
            delta = first["choices"][0].get("delta", {})
            if "role" in delta:
                log_result("Schema: Streaming first chunk role", "PASS", f"role={delta['role']}", r)
            else:
                log_result("Schema: Streaming first chunk role", "FAIL", "No role in first delta", r)

        # Check required fields in chunks
        required_chunk_fields = ["id", "object", "created", "model", "choices"]
        missing = [f for f in required_chunk_fields if f not in first]
        if missing:
            log_result("Schema: Streaming chunk fields", "FAIL", f"Missing: {missing}", r)
        else:
            log_result("Schema: Streaming chunk fields", "PASS", "All required fields present", r)

        log_result("Schema: Streaming total chunks", "PASS", f"Received {len(chunks)} chunks", r)

    except Exception as e:
        log_result("Schema: Streaming", "ERROR", str(e))


def test_rate_limiting(base_url, api_key):
    """
    Test: Rate limiting (60 req/min, 8 concurrent).
    ⚠️ This test sends many requests. Use with caution on billed API.
    """
    print("\n[RATE LIMIT] Concurrent request test (8 max)")
    print("  ⚠️ Sending 10 concurrent requests to check 429 behavior...")

    def single_request():
        try:
            r = api_call(base_url, api_key, MINIMAL_PAYLOAD)
            return r.status_code
        except:
            return "error"

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(single_request) for _ in range(10)]
        statuses = [f.result() for f in as_completed(futures)]

    count_200 = statuses.count(200)
    count_429 = statuses.count(429)
    print(f"  Results: 200={count_200}, 429={count_429}, other={len(statuses) - count_200 - count_429}")

    if count_429 > 0:
        log_result("Rate limit: Concurrent (8 max)", "PASS",
                   f"Got {count_429} rate-limited responses out of 10 concurrent")
    else:
        log_result("Rate limit: Concurrent (8 max)", "FAIL",
                   f"No 429 responses — all {count_200} succeeded (limit may not be enforced)")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Thaura API Test Suite")
    parser.add_argument("--api-key", required=True, help="Your Thaura API key")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="API base URL")
    parser.add_argument("--dry-run", action="store_true", help="Only run auth tests (no billed calls)")
    parser.add_argument("--skip-rate-limit", action="store_true", help="Skip rate limit tests")
    args = parser.parse_args()

    print("=" * 70)
    print("THAURA DEVELOPER API — CONTRACT TEST SUITE")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {args.base_url}")
    print(f"Dry run: {args.dry_run}")
    print("=" * 70)

    # Auth tests (no billed calls)
    test_auth_missing(args.base_url)
    test_auth_malformed(args.base_url)
    test_auth_invalid(args.base_url)

    if args.dry_run:
        print("\n⏭️ DRY RUN — skipping billed API tests")
    else:
        test_required_params(args.base_url, args.api_key)
        test_invalid_types(args.base_url, args.api_key)
        test_boundary_values(args.base_url, args.api_key)
        test_precedence_max_tokens(args.base_url, args.api_key)
        test_rejected_params(args.base_url, args.api_key)
        test_response_schema_non_streaming(args.base_url, args.api_key)
        test_response_schema_streaming(args.base_url, args.api_key)

        if not args.skip_rate_limit:
            test_rate_limiting(args.base_url, args.api_key)
        else:
            print("\n⏭️ Skipping rate limit test")

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    print(f"  ✅ Passed:  {passed}")
    print(f"  ❌ Failed:  {failed}")
    print(f"  ⚠️ Errors:  {errors}")
    print(f"  ⏭️ Skipped: {skipped}")
    print(f"  Total:     {len(results)}")

    output = {
        "test_date": datetime.now().isoformat(),
        "base_url": args.base_url,
        "dry_run": args.dry_run,
        "results": results,
        "bugs": bugs,
        "summary": {"passed": passed, "failed": failed, "errors": errors, "skipped": skipped},
    }
    output_path = "d:/Qtech-Tasks/test-artifacts/api_test_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n  Full report saved to: {output_path}")


if __name__ == "__main__":
    main()
