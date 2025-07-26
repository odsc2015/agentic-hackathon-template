# Environment Setup & Configuration
import os
import requests
import json
import math
import asyncio
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import datetime
import google.generativeai as genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.tools import google_search

# Load environment variables
load_dotenv()

# Configure APIs
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY', 'AIzaSyDdcvpwWOcXzhHmcR5c9DhT9J3uDOxnQzU')

# Trading partner service mapping
TRADING_PARTNER_SERVICE_MAP = {
    "Aetna": "60054",
    "Cigna": "62308", 
    "UnitedHealthcare": "87726",
    "BlueCross BlueShield of Texas": "G84980",
}

# Sample insurance data structure
INSURANCE_DATA = {
    "tradingPartnerServiceId": "62308",
    # "lat": 40.71427,
    # "lng": -74.00597,
    "lat": 42.35843000,
    "lng": -71.05977000,
    "subscriber": {
        "entityIdentifier": "Insured or Subscriber",
    },
    "payer": {
        "entityIdentifier": "Payer",
        "entityType": "Non-Person Entity",
        "lastName": "CHLIC",
        "name": "CHLIC",
        "federalTaxpayersIdNumber": "591056496",
        "contactInformation": {
            "contacts": [
                {
                    "communicationMode": "Telephone",
                    "communicationNumber": "8664942111"
                },
                {
                    "communicationMode": "Uniform Resource Locator (URL)",
                    "communicationNumber": "cignaforhcp.cigna.com"
                }
            ]
        }
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
    ],
    "benefitsInformation": [
        {
            "code": "1",
            "name": "Active Coverage",
            "serviceTypeCodes": ["30"],
            "serviceTypes": ["Health Benefit Plan Coverage"],
            "planCoverage": "Open Access Plus"
        },
        {
            "code": "C",
            "name": "Deductible",
            "coverageLevelCode": "IND",
            "coverageLevel": "Individual",
            "serviceTypeCodes": ["30"],
            "timeQualifierCode": "23",
            "timeQualifier": "Calendar Year",
            "benefitAmount": "5000",
            "inPlanNetworkIndicatorCode": "Y",
            "inPlanNetworkIndicator": "Yes"
        }
    ]
}

# Application constants
APP_NAME = "json_hospital_agent"
USER_ID = "user123"
SESSION_ID = "session123"

# JSON Hospital Search Agent - THE ONLY AGENT WE NEED
json_hospital_agent = Agent(
    name="json_hospital_agent",
    model="gemini-2.0-flash",
    instruction=(
        "You are a JSON data extraction agent. Your ONLY job is to return valid JSON arrays of hospital data. "
        "When given a request for hospitals, you must search and return ONLY a valid JSON array. "
        "Each hospital object must have exactly these fields: "
        "{'name': 'Hospital Name', 'address': '123 Street Address', 'phone': '555-123-4567', 'hospital_type': 'General Hospital', 'accepts_insurance': true} "
        "CRITICAL RULES: "
        "1. Return ONLY valid JSON - no explanatory text, no introduction, no disclaimers "
        "2. Start your response with [ and end with ] "
        "3. Include 5-15 real hospitals if available "
        "4. Use actual hospital names, addresses, and phone numbers from your search "
        "5. If you cannot find data, return an empty array [] "
        "6. Do not include any text outside the JSON array"
    ),
    description="Specialized agent that returns only JSON arrays of hospital data",
    tools=[google_search]
)

