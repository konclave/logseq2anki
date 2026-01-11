import unittest
from unittest.mock import MagicMock, patch
import os
from src.llm import LLMClient

class TestLLMFallback(unittest.TestCase):
    def setUp(self):
        self.original_gemini_key = os.environ.get("GEMINI_API_KEY")
        self.original_openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        os.environ["GEMINI_API_KEY"] = "fake_gemini_key"
        os.environ["OPENROUTER_API_KEY"] = "fake_openrouter_key"

    def tearDown(self):
        if self.original_gemini_key:
            os.environ["GEMINI_API_KEY"] = self.original_gemini_key
        else:
            del os.environ["GEMINI_API_KEY"]
            
        if self.original_openrouter_key:
            os.environ["OPENROUTER_API_KEY"] = self.original_openrouter_key
        else:
             if "OPENROUTER_API_KEY" in os.environ:
                del os.environ["OPENROUTER_API_KEY"]

    @patch("src.llm.genai.Client")
    @patch("src.llm.requests.post")
    def test_fallback_to_openrouter(self, mock_post, mock_genai_client):
        # Setup Gemini mock to fail
        mock_client_instance = MagicMock()
        mock_client_instance.models.generate_content.side_effect = Exception("Quota exceeded")
        mock_genai_client.return_value = mock_client_instance

        # Setup OpenRouter mock to succeed
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Das ist ein Beispiel."}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Initialize client
        client = LLMClient()
        
        # Call generate_example
        result = client.generate_example("Test", "Test")

        # Verify Gemini was called
        mock_client_instance.models.generate_content.assert_called_once()
        
        # Verify OpenRouter was called
        mock_post.assert_called_once()
        self.assertEqual(result, "Das ist ein Beispiel.")

    @patch("src.llm.genai.Client")
    @patch("src.llm.requests.post")
    def test_gemini_success_no_fallback(self, mock_post, mock_genai_client):
        # Setup Gemini mock to succeed
        mock_client_instance = MagicMock()
        mock_response_gemini = MagicMock()
        mock_response_gemini.text = "Gemini example."
        mock_client_instance.models.generate_content.return_value = mock_response_gemini
        mock_genai_client.return_value = mock_client_instance

        # Initialize client
        client = LLMClient()
        
        # Call generate_example
        result = client.generate_example("Test", "Test")

        # Verify Gemini was called
        mock_client_instance.models.generate_content.assert_called_once()
        
        # Verify OpenRouter was NOT called
        mock_post.assert_not_called()
        self.assertEqual(result, "Gemini example.")

if __name__ == "__main__":
    unittest.main()
