# Technical Explanation

## 1. Agent Workflow

Step-by-step process for each user query:
1. **Receive user input** via the React dashboard and FastAPI backend.
2. **Retrieve relevant memory** (optional): `MemoryManager` fetches past interactions for context.
3. **Plan sub-tasks**: The `Planner` uses Gemini LLM to classify intent and generate a step-by-step plan, selecting the most relevant agents.
4. **Agent selection and execution**: The `Executor` invokes selected agents in parallel, passing the plan and context.
5. **Aggregate and summarize output**: Agent responses are combined and returned to the user.

## 2. Key Modules

- **Planner** (`Planner.py`):  
  Uses Gemini LLM to classify user intent and generate a plan. Returns agent keys and steps.
- **Executor** (`executor.py`):  
  Runs the selected agents in parallel, manages workflow, and aggregates responses.
- **Memory Store** (`memory.py`):  
  Stores and retrieves user context, session data, and previous interactions for personalization.

## 3. Tool Integration

External tools and APIs:
- **Google Gemini API**:  
  Used in `Planner.py` for LLM-based planning and classification.
- **Session Service**:  
  Manages session lifecycle and context for each query.
- **Other APIs/Tools**:  
  Agents can call additional APIs (e.g., search, games) as needed.

## 4. Observability & Testing

- **Logging**:  
  All agent decisions, selected agents, and reasoning steps are logged (see `logs/` directory).
- **Testing**:  
  `TEST.sh` script exercises main workflow and endpoints.
- **Error Handling**:  
  Fallbacks to `facts_agent` and default steps if planning or agent selection fails.

## 5. Known Limitations

- **Long-running API calls** may delay responses.
- **Ambiguous user inputs** may result in fallback to default agents.
- **Session isolation**: Each query creates a new session; persistent context is limited to what is stored in `MemoryManager`.
- **Agent extensibility**: Adding new agents requires updating `AGENT_REGISTRY` and implementing agent logic.
