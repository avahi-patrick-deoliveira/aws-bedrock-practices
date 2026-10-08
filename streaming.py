import sys
import boto3
from botocore.exceptions import BotoCoreError, ClientError

MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
MAX_TOKENS = 400

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')


def progress_bar(done, total, width=30):
    filled = int(width * min(done, total) / total)
    return f"[{'#' * filled}{'-' * (width - filled)}] ~{done}/{total} tokens ({min(done, total) * 100 // total}%)"


def stream_response(prompt, model_id=MODEL_ID, save_path=None, live_text=False):
    """Stream a response. Shows a progress bar (or live text), counts chunks
    in real time, and optionally saves the text to a file as it arrives."""
    chunks = 0
    text = ""
    usage = {}
    file = open(save_path, "w") if save_path else None

    try:
        response = bedrock_runtime.converse_stream(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": MAX_TOKENS},
        )
        for event in response['stream']:
            if 'contentBlockDelta' in event:
                delta = event['contentBlockDelta']['delta']['text']
                chunks += 1
                text += delta
                if file:
                    file.write(delta)
                if live_text:
                    print(delta, end="", flush=True)
                else:
                    # Estimate tokens as ~4 characters each
                    print("\r" + progress_bar(len(text) // 4, MAX_TOKENS), end="", flush=True)
            elif 'metadata' in event:
                usage = event['metadata']['usage']
        print()
    except ClientError as e:
        print(f"\nAWS error: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
    except BotoCoreError as e:
        print(f"\nConnection error: {e}")
    except Exception as e:
        print(f"\nStream interrupted: {e}")
    finally:
        if file:
            file.close()

    print(f"Chunks received: {chunks} | Output tokens (reported): {usage.get('outputTokens', 'n/a')}")
    return text


if __name__ == "__main__":
    prompt = "Explain what Amazon Bedrock is in 3 short paragraphs."

    print("--- Progress bar + counter ---")
    stream_response(prompt)

    print("\n--- Live text, saved to file ---")
    stream_response(prompt, save_path="stream_output.txt", live_text=True)

    print("\n--- Error handling (invalid model) ---")
    stream_response(prompt, model_id="invalid.model-id")
