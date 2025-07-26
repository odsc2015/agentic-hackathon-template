class PlanAgent:
    async def create_plan(self, resume_path=None, job_url=None):
        # Example logging
        print("[PlanAgent] Creating plan using:")
        print(f"  Resume: {resume_path}")
        print(f"  Job URL: {job_url}")

        # Later: extract job skills/resume keywords here

        # Return a basic plan structure (could be more dynamic later)
        return [
            {"name": "Parse Resume"},
            {"name": "Parse Job Description"},
            {"name": "Skill Gap Analysis"},
            {"name": "Generate Roadmap"},
        ]
