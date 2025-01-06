import boto3
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

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
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("BenchmarkMetrics")


def get_latest_run_id(streaming: bool):
    """
    Retrieve the latest run_id, optionally filtering by the streaming parameter.

    :param streaming: Whether to filter for streaming metrics (default is False).
    """
    # Build the FilterExpression dynamically
    filter_expression = "#streaming = :streaming"
    expression_attribute_names = {"#streaming": "streaming"}
    expression_attribute_values = {":streaming": streaming}

    # Scan the table
    response = table.scan(
        FilterExpression=filter_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
    ) if filter_expression else table.scan()

    items = response.get("Items", [])
    if not items:
        return {"error": "No data found"}

    # Sort by timestamp to get the latest run_id
    latest_item = max(items, key=lambda x: x["timestamp"])
    return {"run_id": latest_item["run_id"]}

def get_metrics(run_id: str, metricType: str = Query(None)):
    """
    Retrieve metrics for a given run_id and optionally filter by a specific metric type.
    
    :param run_id: The ID of the run to retrieve metrics for.
    :param metricType: (Optional) The specific metric type to return (e.g., "timetofirsttoken").
    """
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

        # Filter metrics if a metricType is specified
        if metricType:
            filtered_metrics = {metricType: metrics.get(metricType)} if metricType in metrics else {}
            metrics_by_provider[provider_name][model_name] = filtered_metrics
        else:
            metrics_by_provider[provider_name][model_name] = metrics
            
    sorted_metrics_by_provider = {
        provider: metrics_by_provider[provider]
        for provider in sorted(metrics_by_provider)
    }

    return {"run_id": run_id, "metrics": sorted_metrics_by_provider}

@app.get("/metrics/period")
def get_metrics_period(metricType: str, timeRange: str, streaming: bool = True):
    """
    Retrieve aggregated metrics for a given time range, grouped by providers.

    :param metricType: The specific metric type to return (e.g., "timetofirsttoken").
    :param timeRange: The time range to aggregate metrics for ("week", "month", "three-month").
    """
    # Define time ranges
    time_ranges = {
        "week": timedelta(weeks=1),
        "month": timedelta(days=30),
        "three-month": timedelta(days=90),
    }

    if timeRange not in time_ranges:
        return {"error": f"Invalid timeRange. Valid options are {list(time_ranges.keys())}"}

    # Calculate the start and end dates for the time range
    end_date = datetime.now()
    start_date = end_date - time_ranges[timeRange]

    # Convert dates to strings for comparison
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")

    # Build FilterExpression dynamically for the time range
    filter_expression = "#ts BETWEEN :start_date AND :end_date AND #streaming = :streaming"
    expression_attribute_names = {"#ts": "timestamp"}
    expression_attribute_names["#streaming"] = "streaming"
    expression_attribute_values = {
        ":start_date": start_date_str,
        ":end_date": end_date_str,
        ":streaming": streaming
    }

    # Scan the table
    response = table.scan(
        FilterExpression=filter_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
    )

    items = response.get("Items", [])
    aggregated_metrics = {}
    date_array = set()

    for item in items:
        provider_name = item["provider_name"]

        # Parse the metrics JSON and check if the specified metricType exists
        metrics = json.loads(item["metrics"])
        if metricType not in metrics:
            continue

        # Calculate the aggregated metric for the row
        metric_data = metrics[metricType]
        latencies = list(map(float, metric_data["latencies"]))
        cdf_length = len(metric_data["cdf"])
        if cdf_length > 0:
            aggregated_latency = sum(latencies) / cdf_length
            formatted_date = datetime.strptime(item["timestamp"], "%Y-%m-%d %H:%M:%S").strftime(
                "%d%b%Y"
            )  # Format as daymonthyear
            date_array.add(formatted_date)
            
            # Group aggregated metrics by provider and date
            if provider_name not in aggregated_metrics:
                aggregated_metrics[provider_name] = {}
            if formatted_date not in aggregated_metrics[provider_name]:
                aggregated_metrics[provider_name][formatted_date] = []
            aggregated_metrics[provider_name][formatted_date].append(aggregated_latency)

    # Average aggregated metrics for each date per provider
    result = {
        provider: [
            {"date": date, "aggregated_metric": sum(values) / len(values)}
            for date, values in dates.items()
        ]
        for provider, dates in aggregated_metrics.items()
    }

    # Sort the result by provider name alphabetically
    sorted_result = {
        provider: result[provider]
        for provider in sorted(result)
    }

    return {"metricType": metricType, "timeRange": timeRange, "aggregated_metrics": sorted_result, "date_array": list(date_array)}


@app.get("/metrics/date")
def get_metrics_by_date(metricType: str, date: str, streaming: bool = True):
    """
    Retrieve metrics for a specific date and metric type.

    :param metricType: The specific metric type to return (e.g., "timetofirsttoken").
    :param date: The date to filter metrics by (format: "12Dec2024").
    :param streaming: Whether to filter for streaming metrics (default is True).
    """
    if date == "latest":
        # Retrieve the latest run_id
        latest_id_response = get_latest_run_id(streaming)
        if "error" in latest_id_response:
            return {"error": "No latest run_id found."}
        
        # Extract the run_id
        run_id = latest_id_response["run_id"]
        
        # Fetch metrics for the latest run_id
        return get_metrics(run_id, metricType)
    try:
        # Parse the date string in the format "12Dec2024"
        start_date = datetime.strptime(date, "%d%b%Y")
        end_date = start_date + timedelta(days=1)
    except ValueError:
        return {"error": "Invalid date format. Use '12Dec2024'."}

    # Convert dates to strings for comparison
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")

    # Build the FilterExpression for the specified date and streaming
    filter_expression = "#ts BETWEEN :start_date AND :end_date AND #streaming = :streaming"
    expression_attribute_names = {
        "#ts": "timestamp",
        "#streaming": "streaming",
    }
    expression_attribute_values = {
        ":start_date": start_date_str,
        ":end_date": end_date_str,
        ":streaming": streaming,
    }

    # Scan the table
    response = table.scan(
        FilterExpression=filter_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
    )

    items = response.get("Items", [])
    metrics_by_provider = {}
    for item in items:
        provider_name = item["provider_name"]
        model_name = item["model_name"]
        metrics = json.loads(item["metrics"])  # Parse the metrics JSON

        if provider_name not in metrics_by_provider:
            metrics_by_provider[provider_name] = {}

        # Filter metrics if a metricType is specified
        if metricType:
            filtered_metrics = {metricType: metrics.get(metricType)} if metricType in metrics else {}
            metrics_by_provider[provider_name][model_name] = filtered_metrics
        else:
            metrics_by_provider[provider_name][model_name] = metrics
            
    sorted_metrics_by_provider = {
        provider: metrics_by_provider[provider]
        for provider in sorted(metrics_by_provider)
    }

    return {"date": date, "metricType": metricType, "metrics": sorted_metrics_by_provider}
