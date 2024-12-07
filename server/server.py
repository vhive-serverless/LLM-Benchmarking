import boto3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins. You can restrict this to specific origins.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("BenchmarkMetrics")

@app.get("/latest-run-id")
def get_latest_run_id():
    # Query table to get the latest `run_id`
    print('test')
    response = table.scan()
    items = response.get("Items", [])
    # Sort by timestamp to get the latest `run_id`
    latest_item = max(items, key=lambda x: x["timestamp"])
    return {"run_id": latest_item["run_id"]}

@app.get("/metrics")
def get_metrics(run_id: str):
    response = table.scan(
        FilterExpression="run_id = :run_id",
        ExpressionAttributeValues={":run_id": run_id},
    )
    items = response.get("Items", [])
    metrics_by_provider = {}

    for item in items:
        provider_name = item["provider_name"]
        model_name = item["model_name"]
        metrics = json.loads(item["metrics"])  # Parse the metrics JSON

        if provider_name not in metrics_by_provider:
            metrics_by_provider[provider_name] = {}
        metrics_by_provider[provider_name][model_name] = metrics

    return {"run_id": run_id, "metrics": metrics_by_provider}
