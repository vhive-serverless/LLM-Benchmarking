import os
import argparse
# import logging
from dotenv import load_dotenv
from benchmarking.benchmark_main import Benchmark
from providers import *
import requests
import matplotlib
from utils.token_config import output_sizes, input_sizes

# Load environment variables
load_dotenv()

# Set up logging based on verbosity level (issues)
# def setup_logging(verbosity):
#     level = logging.DEBUG if verbosity else logging.INFO
#     logging.basicConfig(level=level, format='%(message)s')

#     # Set external library logging levels to WARNING to avoid excessive output
#     logging.getLogger("requests").setLevel(logging.WARNING)
#     logging.getLogger("matplotlib").setLevel(logging.WARNING)

# Available providers dictionary for easy access
AVAILABLE_PROVIDERS = {
    "TogetherAI": TogetherAI(),
    "Cloudflare": Cloudflare(),
    "OpenAI": Open_AI(),
    # TODO Add more providers (Perplexity, Anthropic)
}

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
def run_benchmark(providers, num_requests, models, prompt, streaming, max_output, verbosity):
    # setup_logging(verbosity)
    
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

    # Check output tokens
    print(max_output, output_sizes)
    if max_output not in output_sizes:
        print("Please choose from these token lengths: ", output_sizes)
        return
    # Run the benchmark
    # logging.info("\nRunning benchmark...")
    print("\nRunning benchmark...")
    b = Benchmark(selected_providers, num_requests, valid_models, max_output, prompt=prompt, streaming=streaming)
    b.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a benchmark on selected AI providers and models.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Command-line arguments
    parser.add_argument("-p", "--providers", nargs="+", help="List of providers to benchmark (e.g., TogetherAI, Cloudflare, OpenAI)")
    parser.add_argument("-m", "--models", nargs="+", help="List of models to benchmark")
    parser.add_argument("-n", "--num_requests", type=int, default=1, help="Number of requests to run")
    parser.add_argument("--prompt", type=str, default="Tell me a story.", help="Prompt to use for inference")
    # parser.add_argument("--input-tokens", type=int, default=10, help="Prompt size to use for inference")
    parser.add_argument("--streaming", action="store_true", help="Enable streaming mode")
    parser.add_argument("--max-output", type=int, default=100, help="Max tokens for model output")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output for debugging")
    parser.add_argument("--list", action="store_true", help="List available providers and models")

    args = parser.parse_args()

    # Display available providers and models if --list flag is used
    if args.list:
        display_available_providers()
    elif args.providers and args.models:
        # Run the benchmark with parsed arguments
        run_benchmark(args.providers, args.num_requests, args.models, args.prompt, args.streaming, args.max_output, args.verbose)
    else:
        parser.print_help()

# ----------------

# import os
# from dotenv import load_dotenv
# from benchmarking.benchmark_main import Benchmark
# from providers import *

# # Load environment variables
# load_dotenv()

# # Function to get user input for providers
# def get_providers(available_providers):
#     selected_providers = []
#     print("Available Providers:")
#     for provider in available_providers.keys():
#         print(f"- {provider}")
    
#     while True:
#         provider_input = input("\nEnter a provider name to add or 'done' to finish: ").strip()
#         if provider_input == "done":
#             if selected_providers:
#                 break
#             else:
#                 print("Please select at least one provider.")
#                 continue
#         elif provider_input in available_providers:
#             selected_providers.append(available_providers[provider_input])
#             print(f"{provider_input} added.")
#         else:
#             print("Invalid provider name, please try again.")
    
#     return selected_providers

# # Function to get common models between the selected providers
# def get_common_models(selected_providers):
#     model_sets = []
    
#     for provider in selected_providers:
#         if hasattr(provider, 'model_map'):
#             models = set(provider.model_map.keys())  # Fetch model names from model_map
#             model_sets.append(models)
    
#     # Find common models across selected providers
#     common_models = set.intersection(*model_sets) if model_sets else set()

#     if not common_models:
#         print("No common models found among selected providers.")
#         return None

#     return list(common_models)

# # Function to get user input for models
# def get_models(common_models):
#     selected_models = []
#     print("\nCommon models available:")
#     for model in common_models:
#         print(f"- {model}")
    
#     while True:
#         model_input = input("\nEnter a model name to add or 'done' to finish: ").strip()
#         if model_input == "done":
#             if selected_models:
#                 break
#             else:
#                 print("Please select at least one model.")
#                 continue
#         elif model_input in common_models:
#             selected_models.append(model_input)
#             print(f"{model_input} added.")
#         else:
#             print("Invalid model name, please try again.")
    
#     return selected_models

# # Main function to run the benchmark
# def run_benchmark(available_providers):
#     # Get user-selected providers
#     selected_providers = get_providers(available_providers)
#     print(f"\nSelected Providers: {[provider.__class__.__name__ for provider in selected_providers]}")
    
#     # Get common models from selected providers
#     common_models = get_common_models(selected_providers)
#     if not common_models:
#         return  # Exit if no common models
    
#     # Get user-selected models
#     selected_models = get_models(common_models)
#     print(f"\nSelected Models: {selected_models}")
    
#     # Ask for streaming mode
#     streaming_input = input("\nDo you want to enable streaming? (yes/no): ").strip().lower()
#     streaming = streaming_input == "yes"
    
#     # Ask for the number of requests
#     num_requests = int(input("\nEnter the number of requests: ").strip())
    
#     # Run the benchmark
#     print("\nRunning benchmark...")
#     b = Benchmark(selected_providers, num_requests, selected_models, prompt="What are some fun things to do in New York? Give me 1 short example.", streaming=streaming)
#     b.run()

# if __name__ == "__main__":
#     # Available providers can be passed as a parameter
#     available_providers = {
#         "TogetherAI": TogetherAI(),
#         "Cloudflare": Cloudflare(),
#         "OpenAI": Open_AI(),
#         # "PerplexityAI": PerplexityAI()
#     }
#     run_benchmark(available_providers)
