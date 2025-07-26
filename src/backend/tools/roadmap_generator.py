# tools/roadmap_generator.py

from tools.base_tool import BaseTool
import google.generativeai as genai
import os
import json


class RoadmapGenerator(BaseTool):
    def __init__(self):
        # Initialize Vertex AI
       #vertexai.init(project="katalyst-467100", location="us-central1")

        # Use Vertex AI's GenerativeModel
        self.model = genai.GenerativeModel("gemini-2.0-flash-001")  # or "gemini-1.5-pro" if enabled



    @property
    def name(self):
        return "Generate Learning Roadmap"

    def run(self, resume_data: dict, jd_data: dict, missing_skills: list, leetcode_questions: str):
        try:
            if isinstance(resume_data, str):
                resume_data = json.loads(resume_data)
            info = f"""
            The candidate has the following experience and education:
            Experience: {resume_data.get("experience", [])}
            Education: {resume_data.get("education", [])}
            """
        except Exception as e:
            info = f"The canidate has the following resume: {resume_data}"


        prompt = f"""
        You are a career coach helping a candidate prepare for the role of '{jd_data.get("title", "")}'.

        {info}

        The following skills are **missing** and important for this job:
        {missing_skills}

        Create a structured, 4-week personalized learning roadmap to master these missing skills. Include:
        - Week-wise plan
        - Recommended courses (preferably free or affordable)
        - Projects or hands-on tasks
        - Any open-source resources or GitHub repos
        - Include leetcode questions for the canidate to practice based on the following leetcode questions: 
        The candidate has the following leetcode questions:

        Keep the tone encouraging and concise.
        """

        response = self.model.generate_content(prompt)
        return {"learning_roadmap": response.text}
