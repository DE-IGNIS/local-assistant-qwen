"""
benchmarks/bench_v1.py
======================
Benchmark v1 — system tools only.

Tests that the agent correctly routes prompts to:
  - get_system_info
  - get_current_time

HOW IT WORKS
------------
Each test case defines:
  prompt         : the user message sent to the agent
  expected_tools : tools that MUST appear in the message history
  check          : a function(final_response: str) -> bool that validates
                   the quality of the agent's final answer

After running the agent, we inspect the recorded message history to verify:
  1. Tool was called (routing check)
  2. Final response passes the quality check (content check)

RUNNING
-------
  python -m benchmarks.bench_v1
"""

import sys
import os

# Allow running from project root: python -m benchmarks.bench_v1
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import run_agent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_messages(prompt: str) -> list:
    """Return a fresh message list with the system prompt + one user turn."""
    return [
        {
            "role": "system",
            "content": (
                "You are a local assistant. Use tools step by step. "
                "Call another tool if you need more information."
            ),
        },
        {"role": "user", "content": prompt},
    ]


def tools_called(messages: list) -> list:
    """
    Extract the names of every tool that was actually called during the run.

    The agent appends tool-role messages in the format:
        {"role": "tool", "tool_name": "<name>", "content": "..."}
    """
    return [
        msg["tool_name"]
        for msg in messages
        if msg.get("role") == "tool" and "tool_name" in msg
    ]


def run_case(name, prompt, expected_tools, check):
    """
    Run a single benchmark case. Returns True on pass, False on fail.

    Args:
        name           : Human-readable label for this test.
        prompt         : User message to send to the agent.
        expected_tools : List of tool names that must appear in history.
        check          : Callable(response_text: str) -> bool.
    """
    print(f"\n{'='*60}")
    print(f"CASE  : {name}")
    print(f"PROMPT: {prompt!r}")
    print(f"{'='*60}")

    messages = make_messages(prompt)

    try:
        response = run_agent(messages)
        response_text = response.content or ""
    except Exception as e:
        print(f"  [ERROR] Agent raised an exception: {e}")
        return False

    called = tools_called(messages)
    print(f"  Tools called : {called if called else '(none)'}")
    print(f"  Response     : {response_text[:300]!r}")

    # --- Check 1: Did the agent call the expected tools? ---
    missing = [t for t in expected_tools if t not in called]
    if missing:
        print(f"  [FAIL] Expected tool(s) not called: {missing}")
        return False
    print(f"  [OK]   Tool routing correct")

    # --- Check 2: Does the response contain the right content? ---
    if not check(response_text):
        print(f"  [FAIL] Response quality check failed")
        return False
    print(f"  [OK]   Response quality check passed")

    return True


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------

CASES = [
    {
        "name": "get_system_info — OS name",
        "prompt": "What operating system am I running?",
        "expected_tools": ["get_system_info"],
        # The response must mention a known OS name
        "check": lambda r: any(
            os_name in r.lower()
            for os_name in ["windows", "linux", "darwin", "mac", "ubuntu"]
        ),
    },
    {
        "name": "get_system_info — Python version",
        "prompt": "What version of Python is running on this system?",
        "expected_tools": ["get_system_info"],
        # Response must contain a version-like pattern, e.g. "3.11" or "3.12"
        "check": lambda r: any(f"3.{minor}" in r for minor in range(8, 15)),
    },
    {
        "name": "get_current_time — direct phrasing",
        "prompt": "What time is it right now?",
        "expected_tools": ["get_current_time"],
        # Response must contain AM or PM (12-hour format)
        "check": lambda r: "am" in r.lower() or "pm" in r.lower(),
    },
    {
        "name": "get_current_time — indirect phrasing",
        "prompt": "Can you tell me the current local time?",
        "expected_tools": ["get_current_time"],
        "check": lambda r: "am" in r.lower() or "pm" in r.lower(),
    },
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main():
    print("\nBENCHMARK v1 — System Tools")
    print(f"Running {len(CASES)} case(s)...\n")

    results = []
    for case in CASES:
        passed = run_case(
            name=case["name"],
            prompt=case["prompt"],
            expected_tools=case["expected_tools"],
            check=case["check"],
        )
        results.append((case["name"], passed))

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    passed_count = sum(1 for _, p in results if p)
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}]  {name}")
    print(f"\n  {passed_count}/{len(results)} passed")
    print(f"{'='*60}\n")

    # Exit with non-zero code if any case failed (useful for CI)
    sys.exit(0 if passed_count == len(results) else 1)


if __name__ == "__main__":
    main()
