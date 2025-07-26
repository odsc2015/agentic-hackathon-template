# Enhanced Insurance Hospital Agent with Treatment Cost Calculation
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
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')

# Trading partner service mapping
TRADING_PARTNER_SERVICE_MAP = {
    "Aetna": "60054",
    "Cigna": "62308", 
    "UnitedHealthcare": "87726",
    "BlueCross BlueShield of Texas": "G84980",
}

# Add missing validation function
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
        if insurance_provider not in TRADING_PARTNER_SERVICE_MAP.values():
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

# Enhanced JSON Hospital & Cost Agent
json_hospital_cost_agent = Agent(
    name="json_hospital_cost_agent",
    model="gemini-2.0-flash",
    instruction=(
        "You are a comprehensive healthcare cost and hospital search agent. Your job is to: "
        "1. Search for hospitals that accept specific insurance "
        "2. Calculate treatment costs based on symptoms and insurance coverage "
        "3. Return detailed JSON with hospitals and cost estimates "
        "\n"
        "When given a request, you must: "
        "1. First search for hospitals near the specified coordinates that accept the insurance "
        "2. Then search for treatment costs for the specified symptoms/conditions "
        "3. Calculate patient out-of-pocket costs using the insurance deductible and coverage info "
        "4. Return a JSON object with this exact structure: "
        "{"
        "  \"hospitals\": ["
        "    {"
        "      \"name\": \"Hospital Name\","
        "      \"address\": \"123 Street Address\","
        "      \"phone\": \"555-123-4567\","
        "      \"hospital_type\": \"General Hospital\","
        "      \"accepts_insurance\": true,"
        "      \"estimated_costs\": {"
        "        \"procedure_name\": \"Treatment for [symptoms]\","
        "        \"average_cost\": 1500,"
        "        \"with_insurance_cost\": 300,"
        "        \"patient_responsibility\": 300,"
        "        \"insurance_covers\": 1200"
        "      }"
        "    }"
        "  ],"
        "  \"cost_analysis\": {"
        "    \"symptoms\": \"[provided symptoms]\","
        "    \"likely_procedures\": [\"Procedure 1\", \"Procedure 2\"],"
        "    \"deductible_info\": {"
        "      \"annual_deductible\": 5000,"
        "      \"deductible_met\": false,"
        "      \"remaining_deductible\": 5000"
        "    },"
        "    \"coverage_details\": {"
        "      \"coverage_percentage\": 80,"
        "      \"in_network\": true"
        "    }"
        "  }"
        "}"
        "\n"
        "CRITICAL RULES: "
        "1. Always search for current treatment costs for the specific symptoms "
        "2. Use the insurance deductible and coverage information provided "
        "3. Calculate realistic out-of-pocket costs "
        "4. Return ONLY valid JSON - no explanatory text outside the JSON "
        "5. Include 3-8 real hospitals if available "
        "6. Make multiple searches for cost information to get accurate estimates "
        "7. Consider both emergency and non-emergency treatment costs "
    ),
    description="Agent that finds hospitals and calculates treatment costs based on symptoms and insurance coverage",
    tools=[google_search]
)

# Enhanced insurance data structure with additional cost calculation fields
ENHANCED_INSURANCE_DATA = {
    "tradingPartnerServiceId": "62308",
    "lat": 40.71427,
    "lng": -74.00597,
    "symptoms": "",  # Will be populated from request
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
        "planBegin": "20250101",
        "planEnd": "20251231", 
        "eligibilityBegin": "20250101"
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
        },
        {
            "code": "A",
            "name": "Co-Insurance",
            "coverageLevel": "Individual", 
            "serviceTypeCodes": ["30"],
            "benefitPercent": "80",
            "inPlanNetworkIndicatorCode": "Y"
        },
        {
            "code": "B", 
            "name": "Co-Payment",
            "serviceTypeCodes": ["98"],
            "serviceTypes": ["Emergency Room"],
            "benefitAmount": "150",
            "inPlanNetworkIndicatorCode": "Y"
        }
    ]
}

