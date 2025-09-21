#!/usr/bin/env python3
"""
chat_prompt.py — Send a command-line prompt to OpenAI's ChatGPT API and print the response.

Usage:
    python chat_prompt.py "Write a haiku about autumn leaves"

"""

import argparse
import os
from openai import OpenAI

def main():
    parser = argparse.ArgumentParser(description="Send a prompt to the OpenAI ChatGPT API")
    parser.add_argument("prompt", help="The text prompt to send")
    parser.add_argument("--model", default="gpt-4.1-mini", help="Model name (default: gpt-4.1-mini)")
    args = parser.parse_args()

    # Get API key from env variable
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable")

    client = OpenAI(api_key=api_key)

    # Call the chat completions API
    response = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": args.prompt}],
    )

    # Print the model’s reply
    print(response.choices[0].message.content.strip())

if __name__ == "__main__":
    main()
