# Single query version - no continuous conversation

import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.tools import google_search
import json
from coverageAgent import (
        INSURANCE_DATA, 
        TRADING_PARTNER_SERVICE_MAP
    )
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

async def run_single_query(query: str = "Can you help me find hospitals covered by my insurance?"):
    """Run a single query without continuous conversation."""
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
    
    # Show current insurance info
    insurance_provider = get_insurance_provider_from_data(INSURANCE_DATA)
    print(f"\n📋 Current Insurance: {insurance_provider}")
    print(f"📍 Location: {INSURANCE_DATA.get('lat')}, {INSURANCE_DATA.get('lng')}")
    
    # Execute single query
    hospitals = await call_agent_with_insurance_data(
        query, 
        runner=runner, 
        user_id=USER_ID, 
        session_id=SESSION_ID,
        insurance_data=INSURANCE_DATA
    )
    
    # Display results
    if hospitals:
        print(f"\n🏥 Found {len(hospitals)} hospitals:")
        for i, hospital in enumerate(hospitals, 1):
            print(f"\n{i}. {hospital.get('name', 'Unknown')}")
            print(f"   📍 Address: {hospital.get('address', 'No address')}")
            print(f"   📞 Phone: {hospital.get('phone', 'No phone')}")
            print(f"   🏥 Type: {hospital.get('hospital_type', 'Unknown')}")
            print(f"   ✅ Accepts Insurance: {hospital.get('accepts_insurance', False)}")
        
        # Return JSON for further use
        print(f"\n📄 Complete JSON Response:")
        print(json.dumps(hospitals, indent=2))
        
        return hospitals
    else:
        print("\n❌ No hospitals found or error occurred.")
        return []

# Main execution
if __name__ == "__main__":
    try:
        # You can customize the query here
        query = "Find hospitals near me that accept my Cigna insurance"
        
        result = asyncio.run(run_single_query(query))
        
        print(f"\n✅ Query completed. Found {len(result)} hospitals.")
        
    except Exception as e:
        print(f"An error occurred: {e}")