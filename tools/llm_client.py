import os
from vertexai.preview.generative_models import GenerativeModel

class GeminiClient:
    def __init__(self):
        self.model = GenerativeModel("gemini-1.5-pro")

    def generate(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text
