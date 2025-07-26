"""
FastAPI web server for Insurance Hospital Agent
Integrated agent functionality without external runner.py dependency
"""

import os
import asyncio
import json
import warnings
import logging
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn

# Google ADK imports
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.tools import google_search

# Import from coverageAgent
from coverageAgent import (
    INSURANCE_DATA, 
    TRADING_PARTNER_SERVICE_MAP,
    check_insurance_validity,
    json_hospital_agent
)

# Configure logging
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

# FastAPI app
app = FastAPI(
    title="Insurance Hospital Agent API",
    description="API for finding hospitals covered by insurance using integrated agent",
    version="1.0.0"
)

# Session Management
session_service = InMemorySessionService()
APP_NAME = "insurance_coverage_app"
USER_ID = "user_1" 
SESSION_ID = "session_001"

# Global runner instance
global_runner = None
global_session_created = False

# Pydantic models for request/response
class InsuranceData(BaseModel):
    tradingPartnerServiceId: str
    lat: float
    lng: float
    subscriber: Optional[Dict] = None
    payer: Optional[Dict] = None
    planInformation: Optional[Dict] = None
    planDateInformation: Optional[Dict] = None
    planStatus: Optional[List[Dict]] = None
    benefitsInformation: Optional[List[Dict]] = None

# Removed HospitalSearchRequest class since we're accepting InsuranceData directly

class HospitalResponse(BaseModel):
    status: str
    message: str
    insurance_provider: str
    location: Dict[str, float]
    hospitals: List[Dict]
    total_found: int

class ValidationResponse(BaseModel):
    valid: bool
    insurance_provider: str
    message: Optional[str] = None
    error: Optional[str] = None
    plan_info: Dict

def get_insurance_provider_from_data(insurance_data: Dict) -> str:
    """Extract insurance provider name from insurance data."""
    trading_partner_id = insurance_data.get("tradingPartnerServiceId", "")
    
    for provider, service_id in TRADING_PARTNER_SERVICE_MAP.items():
        if service_id == trading_partner_id:
            return provider
    
    return insurance_data.get("payer", {}).get("name", "Unknown")

async def get_or_create_runner():
    """Get or create the global runner instance"""
    global global_runner, global_session_created
    
    if global_runner is None:
        # Create session if it doesn't exist
        if not global_session_created:
            try:
                session = await session_service.create_session(
                    app_name=APP_NAME,
                    user_id=USER_ID,
                    session_id=SESSION_ID
                )
                global_session_created = True
                print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")
            except Exception as e:
                print(f"Session creation issue: {e}")
        
        # Create runner
        global_runner = Runner(
            agent=json_hospital_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"Runner created for agent '{global_runner.agent.name}'.")
    
    return global_runner

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


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "insurance-hospital-agent"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Insurance Hospital Agent API",
        "version": "1.0.0",
        "description": "Direct agent integration for hospital search",
        "endpoints": {
            "health": "/health",
            "search": "/search"
        }
    }

@app.post("/search", response_model=HospitalResponse)
async def search_hospitals(insurance_data: InsuranceData):
    """Search for hospitals using the agent directly - accepts insurance data directly"""
    try:
        # Convert Pydantic model to dict
        insurance_dict = insurance_data.dict()
        
        # Validate insurance first
        validation_result = check_insurance_validity(insurance_dict)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Insurance validation failed: {validation_result['error']}"
            )
        
        # Call the agent with insurance data (no query parameter needed)
        hospitals = await call_agent_with_insurance_data(insurance_dict)
        
        # Get insurance provider for response
        insurance_provider = get_insurance_provider_from_data(insurance_dict)
        
        return HospitalResponse(
            status="success",
            message=f"Found {len(hospitals)} hospitals using agent",
            insurance_provider=insurance_provider,
            location={
                "lat": insurance_dict.get("lat"),
                "lng": insurance_dict.get("lng")
            },
            hospitals=hospitals,
            total_found=len(hospitals)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


if __name__ == "__main__":
    # Get port from environment variable
    port = int(os.environ.get("PORT", 8080))
    
    # Run the FastAPI app
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=True  # Enable auto-reload during development
    )