import os
from google import genai  # Google GenAI SDK for Gemini
from google.genai import types
from agents import AGENT_REGISTRY
from google.adk.agents import ParallelAgent
import json
import re
from workflow import run_parallel_workflow, run_agent_query
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()


# Initialize Gemini client (API key is expected in environment)
api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    api_key = os.getenv("GOOGLE_API_KEY")
print(aallpi_key)
os.environ['GOOGLE_AI_API_KEY'] = api_key
if api_key is None:
    raise RuntimeError("GEMINI_API_KEY not set in environment. Please configure your API key securely.")
client = genai.Client(api_key=api_key)

async def plan_steps(user_input, memory_context=None):
    """
    Uses the Gemini LLM to create a plan (list of steps) based on the user's input mood.
    Optionally incorporates memory context about past interactions.
    """

    # 1. Classify & Plan
    agent_keys, steps = classify_and_plan(user_input, memory_context)
        # 2. Map agent keys to actual instances
    selected_agents = [AGENT_REGISTRY[k] for k in agent_keys if k in AGENT_REGISTRY]
    if not selected_agents:
        selected_agents = [AGENT_REGISTRY["facts_agent"]]
        # 3. Build and run the ParallelAgent
    print("Selected agents:", [agent.name for agent in selected_agents])
    parallel_agent = ParallelAgent(
        name="parallel_cognitive_agent",
        sub_agents=selected_agents,
    )

    # Run the parallel workflow to execute the plan
    result = await run_parallel_workflow(user_input, parallel_agent)
    # 4. Return a structured result
    return result, steps
   

def classify_and_plan(self, user_query: str, memory_context: str = None):
        """Runs Gemini once → returns agents + steps"""

         # System-level instructions for classification + planning
        system_instructions = """
You are a multi-purpose cognitive planner & intent classifier and you read through the emotions of the person so that you are able to 
provide which agent should be called next. you know what clearly has to be done and you recommend the agents from this below list
if the response is a simple greeting like "hi" or "hello" or "how are you" then you should call the facts agent
You have TWO responsibilities:
**Classify Intent** → Select the most relevant agents from the list below. 
**Plan Steps** → Provide a clear, ordered list of actionable steps to address the query.
---

Available agents and their roles:
- learning_agent → study techniques, memory improvement, learning strategies
- mindcoach_agent → motivation, habit building, self-discipline
- cognitive_neuroscientist_agent → cognitive science, memory, brain performance
- neuropsychologist_agent → neuropsychology, brain-behavior relationship
- psychologist_agent → therapy, emotional support, behavioral guidance
- therapist_agent → mental well-being, stress, anxiety relief
- psychiatrist_agent → mental illnesses, medications, psychiatric conditions
- games_agent → fun cognitive games, brain challenges
- facts_agent → interesting facts about the brain & cognition
- neurologist_agent → medical brain conditions, nervous system issues

---

### Output format STRICTLY as JSON:
{
  "agents": ["agent_key_1", "agent_key_2"],
  "steps": [
    "Step 1 description",
    "Step 2 description",
    "Step 3 description"
  ]
}

- Always include at least one agent (fallback to ["facts_agent"] if unsure)
- Steps must be concise and logical
- Do NOT include extra text outside JSON
"""
        memory_note = f"The user has past context: {memory_context}" if memory_context else ""
        user_prompt = f"User mood/request: {user_query}\n{memory_note}\nProvide a step-by-step plan."
        prompt_text = f"{system_instructions}\n{user_prompt}"
        
        response = client.models.generate_content(
            model= "gemini-2.0-flash-001",
            contents=prompt_text,
            config=types.GenerateContentConfig(
                max_output_tokens=500,
                temperature=0.2
            )
        )

        # Get raw response
        raw_text = response.text.strip()

        # Try parsing JSON
        try:
            # Extract JSON object from the response, even if extra text is present
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                json_str = match.group(0)
                data = json.loads(json_str)
                agents = data.get("agents", ["facts_agent"])
                steps = data.get("steps", [])
            else:
                agents = ["facts_agent"]
                steps = ["Could not parse planning steps due to unexpected output."]
        except json.JSONDecodeError:
            # If parsing fails → fallback
            agents = ["facts_agent"]
            steps = ["Could not parse planning steps due to unexpected output."]

        return agents, steps
