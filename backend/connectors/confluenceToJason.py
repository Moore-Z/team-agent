import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Force using absolute path to set project root directory
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Force using absolute path to load .env file
load_dotenv(project_root / '.env', override=True)

from backend.connectors.confluence import ConfluenceConnector
import json
from typing import List, Dict

# Load environment variables
CONFLUENCE_URL = os.getenv('CONFLUENCE_URL')
USERNAME = os.getenv('CONFLUENCE_USERNAME')
API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN')
PERSONAL_SPACE_KEY = os.getenv('CONFLUENCE_PERSONAL_SPACE_KEY')

class FormConfluenceDataToPersist(ConfluenceConnector):
    def __init__(self, url: str = None, username: str = None, api_token: str = None):
        # Use passed parameters or environment variables
        confluence_url = url or CONFLUENCE_URL
        confluence_username = username or USERNAME
        confluence_api_token = api_token or API_TOKEN

        # Debug information: check credentials
        if not confluence_url:
            raise ValueError("Confluence URL not configured")
        if not confluence_username:
            raise ValueError("Confluence username not configured")
        if not confluence_api_token:
            raise ValueError("Confluence API Token not configured")

        # Call parent class initialization method
        super().__init__(confluence_url, confluence_username, confluence_api_token)

        self.personal_space_key = PERSONAL_SPACE_KEY

    def fetch_personal_space_pages(self, limit: int = 100) -> List[Dict]:
        """Fetch all pages from personal space"""
        if not self.personal_space_key:
            raise ValueError("Personal space key not configured")
        return self.fetch_pages(self.personal_space_key, limit)

    def process_and_save_pages_to_json(self, space_key: str = None, output_file: str = "confluence_data.json") -> str:
        """Process pages and save to JSON format"""
        target_space = space_key or self.personal_space_key
        if not target_space:
            raise ValueError("No space key provided and personal space key not configured")

        # Fetch pages
        pages = self.fetch_pages(target_space)

        # Process each page
        processed_pages = []
        for page in pages:
            processed_page = self.process_page_content(page)
            processed_pages.append(processed_page)

        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_pages, f, ensure_ascii=False, indent=2)

        return f"Successfully saved {len(processed_pages)} pages to {output_file}"


# Test code
if __name__ == "__main__":
    def test_confluence_connector():
        """Test Confluence connector functionality"""
        try:
            print("🚀 Starting Confluence connector test...")

            # Add environment diagnostics
            print(f"\n🔍 Environment diagnostics:")
            print(f"   📁 Working directory: {os.getcwd()}")
            print(f"   📄 Script location: {__file__}")
            print(f"   📁 Project root: {project_root}")
            print(f"   📄 .env file: {project_root / '.env'}")
            print(f"   🔧 URL config: {'Set' if CONFLUENCE_URL else 'Not set'}")
            print(f"   👤 Username config: {'Set' if USERNAME else 'Not set'}")
            print(f"   🔑 API Token: {'Set' if API_TOKEN else 'Not set'}")
            print(f"   🏠 Personal space: {'Set' if PERSONAL_SPACE_KEY else 'Not set'}")

            # Create connector instance
            connector = FormConfluenceDataToPersist()
            print("✅ Connector initialization successful")

            # Test fetching space list
            print("\n📂 Testing space list retrieval...")
            spaces = connector.fetch_spaces()
            print(f"✅ Found {len(spaces)} spaces")
            for space in spaces[:3]:  # Only show first 3
                print(f"   - {space.get('name')} ({space.get('key')})")

            # Test getting personal space info
            if connector.personal_space_key:
                print(f"\n🏠 Testing personal space info retrieval: {connector.personal_space_key}")
                try:
                    personal_space = connector.fetch_space_by_key(connector.personal_space_key)
                    print(f"✅ Personal space: {personal_space.get('name')}")
                except Exception as e:
                    print(f"⚠️ Failed to get personal space: {e}")

                # Test getting personal space pages
                print(f"\n📄 Testing personal space page retrieval...")
                try:
                    pages = connector.fetch_personal_space_pages(limit=5)
                    print(f"✅ Found {len(pages)} pages")
                    for page in pages:
                        print(f"   - {page.get('title')}")
                except Exception as e:
                    print(f"⚠️ Failed to get pages: {e}")
            else:
                print("⚠️ Personal space key not configured, skipping personal space test")

            # Test processing and saving data (if there are pages)
            if connector.personal_space_key:
                print(f"\n💾 Testing data save to JSON...")
                try:
                    result = connector.process_and_save_pages_to_json(
                        output_file="data/jason/test_confluence_data.json"
                    )
                    print(f"✅ {result}")
                except Exception as e:
                    print(f"⚠️ Failed to save data: {e}")

            print("\n🎉 Test completed!")

        except Exception as e:
            print(f"❌ Test failed: {e}")
            print("Please check environment variable configuration:")
            print("- CONFLUENCE_URL")
            print("- CONFLUENCE_USERNAME")
            print("- CONFLUENCE_API_TOKEN")
            print("- CCONFLUENCE_PERSONAL_SPACE_KEY")

    def test_environment_variables():
        """Check environment variable configuration"""
        print("🔧 Checking environment variable configuration...")

        required_vars = {
            'CONFLUENCE_URL': CONFLUENCE_URL,
            'CONFLUENCE_USERNAME': USERNAME,
            'CONFLUENCE_API_TOKEN': API_TOKEN,
            'CCONFLUENCE_PERSONAL_SPACE_KEY': PERSONAL_SPACE_KEY
        }

        missing_vars = []
        for var_name, var_value in required_vars.items():
            if var_value:
                print(f"✅ {var_name}: Configured")
            else:
                print(f"❌ {var_name}: Not configured")
                missing_vars.append(var_name)

        if missing_vars:
            print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
            print("Please configure these variables in .env file")
            return False
        else:
            print("\n✅ All environment variables are configured")
            return True

    # Run tests
    print("=" * 50)
    print("Confluence Connector Test")
    print("=" * 50)

    # First check environment variables
    if test_environment_variables():
        print("\n" + "=" * 50)
        # Then run functionality tests
        test_confluence_connector()
    else:
        print("\n❌ Environment variable configuration incomplete, skipping functionality tests")