def extract_cost_info_from_insurance(insurance_data: Dict) -> Dict[str, Any]:
    """
    Extract cost-related information from insurance data for calculations.
    
    Args:
        insurance_data: Insurance data dictionary
        
    Returns:
        Dictionary with cost calculation parameters
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

async def setup_enhanced_session_and_runner():
    """Set up session and runner for the enhanced hospital and cost agent."""
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="hospital_cost_agent", 
        user_id="cost_user", 
        session_id="cost_session"
    )
    runner = Runner(
        agent=json_hospital_cost_agent, 
        app_name="hospital_cost_agent", 
        session_service=session_service
    )
    return session, runner

async def search_hospitals_with_costs(insurance_provider: str, lat: float, lng: float, 
                                    symptoms: str, cost_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search for hospitals and calculate treatment costs based on symptoms.
    
    Args:
        insurance_provider: Name of the insurance provider
        lat: Latitude coordinate
        lng: Longitude coordinate
        symptoms: Patient symptoms for cost calculation
        cost_info: Insurance cost information
        
    Returns:
        Dictionary with hospital and cost data
    """
    try:
        # Build comprehensive search query
        search_query = (
            f"I need hospitals near coordinates {lat},{lng} that accept {insurance_provider} insurance "
            f"AND treatment cost estimates for these symptoms: '{symptoms}'. "
            f"\n"
            f"Insurance Coverage Details: "
            f"- Annual Deductible: ${cost_info['annual_deductible']} "
            f"- Coinsurance: {cost_info['coinsurance_percentage']}% coverage after deductible "
            f"- Emergency Copay: ${cost_info['emergency_copay']} "
            f"- Office Visit Copay: ${cost_info['office_visit_copay']} "
            f"\n"
            f"Please search for: "
            f"1. Real hospitals in the area that accept {insurance_provider} "
            f"2. Current treatment costs for symptoms: {symptoms} "
            f"3. Calculate patient out-of-pocket costs using the insurance information "
            f"\n"
            f"Return the exact JSON format specified in your instructions with hospitals and cost analysis."
        )
        
        print(f"Enhanced Agent Search Query: {search_query}")
        
        # Create content
        content = types.Content(
            role='user', 
            parts=[types.Part(text=search_query)]
        )
        
        # Set up session and runner
        session, runner = await setup_enhanced_session_and_runner()
        
        # Run the agent
        events = runner.run_async(
            user_id="cost_user", 
            session_id="cost_session", 
            new_message=content
        )
        
        # Process events and get response
        final_response = ""
        async for event in events:
            if event.is_final_response():
                final_response = event.content.parts[0].text
                print("Enhanced Agent Response Received")
                break
        
        print(f"\n=== ENHANCED AGENT RAW RESPONSE ===")
        print(f"Response content: {final_response}")
        print("===================================\n")
        
        # Extract and validate JSON
        hospitals_and_costs = extract_and_validate_cost_json(final_response)
        
        return {
            "status": "success",
            "data": hospitals_and_costs,
            "raw_response": final_response,
            "insurance_provider": insurance_provider,
            "location": {"lat": lat, "lng": lng},
            "symptoms": symptoms
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Enhanced agent error: {str(e)}",
            "data": {"hospitals": [], "cost_analysis": {}},
            "raw_response": ""
        }

def extract_and_validate_cost_json(response_text: str) -> Dict[str, Any]:
    """
    Extract and validate JSON from enhanced agent response.
    
    Args:
        response_text: Raw response from the agent
        
    Returns:
        Dictionary with validated hospital and cost data
    """
    default_response = {
        "hospitals": [],
        "cost_analysis": {
            "symptoms": "",
            "likely_procedures": [],
            "deductible_info": {},
            "coverage_details": {}
        }
    }
    
    try:
        # Clean the response
        cleaned_text = response_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text.replace('```json', '').replace('```', '').strip()
        elif cleaned_text.startswith('```'):
            cleaned_text = cleaned_text.replace('```', '').strip()
        
        # Find JSON object boundaries
        start_brace = cleaned_text.find('{')
        end_brace = cleaned_text.rfind('}')
        
        if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
            json_str = cleaned_text[start_brace:end_brace + 1]
            
            try:
                data = json.loads(json_str)
                
                # Validate structure
                if not isinstance(data, dict):
                    print("Response is not a JSON object")
                    return default_response
                
                # Ensure required keys exist
                if "hospitals" not in data:
                    data["hospitals"] = []
                if "cost_analysis" not in data:
                    data["cost_analysis"] = default_response["cost_analysis"]
                
                # Validate hospitals
                validated_hospitals = []
                for hospital in data.get("hospitals", []):
                    if isinstance(hospital, dict) and validate_enhanced_hospital_object(hospital):
                        validated_hospitals.append(hospital)
                
                data["hospitals"] = validated_hospitals
                
                print(f"Successfully parsed {len(validated_hospitals)} hospitals with cost data")
                return data
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                return default_response
        else:
            print("No valid JSON object found in response")
            return default_response
            
    except Exception as e:
        print(f"Error extracting cost JSON: {e}")
        return default_response

