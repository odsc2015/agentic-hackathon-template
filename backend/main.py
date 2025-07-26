from fastapi import FastAPI
from pydantic import BaseModel
from agents.base_agent import ReActAgent
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ReAct Agent API")
agent = ReActAgent()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    user_input: str

@app.post("/react")
async def react_agent(request: AgentRequest):
    return agent.reason_and_act(request.user_input)
