import os
import argparse
# import logging
from dotenv import load_dotenv
from benchmarking.benchmark_main import Benchmark
from providers import *
import requests
import matplotlib
from utils.prompt_generator import get_prompt
import json

# Load environment variables
load_dotenv()

# Define input parser
parser = argparse.ArgumentParser(
    description="Run a benchmark on selected AI providers and models.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument("-c", "--config", type=str, help="Path to the JSON configuration file")
parser.add_argument("--list", action="store_true", help="List available providers and models")

# Set up logging based on verbosity level (issues)
# def setup_logging(verbosity):
#     level = logging.DEBUG if verbosity else logging.INFO
#     logging.basicConfig(level=level, format='%(message)s')

#     # Set external library logging levels to WARNING to avoid excessive output
#     logging.getLogger("requests").setLevel(logging.WARNING)
#     logging.getLogger("matplotlib").setLevel(logging.WARNING)

# Define possible input sizes
input_sizes = [10, 100, 1000, 10000, 100000]

# Define possible max output tokens
output_size_upper_limit = 5000
output_size_lower_limit = 100

# Available providers dictionary for easy access
AVAILABLE_PROVIDERS = {
    "TogetherAI": TogetherAI(),
    "Cloudflare": Cloudflare(),
    "OpenAI": Open_AI(),
    # TODO Add more providers (Perplexity, Anthropic)
}

# Function to load JSON configuration
def load_config(file_path):
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print("Error: Failed to parse the configuration file. Ensure it is valid JSON.")
        return None

# Function to display available providers and their models
def display_available_providers():
    print("\nAvailable Providers and Models:")
    for provider_name, provider_instance in AVAILABLE_PROVIDERS.items():
        print(f"\n{provider_name}")
        if hasattr(provider_instance, 'model_map'):
            for common_name, model_name in provider_instance.model_map.items():
                print(f"  - {common_name}: {model_name}")

        else:
            print("  No models available.")

# Function to validate provider selection
def validate_providers(selected_providers):
    valid_providers = []
    for provider_name in selected_providers:
        if provider_name in AVAILABLE_PROVIDERS:
            valid_providers.append(AVAILABLE_PROVIDERS[provider_name])
        else:
            # logging.warning(f"Warning: {provider_name} is not a valid provider name.")
            print(f"Warning: {provider_name} is not a valid provider name.")
    return valid_providers

# Function to get common models across selected providers
def get_common_models(selected_providers):
    model_sets = []
    for provider in selected_providers:
        if hasattr(provider, 'model_map'):
            models = set(provider.model_map.keys())  # Fetch model names from model_map
            model_sets.append(models)
    
    common_models = set.intersection(*model_sets) if model_sets else set()
    return list(common_models)

# Validate user-selected models
def validate_selected_models(selected_models, common_models, selected_providers):
    valid_models = []
    for model in selected_models:
        if model in common_models:
            valid_models.append(model)
        else:
            if len(selected_providers) > 1:
                # logging.warning(f"Warning: Model '{model}' is not a common model among the chosen providers. Please select common models.")
                print(f"Warning: Model '{model}' is not a common model among the chosen providers. Please select common models.")
            else:
                for provider in selected_providers:
                    if model in provider.model_map:
                        valid_models.append(model)
                        break
                    else:
                        # logging.warning(f"Warning: Model '{model}' not available for all selected providers.")
                        print(f"Warning: Model '{model}' not available for all selected providers.")
    return valid_models

# Main function to run the benchmark
def run_benchmark(config):
    
    providers = config.get("providers", [])
    num_requests = config.get("num_requests", 1)
    models = config.get("models", [])
    input_tokens = config.get("input_tokens", 10)
    streaming = config.get("streaming", False)
    max_output = config.get("max_output", 100)
    verbose = config.get("verbose", False)    

    # Validate and initialize providers
    selected_providers = validate_providers(providers)
    # logging.info(f"Selected Providers: {[provider.__class__.__name__ for provider in selected_providers]}")
    print(f"Selected Providers: {[provider.__class__.__name__ for provider in selected_providers]}")
    
    # Get common models from selected providers
    common_models = get_common_models(selected_providers) if len(selected_providers) > 1 else []
    if not common_models and len(selected_providers) > 1:
        # logging.error("No common models found among selected providers.")
        print("No common models found among selected providers.")
        return

    # Validate models
    valid_models = validate_selected_models(models, common_models, selected_providers)
    if not valid_models:
        # logging.error("No valid/common models selected. Ensure models are available across providers.")
        print("No valid/common models selected. Ensure models are available across providers.")
        display_available_providers()
        return

    # logging.info(f"Selected Models: {valid_models}")
    print(f"Selected Models: {valid_models}")

    # handling input tokens
    if input_tokens not in input_sizes:
        print(f"Please enter an input token from the following choices: {input_sizes}")
        return
    else:
        prompt = get_prompt(input_tokens)
        # print(f"Prompt: {prompt}")


    if max_output < output_size_lower_limit or max_output > output_size_upper_limit:
        print(f"Please enter an output token length between {output_size_lower_limit} and {output_size_upper_limit}.")
        return
    # Run the benchmark
    # logging.info("\nRunning benchmark...")

    print("\nRunning benchmark...")
    b = Benchmark(selected_providers, num_requests, valid_models, max_output, prompt=prompt, streaming=streaming, verbosity=verbose)
    b.run()

def main():

    args = parser.parse_args()

    # Display available providers and models if --list flag is used
    if args.list:
        display_available_providers()
    elif args.config:
        config = load_config(args.config)
        if config:
            run_benchmark(config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
    # Command-line arguments
    # parser.add_argument("-p", "--providers", nargs="+", help="List of providers to benchmark (e.g., TogetherAI, Cloudflare, OpenAI)")
    # parser.add_argument("-m", "--models", nargs="+", help="List of models to benchmark")
    # parser.add_argument("-n", "--num_requests", type=int, default=1, help="Number of requests to run")
    # # parser.add_argument("--prompt", type=str, default="Tell me a story.", help="Prompt to use for inference")
    # parser.add_argument("--input-tokens", type=int, default=10, help="Prompt size to use for inference")
    # parser.add_argument("--streaming", action="store_true", help="Enable streaming mode")
    # parser.add_argument("--max-output", type=int, default=100, help="Max tokens for model output")
    # parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output for debugging")