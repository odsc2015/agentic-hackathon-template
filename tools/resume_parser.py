class ResumeParser:
    def __init__(self, resume_path: str):
        self.resume_path = resume_path

    def parse(self):
        # TODO: implement actual resume parsing
        return {
            "skills": ["Python", "SQL", "Machine Learning", "Pandas", "TensorFlow"],
            "education": ["Northeastern University", "Hindustan University"],
            "experience": ["Data Scientist Intern", "AI Intern"]
        }
    


from llm_client import GeminiClient

class ResumeParser:
    def __init__(self, resume_text: str):
        self.resume_text = resume_text
        self.client = GeminiClient()

    def parse(self):
        # Read resume as text
        

        prompt = f"""
        Extract the following details from this resume. Return as a JSON object with keys:
        - name
        - email
        - skills (list)
        - education (list)
        - experience (list)

        Resume:
        {resume_text}
        """
        response = self.client.generate(prompt)
        # Optionally: parse response as JSON if LLM returns valid JSON
        import json
        try:
            return json.loads(response)
        except Exception:
            # fallback: return raw response if not valid JSON
            return response