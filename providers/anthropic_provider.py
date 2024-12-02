# anthropic_provider.py
import os
import anthropic
import numpy as np
from timeit import default_timer as timer
from providers.provider_interface import ProviderInterface


class Anthropic(ProviderInterface):
    def __init__(self):
        """
        Initializes the AnthropicProvider with the necessary API key and client.
        """
        super().__init__()

        # Load API key from environment
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided as an environment variable.")

        # Initialize the Anthropic client
        self.client = anthropic.Anthropic(api_key=self.api_key)

        # Model mapping for Anthropic models
        self.model_map = {
            "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
            "claude-3-opus": "claude-3-opus-latest",
            "claude-3-haiku": "claude-3-haiku-20240307",
            "common-model": "claude-3-haiku-20240307"
        }

    def get_model_name(self, model):
        """
        Retrieves the actual model identifier for a given model alias.

        Args:
            model (str): The alias name of the model.

        Returns:
            str: The identifier of the model for API calls.
        """
        return self.model_map.get(model, None)

    def perform_inference(self, model, prompt, max_output=100, verbosity=True):
        """
        Performs a synchronous inference call to the Anthropic API.

        Args:
            model (str): The model name to use for inference.
            prompt (str): The user prompt for the chat completion.

        Returns:
            float: The elapsed time in seconds for the inference request.
        """
        model_id = self.get_model_name(model)
        if model_id is None:
            raise ValueError(f"Model {model} not available for Anthropic.")

        start = timer()
        response = self.client.messages.create(
            model=model_id,
            max_tokens=max_output,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            stop_sequences=["\nUser:"],
        )
        elapsed = timer() - start
        self.log_metrics(model, "response_times", elapsed)
        # Process and display the response
        if verbosity:
            self.display_response(response, elapsed)
        return elapsed

    def perform_inference_streaming(
        self, model, prompt, max_output=100, verbosity=True
    ):
        """
        Performs a streaming inference call to the Anthropic API.

        Args:
            model (str): The model name to use for inference.
            prompt (str): The user prompt for the chat completion.
        """
        model_id = self.get_model_name(model)
        if model_id is None:
            raise ValueError(f"Model {model} not available for Anthropic.")

        first_token_time = None
        inter_token_latencies = []

        start = timer()
        with self.client.messages.stream(
            model=model_id,
            max_tokens=max_output,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            stop_sequences=["\nUser:"],
        ) as stream:
            for chunk in stream.text_stream:
                if first_token_time is None:
                    first_token_time = timer()
                    TTFT = first_token_time - start
                    prev_token_time = first_token_time
                    self.log_metrics(model, "timetofirsttoken", TTFT)
                    if verbosity:
                        print(f"\nTime to First Token (TTFT): {TTFT:.4f} seconds\n")

                # Calculate inter-token latencies
                time_to_next_token = timer()
                inter_token_latency = time_to_next_token - prev_token_time
                prev_token_time = time_to_next_token

                inter_token_latencies.append(inter_token_latency)
                if verbosity:
                    print(chunk, end="", flush=True)

            elapsed = timer() - start
            if verbosity:
                print(f"\nTotal Response Time: {elapsed:.4f} seconds")

        # Log remaining metrics
        self.log_metrics(model, "response_times", elapsed)
        self.log_metrics(model, "timebetweentokens", inter_token_latencies)
        self.log_metrics(model, "totaltokens", len(inter_token_latencies) + 1)
        self.log_metrics(model, "tps", (len(inter_token_latencies) + 1) / elapsed)
        self.log_metrics(
            model, "timebetweentokens_median", np.percentile(inter_token_latencies, 50)
        )
        self.log_metrics(
            model, "timebetweentokens_p95", np.percentile(inter_token_latencies, 95)
        )

    def display_response(self, response, elapsed):
        """
        Prints the response content and the time taken to generate it.

        Args:
            response (dict): The response dictionary from the Anthropic API.
            elapsed (float): Time in seconds taken to generate the response.
        """
        content = "".join(block.get("text", "") for block in response["content"])
        print(content)
        print(f"\nGenerated in {elapsed:.2f} seconds")
