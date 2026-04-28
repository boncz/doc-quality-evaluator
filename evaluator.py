import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from prompts import EVALUATOR_SYSTEM_PROMPT, EVALUATOR_PROMPT

load_dotenv()

client = Anthropic()

def evaluate_documentation(documentation: str, label: str = "unnamed") -> dict:
    """
    Score a piece of documentation on clarity, accuracy, and completeness.
    Returns a structured result with scores and reasoning.
    """
    print(f"  Evaluating: {label}...")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=EVALUATOR_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": EVALUATOR_PROMPT.format(documentation=documentation)
            }
        ]
    )

    raw = response.content[0].text

    # Strip markdown code fences if Claude adds them
    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
        clean = clean.strip()

    scores = json.loads(clean)
    scores["label"] = label
    scores["char_count"] = len(documentation)

    return scores


def evaluate_many(docs: list[dict]) -> list[dict]:
    """
    Evaluate a list of docs. Each dict should have 'content' and 'label' keys.
    """
    results = []
    for doc in docs:
        result = evaluate_documentation(doc["content"], doc["label"])
        results.append(result)
    return results