import json
import sys

import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
BASE_MODEL = "amazon.nova-micro-v1:0:128k"
JOB_NAME = "support-style-nova-micro-ft"
ROLE_NAME = "BedrockFineTuneRole-support-style"
HYPERPARAMETERS = {"epochCount": "2", "learningRate": "0.00001", "learningRateWarmupSteps": "10"}

account = boto3.client("sts").get_caller_identity()["Account"]
BUCKET = f"bedrock-practice-finetune-{account}"

s3 = boto3.client("s3", region_name=REGION)
iam = boto3.client("iam")
bedrock = boto3.client("bedrock", region_name=REGION)


def upload_data():
    try:
        s3.create_bucket(Bucket=BUCKET)
        print(f"Created bucket {BUCKET}")
    except ClientError as e:
        if e.response["Error"]["Code"] not in ("BucketAlreadyOwnedByYou",):
            raise
    for name in ("train", "validation"):
        s3.upload_file(f"dataset/{name}.jsonl", BUCKET, f"{name}.jsonl")
    print("Uploaded dataset/train.jsonl and validation.jsonl")


def create_role():
    trust = {"Version": "2012-10-17", "Statement": [{
        "Effect": "Allow", "Principal": {"Service": "bedrock.amazonaws.com"},
        "Action": "sts:AssumeRole",
        "Condition": {
            "StringEquals": {"aws:SourceAccount": account},
            "ArnEquals": {"aws:SourceArn": f"arn:aws:bedrock:{REGION}:{account}:model-customization-job/*"},
        }}]}
    policy = {"Version": "2012-10-17", "Statement": [
        {"Effect": "Allow", "Action": ["s3:GetObject", "s3:ListBucket", "s3:PutObject"],
         "Resource": [f"arn:aws:s3:::{BUCKET}", f"arn:aws:s3:::{BUCKET}/*"]}]}
    try:
        role = iam.create_role(RoleName=ROLE_NAME, AssumeRolePolicyDocument=json.dumps(trust))
        print(f"Created role {ROLE_NAME}")
    except ClientError as e:
        if e.response["Error"]["Code"] != "EntityAlreadyExists":
            raise
        role = iam.get_role(RoleName=ROLE_NAME)
    iam.put_role_policy(RoleName=ROLE_NAME, PolicyName="s3-access", PolicyDocument=json.dumps(policy))
    return role["Role"]["Arn"]


def start_job(role_arn):
    response = bedrock.create_model_customization_job(
        jobName=JOB_NAME,
        customModelName=JOB_NAME,
        roleArn=role_arn,
        baseModelIdentifier=BASE_MODEL,
        customizationType="FINE_TUNING",
        trainingDataConfig={"s3Uri": f"s3://{BUCKET}/train.jsonl"},
        validationDataConfig={"validators": [{"s3Uri": f"s3://{BUCKET}/validation.jsonl"}]},
        outputDataConfig={"s3Uri": f"s3://{BUCKET}/output/"},
        hyperParameters=HYPERPARAMETERS,
    )
    print("Started job:", response["jobArn"])


def status():
    job = bedrock.get_model_customization_job(jobIdentifier=JOB_NAME)
    print("Status:", job["status"])
    if job.get("failureMessage"):
        print("Failure:", job["failureMessage"])
    if job["status"] == "Completed":
        print("Custom model ARN:", job["outputModelArn"])


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "start"
    if command == "start":
        upload_data()
        start_job(create_role())
    else:
        status()
