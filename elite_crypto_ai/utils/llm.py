# utils/llm.py

import openai
import os
import random

openai.api_key = os.getenv("OPENAI_API_KEY")

MODELS = ["gpt-4", "gpt-3.5-turbo"]


def query_llm_with_fallback(prompt):
    for model in MODELS:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["choices"][0]["message"]["content"]
        except Exception:
            continue
    raise Exception("All LLM model calls failed.")
