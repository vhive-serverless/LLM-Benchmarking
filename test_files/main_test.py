import unittest
import json
from unittest.mock import patch, MagicMock
import os
import tempfile
from main import (
    load_config,
    validate_providers,
    get_common_models,
    validate_selected_models,
    get_available_providers,
    input_sizes,
    output_size_upper_limit,
    output_size_lower_limit,
    run_benchmark
)

class TestMain(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_config = {
            "providers": ["TogetherAI", "OpenAI"],
            "num_requests": 2,
            "models": ["meta-llama-3.2-3b-instruct"],
            "input_tokens": 100,
            "streaming": False,
            "max_output": 1000,
            "verbose": True
        }

        # Create a temporary config file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, "test_config.json")
        with open(self.config_path, 'w') as f:
            json.dump(self.sample_config, f)

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        self.temp_dir.cleanup()

    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        config = load_config(self.config_path)
        self.assertIsInstance(config, dict)
        self.assertIn("providers", config)
        self.assertIn("num_requests", config)
        self.assertIn("models", config)
        self.assertEqual(config["providers"], ["TogetherAI", "OpenAI"])

    def test_load_nonexistent_config(self):
        """Test loading a nonexistent configuration file."""
        config = load_config("nonexistent.json")
        self.assertIsNone(config)

    def test_load_invalid_json(self):
        """Test loading an invalid JSON file."""
        invalid_path = os.path.join(self.temp_dir.name, "invalid.json")
        with open(invalid_path, 'w') as f:
            f.write("invalid json content")
        config = load_config(invalid_path)
        self.assertIsNone(config)

    def test_validate_valid_providers(self):
        """Test validation of valid providers."""
        providers = ["TogetherAI", "OpenAI"]
        valid_providers = validate_providers(providers)
        self.assertEqual(len(valid_providers), 2)
        provider_names = [provider.__class__.__name__ for provider in valid_providers]
        self.assertIn("TogetherAI", provider_names)
        self.assertIn("Open_AI", provider_names)

    def test_validate_invalid_providers(self):
        """Test validation with invalid providers."""
        providers = ["InvalidProvider", "TogetherAI"]
        valid_providers = validate_providers(providers)
        self.assertEqual(len(valid_providers), 1)
        self.assertEqual(valid_providers[0].__class__.__name__, "TogetherAI")

    def test_validate_empty_providers(self):
        """Test validation with empty provider list."""
        providers = []
        valid_providers = validate_providers(providers)
        self.assertEqual(len(valid_providers), 0)

    def test_get_common_models(self):
        """Test getting common models across providers."""
        # Create mock providers
        provider1 = MagicMock()
        provider1.model_map = {
            "model1": "actual_model1",
            "model2": "actual_model2",
            "common_model": "actual_common"
        }
        
        provider2 = MagicMock()
        provider2.model_map = {
            "model3": "actual_model3",
            "model4": "actual_model4",
            "common_model": "actual_common"
        }
        
        mock_providers = [provider1, provider2]
        common_models = get_common_models(mock_providers)
        self.assertIn("common_model", common_models)
        self.assertEqual(len(common_models), 1)

    def test_get_common_models_no_providers(self):
        """Test getting common models with no providers."""
        common_models = get_common_models([])
        self.assertEqual(len(common_models), 0)

    def test_validate_selected_models_common(self):
        """Test validation of selected models with common models."""
        provider1 = MagicMock()
        provider1.model_map = {"common_model": "actual_common", "model1": "actual_model1"}
        provider2 = MagicMock()
        provider2.model_map = {"common_model": "actual_common", "model2": "actual_model2"}
        
        mock_providers = [provider1, provider2]
        selected_models = ["common_model", "invalid_model"]
        common_models = get_common_models(mock_providers)
        valid_models = validate_selected_models(selected_models, common_models, mock_providers)
        
        self.assertEqual(len(valid_models), 1)
        self.assertIn("common_model", valid_models)

    def test_validate_selected_models_single_provider(self):
        """Test validation of selected models with a single provider."""
        provider = MagicMock()
        provider.model_map = {"model1": "actual_model1", "model2": "actual_model2"}
        
        selected_models = ["model1", "model2"]
        valid_models = validate_selected_models(selected_models, [], [provider])
        
        self.assertEqual(len(valid_models), 2)
        self.assertIn("model1", valid_models)
        self.assertIn("model2", valid_models)

    def test_validate_selected_models_no_valid_models(self):
        """Test validation where no models are valid in common or provider model_map."""
        provider = MagicMock()
        provider.model_map = {"model1": "actual_model1", "model2": "actual_model2"}
        
        selected_models = ["invalid_model"]
        common_models = []
        valid_models = validate_selected_models(selected_models, common_models, [provider])
        
        self.assertEqual(len(valid_models), 0)  # Ensure valid_models is empty
    
    def test_validate_selected_models_no_common_models(self):
        """Test validation when models are not common to all providers."""
        provider1 = MagicMock()
        provider1.model_map = {"model1": "actual_model1", "common_model": "actual_common"}
        provider2 = MagicMock()
        provider2.model_map = {"model2": "actual_model2"}
        
        selected_models = ["model1"]
        common_models = get_common_models([provider1, provider2])  # This should be empty
        valid_models = validate_selected_models(selected_models, common_models, [provider1, provider2])
        
        self.assertEqual(valid_models, [])  # Ensure valid_models is empty
        
    @patch.dict(os.environ, {'TOGETHER_AI_API': 'test_api_key'})
    def test_input_size_validation(self):
        """Test input size validation."""
        self.assertIn(self.sample_config["input_tokens"], input_sizes)
        
        invalid_config = self.sample_config.copy()
        invalid_config["input_tokens"] = 42  # Invalid input size
        with patch('main.Benchmark') as mock_benchmark:
            run_benchmark(invalid_config)
            mock_benchmark.assert_not_called()

    def test_output_size_validation(self):
        """Test output size validation."""
        self.assertGreaterEqual(self.sample_config["max_output"], output_size_lower_limit)
        self.assertLessEqual(self.sample_config["max_output"], output_size_upper_limit)
        
        invalid_config = self.sample_config.copy()
        invalid_config["max_output"] = output_size_upper_limit + 1  # Invalid output size
        with patch('main.Benchmark') as mock_benchmark:
            run_benchmark(invalid_config)
            mock_benchmark.assert_not_called()

    @patch('main.Benchmark')
    @patch('main.get_prompt')
    def test_run_benchmark_success(self, mock_get_prompt, mock_benchmark):
        """Test successful benchmark execution."""
        mock_get_prompt.return_value = "test prompt"
        mock_benchmark_instance = MagicMock()
        mock_benchmark.return_value = mock_benchmark_instance
        
        run_benchmark(self.sample_config)
        
        mock_benchmark.assert_called_once()
        mock_benchmark_instance.run.assert_called_once()

    @patch('main.Benchmark')
    def test_run_benchmark_invalid_config(self, mock_benchmark):
        """Test benchmark execution with invalid configuration."""
        invalid_config = self.sample_config.copy()
        invalid_config["providers"] = ["InvalidProvider"]
        
        run_benchmark(invalid_config)
        mock_benchmark.assert_not_called()

if __name__ == '__main__':
    unittest.main()
