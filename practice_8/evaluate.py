import json
import re
import time
from concurrent.futures import ThreadPoolExecutor

import boto3

MODELS = {
    "haiku-4.5": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "sonnet-4.6": "us.anthropic.claude-sonnet-4-6",
    "opus-4.6": "us.anthropic.claude-opus-4-6-v1",
}
JUDGE_MODEL = MODELS["sonnet-4.6"]

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')


def converse(model_id, prompt, max_tokens):
    start = time.time()
    response = bedrock_runtime.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": 0},
    )
    return {
        "text": response['output']['message']['content'][0]['text'].strip(),
        "input_tokens": response['usage']['inputTokens'],
        "output_tokens": response['usage']['outputTokens'],
        "seconds": time.time() - start,
    }


def judge(question, reference, answer):
    """LLM-as-judge: score the answer from 1 to 5 on three criteria."""
    prompt = f"""You are grading an answer to a question.

Question: {question}
Reference answer: {reference}
Answer to grade: {answer}

Score the answer from 1 (very poor) to 5 (excellent) on:
- correctness: is it factually correct compared to the reference?
- completeness: does it cover what the question asks?
- conciseness: is it direct, without unnecessary text?

Reply with only a JSON object, for example {{"correctness": 5, "completeness": 4, "conciseness": 5}}."""
    out = converse(JUDGE_MODEL, prompt, 60)["text"]
    try:
        return json.loads(re.search(r"\{.*?\}", out, re.S).group())
    except Exception:
        return {"correctness": None, "completeness": None, "conciseness": None}


def evaluate_item(args):
    item, name = args
    prompt = f"{item['question']}\nAnswer in one or two sentences."
    try:
        r = converse(MODELS[name], prompt, 150)
        r["scores"] = judge(item['question'], item['reference'], r['text'])
    except Exception as e:
        r = {"error": str(e)}
    return {**item, "model": name, **r}


if __name__ == "__main__":
    items = json.load(open("benchmark.json"))
    jobs = [(item, name) for item in items for name in MODELS]
    print(f"Running {len(jobs)} answers + judgments...")

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(evaluate_item, jobs))

    errors = [r for r in results if "error" in r]
    print(f"Done. {len(results) - len(errors)} ok, {len(errors)} errors")
    with open("results_practice_8.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
