# src/executor.py

import os
from google import genai
from memory import load_user_profile
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Create Gemini client using API key from environment
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_response(user_input):
    # Load saved user profile
    profile = load_user_profile()
    if not profile:
        return "No user profile found."

    name = profile.get("name", "friend")
    routines = profile.get("routines", {})
    meds = routines.get("medications", {})
    contacts = profile.get("contacts", [])

    now = datetime.now().strftime("%A %I:%M %p")

    # Build memory snippet string
    memory_snippets = []
    if routines.get("dinner"):
        memory_snippets.append(f"{name} has dinner at {routines['dinner']}.")
    for med, time in meds.items():
        memory_snippets.append(f"The {med} is taken {time}.")
    if contacts:
        memory_snippets.append(f"Close contacts include: {', '.join(contacts)}.")

    memory_text = "\n".join(memory_snippets)

    # Construct prompt
    prompt = f"""
You are a caring AI assistant helping {name}, an early-stage Alzheimer’s patient.
Current time: {now}
Memory:
{memory_text}

User input:
"{user_input}"

Your job:
- Understand what {name} is asking
- Respond in a friendly, emotionally supportive tone
- If it's a reminder, infer the right time if not mentioned
- Help reduce confusion or anxiety

Respond directly to the user.
"""

    try:
        # Send prompt to Gemini
        response = client.models.generate_content(
            model="gemini-2.5-pro",  # You can switch to gemini-2.5 if available
            contents=prompt
        )
        return response.text.strip()

    except Exception as e:
        return f"Error contacting Gemini: {e}"
