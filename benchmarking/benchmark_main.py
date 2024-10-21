import matplotlib.pyplot as plt
from IPython.display import display, Markdown
import numpy as np
import os
from datetime import datetime

class Benchmark:
    def __init__(self, providers, num_requests, models, prompt, streaming=False):
        self.providers = providers
        self.num_requests = num_requests
        self.models = models
        self.prompt = prompt
        self.streaming = streaming

        base_dir = "streaming" if streaming else "end_to_end"

        provider_names = sorted([provider.__class__.__name__.lower() for provider in providers])
        provider_dir_name = "_".join(provider_names)

        self.graph_dir = os.path.join("benchmark_graph", base_dir, provider_dir_name)

        # Create directories if they don't exist
        if not os.path.exists(self.graph_dir):
            os.makedirs(self.graph_dir)

    def plot_metrics(self, metric, filename_suffix):
        plt.figure(figsize=(8, 8))

        for provider in self.providers:
            provider_name = provider.__class__.__name__
            for model, latencies in provider.metrics[metric].items():
                # Convert to milliseconds and sort for CDF
                latencies_sorted = np.sort(latencies) * 1000
                cdf = np.arange(1, len(latencies_sorted) + 1) / len(latencies_sorted)
                model_name = provider.get_model_name(model)

                plt.plot(latencies_sorted, cdf, marker='o', linestyle='-', markersize=5, label=f'{provider_name} - {model_name}')

        plt.xlabel('Latency (ms)', fontsize=12)
        plt.ylabel('Portion of requests', fontsize=12)
        plt.grid(True)

        # Add legend
        plt.legend(loc='lower right')
        plt.xscale('log')

        # Show and save the plot
        plt.tight_layout()

        current_time = datetime.now().strftime("%y%m%d_%H%M")  
        filename = f"{filename_suffix}_{current_time}.png"
        filepath = os.path.join(self.graph_dir, filename)
        plt.savefig(filepath)
        plt.close()

        print(f"Saved graph: {filepath}")

    def run(self):
        for provider in self.providers:
            display(Markdown(f"### {provider.__class__.__name__}"))
            for model in self.models:
                model_name = provider.get_model_name(model)
                display(Markdown(f"#### Model: {model_name}\n #### Prompt: {self.prompt}"))

                for _ in range(self.num_requests):
                    display(Markdown(f'Request {_}'))
                    if self.streaming:
                        provider.perform_inference_streaming(model, self.prompt)
                    else:
                        provider.perform_inference(model, self.prompt)

        if not self.streaming:
            self.plot_metrics("response_times", "response_times")
        else:
            # Save all the relevant metrics plots when streaming is true
            self.plot_metrics("timetofirsttoken", "timetofirsttoken")
            self.plot_metrics("response_times", "totaltime")
            self.plot_metrics("timebetweentokens", "timebetweentokens")
            self.plot_metrics("timebetweentokens_median", "timebetweentokens_median")
            self.plot_metrics("timebetweentokens_p95", "timebetweentokens_p95")
