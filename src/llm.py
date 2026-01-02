import os
from google import genai
from typing import Optional

class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate_example(self, word: str, translation: str, language: str = "German") -> str:
        if not self.client:
            return ""
            
        prompt = (
            f"Generate a simple, natural example sentence in {language} for the word '{word}' "
            f"which means '{translation}'. "
            f"Return ONLY the sentence, nothing else."
        )
        
        try:
            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating example: {e}")
            return ""
