# Practice 3: Parameter Handling

**Objective:** see how generation parameters (`temperature`, `top_p`, `top_k`) change the variability of responses.

## Setup

- Script: `parameters.py` (Bedrock `converse` API)
- Model: `us.anthropic.claude-haiku-4-5-20251001-v1:0`, region `us-east-1`
- Prompt: "Suggest a name for a coffee shop. Reply with only the name."
- Each configuration ran 5 times. `top_p` and `top_k` were tested with the default temperature.

```bash
source .venv/bin/activate
export AWS_PROFILE=avahi-sandbox-9
python parameters.py
```

Full outputs are saved in `results_practice_3.json`.

## Task 1 and 2: Temperature (5 runs each)

| Temperature | Unique answers | Answers |
| --- | --- | --- |
| 0 | 1 of 5 | The Daily Grind (x5) |
| 0.3 | 1 of 5 | The Daily Grind (x5) |
| 0.7 | 2 of 5 | The Daily Grind (x4), Brew Haven |
| 1.0 | 2 of 5 | The Daily Grind (x2), The Daily Brew (x3) |
| 1.5 | error | Rejected by the API: the maximum value is 1 |

**Observation:** no variation at 0 and 0.3. Variation started at 0.7 and 1.0, but stayed
small. `temperature=1.5` is not allowed (valid range is 0 to 1).

## Task 3: top_p and top_k (5 runs each)

| Setting | Unique answers | Answers |
| --- | --- | --- |
| top_p = 0.1 | 1 of 5 | The Daily Grind (x5) |
| top_p = 0.5 | 1 of 5 | The Daily Grind (x5) |
| top_p = 0.95 | 2 of 5 | The Daily Grind (x3), Brew Haven (x2) |
| top_k = 1 | 1 of 5 | The Daily Grind (x5) |
| top_k = 10 | 2 of 5 | The Daily Grind (x4), The Daily Brew |
| top_k = 250 | 2 of 5 | The Daily Grind (x4), The Daily Brew |

**Observation:** small values (`top_p` 0.1 to 0.5, `top_k` 1) removed all variation. Larger
values allowed some variation. `top_k` is sent in `additionalModelRequestFields`, not in
`inferenceConfig`.

## Task 4: When to use each configuration

| Goal | Configuration |
| --- | --- |
| Facts, data extraction, classification, code | `temperature` 0 to 0.3 |
| General chat and explanations | `temperature` around 0.5 to 0.7 |
| Brainstorming, names, creative writing | `temperature` 0.8 to 1.0 |
| Reproducible output (tests, evaluations) | `temperature` 0, or `top_k` 1 |
| Cut off unlikely words but keep variety | `top_p` around 0.9 |

**Note:** small test (1 prompt, 5 runs per setting), not a benchmark.
