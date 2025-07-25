
import os

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

from learnLite.instructions import (
    CURRICULUM_PLANNER_INSTRUCTION,
    QUIZ_MAKER_INSTRUCTION
)
# 1. Agent to plan curriculum for a given topic
curriculum_planner_agent = LlmAgent(
    name="CurriculumPlanner",
    model=MODEL_NAME,
    instruction=CURRICULUM_PLANNER_INSTRUCTION,
    output_key="curriculum"
)

#2. Agent to generate questions and answers
quiz_maker = LlmAgent(
    name="QuizMaker",
    model=MODEL_NAME,
    instruction=QUIZ_MAKER_INSTRUCTION,
    output_key="quiz"
)

# 3. Custom agent to conduct the quiz
class QuizConductorAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator:
        quiz = ctx.session.state.get("quiz", [])
        print("=======================QUIZ=====================")
        print(quiz)
        print("----------------------------------")
        user_answers = []
        for idx, qa in enumerate(quiz):
            print(f"Question {idx+1}: {qa['question']}")
            user_answer = input("Your answer: ")
            user_answers.append(user_answer)
            ctx.session.state["user_answers"] = user_answers
            # Optionally yield an event here if needed
        yield  # End of quiz

quiz_conductor_agent = QuizConductorAgent(name="QuizConductor")

# 3. Agent to evaluate responses
evaluation_agent = LlmAgent(
    name="QuizEvaluator",
    model=MODEL_NAME,
    instruction=(
        "Compare each user answer in state['user_answers'] to the correct answer in state['quiz']. "
        "For each, provide correctness and a brief review. "
        "Summarize the total score in state['score'] and provide a review in state['review']."
    )
)


# 4. Compose the workflow

learnlite_workflow = SequentialAgent(
    name="LearnLiteQuizWorkflow",
    sub_agents=[
        curriculum_planner_agent,   # 1. Plan curriculum
        quiz_maker,         # 2. Generate questions
        quiz_conductor_agent,       # 3. Conduct quiz
        evaluation_agent            # 4. Evaluate
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