def validate_enhanced_hospital_object(hospital: Dict) -> bool:
    """
    Validate that a hospital object has required fields including cost information.
    
    Args:
        hospital: Hospital dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['name', 'address', 'phone', 'hospital_type', 'accepts_insurance']
    
    # Check basic required fields
    for field in required_fields:
        if field not in hospital:
            print(f"Missing required field: {field}")
            return False
    
    # Check if name is valid
    name = hospital.get('name', '').strip()
    if not name or len(name) < 3:
        print(f"Invalid hospital name: {name}")
        return False
    
    # Validate cost information if present
    if 'estimated_costs' in hospital:
        cost_data = hospital['estimated_costs']
        if isinstance(cost_data, dict):
            # Check for reasonable cost values
            avg_cost = cost_data.get('average_cost', 0)
            if isinstance(avg_cost, (int, float)) and avg_cost > 0:
                return True
    
    return True

async def get_hospitals_with_treatment_costs(insurance_data: Dict = None, symptoms: str = "") -> Dict[str, Any]:
    """
    Main function to get hospitals with treatment cost calculations.
    
    Args:
        insurance_data: Insurance data dictionary
        symptoms: Patient symptoms for cost calculation
        
    Returns:
        Dictionary with hospital and cost results
    """
    if insurance_data is None:
        insurance_data = ENHANCED_INSURANCE_DATA.copy()
        insurance_data["symptoms"] = symptoms
    
    try:
        # Extract location and provider
        lat = insurance_data.get("lat")
        lng = insurance_data.get("lng")
        
        # Extract insurance provider
        trading_partner_id = insurance_data.get("tradingPartnerServiceId", "")
        insurance_provider = None
        
        for provider, service_id in TRADING_PARTNER_SERVICE_MAP.items():
            if service_id == trading_partner_id:
                insurance_provider = provider
                break
        
        if not insurance_provider:
            insurance_provider = insurance_data.get("payer", {}).get("name", "Unknown")
        
        # Validate inputs
        if not lat or not lng:
            return {
                "status": "error",
                "error_message": "Missing coordinates",
                "data": {"hospitals": [], "cost_analysis": {}}
            }
        
        if not insurance_provider or insurance_provider == "Unknown":
            return {
                "status": "error", 
                "error_message": "Could not determine insurance provider",
                "data": {"hospitals": [], "cost_analysis": {}}
            }
        
        if not symptoms.strip():
            return {
                "status": "error",
                "error_message": "No symptoms provided for cost calculation",
                "data": {"hospitals": [], "cost_analysis": {}}
            }
        
        # Extract cost information from insurance data
        cost_info = extract_cost_info_from_insurance(insurance_data)
        
        # Use the enhanced agent to get hospital and cost data
        result = await search_hospitals_with_costs(
            insurance_provider, lat, lng, symptoms, cost_info
        )
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error in enhanced hospital and cost search: {str(e)}",
            "data": {"hospitals": [], "cost_analysis": {}}
        }

# Additional utility functions for cost calculations
def calculate_patient_responsibility(total_cost: float, deductible: float, 
                                   coinsurance_percent: float, deductible_met: bool = False) -> Dict[str, float]:
    """
    Calculate patient's financial responsibility for treatment.
    
    Args:
        total_cost: Total cost of treatment
        deductible: Annual deductible amount
        coinsurance_percent: Insurance coverage percentage after deductible
        deductible_met: Whether annual deductible has been met
        
    Returns:
        Dictionary with cost breakdown
    """
    if deductible_met:
        # Deductible already met, only pay coinsurance
        insurance_pays = total_cost * (coinsurance_percent / 100)
        patient_pays = total_cost - insurance_pays
    else:
        # Need to pay deductible first
        if total_cost <= deductible:
            # Entire cost goes toward deductible
            patient_pays = total_cost
            insurance_pays = 0
        else:
            # Pay deductible + coinsurance on remaining
            remaining_after_deductible = total_cost - deductible
            insurance_pays_after_deductible = remaining_after_deductible * (coinsurance_percent / 100)
            patient_pays = deductible + (remaining_after_deductible - insurance_pays_after_deductible)
            insurance_pays = insurance_pays_after_deductible
    
    return {
        "total_cost": total_cost,
        "patient_responsibility": round(patient_pays, 2),
        "insurance_covers": round(insurance_pays, 2),
        "deductible_applied": deductible if not deductible_met else 0
    }

# Export the enhanced agent and functions
__all__ = [
    'json_hospital_cost_agent',
    'get_hospitals_with_treatment_costs',
    'calculate_patient_responsibility',
    'extract_cost_info_from_insurance',
    'ENHANCED_INSURANCE_DATA'
]