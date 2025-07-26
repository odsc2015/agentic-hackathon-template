# Architecture Overview

This system is a cognitive companion app with a modular agent architecture, supporting multi-agent planning and execution via FastAPI and a React dashboard.

---

## Components

1. **User Interface**
   - **Frontend:** React (Vite) dashboard for user interaction
   - **Backend API:** FastAPI endpoints for chat and agent orchestration

2. **Agent Core**
   - **Planner:** Uses Gemini LLM to classify intent and generate step-by-step plans; selects relevant agents for each query
   - **Executor:** Executes the plan by invoking selected agents in parallel; manages agent responses and workflow
   - **Memory:** `MemoryManager` stores user context, previous interactions, and session data for personalized responses

3. **Agents**
   - Modular agent classes (e.g., `psychologist_agent`, `mindcoach_agent`, `facts_agent`, etc.)
   - Each agent specializes in a cognitive domain (therapy, motivation, facts, games, etc.)
   - Agents are registered in a central `AGENT_REGISTRY` for dynamic selection

4. **Tools / APIs**
   - **Google Gemini API:** LLM for planning, classification, and agent reasoning
   - **Session Service:** Manages session lifecycle and context per user/query

5. **Observability**
   - **Logging:** Each reasoning step, agent selection, and execution is logged for traceability
   - **Error Handling:** Fallbacks to default agents (e.g., `facts_agent`) and retries on failure
   - **Session Isolation:** Each query creates a fresh session for stateless, reproducible workflows

---

## Data Flow

```
User → React Dashboard → FastAPI → Planner (Gemini) → Agent Selection → Executor → Agents (Parallel) → Response → User
```

---

## Extensibility

- Add new agents by implementing and registering them in `AGENT_REGISTRY`
- Swap UI (CLI, Slack, etc.) by changing frontend
- Integrate new tools/APIs via agent or executor modules

---

## Diagram (ASCII)

```
+-------------+      +-----------+      +-----------+      +-----------+
|   User UI   | ---> |  FastAPI  | ---> |  Planner  | ---> |  Executor |
+-------------+      +-----------+      +-----------+      +-----------+
                                                              |
                                                              v
                                                      +------------------+
                                                      |   Agents (N)     |
                                                      +------------------+
                                                              |
                                                              v
                                                      +------------------+
                                                      |   MemoryManager  |
                                                      +------------------+
```

---

Let me know if you want a more detailed diagram or component breakdown!