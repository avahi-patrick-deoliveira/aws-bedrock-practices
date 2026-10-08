import json
import random
import re
import time
from statistics import mean

import boto3

from generate_dataset import SYSTEM_PROMPT
from validate_dataset import count_sentences

JUDGE_MODEL = "us.anthropic.claude-sonnet-4-6"

# Variant A: base model, no style instructions (control).
# Variant B: stand-in for the fine-tuned model (base model + style system prompt).
# To test a real fine-tuned model, set model_id to the custom model ARN
# (needs Provisioned Throughput) and system to None.
VARIANTS = {
    "A_base": {"model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0", "system": None},
    "B_tuned_standin": {"model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0", "system": SYSTEM_PROMPT},
}

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')


def ask(model_id, question, system=None, max_tokens=300):
    kwargs = {
        "modelId": model_id,
        "messages": [{"role": "user", "content": [{"text": question}]}],
        "inferenceConfig": {"maxTokens": max_tokens, "temperature": 0},
    }
    if system:
        kwargs["system"] = [{"text": system}]
    start = time.time()
    response = bedrock_runtime.converse(**kwargs)
    return (response['output']['message']['content'][0]['text'].strip(),
            response['usage']['outputTokens'], time.time() - start)


def follows_style(answer):
    return "Next step:" in answer and count_sentences(answer) <= 3


def judge(question, reference, answer_x, answer_y):
    """Pairwise judge. Returns 'X', 'Y' or 'TIE' (only accuracy and helpfulness, not style)."""
    prompt = f"""Question: {question}
Reference answer: {reference}

Answer X: {answer_x}

Answer Y: {answer_y}

Which answer is more accurate and helpful? Ignore length and formatting.
Reply with only one word: X, Y or TIE."""
    text, _, _ = ask(JUDGE_MODEL, prompt, max_tokens=5)
    match = re.search(r"\b(X|Y|TIE)\b", text.upper())
    return match.group(1) if match else "TIE"


if __name__ == "__main__":
    random.seed(1)
    rows = [json.loads(line) for line in open("dataset/validation.jsonl")]
    results = {name: [] for name in VARIANTS}
    wins = {"A_base": 0, "B_tuned_standin": 0, "TIE": 0}

    for row in rows:
        question = row["messages"][0]["content"][0]["text"]
        reference = row["messages"][1]["content"][0]["text"]
        answers = {}
        for name, v in VARIANTS.items():
            text, tokens, seconds = ask(v["model_id"], question, v["system"])
            answers[name] = text
            results[name].append({"style": follows_style(text), "tokens": tokens, "seconds": seconds})

        # Randomize which answer is shown as X, to avoid position bias
        order = list(VARIANTS)
        random.shuffle(order)
        verdict = judge(question, reference, answers[order[0]], answers[order[1]])
        wins["TIE" if verdict == "TIE" else order[0 if verdict == "X" else 1]] += 1

    print(f"{len(rows)} validation questions\n")
    for name, r in results.items():
        print(f"{name}: style followed {sum(x['style'] for x in r)}/{len(r)}, "
              f"avg output tokens {mean(x['tokens'] for x in r):.0f}, "
              f"avg latency {mean(x['seconds'] for x in r):.2f}s")
    print(f"\nJudge preference (accuracy and helpfulness): {wins}")
