import boto3
import json

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

def invoke_claude(prompt):
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    response = bedrock_runtime.invoke_model(
        modelId='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
        body=body
    )

    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']

# Example usage
result = invoke_claude("Explain what AWS Bedrock is in 3 paragraphs")
print(result)
