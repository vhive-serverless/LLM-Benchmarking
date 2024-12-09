import boto3
import os
import json

from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
             
# Create an &BR; client in the &region-us-east-1; Region.
bedrock = boto3.client(
    service_name="bedrock-runtime",
    aws_access_key_id=os.getenv('AWS_BEDROCK_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_BEDROCK_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_BEDROCK_REGION')
)

# response = bedrock.list_foundation_models()

model_id = "meta.llama3-70b-instruct-v1:0"

prompt = "Tell me a story"

# Format the request payload using the model's native structure.
native_request = {
    "prompt": prompt,
    # "textGenerationConfig": {
    #     "maxTokenCount": 100,
    # },
    "max_gen_len": 5000
}

# Convert the native request to JSON.
request = json.dumps(native_request)

try:
    # Invoke the model with the request.
    response = bedrock.invoke_model(modelId=model_id, body=request)

except (ClientError, Exception) as e:
    print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
    exit(1)

# Decode the response body.
model_response = json.loads(response["body"].read())

# print(response)
print(model_response)

# Extract and print the response text.
response_text = model_response["generation"]
print(response_text)