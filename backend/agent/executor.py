import asyncio
from tools.resume_parser import ResumeParser

class ExecutorAgent:
    async def run(self, plan, resume_path=None, job_url=None):
        print("[ExecutorAgent] Executing the following plan:")
        for task in plan:
            print(f"  - {task['name']}")

        for task in plan:
            print(f"[ExecutorAgent] Running step: {task['name']}")

            if task["name"] == "Parse Resume":
                parser = ResumeParser(resume_path)
                parsed_resume = parser.parse()
                print("[ResumeParser] Skills:", parsed_resume["skills"])
                print("[ResumeParser] Education:", parsed_resume["education"])
                print("[ResumeParser] Experience:", parsed_resume["experience"])

            await asyncio.sleep(1)  # Simulated delay
