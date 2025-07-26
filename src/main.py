"""
Enhanced FastAPI web server for Insurance Hospital Agent with Treatment Cost Calculation
Direct integration with existing structure - no external dependencies
"""

import os
import asyncio
import json
import warnings
import logging
import datetime
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

# Import from your existing coverageAgent
from coverageAgent import (
    TRADING_PARTNER_SERVICE_MAP,
    json_hospital_cost_agent
)

# Configure logging
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

# Add validation function that was missing
def check_insurance_validity(insurance_data: Dict = None) -> Dict[str, Any]:
    """
    Check if insurance plan is currently valid based on plan dates.
    """
    
    try:
        # Get insurance provider from trading partner ID
        trading_partner_id = insurance_data.get("tradingPartnerServiceId", "")
        insurance_provider = None
        
        for provider, service_id in TRADING_PARTNER_SERVICE_MAP.items():
            if service_id == trading_partner_id:
                insurance_provider = provider
                break
        
        if not insurance_provider:
            insurance_provider = insurance_data.get("payer", {}).get("name", "Unknown")
        
        # Check if provider is supported
        supported_ids = list(TRADING_PARTNER_SERVICE_MAP.values())
        if trading_partner_id not in supported_ids:
            return {
                "valid": False,
                "insurance_provider": insurance_provider,
                "error": "Unsupported insurance provider",
                "plan_info": {}
            }
        
        # Check coverage status - simplified validation
        plan_status = insurance_data.get("planStatus", [])
        coverage_active = any(status.get("statusCode") == "1" for status in plan_status)
        
        if not coverage_active and plan_status:  # Only check if planStatus exists
            return {
                "valid": False,
                "insurance_provider": insurance_provider,
                "error": "No active coverage found",
                "plan_info": {}
            }
        
        # Check plan dates if they exist
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        plan_dates = insurance_data.get("planDateInformation", {})
        
        plan_begin = plan_dates.get("planBegin", "")
        plan_end = plan_dates.get("planEnd", "")
        
        # Validate date range if dates are provided
        if plan_begin and current_date < plan_begin:
            return {
                "valid": False,
                "insurance_provider": insurance_provider,
                "error": f"Coverage not yet effective (begins {plan_begin})",
                "plan_info": {"plan_begin": plan_begin, "plan_end": plan_end}
            }
        
        if plan_end and current_date > plan_end:
            return {
                "valid": False,
                "insurance_provider": insurance_provider,
                "error": f"Coverage expired (ended {plan_end})",
                "plan_info": {"plan_begin": plan_begin, "plan_end": plan_end}
            }
        
        # All validations passed
        return {
            "valid": True,
            "insurance_provider": insurance_provider,
            "message": f"Insurance is valid",
            "plan_info": {
                "payer": insurance_data.get("payer", {}).get("name", ""),
                "group_description": insurance_data.get("planInformation", {}).get("groupDescription", ""),
                "plan_begin": plan_begin,
                "plan_end": plan_end
            }
        }
        
    except Exception as e:
        return {
            "valid": False,
            "insurance_provider": "Unknown",
            "error": f"Validation error: {str(e)}",
            "plan_info": {}
        }

def extract_cost_info_from_insurance(insurance_data: Dict) -> Dict[str, Any]:
    """
    Extract cost-related information from insurance data for calculations.
    """
    cost_info = {
        "annual_deductible": 0,
        "coinsurance_percentage": 80,
        "emergency_copay": 0,
        "office_visit_copay": 0,
        "in_network_coverage": True
    }
    
    try:
        benefits = insurance_data.get("benefitsInformation", [])
        
        for benefit in benefits:
            benefit_code = benefit.get("code", "")
            benefit_name = benefit.get("name", "").lower()
            
            # Extract deductible
            if benefit_code == "C" or "deductible" in benefit_name:
                deductible_amount = benefit.get("benefitAmount", "0")
                try:
                    cost_info["annual_deductible"] = float(deductible_amount)
                except (ValueError, TypeError):
                    cost_info["annual_deductible"] = 0
            
            # Extract coinsurance percentage
            elif benefit_code == "A" or "co-insurance" in benefit_name:
                coinsurance_percent = benefit.get("benefitPercent", "80")
                try:
                    cost_info["coinsurance_percentage"] = float(coinsurance_percent)
                except (ValueError, TypeError):
                    cost_info["coinsurance_percentage"] = 80
            
            # Extract copayments
            elif benefit_code == "B" or "co-payment" in benefit_name:
                service_types = benefit.get("serviceTypes", [])
                copay_amount = benefit.get("benefitAmount", "0")
                
                try:
                    copay_value = float(copay_amount)
                    if any("emergency" in service.lower() for service in service_types):
                        cost_info["emergency_copay"] = copay_value
                    else:
                        cost_info["office_visit_copay"] = copay_value
                except (ValueError, TypeError):
                    pass
        
        return cost_info
        
    except Exception as e:
        print(f"Error extracting cost info: {e}")
        return cost_info

