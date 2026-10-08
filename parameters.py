import boto3
import json

MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
PROMPT = "Suggest a name for a coffee shop. Reply with only the name."
RUNS = 5

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')


def invoke(inference_config, extra_fields=None):
    kwargs = {
        "modelId": MODEL_ID,
        "messages": [{"role": "user", "content": [{"text": PROMPT}]}],
        "inferenceConfig": {"maxTokens": 30, **inference_config},
    }
    if extra_fields:
        kwargs["additionalModelRequestFields"] = extra_fields
    response = bedrock_runtime.converse(**kwargs)
    return response['output']['message']['content'][0]['text'].strip()


def run_many(label, inference_config, extra_fields=None):
    try:
        answers = [invoke(inference_config, extra_fields) for _ in range(RUNS)]
    except Exception as e:
        print(f"{label}: ERROR {e}")
        return {"label": label, "error": str(e)}
    print(f"{label}: {len(set(answers))} unique of {RUNS} -> {answers}")
    return {"label": label, "unique": len(set(answers)), "answers": answers}


results = {"temperature": [], "top_p": [], "top_k": []}

for t in [0, 0.3, 0.7, 1.0, 1.5]:
    results["temperature"].append(run_many(f"temperature={t}", {"temperature": t}))

for p in [0.1, 0.5, 0.95]:
    results["top_p"].append(run_many(f"top_p={p}", {"topP": p}))

for k in [1, 10, 250]:
    results["top_k"].append(run_many(f"top_k={k}", {}, {"top_k": k}))

with open('results_practice_3.json', 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
