import pytest
from fastapi.testclient import TestClient
from moto import mock_aws 
import boto3
from server.server import app
from datetime import datetime, timedelta
import json
import os

# Initialize test client
client = TestClient(app)

# Mock DynamoDB setup
@mock_aws 
@pytest.fixture(scope="function")
def setup_dynamodb():
        # Create the mock DynamoDB resource
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        
        # Define the table schema
        dynamodb.create_table(
            TableName="MockTable",
            KeySchema=[
                {"AttributeName": "run_id", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "run_id", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )

        # Mock table instance
        mock_table = dynamodb.Table("MockTable")

        # Insert mock data
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mock_table.put_item(
            Item={
                "run_id": "1",
                "timestamp": current_time,
                "streaming": True,
                "provider_name": "Provider1",
                "model_name": "ModelA",
                "metrics": json.dumps({"timetofirsttoken": {"latencies": [100, 200], "cdf": [0.5, 1.0]}}),
            }
        )
        yield mock_table

@pytest.mark.asyncio
async def test_get_latest_run_id():
    response = client.get("/metrics/date?metricType=timetofirsttoken&date=latest")
    assert response.status_code == 200
    data = response.json()
    assert "run_id" in data
    assert "metrics" in data

@pytest.mark.asyncio
async def test_get_metrics_period():
    response = client.get("/metrics/period?metricType=timetofirsttoken&timeRange=week")
    assert response.status_code == 200
    data = response.json()
    assert "metricType" in data
    assert data["metricType"] == "timetofirsttoken"
    assert "aggregated_metrics" in data

@pytest.mark.asyncio
async def test_get_metrics_by_date():
    # Use a formatted date matching the mock data
    date = datetime.now().strftime("%d%b%Y")
    response = client.get(f"/metrics/date?metricType=timetofirsttoken&date={date}")
    assert response.status_code == 200
    data = response.json()
    assert "date" in data
    assert data["date"] == date
    assert "metrics" in data

@pytest.mark.asyncio
async def test_invalid_time_range():
    response = client.get("/metrics/period?metricType=timetofirsttoken&timeRange=invalid")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "Invalid timeRange" in data["error"]

@pytest.mark.asyncio
async def test_invalid_date_format():
    response = client.get("/metrics/date?metricType=timetofirsttoken&date=invalid_date")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "Invalid date format" in data["error"]
