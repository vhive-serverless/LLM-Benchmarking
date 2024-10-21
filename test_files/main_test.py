import unittest
from unittest.mock import patch, MagicMock
from main import run_benchmark

class TestMain(unittest.TestCase):

    @patch('builtins.input', side_effect=['TogetherAI', 'done', 'meta-llama-3.2-3b-instruct', 'done', 'no', '1'])
    @patch('benchmarking.benchmark_main.Benchmark.run')  # Mock the run method of Benchmark
    @patch('benchmarking.benchmark_main.Benchmark.__init__', return_value=None)  # Mock the initialization of Benchmark
    @patch('dotenv.load_dotenv')  # Mock load_dotenv to avoid loading environment variables
    @patch('main.available_providers',  # Mock the available_providers dictionary
           {
               "TogetherAI": MagicMock(),
               "Cloudflare": MagicMock(),
               "PerplexityAI": MagicMock()
           })
    def test_run_benchmark(self, mock_load_dotenv, mock_benchmark_init, mock_benchmark_run, mock_input):
        # Mock the TogetherAI provider to have a model map
        together_ai_mock = MagicMock()
        together_ai_mock.model_map = {
            "meta-llama-3.2-3b-instruct": "mock_model1", 
            "mistral-7b-instruct-v0.1": "mock_model2",
            "meta-llama-3.1-70b-instruct": "mock_model3",
            "google-gemma-2b-it": "mock_model4"
        }

        # Mock available_providers to return this mock instance for TogetherAI
        mock_providers = {
            "TogetherAI": together_ai_mock,
            "Cloudflare": MagicMock(),
            "PerplexityAI": MagicMock()
        }

        # Replace the original providers with the mock ones
        with patch('main.available_providers', mock_providers):
            # Run the benchmark function
            run_benchmark()

            # Check if the Benchmark class was initialized with the correct parameters
            mock_benchmark_init.assert_called_with(
                [together_ai_mock],  # Providers: TogetherAI (selected by input)
                1,  # Number of requests (from input)
                ['meta-llama-3.2-3b-instruct'],  # Models (common model selected)
                prompt="What are some fun things to do in New York? Give me 1 short example.",  # Prompt
                streaming=False  # Streaming mode (selected as 'no')
            )

            # Check if the run method of Benchmark was called
            mock_benchmark_run.assert_called_once()

if __name__ == '__main__':
    unittest.main()
