from diagram_tools import AI, NEUTRAL, SECURITY, Diagram

d = Diagram("practice_7_architecture")

d.local_group("Local dev (WSL)", 20, 60, 280, 500)
d.cloud_group("AWS Cloud - Account 964217566728 (Avahi Sandbox - 9)", 340, 20, 880, 500)
d.region_group("Region us-east-1", 360, 190, 840, 310)

dev = d.icon("Developer", 130, 90, "client", NEUTRAL)
user = d.icon("IAM user<br>patrick-sandbox", 450, 90, "identity_and_access_management", SECURITY)

log = d.note("agent.log: question, decisions,<br>tool results, tokens", 40, 235, h=50)
agent = d.script("agent.py<br>loop up to 6 steps", 40, 338)
tools = d.note("Local tools<br>calculator (ast, no eval)<br>web_search (simulated)<br>query_database (SQLite, SELECT only)",
               40, 440, h=84)

runtime = d.icon("Amazon Bedrock Runtime<br>Converse API with toolConfig", 450, 330, "bedrock", AI)
model = d.icon("Claude Sonnet 4.6<br>decides which tool to call", 800, 330, "machine_learning", AI)

d.edge(dev, user, "access key", dashed=True)
d.edge(agent, log, "logs each step")
d.edge(agent, runtime, "1. messages + tools / tool_use", both=True)
d.edge(runtime, model, "2. model decides")
d.edge(agent, tools, "3. run tool, send toolResult")

d.save("1500,640")
