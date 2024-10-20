# base_provider.py for chat completions api
from providers.provider_interface import ProviderInterface
from timeit import default_timer as timer
import numpy as np

class BaseProvider(ProviderInterface):
    def __init__(self, api_key, client_class):
        super().__init__()

        if not api_key:
            raise ValueError("API key must be provided as an environment variable.")
        self.client = client_class(api_key=api_key)
        self.model_map = {}

    def get_model_name(self, model):
        return self.model_map.get(model, None)

    def perform_inference(self, model, prompt):
        model_id = self.get_model_name(model)
        if model_id is None:
            raise ValueError(f"Model {model} not available for provider.")
        start = timer()
        response = self.client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens= self.max_tokens
        )
        elapsed = timer() - start
        self.log_metrics(model, "response_times", elapsed)
        self.display_response(response, elapsed)
        return elapsed

    def perform_inference_streaming(self, model, prompt):
        model_id = self.get_model_name(model)
        if model_id is None:
            raise ValueError(f"Model {model} not available for provider.")
        first_token_time = None
        inter_token_latencies = []

        start = timer()
        response = self.client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            stream=True,
            max_tokens= self.max_tokens,
        )

        for chunk in response:
            if first_token_time is None:
                first_token_time = timer()
                TTFT = first_token_time - start
                prev_token_time = first_token_time
                print(f"\nTime to First Token (TTFT): {TTFT:.4f} seconds\n")

            if chunk.choices[0].finish_reason:
                elapsed = timer() - start
                print(f"\nTotal Response Time: {elapsed:.4f} seconds")
                break

            time_to_next_token = timer()
            inter_token_latency = time_to_next_token - prev_token_time
            prev_token_time = time_to_next_token

            inter_token_latencies.append(inter_token_latency)
            print(chunk.choices[0].delta.content or "", end="", flush=True)

        print(f'\nNumber of output tokens/chunks: {len(inter_token_latencies) + 1}')
        self.log_metrics(model, "timetofirsttoken", TTFT)
        self.log_metrics(model, "response_times", elapsed)
        self.log_metrics(model, "timebetweentokens", inter_token_latencies)
        median = np.percentile(inter_token_latencies, 50)
        p95 = np.percentile(inter_token_latencies, 95)
        self.log_metrics(model, "timebetweentokens_median", median)
        self.log_metrics(model, "timebetweentokens_p95", p95)
        self.log_metrics(model, "totaltokens", len(inter_token_latencies) + 1)
        self.log_metrics(model, "tps", (len(inter_token_latencies) + 1)/elapsed)
        
    def display_response(self, response, elapsed):
        print(response.choices[0].message.content)
        print(f"\nGenerated in {elapsed:.2f} seconds")
