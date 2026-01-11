import os
import requests
from google import genai
from typing import Optional

class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")

        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key or self.openrouter_api_key)

    def _generate_with_openrouter(self, prompt: str) -> str:
        if not self.openrouter_api_key:
            print("OpenRouter API key not found. Cannot fallback.")
            return ""

        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/konclave/logseq2anki",
        }
        
        data = {
            "model": self.openrouter_model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"Error generating example with OpenRouter: {e}")
            return ""

    def generate_example(self, word: str, translation: str, language: str = "German") -> str:
        prompt = (
            f"Generate a simple, natural example sentence in {language} for the word '{word}' "
            f"which means '{translation}'. "
            f"Return ONLY the sentence, nothing else."
        )
        
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=prompt
                )
                if response.text:
                    return response.text.strip()
                else:
                    raise Exception("Empty response from Gemini")
            except Exception as e:
                print(f"Error generating example with Gemini: {e}")
                print("Attempting fallback to OpenRouter...")
                return self._generate_with_openrouter(prompt)
        else:
            print("Gemini client not initialized. Attempting OpenRouter...")
            return self._generate_with_openrouter(prompt)