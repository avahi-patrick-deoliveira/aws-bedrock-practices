from diagram_tools import AI, NEUTRAL, SECURITY, STORAGE, Diagram

d = Diagram("practice_9_architecture")

d.local_group("Local dev (WSL)", 20, 60, 280, 620)
d.cloud_group("AWS Cloud - Account 964217566728 (Avahi Sandbox - 9)", 340, 20, 1120, 700)
d.region_group("Region us-east-1", 360, 190, 1080, 510)

dev = d.icon("Developer", 130, 90, "client", NEUTRAL)
user = d.icon("IAM user<br>patrick-sandbox", 450, 90, "identity_and_access_management", SECURITY)

# gen is centered on the Runtime icon (straight arrow); ab_test.py joins it from below
gen = d.script("generate_dataset.py<br>validate_dataset.py", 40, 235, h=50)
ab = d.script("ab_test.py", 40, 305, h=40)
# finetune.py appears twice, each box aligned with its target so the arrows stay straight
ft_job = d.script("finetune.py<br>(create job)", 40, 388)
ft_up = d.script("finetune.py<br>(upload data)", 40, 548)
d.note("boto3 - profile avahi-sandbox-9", 40, 620, h=40)

# top row: Bedrock Runtime and the job role
runtime = d.icon("Amazon Bedrock Runtime (Converse API)<br>"
                 "Claude Sonnet 4.6: generates the synthetic dataset<br>"
                 "Claude Haiku 4.5: baseline answers and judge", 450, 230, "bedrock", AI)
role = d.icon("IAM role<br>BedrockFineTuneRole-support-style<br>trusts bedrock.amazonaws.com", 800, 230,
              "identity_and_access_management", SECURITY, side="right")

# middle row: customization, aligned with finetune.py
job = d.icon("Model customization job<br>Amazon Nova Micro, 2 epochs", 800, 380, "bedrock", AI,
             side="upright")
custom = d.icon("Custom model<br>support-style-nova-micro-ft", 1150, 380, "machine_learning", AI,
                side="right")

# bottom row: storage and optional inference
s3 = d.icon("S3 bucket<br>bedrock-practice-finetune-964217566728<br>train.jsonl, validation.jsonl, output/",
            800, 540, "bucket", STORAGE)
pt = d.icon("Provisioned Throughput (not created yet)<br>future target of ab_test.py variant B",
            1150, 540, "bedrock", AI, dashed=1)

d.edge(dev, user, "access key", dashed=True)
d.edge(gen, runtime, "1. generate examples")
d.edge(ab, runtime, "A. baseline", enter_left=True)
d.edge(ft_up, s3, "2. upload data")
d.edge(ft_job, job, "3. create job")
d.edge(job, s3, "4. read data, write output")
d.edge(job, role, "assumes (S3 access)", dashed=True)
d.edge(job, custom, "5. produces")
d.edge(custom, pt, "6. deploy (optional)", dashed=True)

d.save("1500,760")
