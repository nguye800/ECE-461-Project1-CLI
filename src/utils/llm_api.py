#!/usr/bin/env python3
"""
chat_prompt.py — Send a command-line prompt to OpenAI's ChatGPT API and print the response.

Usage:
    python llm_api.py

    https://genai.rcac.purdue.edu/

"""

import argparse
import os
from dotenv import load_dotenv, dotenv_values
import requests

class llmAPI():

    def make_prompt(self, token, role, content):
        url = "https://genai.rcac.purdue.edu/api/chat/completions"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        body = {
            "model": "llama3.1:latest",
            "messages": [
            {
                "role": role,
                "content": content
            }
            ],
            "stream": False
        }
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

    def main(self, text):
        # Get API key from env variable
        load_dotenv()
        api_key = os.environ.get("GEN_AI_STUDIO_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GENAI_STUDIO_TOKEN environment variable")

        response = self.make_prompt(api_key, role="user", content=text)

        return response

if __name__ == "__main__":
    apiTester = llmAPI()
    print(apiTester.main("Please give me a list of assessment areas that make good quality code"))