# FastAPI app
app = FastAPI(
    title="Enhanced Insurance Hospital Agent API",
    description="API for finding hospitals covered by insurance with treatment cost estimation",
    version="2.0.0"
)

# Session Management
session_service = InMemorySessionService()
APP_NAME = "enhanced_insurance_coverage_app"
USER_ID = "user_1" 
SESSION_ID = "session_001"

# Global runner instance
global_runner = None
global_session_created = False

# Enhanced Pydantic models
class EnhancedInsuranceData(BaseModel):
    tradingPartnerServiceId: str
    lat: float
    lng: float
    symptoms: str = ""  # New field for cost calculation
    subscriber: Optional[Dict] = None
    payer: Optional[Dict] = None
    planInformation: Optional[Dict] = None
    planDateInformation: Optional[Dict] = None
    planStatus: Optional[List[Dict]] = None
    benefitsInformation: Optional[List[Dict]] = None

class EnhancedHospitalResponse(BaseModel):
    status: str
    message: str
    insurance_provider: str
    location: Dict[str, float]
    symptoms: str
    hospitals: List[Dict]
    cost_analysis: Optional[Dict] = None
    total_found: int

class ValidationResponse(BaseModel):
    valid: bool
    insurance_provider: str
    message: Optional[str] = None
    error: Optional[str] = None
    plan_info: Dict
    cost_info: Optional[Dict] = None

def get_insurance_provider_from_data(insurance_data: Dict) -> str:
    """Extract insurance provider name from insurance data."""
    trading_partner_id = insurance_data.get("tradingPartnerServiceId", "")
    
    for provider, service_id in TRADING_PARTNER_SERVICE_MAP.items():
        if service_id == trading_partner_id:
            return provider
    
    return insurance_data.get("payer", {}).get("name", "Unknown")

async def get_or_create_runner():
    """Get or create the global runner instance with enhanced agent"""
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
        
        # Create runner with enhanced agent
        global_runner = Runner(
            agent=json_hospital_cost_agent,  # Use the enhanced agent
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"Enhanced runner created for agent '{global_runner.agent.name}'.")
    
    return global_runner

async def call_enhanced_agent_with_insurance_data(query: str, runner, user_id, session_id, 
                                                insurance_data=None, symptoms=""):
    """Enhanced function that passes insurance data and symptoms to the agent for cost calculation."""
    print(f"\n>>> User Query: {query}")
    print(f">>> Symptoms: {symptoms}")

    
    # Extract relevant information
    insurance_provider = get_insurance_provider_from_data(insurance_data)
    lat = insurance_data.get("lat")
    lng = insurance_data.get("lng")
    
    # Extract cost information from insurance data
    cost_info = extract_cost_info_from_insurance(insurance_data)
    
    # Create enhanced query with insurance and symptom context
    enhanced_query = f"""
    INSURANCE DATA CONTEXT:
    - Insurance Provider: {insurance_provider}
    - Location: {lat}, {lng}
    - Trading Partner ID: {insurance_data.get('tradingPartnerServiceId')}
    - Annual Deductible: ${cost_info['annual_deductible']}
    - Coinsurance Coverage: {cost_info['coinsurance_percentage']}%
    - Emergency Copay: ${cost_info['emergency_copay']}
    - Office Visit Copay: ${cost_info['office_visit_copay']}
    
    PATIENT SYMPTOMS: {symptoms}
    
    USER REQUEST: {query}
    
    Please:
    1. Search for hospitals near coordinates {lat},{lng} that accept {insurance_provider} insurance
    2. Research treatment costs for these symptoms: "{symptoms}"
    3. Calculate patient out-of-pocket costs using the insurance coverage information
    4. Return the complete JSON format with hospitals and cost analysis as specified in your instructions
    
    Include realistic cost estimates and calculate what the patient would pay after insurance coverage.
    """
    
    # Prepare the message
    content = types.Content(role='user', parts=[types.Part(text=enhanced_query)])
    
    final_response_text = "Agent did not produce a final response."
    
    # Run the enhanced agent
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break
    
    print(f"<<< Enhanced Agent Response: {final_response_text}")
    
    # Try to parse and validate the enhanced JSON response
    try:
        # Clean and extract JSON
        cleaned_response = final_response_text.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response.replace('```json', '').replace('```', '').strip()
        
        start_brace = cleaned_response.find('{')
        end_brace = cleaned_response.rfind('}')
        
        if start_brace != -1 and end_brace != -1:
            json_str = cleaned_response[start_brace:end_brace + 1]
            result_data = json.loads(json_str)
            
            # Validate structure
            if isinstance(result_data, dict):
                hospitals = result_data.get('hospitals', [])
                cost_analysis = result_data.get('cost_analysis', {})
                
                print(f"✅ Successfully parsed {len(hospitals)} hospitals with cost data")
                return {
                    'hospitals': hospitals,
                    'cost_analysis': cost_analysis
                }
            else:
                print("❌ Response is not a valid JSON object")
                return {'hospitals': [], 'cost_analysis': {}}
        else:
            print("❌ No valid JSON object found in response")
            return {'hospitals': [], 'cost_analysis': {}}
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return {'hospitals': [], 'cost_analysis': {}}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "enhanced-insurance-hospital-agent"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Enhanced Insurance Hospital Agent API",
        "version": "2.0.0",
        "description": "Direct agent integration for hospital search with treatment cost calculation",
        "new_features": [
            "Treatment cost estimation based on symptoms",
            "Insurance coverage calculation",
            "Patient out-of-pocket cost prediction"
        ],
        "endpoints": {
            "health": "/health",
            "search": "/search",
            "validate": "/validate"
        }
    }

