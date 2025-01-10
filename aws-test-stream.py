import boto3
import json
import os
import time

from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

# Create a Bedrock Runtime client in the AWS Region of your choice.
client = boto3.client(
    "bedrock-runtime",
    aws_access_key_id=os.getenv('AWS_BEDROCK_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_BEDROCK_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_BEDROCK_REGION')
)

# Set the model ID, e.g., Llama 3 70b Instruct.
model_id = "meta.llama3-70b-instruct-v1:0"

# Define the prompt for the model.
prompt = "Tell me a story."

# Embed the prompt in Llama 3's instruction format.
formatted_prompt = f"""
<|begin_of_text|><|start_header_id|>user<|end_header_id|>
{prompt}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""

# Format the request payload using the model's native structure.
native_request = {
    "prompt": formatted_prompt,
    "max_gen_len": 512,
}

# Convert the native request to JSON.
request = json.dumps(native_request)

try:
    # Measure the start time.
    start_time = time.time()
    first_token_time = None
    prev_token_time = None
    inter_token_latencies = []

    print("[DEBUG] Starting streaming response processing.")

    # Invoke the model with the request.
    streaming_response = client.invoke_model_with_response_stream(
        modelId=model_id, body=request
    )

    # Process the streaming response.
    for event in streaming_response["body"]:
        print("[DEBUG] Processing new event")
        if event:
            # Parse the event JSON
            # print(event)
            try:
                # print(event)
                chunk = json.loads(event['chunk']['bytes'].decode("utf-8"))
                print(f"[DEBUG] Decoded chunk: {chunk}")
            except Exception as e:
                print(f"[DEBUG] Failed to decode chunk: {e}")
                continue

            # Check if this event contains a token
            if "generation" in chunk:
                current_token = chunk["generation"]
                print(f"[DEBUG] Received token: {current_token}")
                print(current_token, end="")  # Print the token.

                # Time calculations
                current_time = time.time()
                if first_token_time is None:
                    first_token_time = current_time
                    ttft = first_token_time - start_time
                    prev_token_time = first_token_time
                    print(f"\n##### [DEBUG] Time to First Token (TTFT): {ttft:.4f} seconds\n")

                # Calculate latency between tokens.
                if prev_token_time:
                    inter_token_latency = current_time - prev_token_time
                    inter_token_latencies.append(inter_token_latency)
                    print(f"[DEBUG] Inter-token latency: {inter_token_latency:.4f} seconds")
                    prev_token_time = current_time

    # Measure the total response time.
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\n##### [DEBUG] Total Response Time: {total_time:.4f} seconds")

    # Print inter-token latencies.
    print("\n##### Inter-Token Latencies (in seconds):")
    print(len(inter_token_latencies))

except (ClientError, Exception) as e:
    print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
    exit(1)
