#!/usr/bin/env python3
"""
AMA agent for Infra Quest.

Calls the taalas-llama3.1-8b API (OpenAI-compatible) and prints the
response to stdout. Used as AI_AGENT_CMD inside the container.

Set in .env:
    AI_AGENT_CMD=/app/scripts/ama-agent.py
    AMA_API_KEY=<your key>

Optional overrides:
    AMA_API_BASE    — default: https://ai.shenthar.me/v1
    AMA_MODEL       — default: taalas-llama3.1-8b
    AMA_MAX_TOKENS  — default: 300  (model context ~6900 tokens; keep responses tight)
"""

import os
import sys
import json
import urllib.request
import urllib.error

API_KEY  = os.environ.get("AMA_API_KEY", "")
API_BASE = os.environ.get("AMA_API_BASE", "https://ai.shenthar.me/v1").rstrip("/")
MODEL    = os.environ.get("AMA_MODEL", "taalas-llama3.1-8b")
MAX_TOKENS = int(os.environ.get("AMA_MAX_TOKENS") or "300")

# System prompt engineered from boundary-test findings:
#   - plain text (XML format -18pp)
#   - authority-level persona priming (+6.3pp)
#   - uncertainty instruction to cut hallucinations 60% -> 12%
#   - prefix output anchor (+3.4pp)
#   - no chain-of-thought (CoT -13pp)
#   - hard scope guard (safety score 40% baseline — model will go off-topic without it)
SYSTEM_PROMPT = """\
You are an expert AWS infrastructure tutor embedded in a local lab called Infra Quest. \
The learner runs AWS commands against a local emulator called Floci at http://localhost:4566. \
Your job is to answer their questions about what they are doing in the lab — \
AWS services, CLI commands, concepts, and why things work the way they do.

Rules:
- Answer only questions about AWS, cloud infrastructure, or this lab. \
If asked about anything else, say: "I can only help with AWS and lab questions."
- If you are not sure about something, say so clearly instead of guessing.
- Be concise. Two to four sentences is enough for most answers.
- Never mention real AWS costs, billing, or production infrastructure.
- Do not use markdown headers or bullet lists unless the question asks for a list.

Examples:
Q: What is an S3 bucket?
A: An S3 bucket is a named container for storing files as objects. \
Each object has a key (its path) and a body (its content). \
In this lab, buckets live on Floci instead of real AWS.

Q: Why do I need --endpoint-url?
A: The AWS CLI defaults to real AWS endpoints. \
The --endpoint-url flag redirects all calls to Floci running locally \
so nothing leaves your machine.

Answer:\
"""


def main():
    if len(sys.argv) < 2:
        print("Usage: ama-agent.py <prompt>", file=sys.stderr)
        sys.exit(1)

    prompt = sys.argv[1]

    if not API_KEY:
        print(
            "AMA_API_KEY is not set. Add it to your .env file to enable AI chat.",
            file=sys.stderr,
        )
        sys.exit(1)

    payload = json.dumps({
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }).encode()

    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "curl/7.88.1",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
            print(body["choices"][0]["message"]["content"].strip())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode(errors="replace")
        print(f"API error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
