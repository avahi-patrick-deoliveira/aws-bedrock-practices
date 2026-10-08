import json
from collections import defaultdict
from statistics import mean

from bert_score import score as bert_score
from rouge_score import rouge_scorer
from sacrebleu.metrics import BLEU

# Task 4: list prices in USD per 1M tokens (input, output). Check current AWS pricing.
PRICES = {
    "haiku-4.5": (1.0, 5.0),
    "sonnet-4.6": (3.0, 15.0),
    "opus-4.6": (5.0, 25.0),
}

results = json.load(open("results_practice_8.json"))

# Task 2: automatic metrics against the reference answer
bleu = BLEU(effective_order=True)
rouge = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
for r in results:
    r["bleu"] = bleu.sentence_score(r["text"], [r["reference"]]).score / 100
    r["rouge1"] = rouge.score(r["reference"], r["text"])["rouge1"].fmeasure
    r["rougeL"] = rouge.score(r["reference"], r["text"])["rougeL"].fmeasure

_, _, f1 = bert_score([r["text"] for r in results], [r["reference"] for r in results],
                      model_type="distilbert-base-uncased", lang="en")
for r, value in zip(results, f1.tolist()):
    r["bertscore"] = value

# Aggregate per model
by_model = defaultdict(list)
for r in results:
    by_model[r["model"]].append(r)


def avg(rows, key):
    values = [row[key] for row in rows if row.get(key) is not None]
    return mean(values) if values else 0


summary = {}
for name, rows in by_model.items():
    price_in, price_out = PRICES[name]
    cost = sum(r["input_tokens"] * price_in + r["output_tokens"] * price_out for r in rows) / 1e6
    summary[name] = {
        "correctness": mean(r["scores"]["correctness"] for r in rows if r["scores"]["correctness"]),
        "completeness": mean(r["scores"]["completeness"] for r in rows if r["scores"]["completeness"]),
        "conciseness": mean(r["scores"]["conciseness"] for r in rows if r["scores"]["conciseness"]),
        "bleu": avg(rows, "bleu"), "rouge1": avg(rows, "rouge1"),
        "rougeL": avg(rows, "rougeL"), "bertscore": avg(rows, "bertscore"),
        "latency": avg(rows, "seconds"), "output_tokens": avg(rows, "output_tokens"),
        "cost_total": cost, "cost_per_1000": cost / len(rows) * 1000,
    }

domains = sorted({r["domain"] for r in results})
by_domain = {name: {d: mean(r["scores"]["correctness"] for r in rows
                             if r["domain"] == d and r["scores"]["correctness"])
                    for d in domains} for name, rows in by_model.items()}

json.dump(summary, open("summary_practice_8.json", "w"), indent=2)
for name, s in summary.items():
    print(name, {k: round(v, 3) for k, v in s.items()})

# Task 3: HTML report with Chart.js charts
names = list(summary)


def chart(canvas_id, title, labels, datasets, y_title=""):
    return f"""new Chart(document.getElementById('{canvas_id}'), {{
  type: 'bar', data: {{labels: {json.dumps(labels)}, datasets: {json.dumps(datasets)}}},
  options: {{plugins: {{title: {{display: true, text: '{title}'}}}},
             scales: {{y: {{beginAtZero: true, title: {{display: true, text: '{y_title}'}}}}}}}}}});"""


colors = ["#4e79a7", "#f28e2b", "#59a14f", "#e15759", "#76b7b2", "#edc948"]
quality = [{"label": m, "data": [round(summary[n][m], 2) for n in names], "backgroundColor": colors[i]}
           for i, m in enumerate(["correctness", "completeness", "conciseness"])]
auto = [{"label": m, "data": [round(summary[n][m], 3) for n in names], "backgroundColor": colors[i]}
        for i, m in enumerate(["bleu", "rouge1", "rougeL", "bertscore"])]
dom = [{"label": n, "data": [round(by_domain[n][d], 2) for d in domains], "backgroundColor": colors[i]}
       for i, n in enumerate(names)]

scripts = "\n".join([
    chart("quality", "LLM judge scores (1 to 5)", names, quality),
    chart("auto", "Automatic metrics (0 to 1)", names, auto),
    chart("domain", "Judge correctness by domain (1 to 5)", domains, dom),
    chart("latency", "Average latency", names,
          [{"label": "seconds", "data": [round(summary[n]["latency"], 2) for n in names],
            "backgroundColor": colors[0]}], "seconds"),
    chart("cost", "Cost per 1,000 questions (answers only)", names,
          [{"label": "USD", "data": [round(summary[n]["cost_per_1000"], 3) for n in names],
            "backgroundColor": colors[1]}], "USD"),
])

rows_html = "".join(
    f"<tr><td>{n}</td>" + "".join(f"<td>{summary[n][k]:.2f}</td>" for k in
    ["correctness", "completeness", "conciseness", "bleu", "rouge1", "rougeL", "bertscore", "latency", "cost_per_1000"])
    + "</tr>" for n in names)

html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Model evaluation report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>body{{font-family:sans-serif;max-width:1000px;margin:2rem auto;padding:0 1rem}}
table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:6px;text-align:right}}
th:first-child,td:first-child{{text-align:left}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}}
</style></head><body>
<h1>Model evaluation report</h1>
<p>{len(results) // len(names)} questions, {len(domains)} domains, {len(names)} models. Judge: Claude Sonnet 4.6.</p>
<table><tr><th>Model</th><th>Correct.</th><th>Complete.</th><th>Concise.</th><th>BLEU</th><th>ROUGE-1</th>
<th>ROUGE-L</th><th>BERTScore</th><th>Latency (s)</th><th>USD / 1000 q</th></tr>{rows_html}</table>
<div class="grid"><canvas id="quality"></canvas><canvas id="auto"></canvas>
<canvas id="domain"></canvas><canvas id="latency"></canvas><canvas id="cost"></canvas></div>
<script>{scripts}</script></body></html>"""
open("report.html", "w").write(html)
print("Saved report.html")
