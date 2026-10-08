from diagram_tools import AI, NEUTRAL, SECURITY, Diagram

d = Diagram("practice_4_architecture")

d.local_group("Local dev (WSL)", 20, 60, 280, 400)
d.cloud_group("AWS Cloud - Account 964217566728 (Avahi Sandbox - 9)", 340, 20, 880, 370)
d.region_group("Region us-east-1", 360, 190, 840, 180)

dev = d.icon("Developer", 130, 90, "client", NEUTRAL)
user = d.icon("IAM user<br>patrick-sandbox", 450, 90, "identity_and_access_management", SECURITY)

script = d.script("streaming.py<br>token counter, try/except", 40, 238)
outputs = d.note("Terminal: progress bar and<br>token counter<br>stream_output.txt: saved chunk by chunk",
                 40, 340, h=70)

runtime = d.icon("Amazon Bedrock Runtime<br>ConverseStream API", 450, 230, "bedrock", AI)
model = d.icon("Claude Haiku 4.5<br>generates tokens as a stream", 800, 230, "machine_learning", AI)

d.edge(dev, user, "access key", dashed=True)
d.edge(script, runtime, "1. request / chunks", both=True)
d.edge(runtime, model, "2. inference")
d.edge(script, outputs, "3. show and save")

d.save("1500,560")
