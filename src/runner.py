# Modified version of your runner code that passes data to the agent

import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.tools import google_search
import json

# Import the data and functions from your agent module
# You'll need to make sure coverageAgent.py is importable
try:
    from coverageAgent import (
        INSURANCE_DATA, 
        TRADING_PARTNER_SERVICE_MAP,
        check_insurance_validity,
        get_hospitals_json_format
    )
except ImportError:
    # Fallback: Define the data here if import fails
    INSURANCE_DATA = {
        "tradingPartnerServiceId": "62308",
        "lat": 42.35843000,
        "lng": -71.05977000,
        "subscriber": {"entityIdentifier": "Insured or Subscriber"},
        "payer": {
            "entityIdentifier": "Payer",
            "entityType": "Non-Person Entity", 
            "lastName": "CHLIC",
            "name": "CHLIC",
            "federalTaxpayersIdNumber": "591056496"
        },
        "planInformation": {
            "groupNumber": "00123874",
            "groupDescription": "ACME, Inc."
        },
        "planDateInformation": {
            "planBegin": "20240101",
            "planEnd": "20241231",
            "eligibilityBegin": "20240101"
        },
        "planStatus": [
            {
                "statusCode": "1",
                "status": "Active Coverage", 
                "planDetails": "Open Access Plus",
                "serviceTypeCodes": ["30"]
            }
        ]
    }
    
    TRADING_PARTNER_SERVICE_MAP = {
        "Aetna": "60054",
        "Cigna": "62308",
        "UnitedHealthcare": "87726", 
        "BlueCross BlueShield of Texas": "G84980",
    }

import warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

# Create agent with enhanced instructions that include data context
json_hospital_agent = Agent(
    name="json_hospital_agent",
    model="gemini-2.0-flash",
    instruction=(
        "You are a JSON data extraction agent for insurance hospital searches. "
        "When given a request for hospitals, you must search and return ONLY a valid JSON array. "
        "Each hospital object must have exactly these fields: "
        "{'name': 'Hospital Name', 'address': '123 Street Address', 'phone': '555-123-4567', 'hospital_type': 'General Hospital', 'accepts_insurance': true} "
        
        "CRITICAL RULES: "
        "1. Return ONLY valid JSON - no explanatory text, no introduction, no disclaimers "
        "2. Start your response with [ and end with ] "
        "3. Include 5-15 real hospitals if available "
        "4. Use actual hospital names, addresses, and phone numbers from your search "
        "5. If you cannot find data, return an empty array [] "
        "6. Do not include any text outside the JSON array "
        
        "CONTEXT HANDLING: "
        "- When given insurance data in the query, extract the insurance provider and location "
        "- Use the coordinates (lat/lng) to search for nearby hospitals "
        "- Focus on hospitals that accept the specified insurance provider "
        "- If coordinates are around Boston area (42.35, -71.05), search for Boston hospitals "
    ),
    description="Specialized agent that returns only JSON arrays of hospital data based on insurance information",
    tools=[google_search]
)

# Session Management
session_service = InMemorySessionService()
APP_NAME = "insurance_coverage_app"
USER_ID = "user_1" 
SESSION_ID = "session_001"

def get_insurance_provider_from_data(insurance_data):
    """Extract insurance provider name from insurance data."""
    trading_partner_id = insurance_data.get("tradingPartnerServiceId", "")
    
    for provider, service_id in TRADING_PARTNER_SERVICE_MAP.items():
        if service_id == trading_partner_id:
            return provider
    
    return insurance_data.get("payer", {}).get("name", "Unknown")

