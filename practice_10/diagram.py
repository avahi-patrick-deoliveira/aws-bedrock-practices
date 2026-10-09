from diagram_tools import AI, NEUTRAL, SECURITY, Diagram

d = Diagram("practice_10_architecture")

d.local_group("Local dev (WSL)", 20, 60, 300, 680)
d.cloud_group("AWS Cloud - Account 964217566728 (Avahi Sandbox - 9)", 360, 20, 760, 720)
d.region_group("Region us-east-1", 380, 190, 720, 530)

dev = d.icon("Developer", 140, 90, "client", NEUTRAL)
user = d.icon("IAM user<br>patrick-sandbox", 470, 90, "identity_and_access_management", SECURITY)

# GuardedChat appears once per Bedrock call, each box aligned with its target so the arrows stay straight
gen_call = d.script("GuardedChat<br>4. generate the answer", 40, 235, h=50)
mod_call = d.script("GuardedChat<br>3 and 5. toxicity input and output", 40, 388, h=50)
gr_call = d.script("GuardedChat (optional)<br>managed guardrail on input", 40, 548, h=50)
d.note("Local checks before the model calls:<br>rate limit per user, length, injection, PII.<br>"
       "Every interaction goes to interactions.jsonl<br>and every alert to alerts.jsonl.", 40, 630, h=80)

gen = d.icon("Amazon Bedrock Runtime (Converse)<br>Claude Haiku 4.5: answers", 480, 230, "bedrock", AI)
mod = d.icon("Amazon Bedrock Runtime (Converse)<br>Amazon Nova Lite: toxicity classifier", 480, 380, "bedrock", AI)
gr = d.icon("Bedrock Guardrails (ApplyGuardrail)<br>filters, prompt attack, topic, PII", 480, 540, "bedrock", AI,
            dashed=1)

d.edge(dev, user, "access key", dashed=True)
d.edge(gen_call, gen, "Converse")
d.edge(mod_call, mod, "Converse")
d.edge(gr_call, gr, "ApplyGuardrail", dashed=True)

d.save("1150,780")
