import os
from timeit import default_timer as timer
import numpy as np
from openai import OpenAI
from providers.base_provider import BaseProvider


class PerplexityAI(BaseProvider):
    """perplexity provider class"""

    def __init__(self):
        """
        Initializes the AnthropicProvider with the necessary API key and client.
        """
        perplexity_api = os.environ.get("PERPLEXITY_AI_API")

        if not perplexity_api:
            raise ValueError(
                "Perplexity AI API token must be provided as an environment variable."
            )

        client_class = OpenAI
        base_url = "https://api.perplexity.ai"

        super().__init__(
            api_key=perplexity_api, client_class=client_class, base_url=base_url
        )

        # model names mapping
        self.model_map = {
            "meta-llama-3.1-70b-instruct": "llama-3.1-70b-instruct",  # 70b
            "8b": "llama-3.1-8b-instruct",  # 8b
            "meta-llama-3.1-sonar-405B": "llama-3.1-sonar-huge-128k-online",  # 405B
        }
    def perform_inference_streaming(
        self, model, prompt, max_output=100, verbosity=True
    ):
        model_id = self.get_model_name(model)
        if model_id is None:
            raise ValueError(f"Model {model} not available for provider.")
        first_token_time = None
        inter_token_latencies = []
        total_tokens = 0

        start = timer()
        response = self.client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            stream=True,
            max_tokens=max_output,
        )
        previous_completion_tokens = 0  # Initialize previous token count

        for chunk in response:
            current_completion_tokens = chunk.usage.completion_tokens
            new_tokens = current_completion_tokens - previous_completion_tokens
            previous_completion_tokens = current_completion_tokens
            if first_token_time is None:
                first_token_time = timer()
                ttft = first_token_time - start
                prev_token_time = first_token_time
                if verbosity:
                    print(f"\nTime to First Token (TTFT): {ttft:.4f} seconds\n")

            if chunk.choices[0].finish_reason:
                elapsed = timer() - start
                if verbosity:
                    print(f"\nTotal Response Time: {elapsed:.4f} seconds")
                break

            time_to_next_token = timer()
            inter_token_latency = (time_to_next_token - prev_token_time) / max(1, new_tokens)
            prev_token_time = time_to_next_token
            for _ in range(new_tokens):
                inter_token_latencies.append(inter_token_latency)

            total_tokens += new_tokens

        # Print the content of the chunk if verbosity is enabled
        if verbosity:
            if len(inter_token_latencies) < 20:
                print(chunk.choices[0].delta.content or "", end="", flush=True)
            elif len(inter_token_latencies) == 20:
                print("...")

        # Calculate total response time
        elapsed = timer() - start

        if verbosity:
            print(
                f"\nNumber of output tokens: {total_tokens}, "
                f"Time to First Token (TTFT): {ttft:.4f} seconds, "
                f"Total Response Time: {elapsed:.4f} seconds"
            )
        # Log metrics
        self.log_metrics(model, "timetofirsttoken", ttft)
        self.log_metrics(model, "response_times", elapsed)
        self.log_metrics(model, "timebetweentokens", inter_token_latencies)

        # Calculate additional latency metrics
        median = np.median(inter_token_latencies) if inter_token_latencies else 0
        p95 = np.percentile(inter_token_latencies, 95) if inter_token_latencies else 0
        self.log_metrics(model, "timebetweentokens_median", median)
        self.log_metrics(model, "timebetweentokens_p95", p95)
        self.log_metrics(model, "totaltokens", total_tokens)
        self.log_metrics(model, "tps", total_tokens / elapsed if elapsed > 0 else 0)