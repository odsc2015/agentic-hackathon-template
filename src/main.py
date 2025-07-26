from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from memory import MemoryManager
from Planner import plan_steps
from executor import execute_plan
from dotenv import load_dotenv
import os
from logging import getLogger
logger = getLogger("KIRAN.executor")

load_dotenv()

app = FastAPI()

# Allow all CORS for development (tighten for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# You can re-use your MemoryManager, or create per request
memory = MemoryManager(db_path="kiran_memory.db")

class ChatRequest(BaseModel):
    message: str
    user: str = None

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_input = req.message
    # Optionally: add user context handling
    final_message, reasoning_log = await execute_plan(user_input)
    # Return both the main dialogue and reasoning if you want!
    return {
        "reply": final_message,
        "reasoning": reasoning_log
    }

# Optional: basic home page
@app.get("/")
async def root():
    return {"msg": "KIRAN Cognitive Agent is running."}
