import boto3

PROFILE_ID = 'us.anthropic.claude-haiku-4-5-20251001-v1:0'
MODEL_ID = PROFILE_ID.split('.', 1)[1]

bedrock = boto3.client('bedrock', region_name='us-east-1')

profiles = bedrock.list_inference_profiles()['inferenceProfileSummaries']
match = [p for p in profiles if p['inferenceProfileId'] == PROFILE_ID]
print(f"Inference profile {PROFILE_ID}: {'FOUND' if match else 'NOT FOUND'}")
for p in match:
    print(f"  name={p['inferenceProfileName']} status={p['status']}")

models = bedrock.list_foundation_models()['modelSummaries']
base = [m for m in models if m['modelId'] == MODEL_ID]
print(f"Foundation model {MODEL_ID}: {'FOUND' if base else 'NOT FOUND'}")
for m in base:
    print(f"  inference={m['inferenceTypesSupported']} lifecycle={m['modelLifecycle']['status']}")

runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
try:
    out = runtime.converse(
        modelId=PROFILE_ID,
        messages=[{'role': 'user', 'content': [{'text': 'Diga oi em uma palavra.'}]}],
        inferenceConfig={'maxTokens': 20},
    )
    print('Invoke OK:', out['output']['message']['content'][0]['text'])
except Exception as e:
    print('Invoke FAILED:', e)
