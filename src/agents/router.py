from google.adk.agents import Agent

router_agent = Agent(
    name="router_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are an intent classifier.
    Read the user’s query and output ONLY one label from:
    
    - therapist
    - psychologist
    - neuroscientist
    - neurologist
    - neurosurgeon
    - mindcoach
    - learning
    - academic
    - facts
    - games
    
    Do NOT answer the query, just output the label.
    """
)
