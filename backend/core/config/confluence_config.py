"""
Confluence Configuration Manager
Handles multiple customer configurations dynamically
"""
import os
from typing import Dict, Optional
from dataclasses import dataclass
import json

@dataclass
class ConfluenceConfig:
    """Configuration for a single Confluence instance"""
    url: str
    username: str
    api_token: str
    space_key: Optional[str] = None
    customer_id: Optional[str] = None

class ConfluenceConfigManager:
    """Manage multiple customer Confluence configurations"""

    def __init__(self, config_file: str = "data/customer_configs.json"):
        self.config_file = config_file
        self.configs: Dict[str, ConfluenceConfig] = {}
        self.load_configs()

    def load_configs(self):
        """Load customer configurations from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    for customer_id, config_data in data.items():
                        self.configs[customer_id] = ConfluenceConfig(**config_data)
            except Exception as e:
                print(f"Error loading configs: {e}")

    def save_configs(self):
        """Save customer configurations to file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        data = {}
        for customer_id, config in self.configs.items():
            data[customer_id] = {
                'url': config.url,
                'username': config.username,
                'api_token': config.api_token,
                'space_key': config.space_key,
                'customer_id': config.customer_id
            }

        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_customer(self, customer_id: str, url: str, username: str,
                    api_token: str, space_key: Optional[str] = None) -> bool:
        """Add a new customer configuration"""
        try:
            # Validate the configuration by testing connection
            if self.test_confluence_connection(url, username, api_token):
                self.configs[customer_id] = ConfluenceConfig(
                    url=url,
                    username=username,
                    api_token=api_token,
                    space_key=space_key,
                    customer_id=customer_id
                )
                self.save_configs()
                return True
            return False
        except Exception as e:
            print(f"Error adding customer: {e}")
            return False

    def get_customer_config(self, customer_id: str) -> Optional[ConfluenceConfig]:
        """Get configuration for a specific customer"""
        return self.configs.get(customer_id)

    def test_confluence_connection(self, url: str, username: str, api_token: str) -> bool:
        """Test if Confluence credentials are valid"""
        import requests
        from requests.auth import HTTPBasicAuth

        try:
            # Test API call to get user info
            test_url = f"{url.rstrip('/')}/rest/api/user/current"
            response = requests.get(
                test_url,
                auth=HTTPBasicAuth(username, api_token),
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def list_customers(self) -> list:
        """List all configured customers"""
        return list(self.configs.keys())

# Example usage for customer onboarding
def onboard_customer(customer_id: str, confluence_url: str,
                    username: str, api_token: str, space_key: str = None):
    """
    Onboard a new customer with their Confluence credentials

    Args:
        customer_id: Unique identifier for the customer
        confluence_url: Customer's Confluence URL (e.g., https://company.atlassian.net)
        username: Customer's email/username
        api_token: Customer's API token
        space_key: Optional specific space to focus on

    Returns:
        bool: True if successful, False otherwise
    """
    config_manager = ConfluenceConfigManager()

    print(f"🔄 Onboarding customer: {customer_id}")
    print(f"🌐 Confluence URL: {confluence_url}")

    # Test connection first
    if config_manager.test_confluence_connection(confluence_url, username, api_token):
        print("✅ Confluence connection successful!")

        # Add customer configuration
        if config_manager.add_customer(customer_id, confluence_url, username, api_token, space_key):
            print(f"🎉 Customer {customer_id} onboarded successfully!")
            return True
        else:
            print("❌ Failed to save customer configuration")
            return False
    else:
        print("❌ Confluence connection failed. Please check credentials.")
        return False

if __name__ == "__main__":
    # Example onboarding
    success = onboard_customer(
        customer_id="demo_customer",
        confluence_url="https://company.atlassian.net",
        username="customer@company.com",
        api_token="ATATT3xFfGF0...",  # Customer's API token
        space_key="PROJ"  # Optional
    )

    if success:
        print("Customer onboarded! Ready to sync their Confluence data.")