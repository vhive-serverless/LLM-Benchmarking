from dotenv import load_dotenv
from benchmarking.benchmark_graph import Benchmark
from providers import TogetherAI, Cloudflare, PerplexityAI, Open_AI, Hyperbolic, GroqProvider

# Load environment variables
load_dotenv()


# Function to get user input for providers
def get_providers(available_providers):
    """
    Prompts the user to select providers from a list of available providers.

    Args:
        available_providers (dict): A dictionary where keys are provider names and values are provider objects.

    Returns:
        list: A list of selected provider instances chosen by the user.
    """
    selected_providers = []
    print("Available Providers:")
    for provider in available_providers.keys():
        print(f"- {provider}")

    while True:
        provider_input = input(
            "\nEnter a provider name to add or 'done' to finish: "
        ).strip()
        if provider_input == "done":
            if selected_providers:
                break
            else:
                print("Please select at least one provider.")
                continue
        elif provider_input in available_providers:
            selected_providers.append(available_providers[provider_input])
            print(f"{provider_input} added.")
        else:
            print("Invalid provider name, please try again.")

    return selected_providers


# Function to get common models between the selected providers
def get_common_models(selected_providers):
    """
    Finds common models available across all selected providers.

    Args:
        selected_providers (list): A list of selected provider instances.

    Returns:
        list or None: A list of common model names if found; otherwise, None.
    """
    if not selected_providers:
        return None

    model_sets = [set(provider.model_map.keys()) for provider in selected_providers if hasattr(provider, "model_map")]
    
    # Intersect all model sets to get only common models among all providers
    common_models = set.intersection(*model_sets) if model_sets else set()

    if not common_models:
        print("No common models found among selected providers.")
        return None

    return list(common_models)


# Function to get user input for models
def get_models(common_models):
    """
    Prompts the user to select models from a list of common models available across providers.

    Args:
        common_models (list): A list of common model names shared by the selected providers.

    Returns:
        list: A list of model names selected by the user.
    """
    selected_models = []
    print("\nCommon models available:")
    for model in common_models:
        print(f"- {model}")

    while True:
        model_input = input("\nEnter a model name to add or 'done' to finish: ").strip()
        if model_input == "done":
            if selected_models:
                break
            else:
                print("Please select at least one model.")
                continue
        elif model_input in common_models:
            selected_models.append(model_input)
            print(f"{model_input} added.")
        else:
            print("Invalid model name, please try again.")

    return selected_models


# Main function to run the benchmark
def run_benchmark(available_providers):
    """
    Runs a benchmark test by prompting the user to select providers, models,
    and configure benchmark settings.

    Args:
        available_providers (dict): A dictionary of provider names to provider instances.

    Returns:
        None
    """
    # Get user-selected providers
    selected_providers = get_providers(available_providers)
    print(
        f"\nSelected Providers: {[provider.__class__.__name__ for provider in selected_providers]}"
    )

    # Get common models from selected providers
    common_models = get_common_models(selected_providers)
    if not common_models:
        return  # Exit if no common models

    # Get user-selected models
    selected_models = get_models(common_models)
    print(f"\nSelected Models: {selected_models}")

    # Ask for streaming mode
    streaming_input = (
        input("\nDo you want to enable streaming? (yes/no): ").strip().lower()
    )
    streaming = streaming_input == "yes"

    # Ask for the number of requests
    num_requests = int(input("\nEnter the number of requests: ").strip())

    # Run the benchmark
    print("\nRunning benchmark...")
    b = Benchmark(
        selected_providers,
        num_requests,
        selected_models,
        prompt="What are some fun things to do in New York? Give me 1 short example.",
        streaming=streaming,
    )
    b.run()


if __name__ == "__main__":
    """
    The main entry point of the script. Initializes available providers and
    calls the `run_benchmark` function to start the benchmarking process.
    """
    # Available providers can be passed as a parameter
    available_providers = {
        "TogetherAI": TogetherAI(),
        "Cloudflare": Cloudflare(),
        "OpenAI": Open_AI(),
        "PerplexityAI": PerplexityAI(),
        "Groq": GroqProvider(),
        "Hyperbolic": Hyperbolic(),
    }
    run_benchmark(available_providers)