async def call_agent_with_insurance_data(query: str, runner, user_id, session_id, insurance_data=None):
    """Enhanced function that passes insurance data to the agent."""
    print(f"\n>>> User Query: {query}")
    
    if insurance_data is None:
        insurance_data = INSURANCE_DATA
    
    # Extract relevant information
    insurance_provider = get_insurance_provider_from_data(insurance_data)
    lat = insurance_data.get("lat")
    lng = insurance_data.get("lng")
    
    # Create enhanced query with insurance context
    enhanced_query = f"""
    INSURANCE DATA CONTEXT:
    - Insurance Provider: {insurance_provider}
    - Location: {lat}, {lng}
    - Trading Partner ID: {insurance_data.get('tradingPartnerServiceId')}
    
    USER REQUEST: {query}
    
    Please search for hospitals near the coordinates {lat},{lng} that accept {insurance_provider} insurance.
    Return only a JSON array with hospital data as specified in your instructions.
    """
    
    # Prepare the message
    content = types.Content(role='user', parts=[types.Part(text=enhanced_query)])
    
    final_response_text = "Agent did not produce a final response."
    
    # Run the agent
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break
    
    print(f"<<< Agent Response: {final_response_text}")
    
    # Try to parse and validate the JSON response
    try:
        # Clean and extract JSON
        cleaned_response = final_response_text.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response.replace('```json', '').replace('```', '').strip()
        
        start_bracket = cleaned_response.find('[')
        end_bracket = cleaned_response.rfind(']')
        
        if start_bracket != -1 and end_bracket != -1:
            json_str = cleaned_response[start_bracket:end_bracket + 1]
            hospitals = json.loads(json_str)
            print(f"✅ Successfully parsed {len(hospitals)} hospitals from JSON response")
            return hospitals
        else:
            print("❌ No valid JSON array found in response")
            return []
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return []

def should_continue_conversation(user_input: str) -> bool:
    """Check if the user wants to continue the conversation."""
    exit_phrases = [
        "no thank you", "no thanks", "that's all", "goodbye", "bye",
        "exit", "quit", "done", "finished", "that's it", "nothing else",
        "no", "nope", "i'm good", "all set", "thanks bye"
    ]
    
    user_input_lower = user_input.lower().strip()
    
    for phrase in exit_phrases:
        if phrase in user_input_lower:
            return False
    
    return True

def get_user_input() -> str:
    """Get user input with a nice prompt."""
    try:
        user_input = input("\n💬 You: ").strip()
        return user_input
    except (EOFError, KeyboardInterrupt):
        return "exit"

async def run_continuous_conversation():
    """Run a continuous conversation with insurance data context."""
    # Create session
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")
    
    # Create runner
    runner = Runner(
        agent=json_hospital_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")
    
    # Welcome message
    print("\n🤖 Welcome to the Insurance Coverage Assistant!")
    print("I can help you find hospitals covered by your insurance.")
    print("Type your questions, and when you're done, just say 'no thank you' or 'goodbye'.\n")
    
    # Show current insurance info
    insurance_provider = get_insurance_provider_from_data(INSURANCE_DATA)
    print(f"📋 Current Insurance: {insurance_provider}")
    print(f"📍 Location: {INSURANCE_DATA.get('lat')}, {INSURANCE_DATA.get('lng')}")
    
    # Initial conversation starter
    first_query = "Can you help me find hospitals covered by my insurance?"
    hospitals = await call_agent_with_insurance_data(
        first_query, 
        runner=runner, 
        user_id=USER_ID, 
        session_id=SESSION_ID,
        insurance_data=INSURANCE_DATA
    )
    
    if hospitals:
        print(f"\n🏥 Found {len(hospitals)} hospitals:")
        for i, hospital in enumerate(hospitals[:3], 1):  # Show first 3
            print(f"{i}. {hospital.get('name', 'Unknown')} - {hospital.get('address', 'No address')}")
    
    # Continue conversation loop
    while True:
        user_input = get_user_input()
        
        if not user_input or not should_continue_conversation(user_input):
            print("\n👋 Thank you for using the Insurance Coverage Assistant. Goodbye!")
            break
        
        # Process user query with insurance context
        hospitals = await call_agent_with_insurance_data(
            user_input,
            runner=runner,
            user_id=USER_ID, 
            session_id=SESSION_ID,
            insurance_data=INSURANCE_DATA
        )
        
        if hospitals:
            print(f"\n🏥 Found {len(hospitals)} hospitals:")
            for i, hospital in enumerate(hospitals[:5], 1):  # Show first 5
                print(f"{i}. {hospital.get('name', 'Unknown')} - {hospital.get('phone', 'No phone')}")

if __name__ == "__main__":
    try:
        asyncio.run(run_continuous_conversation())
    except Exception as e:
        print(f"An error occurred: {e}")