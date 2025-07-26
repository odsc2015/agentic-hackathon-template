from tools.llm_client import GeminiClient
import json

class ResumeParser:
    def __init__(self, resume_text: str):
        self.resume_text = resume_text
        self.client = GeminiClient()

    def parse(self):
        # Read resume as text
        

        prompt = f"""
        Extract the following details from this resume. Return as a JSON object with the following:
        - name
        - email
        - skills (list)
        - education (list)
        - experience (list)
        Return only the JSON object, no other text.
        Ensure the output is a valid JSON object.
        Resume:
        {self.resume_text}
        """
        response = self.client.generate(prompt)
        # Optionally: parse response as JSON if LLM returns valid JSON
        
        try:
            return json.loads(response)
        except Exception:
            # fallback: return raw response if not valid JSON
            return response
        