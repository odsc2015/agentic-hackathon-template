"""
FastAPI web server for Insurance Hospital Agent
Suitable for Google Cloud Run deployment
"""

import os
import asyncio
import json
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn

# Import your agent modules
from coverageAgent import (
    INSURANCE_DATA, 
    TRADING_PARTNER_SERVICE_MAP,
    check_insurance_validity,
    get_hospitals_json_format
)
from runner import run_single_query, get_insurance_provider_from_data

# FastAPI app
app = FastAPI(
    title="Insurance Hospital Agent API",
    description="API for finding hospitals covered by insurance",
    version="1.0.0"
)

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

class HospitalSearchRequest(BaseModel):
    query: str = "Find hospitals covered by my insurance"
    insurance_data: Optional[InsuranceData] = None

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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy", "service": "insurance-hospital-agent"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Insurance Hospital Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "validate": "/validate",
            "search": "/search",
            "search_default": "/search/default"
        }
    }

# Insurance validation endpoint
@app.post("/validate", response_model=ValidationResponse)
async def validate_insurance(insurance_data: Optional[InsuranceData] = None):
    """Validate insurance coverage"""
    try:
        # Use provided data or default
        data_dict = insurance_data.dict() if insurance_data else INSURANCE_DATA
        
        # Validate insurance
        validation_result = check_insurance_validity(data_dict)
        
        return ValidationResponse(
            valid=validation_result["valid"],
            insurance_provider=validation_result["insurance_provider"],
            message=validation_result.get("message"),
            error=validation_result.get("error"),
            plan_info=validation_result["plan_info"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

# Hospital search endpoint
@app.post("/search", response_model=HospitalResponse)
async def search_hospitals(request: HospitalSearchRequest):
    """Search for hospitals using the agent"""
    try:
        # Use provided insurance data or default
        insurance_data = request.insurance_data.dict() if request.insurance_data else INSURANCE_DATA
        
        # Validate insurance first
        validation_result = check_insurance_validity(insurance_data)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Insurance validation failed: {validation_result['error']}"
            )
        
        # Get hospitals using the more comprehensive function
        result = await get_hospitals_json_format(insurance_data)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error_message"])
        
        return HospitalResponse(
            status="success",
            message=f"Found {result['total_found']} hospitals",
            insurance_provider=result["insurance_provider"],
            location=result["location"],
            hospitals=result["hospitals"],
            total_found=result["total_found"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

# Simple search endpoint with default data
@app.get("/search/default", response_model=HospitalResponse)
async def search_hospitals_default(query: str = "Find hospitals covered by my insurance"):
    """Search for hospitals using default insurance data"""
    try:
        # Validate default insurance
        validation_result = check_insurance_validity()
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Default insurance validation failed: {validation_result['error']}"
            )
        
        # Get hospitals
        result = await get_hospitals_json_format()
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error_message"])
        
        return HospitalResponse(
            status="success",
            message=f"Found {result['total_found']} hospitals",
            insurance_provider=result["insurance_provider"],
            location=result["location"],
            hospitals=result["hospitals"],
            total_found=result["total_found"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

# Alternative endpoint using the runner approach
@app.post("/search/runner")
async def search_hospitals_runner(request: HospitalSearchRequest):
    """Search for hospitals using the runner approach"""
    try:
        # Run the single query function
        hospitals = await run_single_query(request.query)
        
        # Get insurance provider for response
        insurance_data = request.insurance_data.dict() if request.insurance_data else INSURANCE_DATA
        insurance_provider = get_insurance_provider_from_data(insurance_data)
        
        return {
            "status": "success",
            "message": f"Found {len(hospitals)} hospitals",
            "insurance_provider": insurance_provider,
            "location": {
                "lat": insurance_data.get("lat"),
                "lng": insurance_data.get("lng")
            },
            "hospitals": hospitals,
            "total_found": len(hospitals)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Runner search error: {str(e)}")

# Get current insurance info
@app.get("/insurance/current")
async def get_current_insurance():
    """Get current insurance information"""
    try:
        insurance_provider = get_insurance_provider_from_data(INSURANCE_DATA)
        validation_result = check_insurance_validity()
        
        return {
            "insurance_provider": insurance_provider,
            "location": {
                "lat": INSURANCE_DATA.get("lat"),
                "lng": INSURANCE_DATA.get("lng")
            },
            "trading_partner_id": INSURANCE_DATA.get("tradingPartnerServiceId"),
            "validation": validation_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting insurance info: {str(e)}")

if __name__ == "__main__":
    # Get port from environment variable (Cloud Run provides this)
    port = int(os.environ.get("PORT", 8080))
    
    # Run the FastAPI app
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )