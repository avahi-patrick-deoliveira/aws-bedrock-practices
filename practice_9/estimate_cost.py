import json
import sys

# Assumed prices. Check the current Amazon Bedrock pricing page before relying on them.
TRAINING_USD_PER_1K_TOKENS = 0.001     # fine-tuning, per 1,000 tokens processed
STORAGE_USD_PER_MONTH = 1.95           # custom model storage

CHARS_PER_TOKEN = 4                    # rough estimate for English text


def dataset_tokens(path):
    """Estimate the tokens in a JSONL training file (system + user + assistant text)."""
    chars, examples = 0, 0
    with open(path) as f:
        for line in f:
            ex = json.loads(line)
            chars += sum(len(s["text"]) for s in ex["system"])
            chars += sum(len(m["content"][0]["text"]) for m in ex["messages"])
            examples += 1
    return examples, chars // CHARS_PER_TOKEN


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "dataset/train.jsonl"
    examples, tokens = dataset_tokens(path)
    print(f"{path}: {examples} examples, about {tokens:,} tokens per epoch\n")

    print("| Epochs | Tokens trained | Training cost (USD) |")
    print("| --- | --- | --- |")
    for epochs in (1, 2, 3, 5):
        trained = tokens * epochs
        print(f"| {epochs} | {trained:,} | {trained / 1000 * TRAINING_USD_PER_1K_TOKENS:.2f} |")

    print(f"\nStorage of the custom model: {STORAGE_USD_PER_MONTH} USD per month")
    print("Not included: Provisioned Throughput, which is required to run a custom model "
          "and is billed per hour. Check the pricing page for the hourly rate.")
