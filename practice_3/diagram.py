from diagram_tools import AI, NEUTRAL, SECURITY, Diagram

d = Diagram("practice_3_architecture")

d.local_group("Local dev (WSL)", 20, 60, 280, 400)
d.cloud_group("AWS Cloud - Account 964217566728 (Avahi Sandbox - 9)", 340, 20, 880, 370)
d.region_group("Region us-east-1", 360, 190, 840, 180)

dev = d.icon("Developer", 130, 90, "client", NEUTRAL)
user = d.icon("IAM user<br>patrick-sandbox", 450, 90, "identity_and_access_management", SECURITY)

script = d.script("parameters.py<br>5 runs per setting", 40, 238)
d.note("temperature: 0, 0.3, 0.7, 1.0<br>(1.5 is rejected, max is 1)<br>"
       "topP: 0.1, 0.5, 0.95<br>top_k: 1, 10, 250", 40, 310, h=76)
d.note("Output: unique answers per setting<br>results_practice_3.json", 40, 400, h=44)

runtime = d.icon("Amazon Bedrock Runtime<br>Converse API<br>inferenceConfig: temperature, topP", 450, 230,
                 "bedrock", AI)
model = d.icon("Claude Haiku 4.5<br>top_k sent in additionalModelRequestFields", 800, 230,
               "machine_learning", AI)

d.edge(dev, user, "access key", dashed=True)
d.edge(script, runtime, "1. converse + params")
d.edge(runtime, model, "2. inference")

d.save("1500,560")
