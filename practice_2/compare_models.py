import boto3
import json
import time

MODELS = {
    "haiku-4.5": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "sonnet-4.5": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "opus-4.6": "us.anthropic.claude-opus-4-6-v1",
}

PROMPTS = {
    "factual": "What is the difference between Amazon S3 and Amazon EBS?",
    "code": "Write a Python function that checks whether a string is a palindrome.",
    "reasoning": "A bat and a ball cost $1.10 together. The bat costs $1.00 more than the ball. How much does the ball cost? Explain briefly.",
    "creative": "Write a short poem about the cloud, in 4 lines.",
}

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')


def invoke(model_id, prompt):
    start = time.time()
    response = bedrock_runtime.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 800},
    )
    return {
        "text": response['output']['message']['content'][0]['text'],
        "output_tokens": response['usage']['outputTokens'],
        "seconds": round(time.time() - start, 2),
    }


def compare(prompt):
    results = {}
    for name, model_id in MODELS.items():
        try:
            results[name] = invoke(model_id, prompt)
        except Exception as e:
            results[name] = {"error": str(e)}
    return results


all_results = {}
for label, prompt in PROMPTS.items():
    print(f"\n=== {label}: {prompt}")
    all_results[label] = compare(prompt)
    for name, r in all_results[label].items():
        if "error" in r:
            print(f"[{name}] ERROR: {r['error']}")
        else:
            print(f"[{name}] {r['seconds']}s, {r['output_tokens']} tokens")

with open('results_practice_2.json', 'w') as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)
