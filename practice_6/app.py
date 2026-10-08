import gradio as gr

from rag import answer, build_index

print("Building index...")
index = build_index()
print(f"Indexed {len(index)} chunks")


def ask(question):
    if not question.strip():
        return "Please type a question.", []
    text, candidates, best = answer(index, question)
    best_sources = {c['source'] for c in best}
    rows = [[c['source'], round(c['score'], 2), c['rerank_score'],
             "yes" if c['source'] in best_sources else "", c['text'][:120] + "..."]
            for c in candidates]
    return text, rows


demo = gr.Interface(
    fn=ask,
    inputs=gr.Textbox(label="Question", placeholder="What is the maximum execution time of a Lambda function?"),
    outputs=[
        gr.Textbox(label="Answer"),
        gr.Dataframe(headers=["Source", "Embedding score", "Rerank score", "Used", "Text"],
                     label="Retrieved chunks"),
    ],
    title="Basic RAG with Amazon Bedrock",
    description="Ask about S3, Lambda or Bedrock. Answers come from the files in docs/.",
)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
