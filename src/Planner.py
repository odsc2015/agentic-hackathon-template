import os
from google import genai  # Google GenAI SDK for Gemini
from google.genai import types

# Initialize Gemini client (API key is expected in environment)
api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    raise RuntimeError("GEMINI_API_KEY not set in environment. Please configure your API key securely.")
client = genai.Client(api_key=api_key)

def plan_steps(user_input, memory_context=None):
    """
    Uses the Gemini LLM to create a plan (list of steps) based on the user's input mood.
    Optionally incorporates memory context about past interactions.
    """
    # Construct a prompt instructing the LLM to break the task into steps.
    system_instructions = (
        "You are an AI planning assistant. Given the user's emotional state and query, "
        "break down the task into a concise, ordered plan of steps. "
        "Include steps for memory retrieval or analysis as needed, and a final step to produce a helpful response."
    )
    # If memory context is available, inform the planner about it
    memory_note = f"The user has past context: {memory_context}" if memory_context else ""
    user_prompt = f"User mood/request: {user_input}\n{memory_note}\nProvide a step-by-step plan."
    prompt_text = f"{system_instructions}\n{user_prompt}"
    
    # Call Gemini API to generate plan (as text with steps like '1. ... 2. ...').
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=prompt_text,
        config=types.GenerateContentConfig(max_output_tokens=200, temperature=0.2)
    )
    plan_text = response.text.strip()
    # Parse the response into a list of steps
    steps = []
    for line in plan_text.splitlines():
        # Expect lines like "1. Step description"
        if line.strip() and line[0].isdigit():
            # Remove numbering and strip text
            step = line.strip().lstrip("0123456789. ").strip()
            if step:
                steps.append(step)
    return steps
