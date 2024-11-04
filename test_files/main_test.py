import pytest
from unittest.mock import patch, MagicMock
from main import run_benchmark, get_providers, get_common_models, get_models
from providers import TogetherAI, Cloudflare, PerplexityAI, Open_AI, GroqProvider, Hyperbolic, GoogleGemini
from benchmarking.dynamo_bench import Benchmark


@pytest.fixture
def mock_providers():
    """Fixture to provide mock provider instances with model maps."""
    together_ai_mock = MagicMock()
    together_ai_mock.model_map = {
        "meta-llama-3.2-3b-instruct": "mock_model1",
        "mistral-7b-instruct-v0.1": "mock_model2",
    }
    cloudflare_mock = MagicMock()
    cloudflare_mock.model_map = {
        "meta-llama-3.2-3b-instruct": "mock_model1",
        "mistral-7b-instruct-v0.1": "mock_model2",
    }

    # Define other providers as needed
    return {
        "TogetherAI": together_ai_mock,
        "Cloudflare": cloudflare_mock,
        "PerplexityAI": MagicMock(),
        "OpenAI": MagicMock(),
        "Groq": MagicMock(),
        "Hyperbolic": MagicMock(),
        "Google": MagicMock(),
    }


@patch("builtins.input", side_effect=[
    "TogetherAI",  # Choose TogetherAI as provider
    "done",        # End provider selection
    "meta-llama-3.2-3b-instruct",  # Choose model
    "done",        # End model selection
    "no",          # Disable streaming
    "5"            # Number of requests
])
@patch("benchmarking.dynamo_bench.Benchmark.run")  # Mock Benchmark's run method
@patch("benchmarking.dynamo_bench.Benchmark.__init__", return_value=None)  # Mock Benchmark's initialization
@patch("dotenv.load_dotenv")  # Mock dotenv loading
def test_run_benchmark(mock_load_dotenv, mock_benchmark_init, mock_benchmark_run, mock_input, mock_providers):
    """
    Tests the main run_benchmark flow by simulating user inputs.
    """
    run_benchmark(mock_providers)

    # Check that Benchmark was initialized with expected values
    mock_benchmark_init.assert_called_once_with(
        [mock_providers["TogetherAI"]],  # Providers: TogetherAI
        5,  # Number of requests
        ["meta-llama-3.2-3b-instruct"],  # Selected model
        prompt="What are some fun things to do in New York? Give me 1 short example.",
        streaming=False,
    )

    # Ensure that the run method was called
    mock_benchmark_run.assert_called_once()


@patch("builtins.input", side_effect=["TogetherAI", "done"])
def test_get_providers(mock_input, mock_providers):
    """
    Test get_providers to ensure correct provider selection.
    """
    selected_providers = get_providers(mock_providers)
    assert selected_providers == [mock_providers["TogetherAI"]]


def test_get_common_models(mock_providers):
    """
    Test get_common_models to find models that are available across providers.
    """
    selected_providers = [mock_providers["TogetherAI"], mock_providers["Cloudflare"]]
    common_models = get_common_models(selected_providers)
    assert common_models == ["meta-llama-3.2-3b-instruct", "mistral-7b-instruct-v0.1"]


@patch("builtins.input", side_effect=["meta-llama-3.2-3b-instruct", "done"])
def test_get_models(mock_input):
    """
    Test get_models to verify the correct models are selected by user input.
    """
    common_models = ["meta-llama-3.2-3b-instruct", "mistral-7b-instruct-v0.1"]
    selected_models = get_models(common_models)
    assert selected_models == ["meta-llama-3.2-3b-instruct"]
