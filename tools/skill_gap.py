from tools.base_tool import BaseTool

class SkillGapAnalyzer(BaseTool):
    @property
    def name(self):
        return "Skill Gap Analysis"

    def run(self, resume_data: dict, jd_data: dict):
        resume_skills = set(resume_data.get("skills", []))
        jd_skills = set(jd_data.get("jd_text", "").split(", "))
        missing_skills = jd_skills - resume_skills
        return {"missing_skills": list(missing_skills)}
