from tools.resume_parser import ResumeParser
from tools.job_scraper import JobScraper
from tools.skill_gap import SkillGapAnalyzer
from tools.roadmap_generator import RoadmapGenerator

class KatalystToolkit:
    def __init__(self, resume_path: str, job_url: str):
        self.resume_path = resume_path
        self.job_url = job_url
        self.resume_parser = ResumeParser(resume_path)
        self.job_scraper = JobScraper(job_url)

    def parse_resume(self):
        return self.resume_parser.parse()

    def parse_job_description(self):
        return self.job_scraper.scrape()

    def skill_gap_analysis(self):
        resume_data = self.parse_resume()
        job_data = self.parse_job_description()
        analyzer = SkillGapAnalyzer()
        return analyzer.run(resume_data, job_data)

    def generate_learning_roadmap(self):
        resume_data = self.parse_resume()
        job_data = self.parse_job_description()
        analyzer = SkillGapAnalyzer()
        gap_data = analyzer.run(resume_data, job_data)
        missing_skills = gap_data.get("missing_skills", [])

        if not missing_skills:
            return {"roadmap": "No missing skills! You're already a strong match."}

        generator = RoadmapGenerator()
        return generator.run(resume_data, job_data, missing_skills)




    def get_tools_dict(self):
        return {
            "parse_resume": self.parse_resume,
            "parse_job_description": self.parse_job_description,
            "skill_gap_analysis": self.skill_gap_analysis,
            "generate_learning_roadmap": self.generate_learning_roadmap
        }
