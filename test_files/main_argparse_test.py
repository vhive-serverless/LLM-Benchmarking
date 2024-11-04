import unittest
from unittest.mock import patch, MagicMock
import sys
import main
from main import parser

class TestCommandLineInterface(unittest.TestCase):
    @patch('main.display_available_providers')
    def test_list_flag(self, mock_display_providers):
        """Test --list flag functionality"""
        test_args = ['main.py', '--list']
        with patch.object(sys, 'argv', test_args):
            main.__name__ = '__main__'
            main.main()  # Assuming there is a main() function in main.py

        # Verify display_available_providers was called
        mock_display_providers.assert_called_once()

    @patch('main.run_benchmark')
    @patch('main.load_config', return_value={"providers": ["TogetherAI"]})
    def test_config_flag(self, mock_load_config, mock_run_benchmark):
        """Test -c/--config flag functionality"""
        test_args = ['main.py', '-c', 'config.json']
        with patch.object(sys, 'argv', test_args):
            main.__name__ = '__main__'
            main.main()  # Assuming there is a main() function in main.py

        # Verify the config was loaded and benchmark was run
        mock_load_config.assert_called_once_with('config.json')
        mock_run_benchmark.assert_called_once_with(mock_load_config.return_value)

    @patch('main.run_benchmark')
    @patch('main.load_config', return_value=None)
    def test_config_load_failure(self, mock_load_config, mock_run_benchmark):
        """Test behavior when config loading fails"""
        test_args = ['main.py', '-c', 'config.json']
        with patch.object(sys, 'argv', test_args):
            main.__name__ = '__main__'
            main.main()  # Assuming there is a main() function in main.py

        # Verify benchmark was not run
        mock_run_benchmark.assert_not_called()

    @patch('argparse.ArgumentParser.print_help')
    def test_no_args(self, mock_print_help):
        """Test behavior when no arguments are provided"""
        test_args = ['main.py']
        with patch.object(sys, 'argv', test_args):
            main.__name__ = '__main__'
            main.main()  # Assuming there is a main() function in main.py

        # Verify help was printed
        mock_print_help.assert_called_once()

    def test_argument_parser_creation(self):
        """Test the creation of argument parser with correct arguments"""
        from main import parser

        # Test parser description
        self.assertEqual(
            parser.description,
            "Run a benchmark on selected AI providers and models."
        )

        # Test that the parser has the expected arguments
        args = vars(parser.parse_args([]))
        self.assertIn('config', args)
        self.assertIn('list', args)

        # Test argument types
        self.assertIsNone(args['config'])
        self.assertFalse(args['list'])

        # Test --list flag
        args = vars(parser.parse_args(['--list']))
        self.assertTrue(args['list'])

        # Test --config flag
        args = vars(parser.parse_args(['-c', 'test.json']))
        self.assertEqual(args['config'], 'test.json')

if __name__ == '__main__':
    unittest.main()
