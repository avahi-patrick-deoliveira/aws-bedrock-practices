import json
import re
import sys

MIN_EXAMPLES = 32          # Bedrock minimum for fine-tuning
MAX_CHARS = 20000          # rough guard against very long examples
MAX_SENTENCES = 3


def count_sentences(text):
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s])


def validate_example(ex):
    """Return a list of problems found in one example (empty list = valid)."""
    errors = []
    if ex.get("schemaVersion") != "bedrock-conversation-2024":
        errors.append("schemaVersion must be 'bedrock-conversation-2024'")
    system = ex.get("system")
    if not (isinstance(system, list) and system and system[0].get("text", "").strip()):
        errors.append("missing system prompt")

    messages = ex.get("messages")
    if not isinstance(messages, list) or len(messages) < 2:
        return errors + ["messages must have at least a user and an assistant turn"]

    for i, m in enumerate(messages):
        expected = "user" if i % 2 == 0 else "assistant"
        if m.get("role") != expected:
            errors.append(f"message {i} should have role '{expected}'")
        content = m.get("content")
        if not (isinstance(content, list) and content and content[0].get("text", "").strip()):
            errors.append(f"message {i} has empty content")
    if messages[-1].get("role") != "assistant":
        errors.append("last message must be from the assistant")
    if errors:
        return errors

    total = sum(len(m["content"][0]["text"]) for m in messages)
    if total > MAX_CHARS:
        errors.append(f"example too long ({total} characters)")

    # Style rules of this use case
    answer = messages[-1]["content"][0]["text"].strip()
    if "Next step:" not in answer:
        errors.append("answer is missing 'Next step:'")
    if count_sentences(answer) > MAX_SENTENCES:
        errors.append(f"answer has more than {MAX_SENTENCES} sentences")
    return errors


def validate_file(path):
    problems, questions = [], []
    with open(path) as f:
        for n, line in enumerate(f, 1):
            try:
                ex = json.loads(line)
            except json.JSONDecodeError:
                problems.append((n, ["invalid JSON"]))
                continue
            errors = validate_example(ex)
            if errors:
                problems.append((n, errors))
            else:
                questions.append(ex["messages"][0]["content"][0]["text"].strip().lower())

    duplicates = len(questions) - len(set(questions))
    total = len(questions) + len(problems)
    print(f"{path}: {total} examples, {len(problems)} invalid, {duplicates} duplicate questions")
    for n, errors in problems[:10]:
        print(f"  line {n}: {'; '.join(errors)}")
    if "train" in path and total < MIN_EXAMPLES:
        print(f"  too few examples (minimum {MIN_EXAMPLES})")
        return False
    return not problems and duplicates == 0


if __name__ == "__main__":
    paths = sys.argv[1:] or ["dataset/train.jsonl", "dataset/validation.jsonl"]
    ok = all([validate_file(p) for p in paths])
    print("Dataset is valid" if ok else "Dataset has problems")
    sys.exit(0 if ok else 1)
