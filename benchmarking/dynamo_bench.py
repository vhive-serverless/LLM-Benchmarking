"""
Module for benchmarking performance metrics of Large Language Model providers and storing
results in a DynamoDB table.
"""
import json
import os
import uuid
from datetime import datetime

import boto3
import numpy as np
from botocore.exceptions import ClientError


class Benchmark:
    """
    A class to benchmark the performance of various LLM providers.
    """

    def __init__(
        self,
        providers,
        num_requests,
        models,
        max_output,
        prompt,
        streaming=False,
        verbosity=False,
    ):
        """
        Initialize the Benchmark object.

        Args:
            providers (list): List of provider objects to benchmark.
            num_requests (int): Number of requests to send per provider.
            models (list): List of models to benchmark.
            max_output (int): Maximum output length.
            prompt (str): Input prompt for benchmarking.
            streaming (bool, optional): Whether to use streaming mode. Defaults to False.
            verbosity (bool, optional): Enable verbose output. Defaults to False.
        """
        self.providers = providers
        self.num_requests = num_requests
        self.models = models
        self.prompt = prompt
        self.streaming = streaming
        self.max_output = max_output
        self.verbosity = verbosity
        self.run_id = str(uuid.uuid4())  # Generate a unique ID for each benchmark run

        # Initialize DynamoDB
        self.dynamodb = boto3.resource(
            "dynamodb",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        self.table_name = "BenchmarkMetrics"  # Replace with your DynamoDB table name

        # Data structure to hold all metrics for this run
        self.benchmark_data = {
            "run_id": self.run_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "prompt": self.prompt,
            "providers": {},
        }

    @staticmethod
    def clean_data(data):
        """
        Recursively removes empty values from a dictionary.

        Args:
            data (dict): Input dictionary.

        Returns:
            dict: Cleaned dictionary.
        """
        if isinstance(data, dict):
            return {
                k: Benchmark.clean_data(v)
                for k, v in data.items()
                if v not in [None, "", [], {}]
            }
        if isinstance(data, list):
            return [Benchmark.clean_data(v) for v in data if v not in [None, "", [], {}]]
        return str(data) if isinstance(data, float) else data

    def store_data_points(self):
        """
        Store benchmark data in DynamoDB using an optimized schema with nested metrics.
        """
        table = self.dynamodb.Table(self.table_name)
        try:
            for provider_name, models in self.benchmark_data["providers"].items():
                for model_name, metrics in models.items():
                    item = {
                        "id": str(uuid.uuid4()),
                        "run_id": self.benchmark_data["run_id"],
                        "timestamp": self.benchmark_data["timestamp"],
                        "provider_name": provider_name,
                        "model_name": model_name,
                        "prompt": self.benchmark_data["prompt"],
                        "metrics": json.dumps(metrics),  # Serialize metrics as JSON string
                        "streaming": self.streaming,
                    }
                    table.put_item(Item=item)
            print(f"Successfully stored benchmark data for run ID {self.run_id}")
        except ClientError as e:
            print(f"Error saving to DynamoDB: {e.response['Error']['Message']}")

    def add_metric_data(self, provider_name, model_name, metric, latencies):
        """
        Add latency and CDF data to the benchmark data structure.

        Args:
            provider_name (str): The name of the provider.
            model_name (str): The name of the model.
            metric (str): The metric type (e.g., response_times, timetofirsttoken).
            latencies (list): List of latency values in milliseconds.
        """
        latencies_sorted = np.sort(latencies) * 1000  # Convert to milliseconds
        cdf = np.arange(1, len(latencies_sorted) + 1) / len(latencies_sorted)

        # Convert floats to string for DynamoDB compatibility
        latencies_sorted = [str(val) for val in latencies_sorted.tolist()]
        cdf = [str(val) for val in cdf.tolist()]

        self.benchmark_data["providers"].setdefault(provider_name, {}).setdefault(
            model_name, {}
        )[metric] = {"latencies": latencies_sorted, "cdf": cdf}

    def plot_metrics(self, metric):
        """
        Collect and add latency and CDF data points for each provider and model.

        Args:
            metric (str): The metric type to collect (e.g., response_times).
        """
        for provider in self.providers:
            provider_name = provider.__class__.__name__
            for model, latencies in provider.metrics[metric].items():
                model_name = provider.get_model_name(model)
                self.add_metric_data(provider_name, model_name, metric, latencies)

    def run(self):
        """
        Execute the benchmark and store metrics in DynamoDB.
        """
        for provider in self.providers:
            for model in self.models:
                for _ in range(self.num_requests):
                    if self.streaming:
                        provider.perform_inference_streaming(
                            model, self.prompt, self.max_output, self.verbosity
                        )
                    else:
                        provider.perform_inference(
                            model, self.prompt, self.max_output, self.verbosity
                        )

        metrics_to_plot = (
            ["timetofirsttoken", "response_times", "timebetweentokens", "tps", "timebetweentokens_p95", "timebetweentokens_median"]
            if self.streaming
            else ["response_times"]
        )
        for metric in metrics_to_plot:
            self.plot_metrics(metric)

        self.store_data_points()
