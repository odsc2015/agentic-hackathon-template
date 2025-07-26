# tools/roadmap_generator.py

from tools.base_tool import BaseTool
import google.generativeai as genai
import os

import vertexai
from vertexai.preview.generative_models import GenerativeModel

class RoadmapGenerator(BaseTool):
    def __init__(self):
        # Initialize Vertex AI
        vertexai.init(project="katalyst-467100", location="us-central1")

        # Use Vertex AI's GenerativeModel
        self.model = GenerativeModel("gemini-2.0-flash-001")  # or "gemini-1.5-pro" if enabled


    @property
    def name(self):
        return "Generate Learning Roadmap"

    def run(self, resume_data: dict, jd_data: dict, missing_skills: list, leetcode_questions: str):
        prompt = f"""
        You are a career coach helping a candidate prepare for the role of '{jd_data.get("title", "")}'.

        The candidate has the following experience and education:
        Experience: {resume_data.get("experience", [])}
        Education: {resume_data.get("education", [])}

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
