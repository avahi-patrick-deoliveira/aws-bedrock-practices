# aws-bedrock-practices

Hands-on practice calling Anthropic Claude models through Amazon Bedrock with `boto3`.

## Setup

- Python 3.12 virtual environment (`.venv`) with `boto3`
- AWS account: Avahi Sandbox - 9, IAM user `patrick-sandbox`
- Region: `us-east-1`
- Model: `us.anthropic.claude-sonnet-4-5-20250929-v1:0` (cross-region inference profile)

```bash
source .venv/bin/activate
export AWS_PROFILE=avahi-sandbox-9
python main.py
```

## Files

| File | Purpose |
| --- | --- |
| `check_bedrock.py` | Lists foundation models to confirm Bedrock access |
| `check_model.py` | Checks that the Haiku 4.5 inference profile exists and can be invoked |
| `main.py` / `invoke_claude.py` | Minimal `invoke_model` example |
| `experiments.py` | Runs the exercises below and writes `results.json` |

## Exercises

### 1. Run the code and observe the response

`main.py` sends "Explain what AWS Bedrock is in 3 paragraphs" to Claude Sonnet 4.5.
The model returns exactly three paragraphs: what Bedrock is (a managed service giving
access to several foundation models through one API), its customization features (fine-tuning,
RAG, guardrails), and its serverless, pay-per-use model for enterprise use cases.

### 2. Ask 3 different questions

Besides the original prompt, three more questions were tested:

1. What is the difference between Amazon Bedrock and Amazon SageMaker?
2. Give me 3 real-world use cases for generative AI in customer support.
3. Explain what a foundation model is to a 10-year-old.

All four prompts completed with `stop_reason = end_turn`, meaning the model finished
its answer on its own. The model adapted its tone and structure to each prompt
(comparison, list, simple analogy).

### 3. Change `max_tokens` from 1000 to 500

Each prompt was run with both `max_tokens=1000` and `max_tokens=500`.

| Prompt | max_tokens | Output tokens | Stop reason |
| --- | --- | --- | --- |
| Bedrock in 3 paragraphs | 1000 | 309 | end_turn |
| Bedrock in 3 paragraphs | 500 | 310 | end_turn |
| Bedrock vs SageMaker | 1000 | 329 | end_turn |
| Bedrock vs SageMaker | 500 | 417 | end_turn |
| 3 customer support use cases | 1000 | 370 | end_turn |
| 3 customer support use cases | 500 | 369 | end_turn |
| Foundation model for a 10-year-old | 1000 | 282 | end_turn |
| Foundation model for a 10-year-old | 500 | 296 | end_turn |

**Observation:** there was no visible difference. `max_tokens` is only an upper limit,
not a target length. Every answer used fewer than 500 tokens, so the lower limit never
truncated anything. A truncated answer would show `stop_reason = max_tokens`. The small
differences in output tokens (for example 329 vs 417) come from normal variation between
runs, not from the limit. To see the limit take effect, use a smaller value (such as 100)
or a prompt that asks for a long answer.

### 4. Measure response time with `time.time()`

Time was measured around the `invoke_model` call and the reading of the response body.

| Prompt | max_tokens | Time (s) |
| --- | --- | --- |
| Bedrock in 3 paragraphs | 1000 | 8.19 |
| Bedrock in 3 paragraphs | 500 | 7.31 |
| Bedrock vs SageMaker | 1000 | 6.36 |
| Bedrock vs SageMaker | 500 | 9.68 |
| 3 customer support use cases | 1000 | 8.83 |
| 3 customer support use cases | 500 | 8.74 |
| Foundation model for a 10-year-old | 1000 | 9.95 |
| Foundation model for a 10-year-old | 500 | 7.61 |

**Observation:** responses took between about 6 and 10 seconds, with an average of
roughly 8.3 seconds. Time did not follow output length closely. The shortest answer
(282 tokens) took the longest (9.95 s), so network and service latency vary more than
generation length in this small sample. Each call was made once, so these numbers are
indicative only. Repeating each call several times and averaging would give a more
reliable result.

## Raw results

Full outputs, including the generated text, token counts and timing, are saved in
`results.json` after running `experiments.py`.
