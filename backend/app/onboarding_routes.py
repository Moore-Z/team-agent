"""
Customer Onboarding API Routes
Provides endpoints for customers to connect their Confluence instances
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from backend.core.config.confluence_config import ConfluenceConfigManager, onboard_customer

router = APIRouter(prefix="/api/onboarding", tags=["Customer Onboarding"])

class ConfluenceCredentials(BaseModel):
    customer_id: str
    confluence_url: str
    username: str
    api_token: str
    space_key: Optional[str] = None

class OnboardingResponse(BaseModel):
    success: bool
    message: str
    customer_id: Optional[str] = None

@router.post("/confluence", response_model=OnboardingResponse)
async def onboard_confluence_customer(credentials: ConfluenceCredentials):
    """
    Onboard a new customer with their Confluence credentials

    The customer needs to:
    1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
    2. Create a new API token
    3. Provide their Confluence URL, email, and API token
    """
    try:
        success = onboard_customer(
            customer_id=credentials.customer_id,
            confluence_url=credentials.confluence_url,
            username=credentials.username,
            api_token=credentials.api_token,
            space_key=credentials.space_key
        )

        if success:
            return OnboardingResponse(
                success=True,
                message=f"Customer {credentials.customer_id} onboarded successfully!",
                customer_id=credentials.customer_id
            )
        else:
            return OnboardingResponse(
                success=False,
                message="Failed to connect to Confluence. Please check your credentials."
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/test-connection")
async def test_confluence_connection(
    confluence_url: str,
    username: str,
    api_token: str
):
    """Test Confluence connection without saving credentials"""
    config_manager = ConfluenceConfigManager()

    is_valid = config_manager.test_confluence_connection(
        confluence_url, username, api_token
    )

    return {
        "valid": is_valid,
        "message": "Connection successful!" if is_valid else "Connection failed. Check credentials."
    }

@router.get("/customers")
async def list_customers():
    """List all onboarded customers"""
    config_manager = ConfluenceConfigManager()
    customers = config_manager.list_customers()

    return {
        "customers": customers,
        "count": len(customers)
    }

@router.delete("/customer/{customer_id}")
async def remove_customer(customer_id: str):
    """Remove a customer configuration"""
    config_manager = ConfluenceConfigManager()

    if customer_id in config_manager.configs:
        del config_manager.configs[customer_id]
        config_manager.save_configs()
        return {"success": True, "message": f"Customer {customer_id} removed"}
    else:
        raise HTTPException(status_code=404, detail="Customer not found")

# Add instructions endpoint
@router.get("/instructions")
async def get_onboarding_instructions():
    """Get step-by-step instructions for customers"""
    return {
        "title": "How to Connect Your Confluence",
        "steps": [
            {
                "step": 1,
                "title": "Get your Confluence URL",
                "description": "Find your Confluence URL (e.g., https://yourcompany.atlassian.net)"
            },
            {
                "step": 2,
                "title": "Create API Token",
                "description": "Go to https://id.atlassian.com/manage-profile/security/api-tokens",
                "details": "Click 'Create API token', give it a name, and copy the token"
            },
            {
                "step": 3,
                "title": "Test Connection",
                "description": "Use the /test-connection endpoint to verify your credentials"
            },
            {
                "step": 4,
                "title": "Complete Onboarding",
                "description": "Submit your credentials through the /confluence endpoint"
            }
        ],
        "required_info": [
            "Confluence URL",
            "Email address (username)",
            "API Token",
            "Space Key (optional - specific space to focus on)"
        ]
    }