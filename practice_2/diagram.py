from diagram_tools import AI, NEUTRAL, SECURITY, Diagram

d = Diagram("practice_2_architecture")

d.local_group("Local dev (WSL)", 20, 60, 280, 480)
d.cloud_group("AWS Cloud - Account 964217566728 (Avahi Sandbox - 9)", 340, 20, 880, 540)
d.region_group("Region us-east-1", 360, 190, 840, 350)

dev = d.icon("Developer", 130, 90, "client", NEUTRAL)
user = d.icon("IAM user<br>patrick-sandbox", 450, 90, "identity_and_access_management", SECURITY)

script = d.script("compare_models.py<br>same prompt, time.time()", 40, 343)
d.note("Output: answer, latency and tokens<br>per model, results_practice_2.json", 40, 440, h=50)

runtime = d.icon("Amazon Bedrock Runtime<br>Converse API", 450, 335, "bedrock", AI)
haiku = d.icon("Claude Haiku 4.5<br>us.anthropic.claude-haiku-4-5-20251001-v1:0", 800, 215,
               "machine_learning", AI, side="right")
sonnet = d.icon("Claude Sonnet 4.5<br>us.anthropic.claude-sonnet-4-5-20250929-v1:0", 800, 335,
                "machine_learning", AI, side="right")
opus = d.icon("Claude Opus 4.6<br>us.anthropic.claude-opus-4-6-v1", 800, 455,
              "machine_learning", AI, side="right")

d.edge(dev, user, "access key", dashed=True)
d.edge(script, runtime, "1. converse(prompt)")
# junction centered on the runtime icon row, left of the model icons
fan = d.junction(695, 360)
d.edge(runtime, fan, "2. same prompt", arrow=False)
d.edge(fan, haiku, enter_left=True)
d.edge(fan, sonnet, enter_left=True)
d.edge(fan, opus, enter_left=True)

d.save("1500,640")
