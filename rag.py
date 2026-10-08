import json
import re
from pathlib import Path

import boto3
import numpy as np

EMBED_MODEL = "amazon.titan-embed-text-v2:0"
LLM_MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
CHUNK_WORDS = 100
OVERLAP_WORDS = 20

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')


def load_documents(folder="docs"):
    """Task 1: load every .txt file in a folder."""
    return {p.name: p.read_text() for p in sorted(Path(folder).glob("*.txt"))}


def chunk_text(text, size=CHUNK_WORDS, overlap=OVERLAP_WORDS):
    """Task 2: split text into chunks of `size` words, overlapping by `overlap` words."""
    words = text.split()
    step = size - overlap
    return [" ".join(words[i:i + size]) for i in range(0, len(words), step)
            if len(words[i:i + size]) > overlap]


def embed(text):
    response = bedrock_runtime.invoke_model(
        modelId=EMBED_MODEL,
        body=json.dumps({"inputText": text}),
    )
    return np.array(json.loads(response['body'].read())['embedding'])


def build_index(folder="docs"):
    index = []
    for name, text in load_documents(folder).items():
        for i, chunk in enumerate(chunk_text(text)):
            index.append({"source": f"{name} #{i + 1}", "text": chunk, "vector": embed(chunk)})
    return index


def search(index, question, top_k=6):
    """Semantic search: cosine similarity between question and chunk embeddings."""
    q = embed(question)
    for item in index:
        item["score"] = float(np.dot(q, item["vector"]) /
                              (np.linalg.norm(q) * np.linalg.norm(item["vector"])))
    return sorted(index, key=lambda x: x["score"], reverse=True)[:top_k]


def ask_claude(prompt, max_tokens=500):
    response = bedrock_runtime.converse(
        modelId=LLM_MODEL,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": 0},
    )
    return response['output']['message']['content'][0]['text']


def rerank(question, candidates, top_n=3):
    """Task 3: ask Claude to score each candidate from 0 to 10 and keep the best ones."""
    numbered = "\n\n".join(f"[{i}] {c['text']}" for i, c in enumerate(candidates))
    prompt = (f"Question: {question}\n\nPassages:\n{numbered}\n\n"
              f"Rate how useful each passage is for answering the question, from 0 to 10. "
              f"Reply with only a JSON list of {len(candidates)} numbers, in order.")
    try:
        scores = json.loads(re.search(r"\[.*?\]", ask_claude(prompt, 100), re.S).group())
        for c, s in zip(candidates, scores):
            c["rerank_score"] = s
    except Exception:
        for c in candidates:
            c["rerank_score"] = 0
    return sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)[:top_n]


def answer(index, question):
    candidates = search(index, question)
    best = rerank(question, candidates)
    context = "\n\n".join(f"({c['source']}) {c['text']}" for c in best)
    prompt = (f"Answer the question using only the context below. "
              f"If the answer is not in the context, say you don't know.\n\n"
              f"Context:\n{context}\n\nQuestion: {question}")
    return ask_claude(prompt), candidates, best


if __name__ == "__main__":
    index = build_index()
    print(f"Indexed {len(index)} chunks from {len(load_documents())} documents\n")
    for question in ["What is the maximum execution time of a Lambda function?",
                     "Which S3 storage class is best for archives?",
                     "What is RAG and how does it work?"]:
        text, candidates, best = answer(index, question)
        print(f"Q: {question}")
        print("  Embedding order:", [(c['source'], round(c['score'], 2)) for c in candidates[:3]])
        print("  After rerank:   ", [(c['source'], c['rerank_score']) for c in best])
        print(f"A: {text}\n")
