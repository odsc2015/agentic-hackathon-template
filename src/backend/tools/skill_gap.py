from tools.base_tool import BaseTool
from tools.llm_client import GeminiClient

class SkillGapAnalyzer(BaseTool):
    @property
    def name(self):
        return "Skill Gap Analysis"

    def run(self, resume_data: dict, jd_data: dict):
        try:
            resume_skills = set(resume_data.get("skills", []))
            jd_skills = set(jd_data.get("jd_text", "").split(", "))
            missing_skills = jd_skills - resume_skills
            return {"missing_skills": list(missing_skills)}
        except Exception as e:
            client = GeminiClient()
            prompt = f"""
            You are a skill gap analyzer.
            You are given a resume and a job description.
            You need to find the skills that are missing from the resume to be able to apply for the job.
            Return a list of skills that are missing from the resume and are required for the job.
            If all skills are present, return "No missing skills".
            Return only the list of skills, no other text.
            """
            response = client.generate(prompt)
            return list(response)
    
    