@app.post("/validate", response_model=ValidationResponse)
async def validate_insurance(insurance_data: EnhancedInsuranceData):
    """Validate insurance and extract cost information"""
    try:
        # Convert Pydantic model to dict
        insurance_dict = insurance_data.dict()
        
        # Validate insurance
        validation_result = check_insurance_validity(insurance_dict)
        
        # Extract cost information
        cost_info = extract_cost_info_from_insurance(insurance_dict) if validation_result["valid"] else None
        
        return ValidationResponse(
            valid=validation_result["valid"],
            insurance_provider=validation_result["insurance_provider"],
            message=validation_result.get("message"),
            error=validation_result.get("error"),
            plan_info=validation_result["plan_info"],
            cost_info=cost_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@app.post("/search", response_model=EnhancedHospitalResponse)
async def search_hospitals_with_costs(insurance_data: EnhancedInsuranceData):
    """Search for hospitals with treatment cost calculation - enhanced version"""
    try:
        # Convert Pydantic model to dict
        insurance_dict = insurance_data.dict()
        print(f"Received enhanced insurance data: {insurance_dict}")
        
        # Validate insurance first
        validation_result = check_insurance_validity(insurance_dict)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Insurance validation failed: {validation_result['error']}"
            )
        
        # Get or create runner
        runner = await get_or_create_runner()
        
        # Determine query based on whether symptoms are provided
        if insurance_data.symptoms.strip():
            query_text = "Find hospitals and calculate treatment costs for symptoms"
        else:
            query_text = "Find hospitals that accept this insurance"
        
        # Call the enhanced agent with insurance data and symptoms
        result = await call_enhanced_agent_with_insurance_data(
            query=query_text,
            runner=runner,
            user_id=USER_ID,
            session_id=SESSION_ID,
            insurance_data=insurance_dict,
            symptoms=insurance_data.symptoms
        )
        
        hospitals = result.get('hospitals', [])
        cost_analysis = result.get('cost_analysis', {})
        
        # Get insurance provider for response
        insurance_provider = get_insurance_provider_from_data(insurance_dict)
        
        # Determine success message
        if insurance_data.symptoms.strip():
            message = f"Found {len(hospitals)} hospitals with cost estimates for symptoms: {insurance_data.symptoms}"
        else:
            message = f"Found {len(hospitals)} hospitals (no symptoms provided for cost calculation)"
        
        return EnhancedHospitalResponse(
            status="success",
            message=message,
            insurance_provider=insurance_provider,
            location={
                "lat": insurance_dict.get("lat"),
                "lng": insurance_dict.get("lng")
            },
            symptoms=insurance_data.symptoms,
            hospitals=hospitals,
            cost_analysis=cost_analysis if cost_analysis else None,
            total_found=len(hospitals)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced search error: {str(e)}")

@app.get("/example")
async def get_example_request():
    """Get an example request for testing the enhanced API"""
    return {
        "example_request": {
            "tradingPartnerServiceId": "62308",
            "lat": 40.71427,
            "lng": -74.00597,
            "symptoms": "chest pain, shortness of breath, dizziness",
            "benefitsInformation": [
                {
                    "code": "C",
                    "name": "Deductible",
                    "benefitAmount": "5000",
                    "inPlanNetworkIndicatorCode": "Y"
                },
                {
                    "code": "A",
                    "name": "Co-Insurance",
                    "benefitPercent": "80",
                    "inPlanNetworkIndicatorCode": "Y"
                }
            ]
        },
        "usage": "POST to /search with this data structure to get hospitals with treatment costs"
    }

if __name__ == "__main__":
    # Get port from environment variable
    port = int(os.environ.get("PORT", 8080))
    
    # Run the enhanced FastAPI app
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )