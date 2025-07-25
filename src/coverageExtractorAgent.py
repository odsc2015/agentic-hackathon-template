import os
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts


# Load environment variables
load_dotenv()

API_URL = "https://healthcare.us.stedi.com/2024-04-01/change/medicalnetwork/eligibility/v3"
AUTHORIZATION_VALUE = os.environ.get("AUTHORIZATION_VALUE")

# Debug: Check if loaded (remove this after testing)
print(f"Auth value loaded: {'✅ Yes' if AUTHORIZATION_VALUE else '❌ No'}")

headers = {
    "Authorization": AUTHORIZATION_VALUE,
    "Content-Type": "application/json"
}

trading_partner_service_map = {
    "Aetna": "60054",
    "Cigna": "62308",
    "UnitedHealthcare": "87726",
    "BlueCross BlueShield of Texas": "G84980",
}

def make_eligibility_request(insurance_provider: str, member_id: str, 
                             first_name: str, last_name: str, 
                             date_of_birth: Optional[str] = None,
                             service_type_code: str = "30") -> Dict[str, Any]:

    trading_partner_service_id = trading_partner_service_map.get(insurance_provider)
    if not trading_partner_service_id:
        return {
            "error": "Invalid insurance provider", 
            "message": f"Insurance provider must be one of: {', '.join(trading_partner_service_map.keys())}"
        }
    
    payload = {
        "controlNumber": "123456789",  
        "tradingPartnerServiceId": trading_partner_service_id,
        "provider": {
            "organizationName": "Provider Name",
            "npi": "1999999984"
        },
        "subscriber": {
            "firstName": first_name,
            "lastName": last_name,
            "memberId": member_id
        },
        "encounter": {
            "serviceTypeCodes": [service_type_code]
        }
    }
    
    # Add date of birth if provided
    if date_of_birth:
        payload["subscriber"]["dateOfBirth"] = date_of_birth
    
    # Make the API call
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "message": "Failed to fetch coverage information"}

def parse_coverage_details(api_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts and formats the relevant coverage information from the API response.
    
    Args:
        api_response: The raw API response dictionary
    
    Returns:
        A simplified dictionary with formatted coverage details
    """
    if "error" in api_response:
        return api_response
    
    # Initialize the result structure
    result = {
        "subscriber": {},
        "coverage": {
            "status": "",
            "plan_details": "",
            "in_network": {
                "individual": {},
                "family": {}
            },
            "out_of_network": {
                "individual": {},
                "family": {}
            }
        },
        "limitations": "",
        "notes": []
    }
    
    # Extract subscriber information
    if "subscriber" in api_response:
        subscriber = api_response["subscriber"]
        result["subscriber"] = {
            "first_name": subscriber.get("firstName", ""),
            "last_name": subscriber.get("lastName", ""),
            "member_id": subscriber.get("memberId", ""),
            "date_of_birth": subscriber.get("dateOfBirth", "")
        }
    
    # Extract plan status
    if "planStatus" in api_response:
        for status in api_response["planStatus"]:
            if status.get("statusCode") == "1":
                result["coverage"]["status"] = status.get("status", "")
                result["coverage"]["plan_details"] = status.get("planDetails", "")
                break
    
    # Extract benefits information
    if "benefitsInformation" in api_response:
        for benefit in api_response["benefitsInformation"]:
            code = benefit.get("code")
            name = benefit.get("name")
            coverage_level = benefit.get("coverageLevel", "").lower()
            in_network = benefit.get("inPlanNetworkIndicator") == "Yes"
            
            # Set the appropriate target in the result structure
            network_type = "in_network" if in_network else "out_of_network"
            level_type = coverage_level if coverage_level in ["individual", "family"] else "individual"
            
            target = result["coverage"][network_type][level_type]
            
            # Process based on benefit type
            if code == "C" and name == "Deductible":
                # Deductible information
                target["deductible"] = {
                    "amount": benefit.get("benefitAmount", "0"),
                    "time_qualifier": benefit.get("timeQualifier", "")
                }
                if benefit.get("timeQualifier") == "Remaining":
                    target["deductible"]["remaining"] = benefit.get("benefitAmount", "0")
            
            elif code == "G" and name == "Out of Pocket (Stop Loss)":
                # Out of pocket information
                target["out_of_pocket"] = {
                    "amount": benefit.get("benefitAmount", "0"),
                    "time_qualifier": benefit.get("timeQualifier", "")
                }
                if benefit.get("timeQualifier") == "Remaining":
                    target["out_of_pocket"]["remaining"] = benefit.get("benefitAmount", "0")
            
            elif code == "A" and name == "Co-Insurance":
                # Co-insurance information
                target["coinsurance"] = {
                    "percent": float(benefit.get("benefitPercent", "0")) * 100,
                    "applies_to_out_of_pocket": any("out-of-pocket" in info.get("description", "").lower() 
                                                  for info in benefit.get("additionalInformation", []))
                }
            
            elif code == "B" and name == "Co-Payment":
                # Co-payment information
                target["copay"] = {
                    "amount": benefit.get("benefitAmount", "0"),
                    "per": benefit.get("timeQualifier", "")
                }
    
    # Extract plan date information
    if "planDateInformation" in api_response:
        date_info = api_response["planDateInformation"]
        result["coverage"]["plan_dates"] = {
            "begin": date_info.get("planBegin", ""),
            "end": date_info.get("planEnd", ""),
            "eligibility_begin": date_info.get("eligibilityBegin", "")
        }
    
    return result

def get_insurance_coverage_hardcoded() -> Dict[str, Any]:
    """
    Gets insurance coverage details using hardcoded test data for easy testing.
    No user input required.
    
    Returns:
        A dictionary with coverage details or error information
    """
    print("Insurance Coverage Checker (Hardcoded Test Data)")
    print("================================================")
    
    # Hardcoded payload for testing
    payload = {
        "controlNumber": "123456789",
        "tradingPartnerServiceId": "62308",  # Cigna
        "provider": {
            "organizationName": "Provider Name",
            "npi": "1999999984"
        },
        "subscriber": {
            "firstName": "James",
            "lastName": "Jones",
            "dateOfBirth": "19910202",
            "memberId": "23456789100"
        },
        "encounter": {
            "serviceTypeCodes": ["30"]
        }
    }
    
    print("Using test data:")
    print(f"  Provider: {payload['provider']['organizationName']}")
    print(f"  Trading Partner: {payload['tradingPartnerServiceId']} (Cigna)")
    print(f"  Patient: {payload['subscriber']['firstName']} {payload['subscriber']['lastName']}")
    print(f"  Member ID: {payload['subscriber']['memberId']}")
    print("  Making API call...")
    
    # Make the API call directly with hardcoded payload
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        api_response = response.json()
        
        print("✅ API call successful!")
        return parse_coverage_details(api_response)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API call failed: {str(e)}")
        return {"error": str(e), "message": "Failed to fetch coverage information"}

def get_insurance_coverage() -> Dict[str, Any]:
    """
    Gets insurance coverage details by taking user input and calling the API.
    
    Returns:
        A dictionary with coverage details or error information
    """
    print("Insurance Coverage Checker")
    print("-------------------------")
    
    # Get provider name and validate
    print(f"Available providers: {', '.join(trading_partner_service_map.keys())}")
    insurance_provider = input("Enter insurance provider name: ")
    
    if insurance_provider not in trading_partner_service_map:
        return {
            "error": "Invalid insurance provider", 
            "message": f"Insurance provider must be one of: {', '.join(trading_partner_service_map.keys())}"
        }
    
    # Get member information
    member_id = input("Enter member ID: ")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    
    # Date of birth is optional
    date_of_birth = input("Enter date of birth (YYYYMMDD) or press Enter to skip: ")
    if date_of_birth.strip() == "":
        date_of_birth = None
    
    # Make the API request
    api_response = make_eligibility_request(
        insurance_provider=insurance_provider,
        member_id=member_id,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth
    )
    
    # Parse and return the coverage details
    return parse_coverage_details(api_response)

def main():
    # Get the coverage details using hardcoded test data (no user input required)
    # coverage_details = get_insurance_coverage_hardcoded()
    
    # To use user input instead, uncomment the line below and comment the one above:
    coverage_details = get_insurance_coverage()
    
    # Print the results as formatted JSON
    print("\nCoverage Details:")
    print(json.dumps(coverage_details, indent=2))


if __name__ == "__main__":
    main()