# Insurance Validity Functions
def check_insurance_validity(insurance_data: Dict = None) -> Dict[str, Any]:
    """
    Check if insurance plan is currently valid based on plan dates.
    
    Args:
        insurance_data: Dictionary containing insurance information (optional, uses global data if not provided)
        
    Returns:
        Dictionary with validation results
    """
    if insurance_data is None:
        insurance_data = INSURANCE_DATA
    
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
        if insurance_provider not in TRADING_PARTNER_SERVICE_MAP:
            return {
                "valid": False,
                "insurance_provider": insurance_provider,
                "error": "Unsupported insurance provider",
                "plan_info": {}
            }
        
        # Check coverage status
        coverage_active = False
        active_plans = []
        
        for status in insurance_data.get("planStatus", []):
            if status.get("statusCode") == "1":
                coverage_active = True
                active_plans.append(status.get("planDetails", "Active Coverage"))
        
        if not coverage_active:
            return {
                "valid": False,
                "insurance_provider": insurance_provider,
                "error": "No active coverage found",
                "plan_info": {}
            }
        
        # Check plan dates
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        plan_dates = insurance_data.get("planDateInformation", {})
        
        plan_begin = plan_dates.get("planBegin", "")
        plan_end = plan_dates.get("planEnd", "")
        
        # Validate date range
        if plan_begin and current_date < plan_begin:
            return {
                "valid": False,
                "insurance_provider": insurance_provider,
                "error": f"Coverage not yet effective (begins {plan_begin})",
                "plan_info": {
                    "plan_begin": plan_begin,
                    "plan_end": plan_end,
                    "current_date": current_date
                }
            }
        
        if plan_end and current_date > plan_end:
            return {
                "valid": False,
                "insurance_provider": insurance_provider,
                "error": f"Coverage expired (ended {plan_end})",
                "plan_info": {
                    "plan_begin": plan_begin,
                    "plan_end": plan_end,
                    "current_date": current_date
                }
            }
        
        # All validations passed
        return {
            "valid": True,
            "insurance_provider": insurance_provider,
            "message": f"Insurance is valid from {plan_begin} to {plan_end}",
            "plan_info": {
                "payer": insurance_data.get("payer", {}).get("name", ""),
                "group_description": insurance_data.get("planInformation", {}).get("groupDescription", ""),
                "plan_begin": plan_begin,
                "plan_end": plan_end,
                "current_date": current_date,
                "active_plans": active_plans
            }
        }
        
    except Exception as e:
        return {
            "valid": False,
            "insurance_provider": "Unknown",
            "error": f"Validation error: {str(e)}",
            "plan_info": {}
        }

async def setup_json_session_and_runner():
    """Set up session and runner for the JSON hospital agent."""
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="json_hospital_agent", 
        user_id="json_user", 
        session_id="json_session"
    )
    runner = Runner(
        agent=json_hospital_agent, 
        app_name="json_hospital_agent", 
        session_service=session_service
    )
    return session, runner

async def search_hospitals_return_json(insurance_provider: str, lat: float, lng: float) -> Dict[str, Any]:
    """
    Search for hospitals and return pure JSON data.
    
    Args:
        insurance_provider: Name of the insurance provider
        lat: Latitude coordinate
        lng: Longitude coordinate
        
    Returns:
        Dictionary with JSON hospital data
    """
    try:
        # Build focused search query
        search_query = (
            f"Find hospitals near coordinates {lat},{lng} that accept {insurance_provider} insurance. "
            f"Return only a JSON array with hospital objects containing name, address, phone, hospital_type, and accepts_insurance fields. "
            f"Include real hospitals with actual contact information. "
            f"Format: [{{\"name\": \"Hospital Name\", \"address\": \"123 Main St\", \"phone\": \"555-1234\", \"hospital_type\": \"General Hospital\", \"accepts_insurance\": true}}]"
        )
        
        print(f"JSON Agent Search Query: {search_query}")
        
        # Create content
        content = types.Content(
            role='user', 
            parts=[types.Part(text=search_query)]
        )
        
        # Set up session and runner
        session, runner = await setup_json_session_and_runner()
        
        # Run the agent
        events = runner.run_async(
            user_id="json_user", 
            session_id="json_session", 
            new_message=content
        )
        
        # Process events and get response
        final_response = ""
        async for event in events:
            if event.is_final_response():
                final_response = event.content.parts[0].text
                print("JSON Agent Response Received")
                break
        
        print(f"\n=== JSON AGENT RAW RESPONSE ===")
        print(f"Response length: {len(final_response)}")
        print(f"Response content: {final_response}")
        print("================================\n")
        
        # Extract and validate JSON
        hospitals_json = extract_and_validate_json(final_response)
        
        return {
            "status": "success",
            "hospitals": hospitals_json,
            "total_found": len(hospitals_json),
            "raw_response": final_response,
            "insurance_provider": insurance_provider,
            "location": {"lat": lat, "lng": lng}
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"JSON agent error: {str(e)}",
            "hospitals": [],
            "raw_response": ""
        }

