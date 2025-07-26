from agent.toolkit import KatalystToolkit

class KatalystAgent:
    def __init__(self, resume_path, job_url):
        self.toolkit = KatalystToolkit(resume_path, job_url)
        self.tools = self.toolkit.get_tools_dict()

    def execute_plan(self):
        # Step 1: Parse Resume
        resume = self.tools["parse_resume"]()
        print("✅ Resume parsed.")

        # Step 2: Parse Job Description
        job = self.tools["parse_job_description"]()
        print("✅ Job description parsed.")

        # Step 3: Skill Gap Analysis
        skill_gap = self.tools["skill_gap_analysis"]()
        print("✅ Skill gap analyzed.")

        # Step 4: Leetcode Questions
        leetcode_questions = self.tools["leetcode_questions"]()
        print("✅ Leetcode questions generated.")

        # Step 5: Generate Learning Roadmap
        roadmap = self.tools["generate_learning_roadmap"]()
        print("✅ Learning roadmap generated.")

        return {
            "resume": resume,
            "job_description": job,
            "skill_gap": skill_gap,
            "leetcode_questions": leetcode_questions,
            "roadmap": roadmap
        }
