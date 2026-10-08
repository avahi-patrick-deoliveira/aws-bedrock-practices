from diagram_tools import AI, NEUTRAL, SECURITY, Diagram

d = Diagram("practice_1_architecture")

d.local_group("Local dev (WSL)", 20, 60, 280, 330)
d.cloud_group("AWS Cloud - Account 964217566728 (Avahi Sandbox - 9)", 340, 20, 880, 370)
d.region_group("Region us-east-1", 360, 190, 840, 180)

dev = d.icon("Developer", 130, 90, "client", NEUTRAL)
user = d.icon("IAM user<br>patrick-sandbox", 450, 90, "identity_and_access_management", SECURITY)

script = d.script("main.py / experiments.py<br>boto3 client, time.time()", 40, 238, h=44)
d.note("Output: response text, token usage,<br>latency, results.json", 40, 330, h=50)

runtime = d.icon("Amazon Bedrock Runtime<br>InvokeModel API", 450, 230, "bedrock", AI)
model = d.icon("Claude Sonnet 4.5<br>us.anthropic.claude-sonnet-4-5-20250929-v1:0<br>cross-region inference profile",
               800, 230, "machine_learning", AI)

d.edge(dev, user, "access key", dashed=True)
d.edge(script, runtime, "1. invoke_model")
d.edge(runtime, model, "2. inference")

d.save("1500,560")
