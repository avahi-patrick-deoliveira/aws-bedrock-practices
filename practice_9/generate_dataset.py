import json
import random
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import boto3

from validate_dataset import validate_example

GENERATOR_MODEL = "us.anthropic.claude-sonnet-4-6"

SYSTEM_PROMPT = ("You are a friendly AWS support assistant. Answer in at most two sentences, "
                 "then finish with one line that starts with 'Next step:'.")

TOPICS = ["Amazon S3", "AWS Lambda", "Amazon EC2", "AWS IAM", "Amazon Bedrock",
          "Amazon DynamoDB", "VPC and networking", "Amazon CloudWatch monitoring",
          "AWS cost optimization", "Amazon RDS"]
PER_TOPIC = 20

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')


def generate(topic):
    prompt = f"""Write {PER_TOPIC} different, realistic customer questions about {topic} and the ideal support reply to each.

Rules for every reply:
- Friendly and factually accurate.
- One or two sentences with the answer, then a final line that starts with "Next step:" followed by one short sentence.
- Never more than three sentences in total.

Reply with only a JSON list of objects with the keys "question" and "answer"."""
    response = bedrock_runtime.converse(
        modelId=GENERATOR_MODEL,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 6000, "temperature": 1.0},
    )
    text = response['output']['message']['content'][0]['text']
    return json.loads(re.search(r"\[.*\]", text, re.S).group())


def to_example(question, answer):
    """Bedrock fine-tuning format (bedrock-conversation-2024)."""
    return {
        "schemaVersion": "bedrock-conversation-2024",
        "system": [{"text": SYSTEM_PROMPT}],
        "messages": [
            {"role": "user", "content": [{"text": question.strip()}]},
            {"role": "assistant", "content": [{"text": answer.strip()}]},
        ],
    }


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=5) as pool:
        batches = list(pool.map(generate, TOPICS))

    seen, examples, rejected = set(), [], 0
    for batch in batches:
        for item in batch:
            key = item["question"].strip().lower()
            example = to_example(item["question"], item["answer"])
            if key in seen or validate_example(example):
                rejected += 1
                continue
            seen.add(key)
            examples.append(example)
    print(f"Rejected {rejected} duplicate or invalid examples")

    random.seed(42)
    random.shuffle(examples)
    split = int(len(examples) * 0.9)
    Path("dataset").mkdir(exist_ok=True)
    for name, rows in [("train", examples[:split]), ("validation", examples[split:])]:
        with open(f"dataset/{name}.jsonl", "w") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"{len(examples)} unique examples: {split} train, {len(examples) - split} validation")
