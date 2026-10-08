from diagram_tools import AI, NEUTRAL, SECURITY, Diagram

d = Diagram("practice_6_architecture")

d.local_group("Local dev (WSL)", 20, 60, 280, 590)
d.cloud_group("AWS Cloud - Account 964217566728 (Avahi Sandbox - 9)", 340, 20, 880, 640)
d.region_group("Region us-east-1", 360, 190, 840, 450)

dev = d.icon("Developer", 130, 90, "client", NEUTRAL)
user = d.icon("IAM user<br>patrick-sandbox", 450, 90, "identity_and_access_management", SECURITY)

ui = d.script("Gradio UI<br>127.0.0.1:7860", 40, 230)
rag = d.script("rag.py<br>load docs/*.txt, chunk (100 words, 20 overlap)<br>re-rank, build the answer prompt",
               40, 340, h=70)
index = d.note("In-memory vector index (numpy)<br>cosine similarity, top 6 chunks", 40, 470, h=50)

# rag.py center is y=375: the junction and its two arrows start there
fan = d.junction(440, 370)
titan = d.icon("Amazon Titan Text Embeddings v2<br>amazon.titan-embed-text-v2:0", 520, 230,
               "bedrock", AI, side="right")
haiku = d.icon("Claude Haiku 4.5<br>re-ranks 6 chunks and writes the answer", 520, 480,
               "machine_learning", AI, side="right")

d.edge(dev, user, "access key", dashed=True)
d.edge(ui, rag, "question / answer", both=True)
d.edge(rag, index, "search", both=True)
d.edge(rag, fan, arrow=False)
d.edge(fan, titan, "1. embed chunks and question", enter_left=True)
d.edge(fan, haiku, "2. re-rank, answer", enter_left=True)

d.save("1500,720")
