from planner import plan_steps
from memory import MemoryManager

# Initialize memory manager (handles SQLite connection)
memory = MemoryManager(db_path="kiran_memory.db")

def execute_plan(user_input):
    """
    Executes the plan for the given user input (mood), returns the final healing message.
    Also returns the reasoning steps for display.
    """
    # Step 1: Retrieve relevant memory context (if any)
    past_context = memory.fetch_last_interaction()
    # (In a more complex approach, we could fetch similar moods or do semantic search.)
    
    # Step 2: Plan the subtasks using the planner module (Gemini LLM)
    plan = plan_steps(user_input, memory_context=past_context)
    
    reasoning_log = []  # to collect reasoning steps for UI display
    reasoning_log.append(f"**User Input:** {user_input}")
    if past_context:
        reasoning_log.append(f"Retrieved memory context: {past_context}")
    reasoning_log.append("**Plan:** " + "; ".join(plan))
    
    # Step 3: Execute each step in the plan
    coping_strategies = None
    for step in plan:
        if "memory" in step.lower():
            # e.g., "Retrieve past comforting messages" – already done at start
            reasoning_log.append(f"Action: Memory retrieval -> {past_context or 'None found.'}")
            continue  # we already fetched memory at the beginning
        elif "analyz" in step.lower() or "identify" in step.lower():
            # Use Gemini to analyze user's mood (tool: Gemini API)
            analysis_prompt = (f"You are a psychological AI assistant analyzing a user's mood.\n"
                               f"User says: \"{user_input}\"\nProvide a brief analysis of their emotional state.")
            response = memory.gemini_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=analysis_prompt,
                config=types.GenerateContentConfig(max_output_tokens=150, temperature=0.5)
            )
            analysis = response.text.strip()
            reasoning_log.append(f"Analysis: {analysis}")
        elif "strategy" in step.lower() or "coping" in step.lower() or "tips" in step.lower():
            # Use Gemini to generate coping strategies or positive reframes
            strat_prompt = (f"You are a counseling AI. Provide 3 brief coping strategies or positive insights for someone who says: \"{user_input}\".\n"
                            "Format as a list of bullet points.")
            response = memory.gemini_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=strat_prompt,
                config=types.GenerateContentConfig(max_output_tokens=150, temperature=0.7)
            )
            coping_strategies = response.text.strip()
            reasoning_log.append("Generated coping strategies:\n" + coping_strategies)
        # Additional step types could be handled here (e.g., if plan included others).
    
    # Step 4: Final step - Generate the healing dialogue using Gemini (Healing sub-agent)
    healing_prompt = (
        "You are KIRAN, an empathetic conversational agent and therapist. Your goal is to help the user feel understood and hopeful.\n"
        f"User's mood: {user_input}\n"
        f"{('Earlier, you suggested: ' + coping_strategies + '\n') if coping_strategies else ''}"
        f"{('Recall this context from before: ' + past_context + '\n') if past_context else ''}"
        "Now, engage the user in a brief therapeutic dialogue. Speak as a caring mentor, validate their feelings, and offer gentle guidance. "
        "End with an uplifting note."
    )
    response = memory.gemini_client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=healing_prompt,
        config=types.GenerateContentConfig(max_output_tokens=300, temperature=0.9)
    )
    final_message = response.text.strip()
    reasoning_log.append("**Final Healing Dialogue:** " + final_message)
    
    # Step 5: Save this interaction to memory for long-term recall
    memory.save_interaction(user_input, final_message)
    
    return final_message, reasoning_log