def extract_and_validate_json(response_text: str) -> List[Dict[str, Any]]:
    """
    Extract and validate JSON from agent response.
    
    Args:
        response_text: Raw response from the agent
        
    Returns:
        List of validated hospital dictionaries
    """
    hospitals = []
    
    try:
        # Clean the response - remove any markdown formatting
        cleaned_text = response_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text.replace('```json', '').replace('```', '').strip()
        elif cleaned_text.startswith('```'):
            cleaned_text = cleaned_text.replace('```', '').strip()
        
        # Find JSON array boundaries
        start_bracket = cleaned_text.find('[')
        end_bracket = cleaned_text.rfind(']')
        
        if start_bracket != -1 and end_bracket != -1 and end_bracket > start_bracket:
            json_str = cleaned_text[start_bracket:end_bracket + 1]
            
            try:
                hospitals = json.loads(json_str)
                
                # Validate that it's a list
                if not isinstance(hospitals, list):
                    print("Response is not a JSON array")
                    return []
                
                # Validate each hospital object
                validated_hospitals = []
                for hospital in hospitals:
                    if isinstance(hospital, dict) and validate_hospital_object(hospital):
                        validated_hospitals.append(hospital)
                    else:
                        print(f"Invalid hospital object: {hospital}")
                
                print(f"Successfully parsed {len(validated_hospitals)} valid hospitals from JSON")
                return validated_hospitals
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Attempted to parse: {json_str[:200]}...")
                return []
        else:
            print("No valid JSON array found in response")
            return []
            
    except Exception as e:
        print(f"Error extracting JSON: {e}")
        return []

def validate_hospital_object(hospital: Dict) -> bool:
    """
    Validate that a hospital object has required fields.
    
    Args:
        hospital: Hospital dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['name', 'address', 'phone', 'hospital_type', 'accepts_insurance']
    
    # Check if all required fields exist
    for field in required_fields:
        if field not in hospital:
            print(f"Missing required field: {field}")
            return False
    
    # Check if name is not empty/generic
    name = hospital.get('name', '').strip()
    if not name or len(name) < 3:
        print(f"Invalid hospital name: {name}")
        return False
    
    # Check if it's not a generic description
    generic_phrases = ['comprehensive list', 'please note', 'facilities', 'reported to accept']
    if any(phrase in name.lower() for phrase in generic_phrases):
        print(f"Generic description instead of hospital name: {name}")
        return False
    
    return True

async def get_hospitals_json_format(insurance_data: Dict = None) -> Dict[str, Any]:
    """
    Main function to get hospitals in clean JSON format.
    
    Args:
        insurance_data: Insurance data dictionary (optional, uses global data if not provided)
        
    Returns:
        Dictionary with JSON-formatted hospital results
    """
    if insurance_data is None:
        insurance_data = INSURANCE_DATA
    
    try:
        # Extract location and provider
        lat = insurance_data.get("lat")
        lng = insurance_data.get("lng")
        
        # Extract insurance provider from trading partner ID
        trading_partner_id = insurance_data.get("tradingPartnerServiceId", "")
        insurance_provider = None
        
        for provider, service_id in TRADING_PARTNER_SERVICE_MAP.items():
            if service_id == trading_partner_id:
                insurance_provider = provider
                break
        
        if not insurance_provider:
            insurance_provider = insurance_data.get("payer", {}).get("name", "Unknown")
        
        if not lat or not lng:
            return {
                "status": "error",
                "error_message": "Missing coordinates",
                "hospitals": []
            }
        
        if not insurance_provider or insurance_provider == "Unknown":
            return {
                "status": "error", 
                "error_message": "Could not determine insurance provider",
                "hospitals": []
            }
        
        # Use the JSON agent to get hospital data
        result = await search_hospitals_return_json(insurance_provider, lat, lng)
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error in JSON hospital search: {str(e)}",
            "hospitals": []
        }

# Test function
async def test_json_hospital_agent():
    """Test the JSON hospital agent."""
    print("=== TESTING JSON HOSPITAL AGENT ===\n")
    
    result = await get_hospitals_json_format()
    
    print("JSON Hospital Agent Result:")
    print(f"Status: {result['status']}")
    
    if result['status'] == 'success':
        print(f"Location: {result['location']}")
        print(f"Insurance Provider: {result['insurance_provider']}")
        print(f"Total Hospitals Found: {result['total_found']}")
        
        print("\nHospitals (JSON Format):")
        hospitals_json = json.dumps(result['hospitals'], indent=2)
        print(hospitals_json)
        
        print(f"\nFirst hospital details:")
        if result['hospitals']:
            first_hospital = result['hospitals'][0]
            for key, value in first_hospital.items():
                print(f"  {key}: {value}")
    else:
        print(f"Error: {result['error_message']}")
    
    return result

# Run test if executed directly
if __name__ == "__main__":
    asyncio.run(test_json_hospital_agent())