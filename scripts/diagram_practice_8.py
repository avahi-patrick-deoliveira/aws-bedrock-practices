from diagram_tools import AI, NEUTRAL, SECURITY, Diagram

d = Diagram("practice_8_architecture")

d.local_group("Local dev (WSL)", 20, 60, 280, 600)
d.cloud_group("AWS Cloud - Account 964217566728 (Avahi Sandbox - 9)", 340, 20, 880, 500)
d.region_group("Region us-east-1", 360, 190, 840, 310)

dev = d.icon("Developer", 130, 90, "client", NEUTRAL)
user = d.icon("IAM user<br>patrick-sandbox", 450, 90, "identity_and_access_management", SECURITY)

bench = d.note("benchmark.json<br>50 questions, 5 domains", 40, 210)
evaluate = d.script("evaluate.py<br>answers, latency, tokens, judge", 40, 300)
results = d.note("results_practice_8.json", 40, 390)
report = d.script("report.py<br>BLEU, ROUGE, BERTScore, cost", 40, 480)
html = d.note("report.html<br>comparative charts", 40, 570)

runtime = d.icon("Amazon Bedrock Runtime<br>Converse API<br>judge: Sonnet 4.6 scores 1 to 5",
                 450, 292, "bedrock", AI)
fan = d.junction(695, 317)
haiku = d.icon("Claude Haiku 4.5", 800, 215, "machine_learning", AI, side="right")
sonnet = d.icon("Claude Sonnet 4.6", 800, 292, "machine_learning", AI, side="right")
opus = d.icon("Claude Opus 4.6", 800, 369, "machine_learning", AI, side="right")

d.edge(dev, user, "access key", dashed=True)
d.edge(bench, evaluate, "questions")
d.edge(evaluate, runtime, "1. answers + judge")
d.edge(runtime, fan, "2. same questions", arrow=False)
d.edge(fan, haiku, enter_left=True)
d.edge(fan, sonnet, enter_left=True)
d.edge(fan, opus, enter_left=True)
d.edge(evaluate, results, "3. save")
d.edge(results, report, "4. metrics")
d.edge(report, html, "5. report")

d.save("1500,720")
