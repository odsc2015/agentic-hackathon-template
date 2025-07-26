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
