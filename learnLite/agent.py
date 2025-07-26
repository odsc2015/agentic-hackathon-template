import os
import sys
from json_repair import repair_json
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
try:
    from dotenv import load_dotenv
    load_dotenv()

    MODEL_NAME = os.environ.get("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
except ImportError:
    print("Warning: python-dotenv not installed. Ensure API key is set")
    MODEL_NAME = "gemini-2.0-flash"

from google.adk.agents import LlmAgent, BaseAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator
import asyncio
import json
from pydantic import BaseModel
from typing import List
from google.adk.events import Event, EventActions

from learnLite.instructions import (
    CURRICULUM_PLANNER_INSTRUCTION,
    QUIZ_MAKER_INSTRUCTION,
    COURSE_CONTENT_GENERATOR_INSTRUCTION
)

class QuizItem(BaseModel):
    question: str
    options: List[str]
    answer: str

class QuizMakerOutput(BaseModel):
    quiz: List[QuizItem]

class ItemReview(BaseModel):
    question: str
    user_answer: str
    correct_answer: str
    correctness: str  # e.g., "correct", "incorrect"
    review: str  # e.g., "Good job!", "Try to review the topic again."
    
class EvaluationOutput(BaseModel):
    score: int
    review: list[ItemReview]

# 1. Agent to plan curriculum for a given topic
curriculum_planner_agent = LlmAgent(
    name="CurriculumPlanner",
    model=MODEL_NAME,
    instruction=CURRICULUM_PLANNER_INSTRUCTION,
    output_key="curriculum"
)

# 2. Agent to create course content
course_content_creator = LlmAgent(
    name="CourseContentCreator",
    model=MODEL_NAME,
    instruction=COURSE_CONTENT_GENERATOR_INSTRUCTION,
    output_key="course_content"
)

# 2.2. Agent to act as instructor
instructor_agent = LlmAgent(
    name="Instructor",
    model=MODEL_NAME,
    instruction="""You are an instructor. Deliver the course content provided in state['course_content']. Present it in an engaging manner, as if you are teaching a class. Use clear subheadings and examples to make the content easy to understand. The output should be structured as a lesson.""",
    output_key="instructor_output"
)

# class InstructorAgent(BaseAgent):
#     async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator:
#         course_content = ctx.session.state.get("course_content", "")
#         print("=======================COURSE CONTENT=====================")
#         print(course_content)
#         print("-----------------------------------------------------------")
#         # Simulate the instructor delivering the content
#         print("Instructor: Let's start the lesson!")
#         print(course_content)
#         yield  # End of instructor session

# instructor_agent = InstructorAgent(name="Instructor")

# 3. Agent to generate questions and answers
quiz_maker = LlmAgent(
    name="QuizMaker",
    model=MODEL_NAME,
    instruction=QUIZ_MAKER_INSTRUCTION,
    output_key="quiz",
    output_schema=QuizMakerOutput
    )
    
# 3. Custom agent to conduct the quiz
class QuizConductorAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator:
        quiz = ctx.session.state.get("quiz", {})
        print("=======================QUIZ=====================")
        print(quiz)
        print("----------------------------------")
        # #Correct the quiz_str to json format
        # quiz_repair = repair_json(quiz_str)
        # quiz = json.loads(quiz_repair)
        # Simulate the quiz conduction
        print("Quiz Conductor: Let's start the quiz!")
        print("Please answer the following questions:")
        user_answers = []
        actual_answers = []
        questions =[]

        for idx, qa in enumerate(quiz['quiz']):
            print(f"Question {idx+1}: {qa['question']}")
            print(f"Options {idx+1}: {qa['options']}")
            questions.append(qa['question'])    
            actual_answers.append(qa['answer'])
            user_answer = input("Your answer: ")
            user_answers.append(user_answer)
            ctx.session.state["user_answers"] = user_answers
        
        ctx.session.state["actual_answers"] = actual_answers
        ctx.session.state["questions"] = questions
        print("User's Answers-->", ctx.session.state["user_answers"])
        # Optionally yield an event here if needed
        quiz_is_done = True
        yield Event(
            author=self.name, 
            #content={"text": "Quiz Conductor Finished Job"},
            actions=EventActions(escalate=quiz_is_done)
            ) # End of quiz

quiz_conductor_agent = QuizConductorAgent(name="QuizConductor")

print("Quiz Conductor Agent finished running.")
# 3. Agent to evaluate responses
evaluation_agent = LlmAgent(
    name="QuizEvaluator",
    model=MODEL_NAME,
    instruction=(
        """Compare each user answer in state['user_answers'] to the correct answers in state['actual_answers'] for each question within state['questions']. 
        For each, show the question, user's response, correct response, correctness and a brief review. 
        Give a score of 1 for each correct answer and 0 for each incorrect answer and add them up to generate the final score.
        Summarize the total score in state['score'] and provide a review in state['review'].
        """
    ),
    output_key="evaluation_output",
    output_schema=EvaluationOutput  # Define a suitable schema for the evaluation output
)


# 4. Compose the workflow
learnlite_workflow = SequentialAgent(
    name="LearnLiteQuizWorkflow",
    sub_agents=[
        curriculum_planner_agent,   # 1. Plan curriculum
        course_content_creator,  # 2. Create course content
        instructor_agent,          # 2.2. Act as instructor
        quiz_maker,         # 3. Generate questions
        quiz_conductor_agent,       # 4. Conduct quiz
        evaluation_agent            # 5. Evaluate
    ]
)

root_agent = learnlite_workflow

# async def main():
#     topic = input("What topic do you want to be quizzed on? ")
#     state = {"topic": topic}
#     await learnlite_workflow.run(state)
#     print(f"Curriculum: {state.get('curriculum')}")
#     print(f"Score: {state.get('score')}")
#     print(f"Review: {state.get('review')}")

# if __name__ == "__main__":
#     asyncio.run(main())