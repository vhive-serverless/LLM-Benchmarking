import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime


class Benchmark:
    """
    A class to run and visualize benchmarks for different AI providers.

    Attributes:
        providers (list): List of AI provider instances.
        num_requests (int): Number of requests to run per model.
        models (list): List of model names to benchmark.
        max_output (int): Maximum number of tokens for model output.
        prompt (str): The input prompt to use for benchmarking.
        streaming (bool): Flag to indicate whether to use streaming mode.
        verbosity (bool): Flag to enable verbose output during benchmarking.
        graph_dir (str): Directory path for saving generated plots.
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
        Initializes the Benchmark instance with provided parameters.

        Args:
            providers (list): List of AI provider instances.
            num_requests (int): Number of requests to run per model.
            models (list): List of model names to benchmark.
            max_output (int): Maximum number of tokens for model output.
            prompt (str): The input prompt to use for benchmarking.
            streaming (bool, optional): Flag to indicate streaming mode. Defaults to False.
            verbosity (bool, optional): Flag to enable verbose output. Defaults to False.
        """
        self.providers = providers
        self.num_requests = num_requests
        self.models = models
        self.prompt = prompt
        self.streaming = streaming
        self.max_output = max_output
        self.verbosity = verbosity

        base_dir = "streaming" if streaming else "end_to_end"

        provider_names = sorted(
            [provider.__class__.__name__.lower() for provider in providers]
        )
        provider_dir_name = "_".join(provider_names)

        self.graph_dir = os.path.join("benchmark_graph", base_dir, provider_dir_name)

        # Create directories if they don't exist
        if not os.path.exists(self.graph_dir):
            os.makedirs(self.graph_dir)

    def plot_metrics(self, metric, filename_suffix):
        """
        Plots and saves graphs for the given metric.

        Args:
            metric (str): The name of the metric to plot (e.g., "response_times").
            filename_suffix (str): Suffix to append to the filename for saving the plot.
        """
        plt.figure(figsize=(8, 8))

        for provider in self.providers:
            provider_name = provider.__class__.__name__
            for model, latencies in provider.metrics[metric].items():
                # Convert to milliseconds and sort for CDF
                latencies_sorted = np.sort(latencies) * 1000
                cdf = np.arange(1, len(latencies_sorted) + 1) / len(latencies_sorted)
                model_name = provider.get_model_name(model)

                plt.plot(
                    latencies_sorted,
                    cdf,
                    marker="o",
                    linestyle="-",
                    markersize=5,
                    label=f"{provider_name} - {model_name}",
                )

        plt.xlabel("Latency (ms)", fontsize=12)
        plt.ylabel("Portion of requests", fontsize=12)
        plt.grid(True)

        # Add legend
        plt.legend(loc="best")
        plt.xscale("log")

        # Show and save the plot
        plt.tight_layout()

        current_time = datetime.now().strftime("%y%m%d_%H%M")
        filename = f"{filename_suffix}_{current_time}.png"
        filepath = os.path.join(self.graph_dir, filename)
        plt.savefig(filepath)
        plt.close()

        print(f"Saved graph: {filepath}")

    def run(self):
        """
        Runs the benchmark for the selected providers and models, and plots the results.

        This method sends a number of requests to each model for each provider, collects
        performance metrics, and generates plots based on those metrics.
        """
        for provider in self.providers:
            provider_name = provider.__class__.__name__
            # logging.debug(f"{provider_name}")
            print(f"{provider_name}")
            for model in self.models:
                model_name = provider.get_model_name(model)
                print(f"Model: {model_name}\nPrompt: {self.prompt}")

                for i in range(self.num_requests):
                    if self.verbosity:
                        print(f"Request {i + 1}/{self.num_requests}")
                    elif i % 10 == 0 or i == self.num_requests - 1:
                        print(f"\nRequest {i + 1}/{self.num_requests}")

                    if self.streaming:
                        provider.perform_inference_streaming(
                            model, self.prompt, self.max_output, self.verbosity
                        )
                    else:
                        provider.perform_inference(
                            model, self.prompt, self.max_output, self.verbosity
                        )

        if not self.streaming:
            self.plot_metrics("response_times", "response_times")
        else:
            # Save all the relevant metrics plots when streaming is true
            self.plot_metrics("timetofirsttoken", "timetofirsttoken")
            self.plot_metrics("response_times", "totaltime")
            self.plot_metrics("timebetweentokens", "timebetweentokens")
            self.plot_metrics("timebetweentokens_median", "timebetweentokens_median")
            self.plot_metrics("timebetweentokens_p95", "timebetweentokens_p95")
