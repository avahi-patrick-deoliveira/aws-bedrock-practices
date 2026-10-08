import boto3
import json
import time

MODEL_ID = 'us.anthropic.claude-sonnet-4-5-20250929-v1:0'

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')


def invoke_claude(prompt, max_tokens=1000):
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    })

    start = time.time()
    response = bedrock_runtime.invoke_model(modelId=MODEL_ID, body=body)
    response_body = json.loads(response['body'].read())
    elapsed = time.time() - start

    return {
        "text": response_body['content'][0]['text'],
        "stop_reason": response_body['stop_reason'],
        "input_tokens": response_body['usage']['input_tokens'],
        "output_tokens": response_body['usage']['output_tokens'],
        "seconds": round(elapsed, 2),
    }


PROMPTS = [
    "Explain what AWS Bedrock is in 3 paragraphs",
    "What is the difference between Amazon Bedrock and Amazon SageMaker?",
    "Give me 3 real-world use cases for generative AI in customer support.",
    "Explain what a foundation model is to a 10-year-old.",
]

results = []
for prompt in PROMPTS:
    for max_tokens in (1000, 500):
        r = invoke_claude(prompt, max_tokens)
        r.update(prompt=prompt, max_tokens=max_tokens)
        results.append(r)
        print(f"[{max_tokens}] {r['seconds']}s out={r['output_tokens']} "
              f"stop={r['stop_reason']} :: {prompt}")

with open('results.json', 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
