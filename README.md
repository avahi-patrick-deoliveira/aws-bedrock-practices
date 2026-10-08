# aws-bedrock-practices

Hands-on practices with Amazon Bedrock and Claude, written with `boto3`.
Each practice has its own folder with the code, results, an architecture diagram and a README
that explains what was done and what was observed.

| Practice | Topic | Folder |
| --- | --- | --- |
| 1 | First call to Claude (latency, `max_tokens`) | [practice_1](practice_1) |
| 2 | Model comparison (Haiku, Sonnet, Opus) | [practice_2](practice_2) |
| 3 | Parameter handling (`temperature`, `top_p`, `top_k`) | [practice_3](practice_3) |
| 4 | Response streaming | [practice_4](practice_4) |
| 6 | Basic RAG with embeddings and a Gradio interface | [practice_6](practice_6) |
| 7 | Function calling / tool use agent | [practice_7](practice_7) |
| 8 | Model analysis and evaluation (LLM judge, metrics, report) | [practice_8](practice_8) |
| 9 | Fine-tuning and customization (dataset, validation, cost, A/B plan) | [practice_9](practice_9) |

## Setup

```bash
python3 -m venv .venv          # or: uv venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export AWS_PROFILE=<your-profile>   # credentials with access to Amazon Bedrock in us-east-1
```

Run each practice from inside its folder, because the scripts read and write files with
relative paths:

```bash
cd practice_1
python main.py
```

## Layout

```text
practice_N/
  README.md        what was done, results and architecture diagram
  *.py             code of the practice
  diagrams/        draw.io source and the rendered PNG
  diagram.py       rebuilds the diagram (PYTHONPATH=../tools python diagram.py)
tools/
  diagram_tools.py shared helpers to build and render the diagrams
```

The models, account and region used are described in each practice README. Model IDs and
prices change, so check the current Amazon Bedrock documentation before reusing them.
