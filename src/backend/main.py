from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tools.resume_parser import ResumeParser
from tools.job_scraper import JobScraper
from tools.skill_gap import SkillGapAnalyzer
from tools.roadmap_generator import RoadmapGenerator
from tools.leetcode_questions import LeetcodeQuestions


app = FastAPI()

class RoadmapRequest(BaseModel):
    resume_text: str
    job_url: str

@app.post("/generate_roadmap")
def generate_roadmap(req: RoadmapRequest):

    # Parse resume
    resume = ResumeParser(req.resume_text).parse()
    # Scrape job
    job = JobScraper(req.job_url).scrape()
    # Skill gap
    skill_gap = SkillGapAnalyzer().run(resume, job)

    try:
        company = job.get("company")
        # leetcode questions
        leetcode_questions = LeetcodeQuestions().run(job, company)
    except Exception as e:
        leetcode_questions = "No data available for this company"

    # Roadmap
    if isinstance(skill_gap, list):
        missing_skills = skill_gap
    elif isinstance(skill_gap, dict):
        missing_skills = skill_gap.get("missing_skills", [])
    else:
        missing_skills = skill_gap
    roadmap = RoadmapGenerator().run(resume, job, missing_skills, leetcode_questions)
    if isinstance(roadmap, str):
        roadmap_markdown = roadmap
    else:
        roadmap_markdown = roadmap.get("learning_roadmap") or roadmap.get("roadmap")

    return {
        "resume": resume,
        "job": job,
        "skill_gap": skill_gap,
        "leetcode_questions": leetcode_questions,
        "roadmap_markdown": roadmap_markdown
    }