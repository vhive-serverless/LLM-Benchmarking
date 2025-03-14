import os
import requests
import numpy as np
from providers.base_provider import ProviderInterface
from time import perf_counter as timer
import re


class Azure(ProviderInterface):
    def __init__(self):
        """Initialize AzureProvider with required API information."""
        super().__init__()

        # Map model names to Azure model IDs
        self.model_map = {
            # "mistral-7b-instruct-v0.1": "mistral-7b-instruct-v0.1",
            "meta-llama-3.1-8b-instruct": "Meta-Llama-3-1-8B-Instruct-fyp",
            "meta-llama-3.1-70b-instruct": "Meta-Llama-3-1-70B-Instruct-fyp",
            "mistral-large": "Mistral-Large-2411-yatcd",
            "common-model": "Mistral-Large-2411-yatcd",
        }

        # Define API keys for each model
        self.model_api_keys = {
            # "mistral-7b-instruct-v0.1": os.environ.get("MISTRAL_API_KEY"),
            "meta-llama-3.1-8b-instruct": os.environ.get("AZURE_LLAMA_8B_API"),
            "meta-llama-3.1-70b-instruct": os.environ.get("AZURE_LLAMA_3.1_70B_API"),
            "mistral-large": os.environ.get("MISTRAL_LARGE_API"),
            "common-model": os.environ.get("MISTRAL_LARGE_API")
        }

    def get_model_name(self, model):
        """Retrieve the model name based on the input key."""
        return self.model_map.get(model, None)

    def get_model_api_key(self, model):
        """Retrieve the API key for a specific model."""
        api_key = self.model_api_keys.get(model)
        if not api_key:
            raise ValueError(
                f"No API key found for model '{model}'. Ensure it is set in environment variables."
            )
        return api_key

    def perform_inference(self, model, prompt, max_output=100, verbosity=True):
        """Performs non-streaming inference request to Azure."""
        try:
            model_id = self.get_model_name(model)
            api_key = self.get_model_api_key(model)
            if model_id is None:
                print(f"Model {model} not available.")
                return None
            start_time = timer()
            endpoint = f"https://{model_id}.eastus.models.ai.azure.com/chat/completions"
            response = requests.post(
                f"{endpoint}",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": max_output,
                },
                timeout=500,
            )
            elapsed = timer() - start_time
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
                return None

            # Parse and display response
            inference = response.json()
            self.log_metrics(model, "response_times", elapsed)
            if verbosity:
                print(f"Response: {inference['choices'][0]['message']['content']}")
            return inference
        
        except Exception as e:
            print(f"[ERROR] Inference failed for model '{model}': {e}")
            return None, None

    def perform_inference_streaming(
        self, model, prompt, max_output=100, verbosity=True
    ):
        """Performs streaming inference request to Azure."""
        model_id = self.get_model_name(model)
        api_key = self.get_model_api_key(model)
        if model_id is None:
            print(f"Model {model} not available.")
            return None

        inter_token_latencies = []
        endpoint = f"https://{model_id}.eastus.models.ai.azure.com/chat/completions"
        start_time = timer()
        try:
            response = requests.post(
                f"{endpoint}",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "messages": [
                        # {"role": "system", "content": self.system_prompt + "\nThe number appended at the end is not important."},
                        # {"role": "user", "content": prompt + " " + str(timer())},
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": max_output,
                    "stream": True,
                },
                stream=True,
                timeout=500,
            )

            first_token_time = None
            for line in response.iter_lines():
                if line:
                    # print(line)
                    if first_token_time is None:
                        # print(line)
                        first_token_time = timer()
                        ttft = first_token_time - start_time
                        prev_token_time = first_token_time
                        if verbosity:
                            print(f"##### Time to First Token (TTFT): {ttft:.4f} seconds\n")

                    line_str = line.decode("utf-8").strip()
                    
                    if line_str == "data: [DONE]":
                        # print(line_str)
                        # print("here")
                        total_time = timer() - start_time
                        break

                    # Capture token timing
                    time_to_next_token = timer()
                    inter_token_latency = time_to_next_token - prev_token_time
                    prev_token_time = time_to_next_token
                    inter_token_latencies.append(inter_token_latency)

                    # Display token if verbosity is enabled
                    match = re.search(r'"content"\s*:\s*"(.*?)"', line_str)
                    if match:
                        print(match.group(1), end="")
                    # if verbosity:
                    #     if len(inter_token_latencies) < 20:
                    #         print(line_str[19:].split('"')[5], end="")
                    #     elif len(inter_token_latencies) == 20:
                    #         print("...")

            # Calculate total metrics

            if verbosity:
                print(f"\nTotal Response Time: {total_time:.4f} seconds")
                print(len(inter_token_latencies))

            # Log metrics
            avg_tbt = sum(inter_token_latencies) / len(inter_token_latencies)
            print(f"{avg_tbt:.4f}, {len(inter_token_latencies)}")
            self.log_metrics(model, "timetofirsttoken", ttft)
            self.log_metrics(model, "response_times", total_time)
            self.log_metrics(model, "timebetweentokens", avg_tbt)
            self.log_metrics(
                model, "timebetweentokens_median", np.median(inter_token_latencies)
            )
            self.log_metrics(
                model, "timebetweentokens_p95", np.percentile(inter_token_latencies, 95)
            )
            self.log_metrics(model, "totaltokens", len(inter_token_latencies) + 1)

        except Exception as e:
            print(f"[ERROR] Streaming inference failed for model '{model}': {e}")
            return None, None
