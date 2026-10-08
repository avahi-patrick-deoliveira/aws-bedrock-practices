# Practice 6: Basic RAG with Embeddings

**Objective:** build a simple RAG system: find the most relevant text for a question and let the model answer from it.

## Setup

- Embeddings: `amazon.titan-embed-text-v2:0`
- Answers and re-ranking: `us.anthropic.claude-haiku-4-5-20251001-v1:0`
- Region: `us-east-1`
- Extra packages: `numpy`, `gradio`
- Documents: `docs/s3.txt`, `docs/lambda.txt`, `docs/bedrock.txt` (short texts written for this practice)

```bash
source .venv/bin/activate
export AWS_PROFILE=avahi-sandbox-9
python rag.py      # command-line test with 3 questions
python app.py      # web interface at http://127.0.0.1:7860
```

## How it works

1. Load the `.txt` files and split them into chunks.
2. Create an embedding for each chunk (vector index kept in memory).
3. For a question, create its embedding and rank chunks by cosine similarity (top 6).
4. Re-rank the 6 chunks and keep the best 3.
5. Send the 3 chunks and the question to Claude, which answers using only that context.

## Task 1: Load documents from text files

`load_documents()` reads every `.txt` file in `docs/`. Result: 3 documents.

## Task 2: Chunking

`chunk_text()` splits each document into chunks of 100 words with a 20 word overlap, so
sentences at the edge of a chunk are not lost. Result: 12 chunks from 3 documents.

## Task 3: Re-ranking

Embedding similarity gets the right area but its order is not always the best. `rerank()`
asks Claude to score each of the 6 candidates from 0 to 10 and keeps the 3 best.

| Question | Embedding order (top 3) | After re-ranking |
| --- | --- | --- |
| Max execution time of a Lambda function? | lambda #2 (0.66), #1, #3 | lambda #2, #3, #4 |
| Best S3 storage class for archives? | s3 #2 (0.65), #1, #4 | s3 #2 only scored above 0 |
| What is RAG and how does it work? | bedrock #3 (0.50), #2, lambda #2 | bedrock #3, #2, #4 |

**Observation:** re-ranking removed unrelated chunks (for example `lambda #2` in the RAG
question) and gave 0 to chunks that did not help. The answers were correct for all
3 questions. It costs one extra model call per question.

## Task 4: Web interface with Gradio

`app.py` builds the index at startup and shows a text box for the question. It displays the
answer and a table of the 6 retrieved chunks with embedding score, re-rank score and whether
the chunk was used. The app starts correctly and returns HTTP 200.

**Note:** small test (3 short documents, 3 questions), not a benchmark. The index is rebuilt
each time the app starts, and re-ranking scores come from the model, so they can vary slightly.
