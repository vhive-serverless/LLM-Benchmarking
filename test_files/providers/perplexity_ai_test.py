import unittest
from unittest.mock import patch, MagicMock
from providers import PerplexityAI


class TestPerplexityAI(unittest.TestCase):

    @patch("os.environ.get")
    def test_initialization_with_valid_api_key(self, mock_env_get):
        mock_env_get.return_value = "test_api_key"

        # Mock OpenAI class to avoid making actual API calls
        with patch("providers.perplexity_ai_provider.OpenAI") as mock_openai_client:
            mock_openai_client.return_value = MagicMock()

            # Instantiate the PerplexityAI class
            provider = PerplexityAI()

            # Assert that the client is correctly initialized
            mock_openai_client.assert_called_with(
                api_key="test_api_key", base_url="https://api.perplexity.ai"
            )
            self.assertEqual(provider.client, mock_openai_client.return_value)

            # Assert model map is initialized
            expected_model_map = {
                "meta-llama-3.1-70b-instruct": "llama-3.1-70b-instruct",  # 70b
                "meta-llama-3.1-8b-instruct": "llama-3.1-8b-instruct",  # 8b
                "common-model": "llama-3.1-8b-instruct",  # 8b
                "meta-llama-3.1-sonar-405B": "llama-3.1-sonar-huge-128k-online",  # 405B
                "common-model": "llama-3.1-70b-instruct",
            }
            self.assertEqual(provider.model_map, expected_model_map)

    @patch("os.environ.get")
    def test_initialization_without_api_key(self, mock_env_get):
        mock_env_get.return_value = None

        with self.assertRaises(ValueError) as context:
            PerplexityAI()

        self.assertEqual(
            str(context.exception),
            "Perplexity AI API token must be provided as an environment variable.",
        )

    @patch("os.environ.get")
    def test_get_model_name(self, mock_env_get):
        # Mock the environment variable for API key
        mock_env_get.return_value = "test_api_key"

        # Mock OpenAI class to avoid making actual API calls
        with patch("providers.perplexity_ai_provider.OpenAI") as mock_openai_client:
            mock_openai_client.return_value = MagicMock()

            # Instantiate the PerplexityAI class
            provider = PerplexityAI()

            self.assertEqual(
                provider.get_model_name("meta-llama-3.1-70b-instruct"),
                "llama-3.1-70b-instruct",
            )
            self.assertEqual(
                provider.get_model_name("meta-llama-3.1-8b-instruct"),
                "llama-3.1-8b-instruct",
            )
            self.assertEqual(
                provider.get_model_name("meta-llama-3.1-sonar-405B"),
                "llama-3.1-sonar-huge-128k-online",
            )
            self.assertIsNone(provider.get_model_name("non-existent-model"))


if __name__ == "__main__":
    unittest.main()
