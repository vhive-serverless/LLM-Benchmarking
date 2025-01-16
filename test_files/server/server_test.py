from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from server.server import (
    app,
    get_dynamodb_table,
)  # Replace with your actual import path


# Mock data
@pytest.fixture
def mock_dynamodb_data():
    return [
        {
            "run_id": "1",
            "timestamp": "2025-01-01 10:00:00",
            "streaming": True,
            "provider_name": "Provider1",
            "model_name": "ModelA",
            "metrics": '{"timetofirsttoken": {"latencies": [100, 200], "cdf": [0.5, 1.0]}}',
        },
        {
            "run_id": "2",
            "timestamp": "2025-01-02 11:00:00",
            "streaming": False,
            "provider_name": "Provider2",
            "model_name": "ModelB",
            "metrics": '{"timetofirsttoken": {"latencies": [150, 250], "cdf": [0.5, 1.0]}}',
        },
    ]


# Mock DynamoDB table
@pytest.fixture
def mock_dynamodb_table(mock_dynamodb_data):
    mock_table = MagicMock()

    # Simulate the `scan` method
    def scan_side_effect(**kwargs):
        expression_values = kwargs.get("ExpressionAttributeValues", {})
        return {
            "Items": [
                item
                for item in mock_dynamodb_data
                if all(
                    item.get(key.strip(":")) == value
                    for key, value in expression_values.items()
                )
            ]
        }

    mock_table.scan.side_effect = scan_side_effect
    return mock_table


# Patch `get_dynamodb_table` to return the mocked table
@pytest.fixture
def client(mock_dynamodb_table):
    with patch("server.server.table", mock_dynamodb_table):
        yield TestClient(app)


# Test example: Test the latest run ID endpoint
def test_get_latest_run_id(client):
    response = client.get("/metrics/date?metricType=timetofirsttoken&date=latest")
    assert response.status_code == 200
    data = response.json()
    assert "run_id" in data
    assert data["run_id"] == "1"  # Expected value from mock data


def test_get_metrics_period(client):
    response = client.get("/metrics/period?metricType=timetofirsttoken&timeRange=week")
    assert response.status_code == 200
    data = response.json()
    assert "metricType" in data
    assert data["metricType"] == "timetofirsttoken"
    assert "aggregated_metrics" in data


def test_get_metrics_by_date(client):
    # Use a formatted date matching the mock data
    date = datetime.now().strftime("%d-%m-%Y")
    response = client.get(f"/metrics/date?metricType=timetofirsttoken&date={date}")
    assert response.status_code == 200
    data = response.json()
    assert "date" in data
    assert data["date"] == date
    assert "metrics" in data


def test_invalid_time_range(client):
    response = client.get(
        "/metrics/period?metricType=timetofirsttoken&timeRange=invalid"
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "Invalid timeRange" in data["error"]


def test_invalid_date_format(client):
    response = client.get("/metrics/date?metricType=timetofirsttoken&date=invalid_date")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "Invalid date format. Use '12-12-2024" in data["error"]
