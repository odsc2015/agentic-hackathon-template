import asyncio
from agents import AGENT_REGISTRY
from google.adk.agents import ParallelAgent
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai.types import Content, Part
import uuid
import os
USER_ID = "cognitive_user_001"
api_key = os.getenv("GOOGLE_API_KEY")
os.environ['GOOGLE_API_KEY'] = api_key

async def run_agent_query(agent, query, session, user_id, session_service=None):
    runner = Runner(agent=agent, session_service=session_service, app_name=agent.name)
    final_response = ""

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=Content(parts=[Part(text=query)], role="user")
    ):
        if event.is_final_response():
            final_response = event.content.parts[0].text
    return final_response

async def run_parallel_workflow(user_query: str, parallel_agent: ParallelAgent):
    # 4. Session for workflow
     # Method 1: Get existing agent from registry

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=parallel_agent.name,
        user_id=USER_ID,
    )
    

    # 5. Run and return outputs
    final_response = await run_agent_query(parallel_agent, user_query, session, USER_ID, session_service=session_service)
    print("\nFinal ParallelAgent Response:")
    print(final_response)
    
    return final_response