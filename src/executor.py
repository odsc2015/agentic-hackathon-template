from Planner import plan_steps
from memory import MemoryManager

# Initialize memory manager (handles SQLite connection)
memory = MemoryManager(db_path="kiran_memory.db")

async def execute_plan(user_input):
    """
    Executes the plan for the given user input (mood), returns the final healing message.
    Also returns the reasoning steps for display.
    """
    # Step 1: Retrieve relevant memory context (if any)
    past_context = memory.fetch_last_interaction()
    
    # Step 2: Plan the subtasks using the planner module (Gemini LLM)
    #Get subagents to run the task
    plan = await plan_steps(user_input, memory_context=past_context)
    print("Planned steps:", plan)
    return plan
    reasoning_log = []  # to collect reasoning steps for UI display
    reasoning_log.append(f"**User Input:** {user_input}")
    if past_context:
        reasoning_log.append(f"Retrieved memory context: {past_context}")
    reasoning_log.append("**Plan:** " + "; ".join(plan))
    
    # Step 3: Execute each step in the plan
    coping_strategies = None
    for step in plan:
        if "learn" in step.lower():
            reasoning_log.append(f"Action: Memory retrieval -> {past_context or 'None found.'}")
            continue
        elif "analyz" in step.lower() or "identify" in step.lower():
            analysis_prompt = (
                f"You are a psychological AI assistant analyzing a user's mood.\n"
                f"User says: \"{user_input}\"\nProvide a brief analysis of their emotional state."
            )
            response = memory.gemini_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=analysis_prompt
            )
            analysis = response.text.strip()
            reasoning_log.append(f"Analysis: {analysis}")
        elif "strategy" in step.lower() or "coping" in step.lower() or "tips" in step.lower():
            strat_prompt = (
                f"You are a counseling AI. Provide 3 brief coping strategies or positive insights for someone who says: \"{user_input}\".\n"
                "Format as a list of bullet points."
            )
            response = memory.gemini_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=strat_prompt
            )
            coping_strategies = response.text.strip()
            reasoning_log.append("Generated coping strategies:\n" + coping_strategies)
        # Additional step types could be handled here.

    # Build the optional prompt parts:
    earlier_suggestion = f"Earlier, you suggested: {coping_strategies}\n" if coping_strategies else ""
    recall_context = f"Recall this context from before: {past_context}\n" if past_context else ""

    # Step 4: Final step - Generate the healing dialogue using Gemini
    healing_prompt = (
        "You are KIRAN, an empathetic conversational agent and therapist. Your goal is to help the user feel understood and hopeful.\n"
        f"User's mood: {user_input}\n"
        f"{earlier_suggestion}"
        f"{recall_context}"
        "Now, engage the user in a brief dialogue. Speak as a caring mentor, validate their feelings, and offer gentle guidance. "
        "End with an uplifting note."
    )
    response = memory.gemini_client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=healing_prompt
    )
    final_message = response.text.strip()
    reasoning_log.append("**Final Healing Dialogue:** " + final_message)
    
    # Step 5: Save this interaction to memory for long-term recall
    memory.save_interaction(user_input, final_message)
    
    return final_message, reasoning_log
